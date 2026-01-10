"""Input validation utilities for DeepFake Detector."""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Supported video formats with their MIME types
SUPPORTED_FORMATS = {
    ".mp4": "video/mp4",
    ".avi": "video/x-msvideo",
    ".mov": "video/quicktime",
    ".mkv": "video/x-matroska",
    ".webm": "video/webm",
}


class ValidationError(Exception):
    """Exception raised for validation errors."""


def validate_video_path(path: str) -> Path:
    """
    Validate that the video path exists and has a supported format.

    Args:
        path: Path to the video file.

    Returns:
        Path object for the validated path.

    Raises:
        ValidationError: If the path is invalid or format unsupported.
    """
    video_path = Path(path)

    # Check if file exists
    if not video_path.exists():
        logger.error("Video file not found: %s", path)
        raise ValidationError(f"Video file not found: {path}")

    # Check if it's a file
    if not video_path.is_file():
        logger.error("Path is not a file: %s", path)
        raise ValidationError(f"Path is not a file: {path}")

    # Check file extension
    extension = video_path.suffix.lower()
    if extension not in SUPPORTED_FORMATS:
        supported = ", ".join(SUPPORTED_FORMATS.keys())
        logger.error(
            "Unsupported video format: %s. Supported formats: %s",
            extension,
            supported,
        )
        raise ValidationError(
            f"Unsupported video format: {extension}. " f"Supported formats: {supported}"
        )

    # Check file size (warn if too large)
    file_size_mb = video_path.stat().st_size / (1024 * 1024)
    if file_size_mb > 500:
        logger.warning(
            "Large video file detected (%.1f MB). Processing may take a while.",
            file_size_mb,
        )

    logger.debug("Video path validated: %s", path)
    return video_path


def validate_threshold(threshold: float) -> float:
    """
    Validate confidence threshold is within valid range.

    Args:
        threshold: Confidence threshold value.

    Returns:
        Validated threshold value.

    Raises:
        ValidationError: If threshold is out of range.
    """
    if not 0.0 <= threshold <= 1.0:
        raise ValidationError(
            f"Threshold must be between 0.0 and 1.0, got: {threshold}"
        )
    return threshold


def validate_num_frames(num_frames: int) -> int:
    """
    Validate number of frames is within reasonable range.

    Args:
        num_frames: Number of frames to analyze.

    Returns:
        Validated number of frames.

    Raises:
        ValidationError: If num_frames is out of range.
    """
    if num_frames < 1:
        raise ValidationError(f"Number of frames must be at least 1, got: {num_frames}")
    if num_frames > 1000:
        raise ValidationError(f"Number of frames cannot exceed 1000, got: {num_frames}")
    return num_frames


def validate_device(device: str) -> str:
    """
    Validate and normalize device specification.

    Args:
        device: Device string (cpu, cuda, cuda:0, auto).

    Returns:
        Normalized device string.

    Raises:
        ValidationError: If device specification is invalid.
    """
    device = device.lower().strip()

    valid_devices = ["cpu", "cuda", "auto"]
    cuda_pattern = device.startswith("cuda:")

    if device not in valid_devices and not cuda_pattern:
        raise ValidationError(
            f"Invalid device: {device}. " f"Valid options: cpu, cuda, cuda:N, auto"
        )

    if cuda_pattern:
        try:
            device_id = int(device.split(":")[1])
            if device_id < 0:
                raise ValidationError(
                    f"Invalid CUDA device ID: {device_id}. Must be >= 0"
                )
        except (IndexError, ValueError) as exc:
            raise ValidationError(
                f"Invalid CUDA device specification: {device}"
            ) from exc

    return device


def validate_output_format(output_format: str) -> str:
    """
    Validate output format specification.

    Args:
        output_format: Output format string.

    Returns:
        Normalized output format.

    Raises:
        ValidationError: If format is invalid.
    """
    output_format = output_format.lower().strip()
    valid_formats = ["text", "json", "both"]

    if output_format not in valid_formats:
        raise ValidationError(
            f"Invalid output format: {output_format}. "
            f"Valid options: {', '.join(valid_formats)}"
        )

    return output_format


def get_video_format(path: str) -> Optional[str]:
    """
    Get the video format from file extension.

    Args:
        path: Path to video file.

    Returns:
        Format string (e.g., 'mp4') or None if unknown.
    """
    extension = Path(path).suffix.lower()
    if extension in SUPPORTED_FORMATS:
        return extension[1:]  # Remove leading dot
    return None
