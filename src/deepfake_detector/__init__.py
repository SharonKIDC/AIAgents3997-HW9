"""DeepFake Detector Core Package."""

from deepfake_detector.analyzers import (
    BoundingBox,
    FaceAnalyzer,
    FaceCrop,
    Frame,
    VideoAnalyzer,
    VideoInfo,
)
from deepfake_detector.models import (
    AggregatedResult,
    DeepFakeDetector,
    DetectionIndicator,
    FrameResult,
    ResultAggregator,
)
from deepfake_detector.utils import (
    Config,
    ValidationError,
    load_config,
    setup_logging,
)

__version__ = "0.1.0"

__all__ = [
    # Version
    "__version__",
    # Analyzers
    "VideoAnalyzer",
    "VideoInfo",
    "Frame",
    "FaceAnalyzer",
    "BoundingBox",
    "FaceCrop",
    # Models
    "DeepFakeDetector",
    "ResultAggregator",
    "FrameResult",
    "DetectionIndicator",
    "AggregatedResult",
    # Utils
    "Config",
    "load_config",
    "setup_logging",
    "ValidationError",
]
