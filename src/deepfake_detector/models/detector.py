"""DeepFake detection model module."""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import cv2
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

# HuggingFace model for deepfake detection (from research findings)
HUGGINGFACE_MODEL = "prithivMLmods/Deep-Fake-Detector-v2-Model"


@dataclass
class FrameResult:
    """Detection result for a single frame."""

    frame_index: int
    confidence: float
    faces_detected: int


@dataclass
class DetectionIndicator:
    """A specific indicator of deepfake detection."""

    name: str
    detected: bool
    score: float
    description: str


@dataclass
class AggregatedResult:
    """Aggregated detection result for a video."""

    verdict: str  # "FAKE" or "NOT_FAKE"
    confidence: float
    indicators: list[DetectionIndicator]
    frame_results: list[FrameResult]


class DeepFakeDetector:
    """
    Main deepfake detection model.

    Uses image classification to detect manipulated faces.
    """

    def __init__(
        self,
        model_name: str = "vit-deepfake",
        device: str = "auto",
        cache_dir: str = "./models/cache",
    ) -> None:
        """
        Initialize the deepfake detector.

        Args:
            model_name: Name of the detection model ('vit-deepfake', 'efficientnet').
            device: Device to run inference on (cpu/cuda/auto).
            cache_dir: Directory to cache model weights.
        """
        self.model_name = model_name
        self.device = self._resolve_device(device)
        self.cache_dir = Path(cache_dir)
        self._model: Any = None
        self._processor: Any = None
        self._model_loaded = False
        self._transform: Any = None
        self._use_huggingface = model_name == "vit-deepfake"

    def _resolve_device(self, device: str) -> str:
        """Resolve 'auto' device to actual device."""
        if device == "auto":
            try:
                import torch  # pylint: disable=import-outside-toplevel

                return "cuda" if torch.cuda.is_available() else "cpu"
            except ImportError:
                return "cpu"
        return device

    def load_model(self) -> None:
        """
        Load the detection model.

        Downloads model weights if not cached.
        """
        logger.info("Loading deepfake detection model: %s", self.model_name)

        try:
            if self._use_huggingface:
                self._load_huggingface_model()
            else:
                self._load_pytorch_model()
            self._model_loaded = True
            logger.info("Model loaded successfully on device: %s", self.device)
        except ImportError as exc:
            logger.warning(
                "Required library not available: %s. Using statistical analysis fallback.",
                exc,
            )
            self._model_loaded = False
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.warning(
                "Failed to load model: %s. Using fallback analysis.",
                exc,
            )
            self._model_loaded = False

    def _load_huggingface_model(self) -> None:
        """Load pretrained ViT model from HuggingFace for deepfake detection."""
        # pylint: disable=import-outside-toplevel
        from transformers import AutoImageProcessor, AutoModelForImageClassification

        logger.info("Loading HuggingFace model: %s", HUGGINGFACE_MODEL)

        self._processor = AutoImageProcessor.from_pretrained(
            HUGGINGFACE_MODEL,
            cache_dir=self.cache_dir,
        )
        self._model = AutoModelForImageClassification.from_pretrained(
            HUGGINGFACE_MODEL,
            cache_dir=self.cache_dir,
        )

        # Move to device if CUDA available
        if self.device.startswith("cuda"):
            self._model = self._model.to(self.device)

        self._model.eval()
        logger.info(
            "HuggingFace ViT model loaded: %d parameters",
            sum(p.numel() for p in self._model.parameters()),
        )

    def _load_pytorch_model(self) -> None:
        """Load PyTorch-based model."""
        # pylint: disable=import-outside-toplevel
        import torch
        from torchvision import models, transforms

        # Use EfficientNet as base model
        if self.model_name == "efficientnet":
            self._model = models.efficientnet_b0(weights=None)
            # Modify classifier for binary classification
            num_features = self._model.classifier[1].in_features
            self._model.classifier[1] = torch.nn.Linear(num_features, 2)
        else:
            # Default to ResNet
            self._model = models.resnet18(weights=None)
            num_features = self._model.fc.in_features
            self._model.fc = torch.nn.Linear(num_features, 2)

        self._model.eval()

        if self.device.startswith("cuda"):
            self._model = self._model.to(self.device)

        # Define preprocessing transform
        self._transform = transforms.Compose(
            [
                transforms.ToPILImage(),
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225],
                ),
            ]
        )

    def predict(self, face_crops: list) -> list[float]:
        """
        Run prediction on face crops.

        Args:
            face_crops: List of FaceCrop objects.

        Returns:
            List of confidence scores (0.0 = real, 1.0 = fake).
        """
        if not face_crops:
            return []

        if self._model_loaded:
            if self._use_huggingface:
                return self._predict_with_huggingface(face_crops)
            return self._predict_with_model(face_crops)
        return self._predict_with_fallback(face_crops)

    def _predict_with_huggingface(self, face_crops: list) -> list[float]:
        """Run prediction using HuggingFace ViT model."""
        import torch  # pylint: disable=import-outside-toplevel

        scores = []

        with torch.no_grad():
            for crop in face_crops:
                # Convert numpy array to PIL Image
                if isinstance(crop.image, np.ndarray):
                    pil_image = Image.fromarray(crop.image)
                else:
                    pil_image = crop.image

                # Preprocess with HuggingFace processor
                inputs = self._processor(images=pil_image, return_tensors="pt")

                if self.device.startswith("cuda"):
                    inputs = {k: v.to(self.device) for k, v in inputs.items()}

                # Forward pass
                outputs = self._model(**inputs)
                probs = torch.nn.functional.softmax(outputs.logits, dim=1)

                # Get fake probability
                # Model labels: 0=Real, 1=Fake (check model config)
                fake_idx = 1
                if hasattr(self._model.config, "id2label"):
                    for idx, label in self._model.config.id2label.items():
                        if "fake" in label.lower():
                            fake_idx = int(idx)
                            break

                fake_prob = probs[0, fake_idx].item()
                scores.append(fake_prob)

        return scores

    def _predict_with_model(self, face_crops: list) -> list[float]:
        """Run prediction using the loaded model."""
        import torch  # pylint: disable=import-outside-toplevel

        scores = []

        with torch.no_grad():
            for crop in face_crops:
                # Preprocess
                tensor = self._transform(crop.image)
                tensor = tensor.unsqueeze(0)

                if self.device.startswith("cuda"):
                    tensor = tensor.to(self.device)

                # Forward pass
                output = self._model(tensor)
                probs = torch.nn.functional.softmax(output, dim=1)

                # Get fake probability (assuming class 1 is fake)
                fake_prob = probs[0, 1].item()
                scores.append(fake_prob)

        return scores

    def _predict_with_fallback(self, face_crops: list) -> list[float]:
        """
        Fallback prediction using statistical analysis.

        Analyzes image artifacts that may indicate manipulation.
        """
        scores = []

        for crop in face_crops:
            score = self._analyze_artifacts(crop.image)
            scores.append(score)

        return scores

    def _analyze_artifacts(self, image: np.ndarray) -> float:
        """
        Analyze image for manipulation artifacts.

        This is a simplified heuristic-based analysis.
        Real detection would use trained deep learning models.

        Args:
            image: Face crop as numpy array.

        Returns:
            Score between 0 (likely real) and 1 (likely fake).
        """
        indicators = []

        # 1. Check for blur/sharpness inconsistencies
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

        # Very low or very high variance can indicate manipulation
        if laplacian_var < 50:
            indicators.append(0.3)  # Too blurry
        elif laplacian_var > 2000:
            indicators.append(0.2)  # Oversharpened
        else:
            indicators.append(0.0)

        # 2. Check color histogram for anomalies
        hist_score = self._analyze_color_histogram(image)
        indicators.append(hist_score)

        # 3. Check for edge artifacts
        edge_score = self._analyze_edge_artifacts(image)
        indicators.append(edge_score)

        # 4. Check for noise patterns
        noise_score = self._analyze_noise_pattern(image)
        indicators.append(noise_score)

        # Aggregate scores
        if indicators:
            return float(np.mean(indicators))
        return 0.5

    def _analyze_color_histogram(self, image: np.ndarray) -> float:
        """Analyze color distribution for anomalies."""
        # Calculate histogram for each channel
        histograms = []
        for i in range(3):
            hist = cv2.calcHist([image], [i], None, [256], [0, 256])
            histograms.append(hist.flatten())

        # Check for unusual spikes or gaps
        score = 0.0
        for hist in histograms:
            # Normalize
            hist = hist / (hist.sum() + 1e-6)

            # Check entropy (low entropy may indicate manipulation)
            entropy = -np.sum(hist * np.log2(hist + 1e-10))
            if entropy < 5.0:
                score += 0.1

        return min(score, 0.3)

    def _analyze_edge_artifacts(self, image: np.ndarray) -> float:
        """Analyze edges for manipulation artifacts."""
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        # Detect edges
        edges = cv2.Canny(gray, 50, 150)

        # Check edge density in border regions
        h, w = edges.shape
        border = int(min(h, w) * 0.1)

        border_edges = np.concatenate(
            [
                edges[:border, :].flatten(),
                edges[-border:, :].flatten(),
                edges[:, :border].flatten(),
                edges[:, -border:].flatten(),
            ]
        )

        center_edges = edges[border:-border, border:-border].flatten()

        border_density = border_edges.mean() / 255.0
        center_density = center_edges.mean() / 255.0

        # Unusual border/center ratio may indicate blending
        if border_density > center_density * 2:
            return 0.2
        return 0.0

    def _analyze_noise_pattern(self, image: np.ndarray) -> float:
        """Analyze noise pattern for inconsistencies."""
        # Extract high-frequency components
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY).astype(float)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        noise = gray - blurred

        # Check noise standard deviation
        noise_std = np.std(noise)

        # Unusual noise levels may indicate manipulation
        if noise_std < 2.0 or noise_std > 20.0:
            return 0.15
        return 0.0

    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._model_loaded


class ResultAggregator:
    """Aggregates per-frame results into final verdict."""

    def __init__(self, threshold: float = 0.5) -> None:
        """
        Initialize the aggregator.

        Args:
            threshold: Confidence threshold for fake classification.
        """
        self.threshold = threshold

    def aggregate(
        self,
        frame_scores: list[float],
        frame_indices: list[int],
        faces_per_frame: Optional[list[int]] = None,
    ) -> AggregatedResult:
        """
        Aggregate frame-level scores into video-level result.

        Args:
            frame_scores: Confidence scores per frame.
            frame_indices: Frame indices corresponding to scores.
            faces_per_frame: Number of faces detected per frame.

        Returns:
            AggregatedResult with verdict and reasoning.
        """
        if not frame_scores:
            return AggregatedResult(
                verdict="NOT_FAKE",
                confidence=0.0,
                indicators=[
                    DetectionIndicator(
                        name="no_faces",
                        detected=True,
                        score=0.0,
                        description="No faces detected in video",
                    )
                ],
                frame_results=[],
            )

        # Calculate overall confidence
        mean_score = float(np.mean(frame_scores))
        max_score = float(np.max(frame_scores))

        # Use weighted combination
        confidence = 0.7 * mean_score + 0.3 * max_score

        # Determine verdict
        verdict = "FAKE" if confidence >= self.threshold else "NOT_FAKE"

        # Build frame results
        frame_results = []
        for i, (score, idx) in enumerate(zip(frame_scores, frame_indices)):
            faces = faces_per_frame[i] if faces_per_frame else 1
            frame_results.append(
                FrameResult(
                    frame_index=idx,
                    confidence=score,
                    faces_detected=faces,
                )
            )

        # Build indicators
        indicators = self._build_indicators(frame_scores, confidence)

        logger.info(
            "Aggregated result: %s (confidence: %.1f%%)",
            verdict,
            confidence * 100,
        )

        return AggregatedResult(
            verdict=verdict,
            confidence=confidence,
            indicators=indicators,
            frame_results=frame_results,
        )

    def set_threshold(self, threshold: float) -> None:
        """
        Update the confidence threshold.

        Args:
            threshold: New threshold value (0.0-1.0).
        """
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("Threshold must be between 0.0 and 1.0")
        self.threshold = threshold

    def _build_indicators(
        self,
        frame_scores: list[float],
        confidence: float,
    ) -> list[DetectionIndicator]:
        """Build list of detection indicators."""
        indicators = []

        # Face manipulation indicator
        high_score_frames = sum(1 for s in frame_scores if s > 0.5)
        face_manip_score = high_score_frames / max(len(frame_scores), 1)

        indicators.append(
            DetectionIndicator(
                name="face_manipulation",
                detected=face_manip_score > 0.3,
                score=face_manip_score,
                description=(
                    f"Face manipulation detected in "
                    f"{high_score_frames}/{len(frame_scores)} frames"
                ),
            )
        )

        # Temporal consistency indicator
        if len(frame_scores) > 1:
            score_variance = float(np.var(frame_scores))
            temporal_inconsistent = score_variance > 0.1

            indicators.append(
                DetectionIndicator(
                    name="temporal_consistency",
                    detected=temporal_inconsistent,
                    score=min(score_variance * 2, 1.0),
                    description=(
                        "Inconsistent detection across frames"
                        if temporal_inconsistent
                        else "Consistent detection across frames"
                    ),
                )
            )

        # Overall confidence indicator
        indicators.append(
            DetectionIndicator(
                name="overall_confidence",
                detected=confidence >= self.threshold,
                score=confidence,
                description=(
                    f"Overall confidence: {confidence:.1%} "
                    f"(threshold: {self.threshold:.1%})"
                ),
            )
        )

        return indicators
