"""Video analysis and frame extraction module."""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class VideoInfo:
    """Information about a video file."""

    path: str
    duration: float
    fps: float
    width: int
    height: int
    frame_count: int


@dataclass
class Frame:
    """A single video frame with metadata."""

    index: int
    timestamp: float
    image: np.ndarray


class VideoAnalyzer:
    """Handles video loading and frame extraction."""

    def __init__(self, max_duration: int = 300) -> None:
        """
        Initialize the video analyzer.

        Args:
            max_duration: Maximum video duration in seconds.
        """
        self.max_duration = max_duration
        self._capture: Optional[cv2.VideoCapture] = None
        self._video_info: Optional[VideoInfo] = None

    def load(self, path: str) -> VideoInfo:
        """
        Load a video file and extract metadata.

        Args:
            path: Path to the video file.

        Returns:
            VideoInfo object with video metadata.

        Raises:
            ValueError: If video cannot be loaded.
        """
        video_path = Path(path)
        if not video_path.exists():
            raise ValueError(f"Video file not found: {path}")

        self._capture = cv2.VideoCapture(str(video_path))
        if not self._capture.isOpened():
            raise ValueError(f"Failed to open video: {path}")

        fps = self._capture.get(cv2.CAP_PROP_FPS)
        frame_count = int(self._capture.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(self._capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Calculate duration
        if fps > 0:
            duration = frame_count / fps
        else:
            duration = 0.0

        self._video_info = VideoInfo(
            path=str(video_path),
            duration=duration,
            fps=fps,
            width=width,
            height=height,
            frame_count=frame_count,
        )

        logger.info(
            "Loaded video: %s (%.1fs, %dx%d, %.1f fps, %d frames)",
            video_path.name,
            duration,
            width,
            height,
            fps,
            frame_count,
        )

        if duration > self.max_duration:
            logger.warning(
                "Video duration (%.1fs) exceeds maximum (%.1fs). "
                "Only first %.1fs will be analyzed.",
                duration,
                self.max_duration,
                self.max_duration,
            )

        return self._video_info

    def extract_frames(
        self,
        num_frames: int = 30,
        sample_rate: int = 10,
    ) -> list[Frame]:
        """
        Extract frames from the loaded video.

        Uses uniform temporal sampling to select frames evenly
        distributed across the video duration.

        Args:
            num_frames: Target number of frames to extract.
            sample_rate: Sampling rate (every Nth frame) used when
                num_frames is 0 or None.

        Returns:
            List of Frame objects.

        Raises:
            ValueError: If no video is loaded.
        """
        if self._capture is None or self._video_info is None:
            raise ValueError("No video loaded. Call load() first.")

        total_frames = self._video_info.frame_count
        fps = self._video_info.fps

        # Calculate frame indices using max_duration limit
        if fps > 0:
            max_frame = min(total_frames, int(self.max_duration * fps))
        else:
            max_frame = total_frames

        # Determine sampling strategy
        if num_frames <= 0:
            # Use sample_rate when num_frames not specified
            indices = np.arange(0, max_frame, sample_rate)
            actual_num_frames = len(indices)
            logger.info(
                "Using sample_rate=%d, extracting %d frames",
                sample_rate,
                actual_num_frames,
            )
        else:
            # Adjust num_frames if video is too short
            actual_num_frames = min(num_frames, max_frame)

            if actual_num_frames < num_frames:
                logger.warning(
                    "Video has fewer frames (%d) than requested (%d). "
                    "Extracting all available frames.",
                    max_frame,
                    num_frames,
                )

            # Calculate evenly spaced frame indices
            if actual_num_frames > 1:
                indices = np.linspace(0, max_frame - 1, actual_num_frames, dtype=int)
            else:
                indices = np.array([0])

        frames = []
        for idx in indices:
            self._capture.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
            ret, image = self._capture.read()

            if ret:
                # Convert BGR to RGB
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                timestamp = idx / fps if fps > 0 else 0.0
                frame = Frame(index=int(idx), timestamp=timestamp, image=image_rgb)
                frames.append(frame)
            else:
                logger.warning("Failed to read frame at index %d", idx)

        logger.info(
            "Extracted %d frames from video (requested: %d)",
            len(frames),
            num_frames,
        )

        return frames

    def close(self) -> None:
        """Release video capture resources."""
        if self._capture is not None:
            self._capture.release()
            self._capture = None
            self._video_info = None

    def __enter__(self) -> "VideoAnalyzer":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()

    @property
    def video_info(self) -> Optional[VideoInfo]:
        """Get the current video info."""
        return self._video_info
