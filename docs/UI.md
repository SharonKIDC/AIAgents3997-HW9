# User Interface Documentation

## Design Decision: Command-Line Interface (CLI)

### Why CLI Instead of GUI?

This project deliberately uses a **command-line interface** rather than a graphical user interface. Here's the comprehensive reasoning behind this architectural decision:

#### 1. Target Use Case: Automation and Integration

The primary use case for deepfake detection is **batch processing and pipeline integration**:

- **Forensic analysts** need to scan hundreds of videos programmatically
- **Content moderators** integrate detection into existing moderation pipelines
- **Researchers** run experiments across large datasets
- **DevOps teams** automate detection in CI/CD or content pipelines

A CLI enables:
```bash
# Batch process entire directory
for video in /videos/*.mp4; do
    deepfake-detector analyze "$video" --json >> results.json
done

# Integrate with other tools
ffmpeg -i input.mp4 -t 30 clip.mp4 && deepfake-detector analyze clip.mp4

# Use in scripts with conditional logic
if deepfake-detector analyze video.mp4 --json | jq -e '.verdict == "FAKE"'; then
    echo "Warning: Potential deepfake detected"
fi
```

A GUI would require manual interaction for each video, making batch processing impractical.

#### 2. Server-Side Deployment

Deepfake detection often runs on:
- **Headless servers** without display capabilities
- **Docker containers** in cloud environments
- **HPC clusters** for research workloads
- **Edge devices** with limited resources

CLI applications work seamlessly in these environments without X11/display dependencies.

#### 3. Resource Efficiency

GUI frameworks add significant overhead:
- **Memory**: Qt/Tkinter/Electron add 100-500MB RAM usage
- **Dependencies**: GUI libraries increase package size 10-50x
- **Startup time**: GUI initialization adds seconds to startup

For a tool that processes videos (already memory-intensive), avoiding GUI overhead is critical.

#### 4. Reproducibility and Auditability

CLI commands are:
- **Self-documenting**: The exact command used is visible in logs/scripts
- **Reproducible**: Same command produces same results
- **Auditable**: Command history provides forensic trail

Example audit trail:
```bash
# Exactly what was run is recorded
$ history | grep deepfake
  142  deepfake-detector analyze suspect.mp4 --threshold 0.7 --json
  143  deepfake-detector analyze suspect.mp4 --threshold 0.5 --json
```

#### 5. Cross-Platform Consistency

CLI behavior is identical across:
- Linux (Ubuntu, CentOS, etc.)
- macOS
- Windows (PowerShell, WSL)

GUI applications often have platform-specific quirks and require separate testing.

### What About Users Who Want a GUI?

For users who prefer graphical interaction:

1. **Use JSON output with visualization tools**:
   ```bash
   deepfake-detector analyze video.mp4 --json | jq '.' | less
   ```

2. **Web-based wrappers** can be built on top:
   ```python
   # Flask/FastAPI wrapper example
   @app.post("/analyze")
   def analyze(video: UploadFile):
       result = subprocess.run(["deepfake-detector", "analyze", video.filename, "--json"])
       return json.loads(result.stdout)
   ```

3. **Future consideration**: A lightweight web UI could be added as a separate optional package without affecting the core CLI functionality.

### CLI Design Principles

The CLI follows established conventions for usability:

| Principle | Implementation |
|-----------|----------------|
| **Discoverability** | `--help` shows all options |
| **Sensible defaults** | Works without any flags |
| **Progressive disclosure** | Basic use is simple, advanced options available |
| **Machine-readable output** | `--json` for programmatic use |
| **Human-readable output** | Default text output is clear |
| **Exit codes** | 0=success, 1=error for scripting |

### Conclusion

The CLI design is **intentional and well-reasoned**, optimized for:
- Professional forensic and research workflows
- Automation and batch processing
- Server-side and containerized deployment
- Resource efficiency on GPU-heavy workloads

This is not a limitation but a **feature** aligned with the tool's primary use cases.

---

## CLI Usage Reference

For complete CLI documentation, see:
- [README.md](../README.md#quick-start) - Quick start examples
- [CONFIG.md](CONFIG.md#cli-options) - All CLI options
- [EXPECTED_RESULTS.md](EXPECTED_RESULTS.md) - Output format examples
