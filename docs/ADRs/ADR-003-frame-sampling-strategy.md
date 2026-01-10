# ADR-003: Uniform Frame Sampling Strategy

## Status

Accepted

## Date

2026-01-10

## Context

Videos can contain thousands of frames. Analyzing every frame is:
1. Computationally expensive
2. Redundant (adjacent frames are similar)
3. Unnecessary for detection (patterns visible in samples)

We need a strategy to select representative frames for analysis.

## Decision

Use uniform temporal sampling to select N frames distributed evenly across the video duration.

```python
def sample_frames(video, num_frames=30):
    total_frames = video.frame_count
    indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)
    return [video.get_frame(i) for i in indices]
```

**Default parameters:**
- `num_frames`: 30 frames
- `sample_rate`: Every 10th frame (fallback for short videos)

## Consequences

### Positive

- **Consistent coverage**: Samples from beginning, middle, and end
- **Predictable performance**: Fixed number of inference calls
- **Catches temporal patterns**: Distributed samples reveal inconsistencies
- **Configurable**: Users can adjust for accuracy/speed trade-off

### Negative

- **May miss localized fakes**: If manipulation only in small segment
- **Fixed overhead**: Same compute for 10s and 10min videos
- **Aliasing risk**: Could systematically miss periodic artifacts

### Neutral

- Trade-off between coverage and speed
- May need video-specific tuning

## Alternatives Considered

### Alternative 1: Scene-Change Detection

Sample frames at scene boundaries.

**Pros:**
- Focuses on distinct visual moments
- Reduces redundancy

**Cons:**
- More complex implementation
- May miss fakes within scenes
- Inconsistent frame count

**Why not chosen:** Added complexity without clear accuracy benefit.

### Alternative 2: Face-Motion Tracking

Sample frames with significant face movement.

**Pros:**
- Targets frames where artifacts more visible
- Reduces redundant similar faces

**Cons:**
- Requires two-pass processing
- Complex motion estimation

**Why not chosen:** Performance overhead too high.

### Alternative 3: Random Sampling

Select frames randomly.

**Pros:**
- Simple implementation
- Avoids aliasing

**Cons:**
- Non-deterministic results
- May cluster samples in one region
- Harder to debug

**Why not chosen:** Reproducibility and coverage concerns.

### Alternative 4: All Frames

Process every frame.

**Pros:**
- Maximum accuracy
- No sampling bias

**Cons:**
- Extremely slow
- Impractical for long videos
- Diminishing returns

**Why not chosen:** Performance unacceptable for practical use.

## References

- [Temporal Sampling in Video Understanding](https://arxiv.org/abs/1904.02811)
- FaceForensics++ evaluation protocols
