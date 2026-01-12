"""
Experiment 1: Integrate Deep-Fake-Detector-v2-Model (ViT-based)

This experiment tests the pretrained ViT model from HuggingFace for deepfake detection.
Model: prithivMLmods/Deep-Fake-Detector-v2-Model
"""

import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

import cv2
import torch
from PIL import Image
from transformers import ViTForImageClassification, ViTImageProcessor

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.deepfake_detector.analyzers.video_analyzer import VideoAnalyzer
from src.deepfake_detector.analyzers.face_analyzer import FaceAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ViTDeepfakeDetector:
    """DeepFake detector using pretrained ViT model from HuggingFace."""

    MODEL_NAME = "prithivMLmods/Deep-Fake-Detector-v2-Model"

    def __init__(self, device: str = "auto"):
        """Initialize the ViT detector."""
        self.device = self._resolve_device(device)
        self.model = None
        self.processor = None

    def _resolve_device(self, device: str) -> str:
        """Resolve device to use."""
        if device == "auto":
            return "cuda" if torch.cuda.is_available() else "cpu"
        return device

    def load_model(self):
        """Load the pretrained model from HuggingFace."""
        logger.info("Loading model: %s", self.MODEL_NAME)
        start = time.time()

        self.model = ViTForImageClassification.from_pretrained(self.MODEL_NAME)
        self.processor = ViTImageProcessor.from_pretrained(self.MODEL_NAME)

        if self.device == "cuda":
            self.model = self.model.to(self.device)

        self.model.eval()
        logger.info("Model loaded in %.2fs on %s", time.time() - start, self.device)
        logger.info("Labels: %s", self.model.config.id2label)

    @torch.no_grad()
    def predict_image(self, image) -> dict:
        """
        Predict if an image is real or fake.

        Args:
            image: PIL Image or numpy array (RGB)

        Returns:
            dict with 'label' and 'confidence'
        """
        if isinstance(image, Image.Image):
            pil_image = image
        else:
            # Assume numpy array (RGB)
            pil_image = Image.fromarray(image)

        # Preprocess
        inputs = self.processor(images=pil_image, return_tensors="pt")

        if self.device == "cuda":
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Forward pass
        outputs = self.model(**inputs)
        probs = torch.softmax(outputs.logits, dim=1)

        # Get prediction
        pred_idx = probs.argmax(dim=1).item()
        pred_label = self.model.config.id2label[pred_idx]
        confidence = probs[0, pred_idx].item()

        # Get fake probability specifically
        fake_idx = None
        for idx, label in self.model.config.id2label.items():
            if "fake" in label.lower() or "deepfake" in label.lower():
                fake_idx = idx
                break

        fake_prob = probs[0, fake_idx].item() if fake_idx is not None else 1 - confidence

        return {
            "label": pred_label,
            "confidence": confidence,
            "fake_probability": fake_prob,
            "all_probs": {self.model.config.id2label[i]: probs[0, i].item() for i in range(len(probs[0]))}
        }

    def predict_faces(self, face_crops: list) -> list:
        """Predict on list of face crops."""
        results = []
        for crop in face_crops:
            result = self.predict_image(crop.image)
            results.append(result)
        return results


def analyze_video(video_path: str, detector: ViTDeepfakeDetector, num_frames: int = 30):
    """Analyze a video for deepfakes using the ViT detector."""
    logger.info("Analyzing video: %s", video_path)

    # Load video
    video_analyzer = VideoAnalyzer()
    video_info = video_analyzer.load(video_path)
    logger.info("Video loaded: %s", video_info)

    # Extract frames
    frames = video_analyzer.extract_frames(num_frames)
    logger.info("Extracted %d frames", len(frames))

    # Detect faces
    face_analyzer = FaceAnalyzer()
    all_results = []

    for frame in frames:
        # Detect faces in frame
        boxes = face_analyzer.detect_faces(frame.image)

        if boxes:
            # Crop faces
            face_crops = face_analyzer.crop_faces(frame.image, boxes, frame.index)

            # Predict on each face
            for crop in face_crops:
                result = detector.predict_image(crop.image)
                result["frame_index"] = frame.index
                all_results.append(result)

    return all_results


def aggregate_results(results: list, threshold: float = 0.5) -> dict:
    """Aggregate frame-level results into video verdict."""
    if not results:
        return {
            "verdict": "UNKNOWN",
            "confidence": 0.0,
            "num_frames_analyzed": 0,
            "fake_frame_ratio": 0.0
        }

    # Count fake predictions
    fake_probs = [r["fake_probability"] for r in results]
    avg_fake_prob = sum(fake_probs) / len(fake_probs)
    max_fake_prob = max(fake_probs)
    fake_frames = sum(1 for p in fake_probs if p > threshold)

    # Weighted combination
    confidence = 0.7 * avg_fake_prob + 0.3 * max_fake_prob
    verdict = "FAKE" if confidence >= threshold else "NOT_FAKE"

    return {
        "verdict": verdict,
        "confidence": confidence,
        "avg_fake_probability": avg_fake_prob,
        "max_fake_probability": max_fake_prob,
        "num_frames_analyzed": len(results),
        "fake_frame_ratio": fake_frames / len(results),
        "threshold": threshold
    }


def run_experiment(video_paths: list, output_dir: str = "research/results"):
    """Run Experiment 1 on given videos."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize detector
    detector = ViTDeepfakeDetector(device="auto")
    detector.load_model()

    # Results storage
    experiment_results = {
        "experiment_id": "exp1_vit_detector",
        "model": ViTDeepfakeDetector.MODEL_NAME,
        "timestamp": datetime.now().isoformat(),
        "videos": {}
    }

    for video_path in video_paths:
        video_name = Path(video_path).name
        logger.info("\n" + "=" * 50)
        logger.info("Processing: %s", video_name)
        logger.info("=" * 50)

        start_time = time.time()

        # Analyze video
        frame_results = analyze_video(video_path, detector, num_frames=30)

        # Aggregate results
        aggregated = aggregate_results(frame_results)
        processing_time = time.time() - start_time

        # Store results
        experiment_results["videos"][video_name] = {
            "aggregated": aggregated,
            "processing_time_seconds": processing_time,
            "frame_results": frame_results
        }

        # Print summary
        logger.info("\nResults for %s:", video_name)
        logger.info("  Verdict: %s", aggregated["verdict"])
        logger.info("  Confidence: %.1f%%", aggregated["confidence"] * 100)
        logger.info("  Avg Fake Prob: %.1f%%", aggregated["avg_fake_probability"] * 100)
        logger.info("  Fake Frame Ratio: %.1f%%", aggregated["fake_frame_ratio"] * 100)
        logger.info("  Processing Time: %.2fs", processing_time)

    # Save results
    results_path = output_dir / f"exp1_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_path, "w") as f:
        json.dump(experiment_results, f, indent=2, default=str)

    logger.info("\nResults saved to: %s", results_path)

    return experiment_results


if __name__ == "__main__":
    # Test videos
    test_videos = [
        "data/fake/man_hair.1.mp4",
        "data/fake/man_hair.2.mp4"
    ]

    # Run experiment
    results = run_experiment(test_videos)

    # Summary
    print("\n" + "=" * 60)
    print("EXPERIMENT 1 SUMMARY: Deep-Fake-Detector-v2-Model (ViT)")
    print("=" * 60)
    for video_name, video_results in results["videos"].items():
        agg = video_results["aggregated"]
        print(f"\n{video_name}:")
        print(f"  Verdict: {agg['verdict']}")
        print(f"  Confidence: {agg['confidence']*100:.1f}%")
