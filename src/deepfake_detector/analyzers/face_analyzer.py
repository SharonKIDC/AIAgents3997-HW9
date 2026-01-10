"""Face detection and analysis module."""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class BoundingBox:
    """Bounding box for a detected face."""

    x: int
    y: int
    width: int
    height: int
    confidence: float


@dataclass
class FaceCrop:
    """Cropped face region from a frame."""

    frame_index: int
    box: BoundingBox
    image: np.ndarray


class FaceAnalyzer:
    """Detects and extracts faces from video frames."""

    def __init__(
        self,
        target_size: tuple[int, int] = (224, 224),
        min_confidence: float = 0.5,
    ) -> None:
        """
        Initialize the face analyzer.

        Args:
            target_size: Target size for cropped face images.
            min_confidence: Minimum confidence threshold for detection.
        """
        self.target_size = target_size
        self.min_confidence = min_confidence
        self._detector: Optional[cv2.CascadeClassifier] = None
        self._load_detector()

    def _load_detector(self) -> None:
        """Load the face detection model."""
        # Use OpenCV's built-in Haar Cascade classifier
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"

        if not Path(cascade_path).exists():
            logger.error("Face cascade file not found: %s", cascade_path)
            raise RuntimeError("Failed to load face detection model")

        self._detector = cv2.CascadeClassifier(cascade_path)
        if self._detector.empty():
            raise RuntimeError("Failed to load face detection model")

        logger.debug("Loaded face detector from: %s", cascade_path)

    def detect_faces(self, image: np.ndarray) -> list[BoundingBox]:
        """
        Detect faces in an image.

        Args:
            image: RGB image as numpy array.

        Returns:
            List of BoundingBox objects for detected faces.
        """
        if self._detector is None:
            raise RuntimeError("Face detector not initialized")

        # Convert to grayscale for detection
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        # Detect faces
        faces = self._detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE,
        )

        boxes = []
        for x, y, w, h in faces:
            # Haar cascade doesn't provide confidence, use 1.0 as placeholder
            box = BoundingBox(
                x=int(x),
                y=int(y),
                width=int(w),
                height=int(h),
                confidence=1.0,
            )
            boxes.append(box)

        return boxes

    def crop_faces(  # pylint: disable=too-many-locals
        self,
        image: np.ndarray,
        boxes: list[BoundingBox],
        frame_index: int,
        padding: float = 0.2,
    ) -> list[FaceCrop]:
        """
        Crop face regions from an image.

        Args:
            image: RGB image as numpy array.
            boxes: List of detected face bounding boxes.
            frame_index: Index of the source frame.
            padding: Padding ratio to add around face.

        Returns:
            List of FaceCrop objects with resized face images.
        """
        height, width = image.shape[:2]
        crops = []

        for box in boxes:
            # Add padding
            pad_w = int(box.width * padding)
            pad_h = int(box.height * padding)

            x1 = max(0, box.x - pad_w)
            y1 = max(0, box.y - pad_h)
            x2 = min(width, box.x + box.width + pad_w)
            y2 = min(height, box.y + box.height + pad_h)

            # Crop and resize
            face_img = image[y1:y2, x1:x2]

            if face_img.size > 0:
                resized = cv2.resize(
                    face_img,
                    self.target_size,
                    interpolation=cv2.INTER_LINEAR,
                )

                crop = FaceCrop(frame_index=frame_index, box=box, image=resized)
                crops.append(crop)

        return crops

    def extract_faces_from_frames(
        self,
        frames: list,
        select_primary: bool = True,
    ) -> list[FaceCrop]:
        """
        Extract face crops from a list of frames.

        Args:
            frames: List of Frame objects.
            select_primary: If True, track and select the primary face.

        Returns:
            List of FaceCrop objects.
        """
        all_crops = []
        face_counts = []

        for frame in frames:
            boxes = self.detect_faces(frame.image)
            face_counts.append(len(boxes))

            if boxes:
                if select_primary:
                    # Select the largest face (likely the primary subject)
                    boxes = sorted(
                        boxes,
                        key=lambda b: b.width * b.height,
                        reverse=True,
                    )
                    boxes = boxes[:1]  # Keep only the largest

                crops = self.crop_faces(frame.image, boxes, frame.index)
                all_crops.extend(crops)

        total_faces = sum(face_counts)
        frames_with_faces = sum(1 for c in face_counts if c > 0)

        logger.info(
            "Detected %d faces across %d/%d frames",
            total_faces,
            frames_with_faces,
            len(frames),
        )

        if frames_with_faces == 0:
            logger.warning("No faces detected in any frame")

        return all_crops

    def get_primary_face_track(
        self,
        frames: list,
    ) -> list[FaceCrop]:
        """
        Track the primary face across all frames.

        Uses simple largest-face heuristic for tracking.

        Args:
            frames: List of Frame objects.

        Returns:
            List of FaceCrop objects for the primary face.
        """
        return self.extract_faces_from_frames(frames, select_primary=True)
