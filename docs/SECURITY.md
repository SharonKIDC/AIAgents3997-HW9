# Security Guidelines

## Overview

This document outlines security best practices for the DeepFake Video Detector project.

## Handling Secrets

### Environment Variables

All sensitive configuration must be stored in environment variables, never in code:

```bash
# Copy the template
cp .env.example .env

# Edit with your values
nano .env
```

**Never commit `.env` files to version control.**

### Sensitive Variables

| Variable | Purpose | Security Level |
|----------|---------|----------------|
| `HUGGINGFACE_TOKEN` | API access for model downloads | Optional, High |
| `LOG_FILE` | Path to log file | Low |

### Best Practices

1. **Use `.env` for local development** - Never hardcode credentials
2. **Rotate credentials regularly** - Especially API tokens
3. **Use environment-specific configs** - Different values for dev/staging/prod
4. **Limit token permissions** - Use read-only tokens when possible

## Model Security

### Trusted Model Sources

Only download models from verified sources:

- **HuggingFace Hub**: Official repositories with verified badges
- **PyTorch Hub**: Official model zoo
- **facenet-pytorch**: Published PyPI package

### Model Integrity

```python
# Verify model checksums when available
import hashlib

def verify_model(path, expected_sha256):
    with open(path, 'rb') as f:
        actual = hashlib.sha256(f.read()).hexdigest()
    return actual == expected_sha256
```

### Untrusted Input Handling

- Videos are processed in isolated temporary directories
- No shell commands are constructed from user input
- File paths are validated before processing

## Input Validation

### Video File Validation

1. **File extension check** - Only allow supported formats
2. **MIME type verification** - Validate actual file type
3. **Size limits** - Configurable maximum file size
4. **Path traversal prevention** - Sanitize file paths

```python
# Example validation
ALLOWED_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}

def is_valid_video(path):
    ext = Path(path).suffix.lower()
    return ext in ALLOWED_EXTENSIONS
```

## Dependency Security

### Regular Updates

```bash
# Check for security vulnerabilities
pip install safety
safety check

# Update dependencies
pip install --upgrade -r requirements.txt
```

### Pinned Versions

All dependencies are pinned in `pyproject.toml` to prevent supply chain attacks.

## Vulnerability Reporting

### Reporting Process

1. **Do not** open public issues for security vulnerabilities
2. Email security concerns to the project maintainers
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### Response Timeline

- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 1 week
- **Fix Timeline**: Depends on severity
  - Critical: 24-48 hours
  - High: 1 week
  - Medium: 2 weeks
  - Low: Next release

## Security Checklist

### Before Committing

- [ ] No hardcoded secrets or API keys
- [ ] No sensitive data in logs
- [ ] Input validation on all user inputs
- [ ] Dependencies updated and scanned

### Before Release

- [ ] Security scan with `bandit`
- [ ] Dependency audit with `safety`
- [ ] Review of all new dependencies
- [ ] Update security documentation if needed

## Tools

### Static Analysis

```bash
# Run bandit for security issues
pip install bandit
bandit -r src/

# Check dependencies
pip install safety
safety check
```

### Pre-commit Hooks

Security checks are included in pre-commit configuration:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ["-r", "src/"]
```

## License

This security policy applies to the DeepFake Video Detector project.
