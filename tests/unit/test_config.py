"""Unit tests for config module."""

import os
from pathlib import Path

import pytest
import yaml

from deepfake_detector.utils.config import (
    AnalysisConfig,
    Config,
    DetectionConfig,
    LoggingConfig,
    OutputConfig,
    VideoConfig,
    load_config,
)


class TestDefaultConfig:
    """Tests for default configuration values."""

    def test_detection_defaults(self) -> None:
        """Test default detection configuration."""
        config = DetectionConfig()
        assert config.model == "vit-deepfake"
        assert config.confidence_threshold == 0.5
        assert config.num_frames == 30
        assert config.sample_rate == 10

    def test_video_defaults(self) -> None:
        """Test default video configuration."""
        config = VideoConfig()
        assert config.max_duration == 300
        assert config.frame_size == (224, 224)
        assert "mp4" in config.supported_formats

    def test_analysis_defaults(self) -> None:
        """Test default analysis configuration."""
        config = AnalysisConfig()
        assert config.face_detection is True
        assert config.temporal_analysis is True
        assert config.artifact_detection is True
        assert config.av_sync_check is False

    def test_output_defaults(self) -> None:
        """Test default output configuration."""
        config = OutputConfig()
        assert config.include_reasoning is True
        assert config.generate_visualization is False
        assert config.output_format == "text"

    def test_logging_defaults(self) -> None:
        """Test default logging configuration."""
        config = LoggingConfig()
        assert config.level == "INFO"
        assert config.log_file is None


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_config_with_defaults(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test loading config with default values."""
        # Clear any environment variables that might affect test
        for key in list(os.environ.keys()):
            if key.startswith(("DEFAULT_", "CONFIDENCE_", "NUM_FRAMES")):
                monkeypatch.delenv(key, raising=False)

        config = load_config()

        assert isinstance(config, Config)
        assert isinstance(config.detection, DetectionConfig)
        assert isinstance(config.video, VideoConfig)

    def test_load_config_from_yaml(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test loading config from YAML file."""
        # Clear environment variables
        for key in list(os.environ.keys()):
            if key.startswith(("DEFAULT_", "CONFIDENCE_", "NUM_FRAMES")):
                monkeypatch.delenv(key, raising=False)

        config_data = {
            "detection": {
                "model": "xception",
                "confidence_threshold": 0.7,
                "num_frames": 50,
            },
            "output": {"format": "json", "include_reasoning": False},
        }

        config_file = tmp_path / "config.yaml"
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        config = load_config(str(config_file))

        assert config.detection.model == "xception"
        assert config.detection.confidence_threshold == 0.7
        assert config.detection.num_frames == 50
        assert config.output.output_format == "json"
        assert config.output.include_reasoning is False

    def test_env_overrides_yaml(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that environment variables override YAML config."""
        config_data = {"detection": {"model": "xception", "confidence_threshold": 0.7}}

        config_file = tmp_path / "config.yaml"
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        # Set environment variable to override
        monkeypatch.setenv("DEFAULT_MODEL", "efficientnet")
        monkeypatch.setenv("CONFIDENCE_THRESHOLD", "0.8")

        config = load_config(str(config_file))

        # Env should override YAML
        assert config.detection.model == "efficientnet"
        assert config.detection.confidence_threshold == 0.8

    def test_env_gpu_settings(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test GPU settings from environment."""
        monkeypatch.setenv("USE_GPU", "true")
        monkeypatch.setenv("GPU_DEVICE_ID", "1")

        config = load_config()

        assert config.device == "cuda:1"

    def test_env_cpu_settings(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test CPU settings from environment."""
        monkeypatch.setenv("USE_GPU", "false")

        config = load_config()

        assert config.device == "cpu"


class TestConfigDataclasses:
    """Tests for config dataclasses."""

    def test_config_is_mutable(self) -> None:
        """Test that config values can be modified."""
        config = Config()
        config.detection.model = "xception"
        assert config.detection.model == "xception"

    def test_video_config_supported_formats(self) -> None:
        """Test VideoConfig supported formats default."""
        config = VideoConfig()
        expected_formats = ["mp4", "avi", "mov", "mkv", "webm"]
        assert config.supported_formats == expected_formats

    def test_config_nested_structure(self) -> None:
        """Test Config has all nested configs."""
        config = Config()
        assert hasattr(config, "detection")
        assert hasattr(config, "video")
        assert hasattr(config, "analysis")
        assert hasattr(config, "output")
        assert hasattr(config, "logging")
