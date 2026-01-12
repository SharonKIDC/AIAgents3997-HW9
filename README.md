# DeepFake Video Detector

AI-powered command-line tool for detecting deepfake videos using state-of-the-art machine learning models.

## Overview

DeepFake Video Detector analyzes video files to determine if they contain AI-generated or manipulated content (deepfakes). It uses pre-trained deep learning models to identify various indicators of synthetic media and provides a clear verdict (Fake/Not Fake) along with detailed reasoning.

## Key Features

- **Multiple Format Support**: Analyze MP4, AVI, MOV, MKV, and WebM videos
- **Pre-trained Models**: Uses EfficientNet-B4 for accurate detection
- **Face Detection**: MTCNN-based face detection and tracking
- **Detailed Reasoning**: Explains why a video was classified as fake or real
- **Configurable Thresholds**: Adjust sensitivity for your use case
- **GPU Acceleration**: CUDA support for fast inference
- **CLI Interface**: Easy integration into scripts and pipelines

## Requirements

- Python 3.9 or higher
- 4GB RAM minimum (8GB recommended)
- GPU with CUDA support (optional, for faster processing)
- 500MB disk space for model weights

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/example/deepfake-detector.git
cd deepfake-detector

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e ".[dev]"
```

### Using pip (when published)

```bash
pip install deepfake-detector
```

## Quick Start

### Basic Usage

```bash
# Analyze a video
deepfake-detector analyze video.mp4
```

**Output:**
```
Analyzing: video.mp4
Processing: 30 frames extracted

═══════════════════════════════════════
Verdict: FAKE
Confidence: 87.3%
═══════════════════════════════════════

Reasoning:
• Face manipulation detected: High confidence (0.89)
• Temporal inconsistency: Flickering detected in frames 12-15
• Boundary artifacts: Edge blending anomalies around face region

Analyzed: 30 frames in 4.2 seconds
```

### Command Options

```bash
# Adjust detection threshold (default: 0.5)
deepfake-detector analyze video.mp4 --threshold 0.7

# Analyze more frames for accuracy
deepfake-detector analyze video.mp4 --num-frames 60

# Use CPU instead of GPU
deepfake-detector analyze video.mp4 --device cpu

# Output as JSON
deepfake-detector analyze video.mp4 --json

# Verbose output with progress
deepfake-detector analyze video.mp4 --verbose
```

### JSON Output

```bash
deepfake-detector analyze video.mp4 --json
```

```json
{
  "verdict": "FAKE",
  "confidence": 0.873,
  "reasoning": [
    {"indicator": "face_manipulation", "detected": true, "score": 0.89},
    {"indicator": "temporal_consistency", "detected": true, "score": 0.72},
    {"indicator": "boundary_artifacts", "detected": true, "score": 0.65}
  ],
  "metadata": {
    "video_path": "video.mp4",
    "frames_analyzed": 30,
    "processing_time_seconds": 4.2,
    "model_used": "efficientnet",
    "threshold": 0.5
  }
}
```

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

Key variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `DEFAULT_MODEL` | Detection model | `efficientnet` |
| `CONFIDENCE_THRESHOLD` | Fake detection threshold | `0.5` |
| `NUM_FRAMES_TO_ANALYZE` | Frames to sample | `30` |
| `USE_GPU` | Enable GPU acceleration | `true` |

See [docs/CONFIG.md](./docs/CONFIG.md) for complete configuration reference.

### Configuration File

Edit `config.yaml` for persistent settings:

```yaml
detection:
  model: vit-deepfake  # recommended model (83%+ accuracy)
  confidence_threshold: 0.5
  num_frames: 30

output:
  include_reasoning: true
  format: text
```

## How It Works

1. **Frame Extraction**: Samples frames evenly across the video
2. **Face Detection**: Identifies faces using MTCNN
3. **Classification**: Analyzes face regions with EfficientNet-B4
4. **Aggregation**: Combines per-frame results into overall verdict
5. **Reasoning**: Compiles detected indicators into explanation

## Supported Detection Indicators

| Indicator | Description |
|-----------|-------------|
| Face Manipulation | AI-generated or swapped face regions |
| Temporal Inconsistency | Flickering or unnatural frame transitions |
| Boundary Artifacts | Edge blending around manipulated areas |
| GAN Fingerprints | Frequency-domain artifacts from generation |

## Troubleshooting

### Common Issues

**Model download fails:**
```bash
# Manually set cache directory
export MODEL_CACHE_DIR=/path/to/cache

# Or download with retry
deepfake-detector --download-models
```

**Out of memory:**
```bash
# Reduce batch size
export BATCH_SIZE=4

# Or use CPU
deepfake-detector analyze video.mp4 --device cpu
```

**No faces detected:**
- Ensure video contains visible human faces
- Check video isn't corrupted
- Try a shorter video segment

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success (analysis completed) |
| 1 | Input error (file not found, invalid format) |
| 2 | Processing error (model loading failed) |

## Documentation

- [Configuration Guide](./docs/CONFIG.md)
- [Architecture](./docs/Architecture.md)
- [Security Guidelines](./docs/SECURITY.md)
- [Product Requirements](./docs/PRD.md)
- [Contributing](./docs/CONTRIBUTING.md)

## Project Structure

```
deepfake-detector/
├── src/deepfake_detector/    # Main package
│   ├── models/               # Detection models
│   ├── analyzers/            # Video analysis
│   └── utils/                # Utilities
├── tests/                    # Test suite
├── docs/                     # Documentation
├── config/                   # Configuration
└── results/                  # Output storage
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./docs/CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](./LICENSE) for details.

## Acknowledgments

- [FaceForensics++](https://github.com/ondyari/FaceForensics) for benchmark datasets
- [facenet-pytorch](https://github.com/timesler/facenet-pytorch) for MTCNN implementation
- [timm](https://github.com/huggingface/pytorch-image-models) for EfficientNet models
