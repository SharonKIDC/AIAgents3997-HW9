# Contributing to DeepFake Detector

Thank you for your interest in contributing to DeepFake Detector! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow

## Getting Started

### Development Setup

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/deepfake-detector.git
   cd deepfake-detector
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

5. **Verify setup:**
   ```bash
   pytest tests/
   pylint src/ --score=y
   ```

### Project Structure

```
deepfake-detector/
├── src/deepfake_detector/    # Main package
│   ├── cli.py                # CLI entry point
│   ├── models/               # ML model wrappers
│   ├── analyzers/            # Video analysis logic
│   └── utils/                # Helper functions
├── tests/
│   ├── unit/                 # Unit tests
│   └── integration/          # Integration tests
├── docs/                     # Documentation
└── config/                   # Configuration files
```

## Development Workflow

### Branch Naming

Use descriptive branch names:

- `feature/add-xception-model` - New features
- `bugfix/fix-memory-leak` - Bug fixes
- `docs/update-readme` - Documentation
- `refactor/simplify-pipeline` - Code refactoring

### Making Changes

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes following code standards (see below)**

3. **Run quality checks:**
   ```bash
   # Format code
   black src/ tests/
   isort --profile black src/ tests/

   # Run linting
   pylint src/ --score=y  # Must achieve 10.0/10
   ruff check src/ tests/

   # Run tests
   pytest tests/ -v
   ```

4. **Commit with conventional format:**
   ```bash
   git commit -m "feat(models): add XceptionNet detector

   - Implemented XceptionNet wrapper class
   - Added model weight downloading
   - Created unit tests for new detector

   🤖 Generated with [Claude Code](https://claude.com/claude-code)"
   ```

5. **Push and create a pull request:**
   ```bash
   git push origin feature/your-feature-name
   ```

## Code Standards

### Python Style

- **Formatter**: Black (line length 88)
- **Import sorting**: isort with black profile
- **Linting**: pylint (target 10.0/10) and ruff
- **Type hints**: Required for all public functions

```python
# Good example
def analyze_video(
    video_path: str,
    num_frames: int = 30,
    threshold: float = 0.5,
) -> AnalysisResult:
    """
    Analyze a video for deepfake content.

    Args:
        video_path: Path to the video file.
        num_frames: Number of frames to sample.
        threshold: Confidence threshold for fake detection.

    Returns:
        AnalysisResult with verdict and reasoning.

    Raises:
        FileNotFoundError: If video file doesn't exist.
        ValueError: If video format is unsupported.
    """
    ...
```

### Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting (no code change)
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance tasks

### Testing Requirements

- **Coverage target**: 80% minimum
- **Unit tests**: For all public functions
- **Integration tests**: For CLI and pipeline

```python
# tests/unit/test_detector.py
import pytest
from deepfake_detector.models import DeepFakeDetector


class TestDeepFakeDetector:
    def test_load_model_success(self, mock_model):
        """Test that model loads successfully."""
        detector = DeepFakeDetector(model_name="efficientnet")
        detector.load_model()
        assert detector.model is not None

    def test_predict_returns_scores(self, sample_faces):
        """Test that predict returns valid confidence scores."""
        detector = DeepFakeDetector(model_name="efficientnet")
        scores = detector.predict(sample_faces)
        assert all(0.0 <= s <= 1.0 for s in scores)
```

Run tests:
```bash
# All tests
pytest tests/

# With coverage
pytest tests/ --cov=src --cov-report=html

# Specific test file
pytest tests/unit/test_detector.py -v
```

## Pull Request Process

### Before Submitting

1. **All checks pass:**
   - [ ] `black --check src/ tests/` passes
   - [ ] `isort --check-only --profile black src/ tests/` passes
   - [ ] `pylint src/ --score=y` shows 10.0/10
   - [ ] `ruff check src/ tests/` passes
   - [ ] `pytest tests/` all pass

2. **Documentation updated:**
   - [ ] Docstrings for new functions
   - [ ] README updated if needed
   - [ ] ADR created for architectural decisions

3. **Tests added:**
   - [ ] Unit tests for new code
   - [ ] Integration tests if applicable

### PR Description Template

```markdown
## Summary
Brief description of changes.

## Changes
- Change 1
- Change 2

## Test Plan
- [ ] Unit tests added
- [ ] Integration tests added
- [ ] Manual testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] All tests pass
- [ ] PR has descriptive title
```

### Review Process

1. Submit PR with description
2. Automated checks run (CI)
3. Code review by maintainers
4. Address feedback
5. Merge when approved

## Reporting Issues

### Bug Reports

Include:
- Python version
- OS and version
- Steps to reproduce
- Expected vs actual behavior
- Error messages/logs

### Feature Requests

Include:
- Use case description
- Proposed solution
- Alternatives considered

## Architecture Decisions

For significant changes, create an ADR:

1. Copy `docs/ADRs/ADR-000-template.md`
2. Fill in context, decision, consequences
3. Submit with your PR

## Getting Help

- Open an issue for questions
- Check existing issues and PRs
- Review documentation in `/docs`

## Recognition

Contributors are recognized in:
- CHANGELOG.md
- GitHub contributors page
- Release notes

Thank you for contributing!
