# DeepFake Video Detector

AI-powered command-line tool for detecting deepfake videos using state-of-the-art machine learning models.

## Overview

DeepFake Video Detector analyzes video files to determine if they contain AI-generated or manipulated content (deepfakes). It uses pre-trained deep learning models to identify various indicators of synthetic media and provides a clear verdict (Fake/Not Fake) along with detailed reasoning.

## Key Features

- **Multiple Format Support**: Analyze MP4, AVI, MOV, MKV, and WebM videos
- **Pre-trained Models**: Uses ViT-based deepfake detector (83%+ accuracy)
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

Copy `.env.example` to `.env` for secrets, and edit `config.yaml` for settings:

```bash
cp .env.example .env
```

For complete configuration reference including all environment variables, CLI options, and model selection, see [docs/CONFIG.md](./docs/CONFIG.md).

## How It Works

1. **Frame Extraction**: Samples frames evenly across the video
2. **Face Detection**: Identifies faces using MTCNN
3. **Classification**: Analyzes face regions with ViT-based model
4. **Aggregation**: Combines per-frame results into overall verdict
5. **Reasoning**: Compiles detected indicators into explanation

For detailed architecture, see [docs/Architecture.md](./docs/Architecture.md).

## Expected Results

For detailed output examples, performance benchmarks, and edge case handling, see [docs/EXPECTED_RESULTS.md](./docs/EXPECTED_RESULTS.md).

## Troubleshooting

**Common issues:**
- Model download fails → Set `MODEL_CACHE_DIR` environment variable
- Out of memory → Use `--device cpu` or reduce `BATCH_SIZE`
- No faces detected → Ensure video contains visible human faces

See [docs/CONFIG.md](./docs/CONFIG.md) for detailed troubleshooting and configuration options.

## Documentation

- [Configuration Guide](./docs/CONFIG.md) - Environment variables, CLI options, model selection
- [Expected Results](./docs/EXPECTED_RESULTS.md) - Output examples, benchmarks
- [Architecture](./docs/Architecture.md) - System design, components
- [Research](./docs/RESEARCH.md) - Model evaluation, experiments
- [Security Guidelines](./docs/SECURITY.md) - Security considerations
- [Product Requirements](./docs/PRD.md) - Feature specifications
- [Contributing](./docs/CONTRIBUTING.md) - Development setup

## Contributing

We welcome contributions! See [CONTRIBUTING.md](./docs/CONTRIBUTING.md) for development setup and guidelines.

## License

MIT License - see [LICENSE](./LICENSE) for details.

## Acknowledgments

- [FaceForensics++](https://github.com/ondyari/FaceForensics) for benchmark datasets
- [facenet-pytorch](https://github.com/timesler/facenet-pytorch) for MTCNN implementation
- [timm](https://github.com/huggingface/pytorch-image-models) for EfficientNet models
