"""Configuration management for DeepFake Detector."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml
from dotenv import load_dotenv


@dataclass
class DetectionConfig:
    """Detection-related configuration."""

    model: str = "vit-deepfake"
    confidence_threshold: float = 0.5
    num_frames: int = 30
    sample_rate: int = 10


@dataclass
class VideoConfig:
    """Video processing configuration."""

    max_duration: int = 300
    frame_size: tuple[int, int] = (224, 224)
    supported_formats: list[str] = field(
        default_factory=lambda: ["mp4", "avi", "mov", "mkv", "webm"]
    )


@dataclass
class AnalysisConfig:
    """Analysis options configuration."""

    face_detection: bool = True
    temporal_analysis: bool = True
    artifact_detection: bool = True
    av_sync_check: bool = False


@dataclass
class OutputConfig:
    """Output configuration."""

    include_reasoning: bool = True
    generate_visualization: bool = False
    output_format: str = "text"


@dataclass
class LoggingConfig:
    """Logging configuration."""

    level: str = "INFO"
    log_file: Optional[str] = None


@dataclass
class Config:
    """Main configuration container."""

    detection: DetectionConfig = field(default_factory=DetectionConfig)
    video: VideoConfig = field(default_factory=VideoConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    device: str = "auto"
    model_cache_dir: str = "./models/cache"


def _get_env_value(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get environment variable value with optional default."""
    return os.environ.get(key, default)


def _get_env_bool(key: str, default: bool = False) -> bool:
    """Get boolean value from environment variable."""
    value = os.environ.get(key)
    if value is None:
        return default
    return value.lower() in ("true", "1", "yes", "on")


def _get_env_int(key: str, default: int) -> int:
    """Get integer value from environment variable."""
    value = os.environ.get(key)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _get_env_float(key: str, default: float) -> float:
    """Get float value from environment variable."""
    value = os.environ.get(key)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def load_config(config_path: Optional[str] = None) -> Config:
    """
    Load configuration from YAML file and environment variables.

    Priority (highest to lowest):
    1. Environment variables
    2. Custom config file (if provided)
    3. Default config file (config.yaml)
    4. Built-in defaults

    Args:
        config_path: Optional path to custom configuration file.

    Returns:
        Config object with all settings.
    """
    # Load .env file if present
    load_dotenv()

    config = Config()

    # Try to load YAML config
    yaml_config = _load_yaml_config(config_path)
    if yaml_config:
        config = _apply_yaml_config(config, yaml_config)

    # Apply environment variable overrides
    config = _apply_env_overrides(config)

    return config


def _load_yaml_config(config_path: Optional[str] = None) -> Optional[dict]:
    """Load configuration from YAML file."""
    paths_to_try = []

    if config_path:
        paths_to_try.append(Path(config_path))

    # Default config locations
    paths_to_try.extend(
        [
            Path("config.yaml"),
            Path("config.yml"),
            Path.home() / ".deepfake-detector" / "config.yaml",
        ]
    )

    for path in paths_to_try:
        if path.exists():
            with open(path, encoding="utf-8") as config_file:
                return yaml.safe_load(config_file)

    return None


def _apply_yaml_config(config: Config, yaml_data: dict) -> Config:
    """Apply YAML configuration to config object."""
    if "detection" in yaml_data:
        detection = yaml_data["detection"]
        config.detection.model = detection.get("model", config.detection.model)
        config.detection.confidence_threshold = detection.get(
            "confidence_threshold", config.detection.confidence_threshold
        )
        config.detection.num_frames = detection.get(
            "num_frames", config.detection.num_frames
        )
        config.detection.sample_rate = detection.get(
            "sample_rate", config.detection.sample_rate
        )

    if "video" in yaml_data:
        video = yaml_data["video"]
        config.video.max_duration = video.get("max_duration", config.video.max_duration)
        if "frame_size" in video:
            config.video.frame_size = tuple(video["frame_size"])
        if "supported_formats" in video:
            config.video.supported_formats = video["supported_formats"]

    if "analysis" in yaml_data:
        analysis = yaml_data["analysis"]
        config.analysis.face_detection = analysis.get(
            "face_detection", config.analysis.face_detection
        )
        config.analysis.temporal_analysis = analysis.get(
            "temporal_analysis", config.analysis.temporal_analysis
        )
        config.analysis.artifact_detection = analysis.get(
            "artifact_detection", config.analysis.artifact_detection
        )
        config.analysis.av_sync_check = analysis.get(
            "av_sync_check", config.analysis.av_sync_check
        )

    if "output" in yaml_data:
        output = yaml_data["output"]
        config.output.include_reasoning = output.get(
            "include_reasoning", config.output.include_reasoning
        )
        config.output.generate_visualization = output.get(
            "generate_visualization", config.output.generate_visualization
        )
        config.output.output_format = output.get("format", config.output.output_format)

    if "logging" in yaml_data:
        logging_cfg = yaml_data["logging"]
        config.logging.level = logging_cfg.get("level", config.logging.level)
        config.logging.log_file = logging_cfg.get("file", config.logging.log_file)

    return config


def _apply_env_overrides(config: Config) -> Config:
    """Apply environment variable overrides to config."""
    # Detection settings
    model = _get_env_value("DEFAULT_MODEL")
    if model:
        config.detection.model = model

    config.detection.confidence_threshold = _get_env_float(
        "CONFIDENCE_THRESHOLD", config.detection.confidence_threshold
    )
    config.detection.num_frames = _get_env_int(
        "NUM_FRAMES_TO_ANALYZE", config.detection.num_frames
    )
    config.detection.sample_rate = _get_env_int(
        "FRAME_SAMPLE_RATE", config.detection.sample_rate
    )

    # Video settings
    config.video.max_duration = _get_env_int(
        "MAX_VIDEO_DURATION", config.video.max_duration
    )

    # Output settings
    config.output.include_reasoning = _get_env_bool(
        "VERBOSE_OUTPUT", config.output.include_reasoning
    )
    output_format = _get_env_value("OUTPUT_FORMAT")
    if output_format:
        config.output.output_format = output_format

    # Logging settings
    log_level = _get_env_value("LOG_LEVEL")
    if log_level:
        config.logging.level = log_level
    log_file = _get_env_value("LOG_FILE")
    if log_file:
        config.logging.log_file = log_file

    # Device settings
    use_gpu = _get_env_bool("USE_GPU", True)
    gpu_device_id = _get_env_int("GPU_DEVICE_ID", 0)
    if use_gpu:
        config.device = f"cuda:{gpu_device_id}"
    else:
        config.device = "cpu"

    # Model cache directory
    cache_dir = _get_env_value("MODEL_CACHE_DIR")
    if cache_dir:
        config.model_cache_dir = cache_dir

    return config
