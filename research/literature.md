# Literature Review: DeepFake Detection

## Research Question

How can we improve deepfake video detection accuracy using state-of-the-art pretrained models with minimal implementation effort?

---

## Key Papers

| Paper | Year | Method | Reported Metrics | Notes |
|-------|------|--------|------------------|-------|
| Unlocking the Hidden Potential of CLIP in Generalizable Deepfake Detection | 2025 | CLIP ViT-L/14 + LN-tuning | 96.62% AUC (Celeb-DF-v2), 87.15% (DFDC) | Best cross-dataset generalization |
| DeepfakeBench: A Comprehensive Benchmark | 2023 | Benchmark of 36 methods | Varies by method | Reference for comparing methods |
| Effort: Orthogonal Subspace Decomposition | 2025 | ICML Spotlight | SOTA on DeepfakeBench | Highly generalizable |
| GenD: Deepfake Detection that Generalizes | 2026 | Layer Norm tuning (0.03% params) | SOTA cross-dataset AUROC | WACV 2026 |

---

## State-of-the-Art Summary

### Best Reported Performance

| Dataset | Best Method | Performance | Reference |
|---------|-------------|-------------|-----------|
| FaceForensics++ | Various ViT | 99%+ | DeepfakeBench |
| Celeb-DF-v2 | CLIP-based | 96.62% AUC | yermandy |
| DFDC | CLIP-based | 87.15% AUC | yermandy |
| Cross-dataset average | GenD | SOTA AUROC | arXiv |

### Common Approaches

1. **Vision Transformers (ViT)**
   - Dominant architecture for 2024-2025
   - Better at capturing global features vs CNNs
   - EfficientNet/ResNet now considered baseline

2. **CLIP-based Methods**
   - Leverage pretrained vision-language representations
   - Strong zero-shot and few-shot capabilities
   - Best cross-dataset generalization

3. **Parameter-Efficient Fine-Tuning (PEFT)**
   - LoRA, LN-tuning for adaptation
   - Preserves pretrained knowledge
   - Reduces overfitting to training set

4. **Metric Learning**
   - L2 normalization on hyperspherical manifold
   - Improves feature separability
   - Better generalization

---

## Relevant Pretrained Models (Hugging Face)

### Tier 1: Production-Ready (Recommended)

#### 1. prithivMLmods/Deep-Fake-Detector-v2-Model
- **Architecture**: ViT-base-patch16-224 (google/vit-base-patch16-224-in21k)
- **Accuracy**: 92.12%
- **F1-Score**: ~0.92
- **Size**: 85.8M parameters
- **Last Updated**: February 2025
- **License**: MIT
- **Usage**:
```python
from transformers import pipeline
pipe = pipeline('image-classification', model="prithivMLmods/Deep-Fake-Detector-v2-Model")
result = pipe("image.jpg")
```

#### 2. yermandy/deepfake-detection
- **Architecture**: CLIP ViT-L/14 with LN-tuning
- **Performance**: 96.62% AUC (Celeb-DF-v2), 87.15% (DFDC)
- **Trained On**: FaceForensics++
- **Key Advantage**: Best cross-dataset generalization
- **License**: MIT
- **Paper**: arXiv:2503.19683

### Tier 2: Alternative Options

#### 3. dima806/deepfake_vs_real_image_detection
- **Accuracy**: 99.27% (on test set)
- **Warning**: Model is ~3 years old, concept drift likely
- **Recommendation**: Use as ensemble member, not primary

#### 4. prithivMLmods/Deepfake-Detect-Siglip2
- **Architecture**: SigLIP-based vision-language model
- **Accuracy**: 94.44%
- **Advantage**: Vision-language pretraining

---

## Open Challenges

1. **Concept Drift**
   - Newer deepfake generation methods may evade older detectors
   - Models need periodic retraining

2. **Cross-Dataset Generalization**
   - Models trained on FF++ often fail on Celeb-DF, DFDC
   - CLIP-based methods show best generalization

3. **Video-Level Detection**
   - Most models are frame-level classifiers
   - Temporal consistency reasoning needed

4. **Adversarial Robustness**
   - Deepfakes can be crafted to evade detection
   - Ensemble methods may help

---

## Recommended Approach

Based on literature review, the recommended approach is:

1. **Primary Model**: yermandy/deepfake-detection (CLIP-based)
   - Best generalization, well-documented
   - GitHub: https://github.com/yermandy/deepfake-detection

2. **Fallback/Ensemble**: prithivMLmods/Deep-Fake-Detector-v2-Model
   - Simple integration, good accuracy
   - Direct HuggingFace pipeline support

3. **Evaluation**: Compare both on test videos and select best performer

---

## Sources

- [Hugging Face - Deep-Fake-Detector-v2-Model](https://huggingface.co/prithivMLmods/Deep-Fake-Detector-v2-Model)
- [Hugging Face - yermandy/deepfake-detection](https://huggingface.co/yermandy/deepfake-detection)
- [GitHub - DeepfakeBench](https://github.com/SCLBD/DeepfakeBench)
- [Papers With Code - DeepFake Detection](https://paperswithcode.com/task/deepfake-detection)
- [arXiv - Unlocking CLIP for Deepfake Detection](https://arxiv.org/abs/2503.19683)
