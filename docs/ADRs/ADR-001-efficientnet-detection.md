# ADR-001: Use EfficientNet-B4 for DeepFake Detection

## Status

Accepted

## Date

2026-01-10

## Context

We need to select a neural network architecture for classifying video frames as real or fake. The model must:

1. Be pre-trained and available publicly
2. Achieve high accuracy on deepfake benchmarks
3. Be efficient enough for practical use
4. Support both CPU and GPU inference

## Decision

Use EfficientNet-B4 architecture with weights pre-trained on deepfake detection datasets.

Specifically, we will use models from the `timm` library that have been fine-tuned for binary classification (real vs. fake).

## Consequences

### Positive

- **High accuracy**: EfficientNet-B4 achieves >90% accuracy on FaceForensics++ benchmark
- **Efficient**: Compound scaling provides better accuracy/compute trade-off than ResNet or VGG
- **Well-supported**: Available via timm with PyTorch, extensive documentation
- **Transfer learning**: ImageNet pre-training provides strong feature extraction
- **Reasonable size**: ~19M parameters, manageable for edge deployment

### Negative

- **Single architecture**: May miss detections that other architectures would catch
- **Fine-tuning required**: Base model needs deepfake-specific training
- **Input size constraints**: Fixed 224x224 or 380x380 input size

### Neutral

- Requires GPU for reasonable inference speed
- Model weights must be downloaded (initial setup time)

## Alternatives Considered

### Alternative 1: XceptionNet

XceptionNet was the original architecture used in FaceForensics++.

**Pros:**
- Proven on deepfake detection
- Depth-wise separable convolutions

**Cons:**
- Larger model size
- Slower inference

**Why not chosen:** EfficientNet provides better accuracy/efficiency trade-off.

### Alternative 2: Vision Transformer (ViT)

Modern transformer-based image classification.

**Pros:**
- State-of-the-art on many benchmarks
- Better at capturing global patterns

**Cons:**
- Requires more data for training
- Heavier computational requirements
- Fewer pre-trained deepfake-specific models

**Why not chosen:** Higher resource requirements, less mature deepfake-specific pre-training.

### Alternative 3: Ensemble of Multiple Architectures

Combine predictions from multiple models.

**Pros:**
- Higher accuracy
- Robustness to different fake types

**Cons:**
- Much slower inference
- More complex deployment
- Higher resource usage

**Why not chosen:** Saved for future "ensemble" mode, not default.

## References

- [EfficientNet Paper](https://arxiv.org/abs/1905.11946)
- [FaceForensics++ Benchmark](https://github.com/ondyari/FaceForensics)
- [timm library](https://github.com/huggingface/pytorch-image-models)
