"""Unit tests for validators module."""

from pathlib import Path

import pytest

from deepfake_detector.utils.validators import (
    ValidationError,
    get_video_format,
    validate_device,
    validate_num_frames,
    validate_output_format,
    validate_threshold,
    validate_video_path,
)


class TestValidateVideoPath:
    """Tests for validate_video_path function."""

    def test_valid_mp4_file(self, tmp_path: Path) -> None:
        """Test validation of existing MP4 file."""
        video_file = tmp_path / "test.mp4"
        video_file.write_bytes(b"fake video content")

        result = validate_video_path(str(video_file))
        assert result == video_file

    def test_valid_avi_file(self, tmp_path: Path) -> None:
        """Test validation of existing AVI file."""
        video_file = tmp_path / "test.avi"
        video_file.write_bytes(b"fake video content")

        result = validate_video_path(str(video_file))
        assert result == video_file

    def test_nonexistent_file(self) -> None:
        """Test that nonexistent file raises ValidationError."""
        with pytest.raises(ValidationError, match="Video file not found"):
            validate_video_path("/nonexistent/path/video.mp4")

    def test_unsupported_format(self, tmp_path: Path) -> None:
        """Test that unsupported format raises ValidationError."""
        video_file = tmp_path / "test.xyz"
        video_file.write_bytes(b"fake content")

        with pytest.raises(ValidationError, match="Unsupported video format"):
            validate_video_path(str(video_file))

    def test_directory_path(self, tmp_path: Path) -> None:
        """Test that directory path raises ValidationError."""
        with pytest.raises(ValidationError, match="Path is not a file"):
            validate_video_path(str(tmp_path))


class TestValidateThreshold:
    """Tests for validate_threshold function."""

    def test_valid_threshold_zero(self) -> None:
        """Test threshold at lower bound."""
        assert validate_threshold(0.0) == 0.0

    def test_valid_threshold_one(self) -> None:
        """Test threshold at upper bound."""
        assert validate_threshold(1.0) == 1.0

    def test_valid_threshold_middle(self) -> None:
        """Test threshold in valid range."""
        assert validate_threshold(0.5) == 0.5

    def test_invalid_threshold_negative(self) -> None:
        """Test that negative threshold raises ValidationError."""
        with pytest.raises(ValidationError, match="Threshold must be between"):
            validate_threshold(-0.1)

    def test_invalid_threshold_above_one(self) -> None:
        """Test that threshold > 1 raises ValidationError."""
        with pytest.raises(ValidationError, match="Threshold must be between"):
            validate_threshold(1.1)


class TestValidateNumFrames:
    """Tests for validate_num_frames function."""

    def test_valid_num_frames(self) -> None:
        """Test valid number of frames."""
        assert validate_num_frames(30) == 30

    def test_valid_num_frames_min(self) -> None:
        """Test minimum valid number of frames."""
        assert validate_num_frames(1) == 1

    def test_valid_num_frames_max(self) -> None:
        """Test maximum valid number of frames."""
        assert validate_num_frames(1000) == 1000

    def test_invalid_num_frames_zero(self) -> None:
        """Test that zero frames raises ValidationError."""
        with pytest.raises(ValidationError, match="must be at least 1"):
            validate_num_frames(0)

    def test_invalid_num_frames_negative(self) -> None:
        """Test that negative frames raises ValidationError."""
        with pytest.raises(ValidationError, match="must be at least 1"):
            validate_num_frames(-10)

    def test_invalid_num_frames_too_large(self) -> None:
        """Test that too many frames raises ValidationError."""
        with pytest.raises(ValidationError, match="cannot exceed 1000"):
            validate_num_frames(1001)


class TestValidateDevice:
    """Tests for validate_device function."""

    def test_valid_device_cpu(self) -> None:
        """Test CPU device validation."""
        assert validate_device("cpu") == "cpu"

    def test_valid_device_cuda(self) -> None:
        """Test CUDA device validation."""
        assert validate_device("cuda") == "cuda"

    def test_valid_device_auto(self) -> None:
        """Test auto device validation."""
        assert validate_device("auto") == "auto"

    def test_valid_device_cuda_with_id(self) -> None:
        """Test CUDA device with ID validation."""
        assert validate_device("cuda:0") == "cuda:0"
        assert validate_device("cuda:1") == "cuda:1"

    def test_valid_device_uppercase(self) -> None:
        """Test that uppercase is normalized."""
        assert validate_device("CPU") == "cpu"
        assert validate_device("CUDA") == "cuda"

    def test_invalid_device(self) -> None:
        """Test invalid device raises ValidationError."""
        with pytest.raises(ValidationError, match="Invalid device"):
            validate_device("gpu")

    def test_invalid_cuda_device_id(self) -> None:
        """Test invalid CUDA device ID raises ValidationError."""
        with pytest.raises(ValidationError, match="Invalid CUDA device"):
            validate_device("cuda:abc")


class TestValidateOutputFormat:
    """Tests for validate_output_format function."""

    def test_valid_format_text(self) -> None:
        """Test text format validation."""
        assert validate_output_format("text") == "text"

    def test_valid_format_json(self) -> None:
        """Test JSON format validation."""
        assert validate_output_format("json") == "json"

    def test_valid_format_both(self) -> None:
        """Test both format validation."""
        assert validate_output_format("both") == "both"

    def test_valid_format_uppercase(self) -> None:
        """Test that uppercase is normalized."""
        assert validate_output_format("TEXT") == "text"
        assert validate_output_format("JSON") == "json"

    def test_invalid_format(self) -> None:
        """Test invalid format raises ValidationError."""
        with pytest.raises(ValidationError, match="Invalid output format"):
            validate_output_format("xml")


class TestGetVideoFormat:
    """Tests for get_video_format function."""

    def test_mp4_format(self) -> None:
        """Test MP4 format detection."""
        assert get_video_format("/path/to/video.mp4") == "mp4"

    def test_avi_format(self) -> None:
        """Test AVI format detection."""
        assert get_video_format("/path/to/video.avi") == "avi"

    def test_unknown_format(self) -> None:
        """Test unknown format returns None."""
        assert get_video_format("/path/to/file.xyz") is None

    def test_case_insensitive(self) -> None:
        """Test format detection is case insensitive."""
        assert get_video_format("/path/to/video.MP4") == "mp4"
        assert get_video_format("/path/to/video.AVI") == "avi"
