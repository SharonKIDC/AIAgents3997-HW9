# Development Prompts

This document contains all the prompts used during the development of the DeepFake Video Detector project.

---

## Phase 1: Project Initialization

### Prompt 1: Initial Project Request
```
Create an app that gets a video as input and prints if the video is fake or not.
Use models from the internet to find features that indicate AI-generated video.
Output should include reasons for the Fake/NotFake determination.
```

### Prompt 2: PRD Creation
```
Phase: PreProject
Agent: prd-author
Task: Create comprehensive PRD for deepfake detection app

Include:
- Problem statement
- Functional requirements (FR-1, FR-2...)
- Success metrics with KPIs
- User stories
- Acceptance criteria
```

### Prompt 3: Architecture Design
```
Phase: PreProject
Agent: architecture-author
Task: Design system architecture for video deepfake detector

Requirements:
- CLI-based interface
- Frame extraction and face detection pipeline
- Pretrained model integration (EfficientNet/ViT)
- JSON output with evidence
```

---

## Phase 2: Implementation

### Prompt 4: Core Implementation
```
Phase: TaskLoop
Agent: implementer
Task: Implement the deepfake detector based on PRD and Architecture docs

Follow:
- FR-001 through FR-015 from PRD
- C4 architecture diagrams
- ADR decisions for model selection
```

### Prompt 5: Face Detection Pipeline
```
Implement face detection using MTCNN:
- Extract frames from video at configurable intervals
- Detect faces in each frame
- Crop and align faces for model input
- Handle videos with no detectable faces
```

### Prompt 6: Model Integration
```
Integrate pretrained deepfake detection model:
- Use EfficientNet-B0 as baseline
- Support model switching via config
- Return confidence scores per frame
- Aggregate frame results for video-level verdict
```

---

## Phase 3: Research & Improvement

### Prompt 7: Research Task
```
Phase: ResearchLoop
Agent: research-agent
Task: Improve deepfake detection accuracy from ~50% baseline

Approach:
- Survey state-of-the-art methods (2024-2025)
- Identify pretrained models on HuggingFace
- Run experiments comparing models
- Document results with visualizations
```

### Prompt 8: Model Comparison Experiment
```
Run experiments comparing:
1. Baseline EfficientNet-B0 (untrained)
2. Deep-Fake-Detector-v2 (ViT pretrained)
3. CLIP zero-shot detection

Metrics: confidence, accuracy, inference time
Test videos: man_hair.1.mp4, man_hair.2.mp4
```

### Prompt 9: Generate Visualizations
```
Create research figures:
- Model comparison bar chart
- Improvement over baseline chart
- Fake frame ratio comparison
- Research summary dashboard

Save to results/figures/ as PNG
```

---

## Phase 4: Quality & Release

### Prompt 10: Unit Test Creation
```
Phase: TaskLoop
Agent: unit-test-writer
Task: Write unit tests for deepfake detector

Coverage targets:
- Video analyzer module
- Face analyzer module
- Model detector class
- Configuration utilities
- CLI interface
```

### Prompt 11: Edge Case Handling
```
Phase: TaskLoop
Agent: edge-case-defender
Task: Handle edge cases in video processing

Cases to handle:
- Video with no faces detected
- Corrupted video files
- Very short videos (<1 second)
- Very long videos (>10 minutes)
- Invalid file formats
```

### Prompt 12: CI Pipeline Setup
```
Create GitHub Actions CI pipeline:
- Lint job: Black, isort, Ruff, Pylint
- Test job: pytest with coverage
- Security job: Bandit scan

Trigger on push/PR to main branch
```

### Prompt 13: Cost Analysis
```
Phase: ReleaseGate
Agent: cost-analyzer
Task: Analyze API and compute costs

Include:
- Token usage estimates
- Model inference costs
- Storage requirements
- Budget recommendations
```

### Prompt 14: Final Checklist
```
Phase: ReleaseGate
Agent: final-checklist-gate
Task: Complete release checklist

Verify:
- All tests passing
- Documentation complete
- Security scan clean
- Git workflow followed (15+ commits)
- Package installable
```

---

## Effective Prompt Patterns

### 1. Phase + Agent Context
```
Phase: [PreProject|TaskLoop|ResearchLoop|ReleaseGate]
Agent: [agent-id]
Task: [clear task description]
```

### 2. Structured Requirements
```
Requirements:
- Point 1
- Point 2
- Point 3

Constraints:
- Constraint 1
- Constraint 2
```

### 3. Metrics-Driven Goals
```
Success Criteria:
| Metric | Baseline | Target |
|--------|----------|--------|
| Accuracy | 50% | 85% |
| Speed | N/A | <2s/frame |
```

### 4. Experiment Format
```
Experiment: [Name]
Hypothesis: [What we expect]
Config: [Settings/models]
Expected Result: [Outcome]
```

---

## Anti-Patterns Avoided

1. **Vague requests** - Always specified acceptance criteria
2. **Skipping docs** - Created docs before/with code
3. **Massive commits** - Broke work into logical units
4. **Manual git** - Used git-workflow agent consistently

---

## Summary Statistics

| Phase | Prompts | Artifacts |
|-------|---------|-----------|
| PreProject | 3 | PRD, Architecture, Security docs |
| TaskLoop | 4 | Core implementation, tests |
| ResearchLoop | 3 | Research paper, experiments, figures |
| ReleaseGate | 4 | CI, costs, checklist |
| **Total** | **14** | **30+ files** |
