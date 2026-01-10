# Architecture Documentation

## Overview

DeepFake Video Detector is a command-line application that analyzes video files to detect AI-generated or manipulated content. The system uses pre-trained deep learning models to identify various indicators of synthetic media.

## C4 Model

### Level 1: System Context

```
┌─────────────────────────────────────────────────────────────────────┐
│                        SYSTEM CONTEXT                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│    ┌──────────┐         ┌─────────────────────┐                     │
│    │   User   │────────▶│  DeepFake Detector  │                     │
│    │(Analyst) │         │       (CLI)         │                     │
│    └──────────┘         └─────────────────────┘                     │
│         │                        │                                   │
│         │                        │                                   │
│         ▼                        ▼                                   │
│    ┌──────────┐         ┌─────────────────────┐                     │
│    │  Video   │         │   HuggingFace Hub   │                     │
│    │  Files   │         │  (Model Download)   │                     │
│    └──────────┘         └─────────────────────┘                     │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

**Actors:**
- **User (Analyst)**: Fact-checker, journalist, researcher who needs to verify video authenticity
- **Video Files**: Local video files in supported formats (MP4, AVI, MOV, etc.)
- **HuggingFace Hub**: External service for downloading pre-trained models

### Level 2: Container Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                      DEEPFAKE DETECTOR                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────┐    ┌──────────────────┐    ┌──────────────────┐   │
│  │     CLI     │───▶│  Video Processor │───▶│  Frame Extractor │   │
│  │  Interface  │    │                  │    │                  │   │
│  └─────────────┘    └──────────────────┘    └──────────────────┘   │
│         │                                           │               │
│         │                                           ▼               │
│         │           ┌──────────────────┐    ┌──────────────────┐   │
│         │           │  Report Generator│◀───│  Face Detector   │   │
│         │           │                  │    │    (MTCNN)       │   │
│         │           └──────────────────┘    └──────────────────┘   │
│         │                    ▲                      │               │
│         │                    │                      ▼               │
│         │           ┌──────────────────┐    ┌──────────────────┐   │
│         └──────────▶│   Aggregator     │◀───│ DeepFake Model   │   │
│                     │                  │    │ (EfficientNet)   │   │
│                     └──────────────────┘    └──────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

**Containers:**
- **CLI Interface**: Entry point, argument parsing, configuration loading
- **Video Processor**: Video file handling, format validation
- **Frame Extractor**: Samples frames from video at configured rate
- **Face Detector**: Identifies and crops face regions using MTCNN
- **DeepFake Model**: Pre-trained classifier for fake detection
- **Aggregator**: Combines per-frame results into overall verdict
- **Report Generator**: Formats output with reasoning

### Level 3: Component Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         src/deepfake_detector/                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                         cli.py                               │    │
│  │  - main(): Entry point                                       │    │
│  │  - parse_args(): CLI argument handling                       │    │
│  │  - run_analysis(): Orchestrates detection pipeline           │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              │                                       │
│         ┌────────────────────┼────────────────────┐                 │
│         ▼                    ▼                    ▼                 │
│  ┌─────────────┐    ┌─────────────────┐   ┌──────────────┐         │
│  │   models/   │    │   analyzers/    │   │    utils/    │         │
│  ├─────────────┤    ├─────────────────┤   ├──────────────┤         │
│  │ detector.py │    │ video_analyzer  │   │ config.py    │         │
│  │ face_detect │    │ frame_analyzer  │   │ logging.py   │         │
│  │ model_load  │    │ temporal_check  │   │ validators.py│         │
│  └─────────────┘    └─────────────────┘   └──────────────┘         │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Detection Pipeline

```
┌──────────┐     ┌───────────┐     ┌────────────┐     ┌──────────────┐
│  Video   │────▶│  Extract  │────▶│   Detect   │────▶│    Crop      │
│  Input   │     │  Frames   │     │   Faces    │     │   Faces      │
└──────────┘     └───────────┘     └────────────┘     └──────────────┘
                                                              │
┌──────────┐     ┌───────────┐     ┌────────────┐            │
│  Output  │◀────│ Generate  │◀────│  Aggregate │◀───────────┘
│  Result  │     │  Report   │     │   Scores   │
└──────────┘     └───────────┘     └────────────┘
                                          ▲
                                          │
                                   ┌────────────┐
                                   │  Classify  │
                                   │  (Model)   │
                                   └────────────┘
```

### Detailed Flow

1. **Input Validation**
   - Verify file exists
   - Check format support
   - Validate file integrity

2. **Frame Extraction**
   - Open video with OpenCV
   - Calculate frame sampling indices
   - Extract N frames evenly distributed

3. **Face Detection**
   - Load MTCNN model
   - Detect faces in each frame
   - Track primary face across frames
   - Crop and align face regions

4. **Classification**
   - Load pre-trained detector model
   - Preprocess face crops
   - Run inference in batches
   - Get per-frame confidence scores

5. **Aggregation**
   - Calculate mean confidence
   - Identify temporal anomalies
   - Check for GAN artifacts
   - Compute final score

6. **Reporting**
   - Determine verdict (Fake/Not Fake)
   - Compile reasoning from indicators
   - Format output (text/JSON)

## API Contracts

### CLI Interface

```bash
deepfake-detector analyze <video_path> [options]
```

**Input Contract:**
```
video_path: string (required)
  - Must be valid file path
  - Supported formats: mp4, avi, mov, mkv, webm

options:
  --threshold: float [0.0, 1.0], default 0.5
  --num-frames: int [1, 1000], default 30
  --device: string {cpu, cuda, cuda:N}
  --output: string {text, json}
  --verbose: boolean
```

**Output Contract (Text):**
```
Verdict: FAKE | NOT FAKE
Confidence: XX.X%

Reasoning:
- [indicator 1]
- [indicator 2]
...

Analyzed: X frames from video.mp4
Processing time: X.XXs
```

**Output Contract (JSON):**
```json
{
  "verdict": "FAKE" | "NOT_FAKE",
  "confidence": 0.0-1.0,
  "reasoning": [
    {"indicator": "string", "detected": boolean, "score": float}
  ],
  "metadata": {
    "video_path": "string",
    "frames_analyzed": int,
    "processing_time_seconds": float,
    "model_used": "string",
    "threshold": float
  }
}
```

**Exit Codes:**
```
0 - Success (analysis completed)
1 - Input error (file not found, invalid format)
2 - Processing error (model loading, runtime error)
```

### Internal Module Interfaces

#### VideoProcessor

```python
class VideoProcessor:
    def __init__(self, config: Config) -> None: ...
    def load(self, path: str) -> VideoInfo: ...
    def extract_frames(self, count: int, sample_rate: int) -> list[Frame]: ...
    def close(self) -> None: ...
```

#### FaceDetector

```python
class FaceDetector:
    def __init__(self, device: str) -> None: ...
    def detect(self, frame: Frame) -> list[BoundingBox]: ...
    def crop_faces(self, frame: Frame, boxes: list[BoundingBox]) -> list[FaceCrop]: ...
```

#### DeepFakeDetector

```python
class DeepFakeDetector:
    def __init__(self, model_name: str, device: str) -> None: ...
    def load_model(self) -> None: ...
    def predict(self, face_crops: list[FaceCrop]) -> list[float]: ...
```

#### ResultAggregator

```python
class ResultAggregator:
    def __init__(self, threshold: float) -> None: ...
    def aggregate(self, frame_scores: list[float]) -> AggregatedResult: ...
```

## Data Model

### Core Types

```python
@dataclass
class Config:
    model: str
    threshold: float
    num_frames: int
    sample_rate: int
    device: str
    output_format: str
    verbose: bool

@dataclass
class VideoInfo:
    path: str
    duration: float
    fps: float
    width: int
    height: int
    frame_count: int

@dataclass
class Frame:
    index: int
    timestamp: float
    image: np.ndarray

@dataclass
class BoundingBox:
    x: int
    y: int
    width: int
    height: int
    confidence: float

@dataclass
class FaceCrop:
    frame_index: int
    box: BoundingBox
    image: np.ndarray

@dataclass
class FrameResult:
    frame_index: int
    confidence: float
    faces_detected: int

@dataclass
class DetectionIndicator:
    name: str
    detected: bool
    score: float
    description: str

@dataclass
class AggregatedResult:
    verdict: str  # "FAKE" or "NOT_FAKE"
    confidence: float
    indicators: list[DetectionIndicator]
    frame_results: list[FrameResult]
```

## Deployment

### Local Installation

```bash
# Clone repository
git clone <repo-url>
cd deepfake-detector

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install package
pip install -e ".[dev]"

# Download models (automatic on first run)
deepfake-detector --download-models
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -e .

ENTRYPOINT ["deepfake-detector"]
```

```bash
docker build -t deepfake-detector .
docker run -v /path/to/videos:/videos deepfake-detector analyze /videos/test.mp4
```

### GPU Support

```bash
# Requires NVIDIA Container Toolkit
docker run --gpus all -v /path/to/videos:/videos deepfake-detector analyze /videos/test.mp4 --device cuda
```

## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| CLI | Click | Command-line interface |
| Output | Rich | Terminal formatting |
| Video | OpenCV | Video processing |
| ML Framework | PyTorch | Deep learning |
| Face Detection | facenet-pytorch | MTCNN implementation |
| Models | HuggingFace/timm | Pre-trained models |
| Config | python-dotenv, PyYAML | Configuration |
| Testing | pytest | Test framework |

## Quality Attributes

### Performance
- GPU inference: < 2s per frame
- CPU inference: < 10s per frame
- Memory: < 4GB peak usage

### Reliability
- Graceful degradation to CPU if GPU unavailable
- Comprehensive error handling
- Deterministic results

### Maintainability
- Modular architecture
- Type hints throughout
- 80%+ test coverage

### Security
- No network calls during inference
- Input validation
- Model integrity verification

## Architecture Decision Records

See [ADRs/](./ADRs/) for documented decisions:
- ADR-001: Use EfficientNet for detection
- ADR-002: MTCNN for face detection
- ADR-003: Frame sampling strategy
