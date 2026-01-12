# Extensibility Plan

## Current Extension Points

### 1. Model Integration

New detection models can be added by:

1. Adding model configuration to `src/deepfake_detector/models/detector.py`
2. Implementing the model loading in `_load_huggingface_model()` or adding a new loader
3. Updating `config.yaml` with new model options

See [RESEARCH.md](RESEARCH.md) for model evaluation methodology.

### 2. Output Formats

Additional output formats can be added in `src/deepfake_detector/cli.py`:
- Current: `text`, `json`
- Potential: `xml`, `csv`, `html`

### 3. Detection Indicators

New detection indicators can be added to `ResultAggregator._build_indicators()` in `detector.py`.

## Future Extension Opportunities

| Feature | Effort | Priority | Notes |
|---------|--------|----------|-------|
| Additional HuggingFace models | Low | Medium | Just config changes |
| Batch video processing | Medium | Medium | CLI enhancement |
| REST API wrapper | Medium | Low | Not in current scope |
| Real-time streaming | High | Low | Architecture change needed |

## Not Planned

- **GUI Interface**: This is a CLI-focused tool. See [UI.md](UI.md).
- **Training Pipeline**: Uses pretrained models only. See [RESEARCH.md](RESEARCH.md).
- **Cloud Deployment**: Local execution only. Docker support available in [Architecture.md](Architecture.md).
