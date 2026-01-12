# Quality Standards

## Code Quality

### Linting & Formatting

| Tool | Standard | Config |
|------|----------|--------|
| Black | Code formatting | Default (line length 88) |
| isort | Import sorting | Profile: black |
| Ruff | Linting | Default rules |
| Pylint | Code analysis | Score >= 9.0 |

### Type Safety

- Type hints required for all public functions
- `mypy` compatible (strict mode not enforced)

### Testing

| Metric | Target | Current |
|--------|--------|---------|
| Unit test coverage | 80% | See CI |
| Integration tests | Key flows | Implemented |
| Edge case coverage | All known | See [EXPECTED_RESULTS.md](EXPECTED_RESULTS.md) |

## Documentation Standards

- All public modules have docstrings
- README kept up-to-date with changes
- Architecture docs reflect implementation
- See [docs-deduplicator guidelines](../README.md#documentation) for cross-references

## Security Standards

- No secrets in code (see [SECURITY.md](SECURITY.md))
- Dependencies scanned with Bandit
- `.env.example` provided, `.env` gitignored

## CI/CD Pipeline

Located in `.github/workflows/ci.yml`:

1. **Lint Job**: Black, isort, Ruff, Pylint
2. **Test Job**: pytest with coverage
3. **Security Job**: Bandit scan

All jobs must pass for PR merge.

## Not Applicable

- **Performance Benchmarks**: Not enforced in CI. See [EXPECTED_RESULTS.md](EXPECTED_RESULTS.md) for manual benchmarks.
- **Load Testing**: CLI tool, not a service.
- **Accessibility Standards**: No UI. See [UI.md](UI.md).
