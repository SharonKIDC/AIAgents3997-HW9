"""Detection models package."""

from deepfake_detector.models.detector import (
    AggregatedResult,
    DeepFakeDetector,
    DetectionIndicator,
    FrameResult,
    ResultAggregator,
)

__all__ = [
    "DeepFakeDetector",
    "ResultAggregator",
    "FrameResult",
    "DetectionIndicator",
    "AggregatedResult",
]
