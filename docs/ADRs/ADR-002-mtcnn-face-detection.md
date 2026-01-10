# ADR-002: Use MTCNN for Face Detection

## Status

Accepted

## Date

2026-01-10

## Context

DeepFake detection requires extracting face regions from video frames before classification. We need a face detection algorithm that:

1. Is accurate and handles various face poses
2. Provides facial landmarks for alignment
3. Works well with the PyTorch ecosystem
4. Has reasonable inference speed

## Decision

Use MTCNN (Multi-task Cascaded Convolutional Networks) via the `facenet-pytorch` library.

```python
from facenet_pytorch import MTCNN

detector = MTCNN(keep_all=True, device=device)
boxes, probs, landmarks = detector.detect(frame, landmarks=True)
```

## Consequences

### Positive

- **High accuracy**: Robust face detection across poses and lighting
- **Landmark detection**: Provides 5-point landmarks for face alignment
- **PyTorch native**: Seamless integration with our stack
- **Batched inference**: Can process multiple frames efficiently
- **Well-maintained**: Active community, good documentation

### Negative

- **Speed**: Slower than single-shot detectors like RetinaFace
- **Memory**: Three-stage cascade uses more memory
- **Small faces**: May miss very small faces in frame

### Neutral

- Returns multiple faces per frame (need to select primary)
- Confidence threshold tuning may be needed

## Alternatives Considered

### Alternative 1: RetinaFace

Single-shot face detector with high accuracy.

**Pros:**
- Faster inference
- Better small face detection

**Cons:**
- Less mature PyTorch implementations
- Separate library dependency

**Why not chosen:** facenet-pytorch provides well-integrated MTCNN.

### Alternative 2: OpenCV Haar Cascades

Classical computer vision approach.

**Pros:**
- Very fast
- No deep learning required
- Built into OpenCV

**Cons:**
- Lower accuracy
- No landmark detection
- Struggles with non-frontal faces

**Why not chosen:** Accuracy insufficient for reliable deepfake detection.

### Alternative 3: MediaPipe Face Detection

Google's cross-platform face detection.

**Pros:**
- Fast
- Mobile-optimized
- Face mesh available

**Cons:**
- TensorFlow-based (ecosystem mismatch)
- Different dependency chain

**Why not chosen:** PyTorch ecosystem preferred for consistency.

## References

- [MTCNN Paper](https://arxiv.org/abs/1604.02878)
- [facenet-pytorch](https://github.com/timesler/facenet-pytorch)
