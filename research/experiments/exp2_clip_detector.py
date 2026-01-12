"""
Experiment 2: Test CLIP-based deepfake detection (yermandy/deepfake-detection)

This experiment tests the CLIP-based detector which achieved 96% AUC on Celeb-DF-v2.
"""

import json
import logging
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
import torch
from PIL import Image

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.deepfake_detector.analyzers.video_analyzer import VideoAnalyzer
from src.deepfake_detector.analyzers.face_analyzer import FaceAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_and_install_clip():
    """Check if CLIP is installed, install if needed."""
    try:
        import clip
        return True
    except ImportError:
        logger.info("Installing CLIP...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "git+https://github.com/openai/CLIP.git", "-q"])
        return True


class CLIPDeepfakeDetector:
    """DeepFake detector using CLIP-based approach from yermandy."""

    def __init__(self, device: str = "auto"):
        """Initialize the CLIP detector."""
        self.device = self._resolve_device(device)
        self.model = None
        self.preprocess = None

    def _resolve_device(self, device: str) -> str:
        """Resolve device to use."""
        if device == "auto":
            return "cuda" if torch.cuda.is_available() else "cpu"
        return device

    def load_model(self):
        """Load the CLIP model."""
        import clip

        logger.info("Loading CLIP ViT-L/14 model...")
        start = time.time()

        self.model, self.preprocess = clip.load("ViT-L/14", device=self.device)
        self.model.eval()

        logger.info("CLIP model loaded in %.2fs on %s", time.time() - start, self.device)

    @torch.no_grad()
    def predict_image(self, image) -> dict:
        """
        Predict if an image is real or fake using CLIP features.

        For deepfake detection, we use a simple approach:
        - Extract CLIP visual features
        - Use text prompts to classify

        Args:
            image: PIL Image or numpy array (RGB)

        Returns:
            dict with label and scores
        """
        import clip

        if isinstance(image, np.ndarray):
            pil_image = Image.fromarray(image)
        else:
            pil_image = image

        # Preprocess image
        image_tensor = self.preprocess(pil_image).unsqueeze(0).to(self.device)

        # Text prompts for classification
        text_prompts = [
            "a real authentic photograph of a human face",
            "a deepfake manipulated synthetic AI-generated face"
        ]
        text_tokens = clip.tokenize(text_prompts).to(self.device)

        # Get features
        image_features = self.model.encode_image(image_tensor)
        text_features = self.model.encode_text(text_tokens)

        # Normalize
        image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)

        # Compute similarity
        similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)

        real_prob = similarity[0, 0].item()
        fake_prob = similarity[0, 1].item()

        label = "FAKE" if fake_prob > real_prob else "REAL"

        return {
            "label": label,
            "confidence": max(real_prob, fake_prob),
            "fake_probability": fake_prob,
            "real_probability": real_prob,
        }


def analyze_video(video_path: str, detector: CLIPDeepfakeDetector, num_frames: int = 30):
    """Analyze a video for deepfakes using the CLIP detector."""
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
    """Run Experiment 2 on given videos."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Check CLIP installation
    check_and_install_clip()

    # Initialize detector
    detector = CLIPDeepfakeDetector(device="auto")
    detector.load_model()

    # Results storage
    experiment_results = {
        "experiment_id": "exp2_clip_detector",
        "model": "CLIP ViT-L/14 (zero-shot)",
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
    results_path = output_dir / f"exp2_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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
    print("EXPERIMENT 2 SUMMARY: CLIP ViT-L/14 (Zero-Shot)")
    print("=" * 60)
    for video_name, video_results in results["videos"].items():
        agg = video_results["aggregated"]
        print(f"\n{video_name}:")
        print(f"  Verdict: {agg['verdict']}")
        print(f"  Confidence: {agg['confidence']*100:.1f}%")
