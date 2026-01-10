# Configuration Guide

## Overview

DeepFake Detector uses a layered configuration system:

1. **Default values** - Built into the application
2. **Configuration file** - `config/settings.yaml`
3. **Environment variables** - Override via `DEEPFAKE_*` prefix
4. **CLI flags** - Highest priority overrides

## Configuration Files

### config/settings.yaml

The main configuration file with default settings:

```yaml
detection:
  model: efficientnet        # Detection model to use
  confidence_threshold: 0.5  # Threshold for fake classification
  num_frames: 30             # Number of frames to analyze
  sample_rate: 10            # Sample every Nth frame

video:
  max_duration: 300          # Maximum video duration (seconds)
  frame_size: [224, 224]     # Target frame size for processing
  supported_formats:
    - mp4
    - avi
    - mov
    - mkv
    - webm

analysis:
  face_detection: true       # Enable face detection
  temporal_analysis: true    # Check temporal consistency
  artifact_detection: true   # Look for GAN artifacts
  av_sync_check: false       # Audio-visual sync (future)

output:
  include_reasoning: true    # Show detection reasoning
  generate_visualization: false
  format: text               # text, json, or both

logging:
  level: INFO
  file: null                 # Log file path (null = stdout only)
```

### .env

Environment-specific configuration (not committed to git):

```bash
# Copy from template
cp .env.example .env
```

## Environment Variables

All configuration can be overridden via environment variables with the `DEEPFAKE_` prefix:

| Variable | Description | Default |
|----------|-------------|---------|
| `HUGGINGFACE_TOKEN` | HuggingFace API token for model downloads | (none) |
| `MODEL_CACHE_DIR` | Directory to cache model weights | `./models/cache` |
| `DEFAULT_MODEL` | Default detection model | `efficientnet` |
| `MAX_VIDEO_DURATION` | Maximum video duration in seconds | `300` |
| `FRAME_SAMPLE_RATE` | Process every Nth frame | `10` |
| `NUM_FRAMES_TO_ANALYZE` | Total frames to analyze | `30` |
| `BATCH_SIZE` | Inference batch size | `8` |
| `CONFIDENCE_THRESHOLD` | Fake detection threshold (0.0-1.0) | `0.5` |
| `VERBOSE_OUTPUT` | Enable verbose output | `false` |
| `OUTPUT_FORMAT` | Output format: text, json, both | `text` |
| `USE_GPU` | Use GPU if available | `true` |
| `GPU_DEVICE_ID` | GPU device ID for multi-GPU | `0` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `LOG_FILE` | Log file path | (none) |

## CLI Options

Command-line flags override all other configuration:

```bash
deepfake-detector analyze VIDEO_PATH [OPTIONS]

Options:
  -i, --input PATH          Video file to analyze (required)
  -t, --threshold FLOAT     Confidence threshold [default: 0.5]
  -n, --num-frames INT      Number of frames to analyze [default: 30]
  -s, --sample-rate INT     Frame sampling rate [default: 10]
  -m, --model TEXT          Detection model [default: efficientnet]
  -d, --device TEXT         Compute device (cpu/cuda/cuda:N)
  -o, --output TEXT         Output format (text/json)
  -v, --verbose             Enable verbose output
  -c, --config PATH         Custom config file path
  --json                    Output results as JSON
  -h, --help                Show this help message
```

## Configuration Priority

Configuration is applied in this order (later overrides earlier):

```
1. Built-in defaults
   ↓
2. config/settings.yaml
   ↓
3. Custom config file (--config)
   ↓
4. Environment variables
   ↓
5. CLI flags
```

## Model Configuration

### Available Models

| Model | Description | Speed | Accuracy |
|-------|-------------|-------|----------|
| `efficientnet` | EfficientNet-B4 based | Fast | High |
| `xception` | Xception based | Medium | High |
| `ensemble` | Multiple models | Slow | Highest |

### Model Cache

Models are downloaded and cached locally:

```bash
# Default cache location
~/.cache/deepfake-detector/

# Or set custom location
export MODEL_CACHE_DIR=/path/to/cache
```

## Performance Tuning

### GPU Configuration

```bash
# Use specific GPU
export GPU_DEVICE_ID=1
deepfake-detector analyze video.mp4

# Or via CLI
deepfake-detector analyze video.mp4 --device cuda:1
```

### Batch Processing

Adjust batch size based on available VRAM:

| VRAM | Recommended Batch Size |
|------|------------------------|
| 4GB  | 4 |
| 8GB  | 8 |
| 16GB | 16 |
| 24GB | 32 |

```bash
export BATCH_SIZE=16
```

### Memory Optimization

For long videos or limited memory:

```bash
# Reduce frames analyzed
export NUM_FRAMES_TO_ANALYZE=15

# Increase sampling rate (skip more frames)
export FRAME_SAMPLE_RATE=20
```

## Logging Configuration

### Log Levels

- `DEBUG`: Detailed debugging information
- `INFO`: General operational messages
- `WARNING`: Warning messages
- `ERROR`: Error messages only

### File Logging

```bash
# Log to file
export LOG_FILE=/var/log/deepfake-detector.log
export LOG_LEVEL=DEBUG
```

## Examples

### Development Setup

```bash
# .env for development
HUGGINGFACE_TOKEN=hf_xxxxxxxxxxxx
MODEL_CACHE_DIR=./models/cache
LOG_LEVEL=DEBUG
VERBOSE_OUTPUT=true
USE_GPU=true
```

### Production Setup

```bash
# .env for production
MODEL_CACHE_DIR=/opt/models
LOG_LEVEL=WARNING
LOG_FILE=/var/log/deepfake-detector.log
VERBOSE_OUTPUT=false
USE_GPU=true
BATCH_SIZE=16
```

### CPU-Only Setup

```bash
# For systems without GPU
USE_GPU=false
BATCH_SIZE=4
NUM_FRAMES_TO_ANALYZE=20
```

## Validation

Validate your configuration:

```bash
# Check configuration loading
deepfake-detector config --validate

# Show effective configuration
deepfake-detector config --show
```
