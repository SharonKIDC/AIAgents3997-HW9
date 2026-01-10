# DeepFake Video Detector

AI-powered tool for detecting deepfake videos using state-of-the-art machine learning models.

## Overview

This application analyzes video files to determine if they contain AI-generated or manipulated content (deepfakes). It uses multiple detection techniques and provides detailed reasoning for its conclusions.

## Features

- Video input analysis with multiple format support
- AI-based deepfake detection using pre-trained models
- Detailed reasoning output explaining detection results
- Configurable confidence thresholds
- CLI interface for easy integration

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd deepfake-detector

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

## Quick Start

```bash
# Analyze a video
deepfake-detector analyze /path/to/video.mp4

# Get detailed output
deepfake-detector analyze /path/to/video.mp4 --verbose
```

## Documentation

See the [docs](./docs) directory for detailed documentation.

## License

MIT License
