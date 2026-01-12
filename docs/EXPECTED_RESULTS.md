# Expected Results

This document describes the expected behavior and outputs of the DeepFake Video Detector.

## CLI Output Examples

### Successful Detection - Fake Video

```bash
$ deepfake-detector analyze suspicious_video.mp4

DeepFake Video Detector v1.0.0
==============================

Analyzing: suspicious_video.mp4
Duration: 00:15
Frames analyzed: 30/450

Detection Results
-----------------
Verdict: FAKE
Confidence: 83.6%

Evidence:
  - Face manipulation detected in 30/30 frames (100%)
  - Temporal consistency: Consistent detection across frames
  - Overall confidence: 83.6% (threshold: 50.0%)

Analysis Time: 6.44s
```

### Successful Detection - Real Video

```bash
$ deepfake-detector analyze authentic_video.mp4

DeepFake Video Detector v1.0.0
==============================

Analyzing: authentic_video.mp4
Duration: 00:30
Frames analyzed: 30/900

Detection Results
-----------------
Verdict: NOT_FAKE
Confidence: 15.2%

Evidence:
  - Face manipulation detected in 2/30 frames (6.7%)
  - Temporal consistency: Consistent detection across frames
  - Overall confidence: 15.2% (threshold: 50.0%)

Analysis Time: 7.12s
```

### JSON Output Format

```bash
$ deepfake-detector analyze video.mp4 --json
```

```json
{
  "video_path": "video.mp4",
  "verdict": "FAKE",
  "confidence": 0.836,
  "analysis": {
    "frames_analyzed": 30,
    "total_frames": 450,
    "faces_detected": 30,
    "duration_seconds": 15.0
  },
  "indicators": [
    {
      "name": "face_manipulation",
      "detected": true,
      "score": 1.0,
      "description": "Face manipulation detected in 30/30 frames"
    },
    {
      "name": "temporal_consistency",
      "detected": false,
      "score": 0.02,
      "description": "Consistent detection across frames"
    },
    {
      "name": "overall_confidence",
      "detected": true,
      "score": 0.836,
      "description": "Overall confidence: 83.6% (threshold: 50.0%)"
    }
  ],
  "frame_results": [
    {"frame_index": 0, "confidence": 0.82, "faces_detected": 1},
    {"frame_index": 15, "confidence": 0.85, "faces_detected": 1},
    {"frame_index": 30, "confidence": 0.81, "faces_detected": 1}
  ],
  "processing_time_seconds": 6.44,
  "model_used": "vit-deepfake",
  "version": "1.0.0"
}
```

## Performance Benchmarks

### Detection Accuracy

For detailed model comparison and research experiments, see [RESEARCH.md](RESEARCH.md).

**Summary:** The default `vit-deepfake` model achieves 83-86% accuracy on test videos.

### Processing Speed

| Video Length | Frames Analyzed | Expected Time |
|--------------|-----------------|---------------|
| 15 seconds | 30 | ~6-7 seconds |
| 60 seconds | 30 | ~6-7 seconds |
| 5 minutes | 30 | ~6-7 seconds |

Note: Processing time is primarily determined by number of frames analyzed, not video length.

### Resource Usage

| Resource | Typical Usage |
|----------|--------------|
| RAM | 2-4 GB |
| VRAM (GPU) | 1-2 GB |
| Disk (model cache) | ~350 MB |

## Edge Cases

### No Faces Detected

```bash
$ deepfake-detector analyze landscape_video.mp4

DeepFake Video Detector v1.0.0
==============================

Analyzing: landscape_video.mp4
Duration: 00:30
Frames analyzed: 30/900

Detection Results
-----------------
Verdict: NOT_FAKE
Confidence: 0.0%

Evidence:
  - No faces detected in video

Analysis Time: 2.15s
```

### Corrupted Video

```bash
$ deepfake-detector analyze corrupted.mp4

Error: Unable to read video file: corrupted.mp4
Please ensure the file is a valid video format (mp4, avi, mov, mkv, webm).
```

### Unsupported Format

```bash
$ deepfake-detector analyze video.wmv

Error: Unsupported video format: wmv
Supported formats: mp4, avi, mov, mkv, webm
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success - video analyzed |
| 1 | Error - invalid input or processing failure |
| 2 | Error - missing dependencies |

## Confidence Interpretation

| Confidence Range | Interpretation |
|------------------|----------------|
| 0-30% | Likely authentic |
| 30-50% | Uncertain, review manually |
| 50-70% | Likely manipulated |
| 70-100% | High confidence fake |

## See Also

- [README.md](../README.md) - Quick start guide
- [CONFIG.md](CONFIG.md) - Configuration options
- [RESEARCH.md](RESEARCH.md) - Research methodology and findings
