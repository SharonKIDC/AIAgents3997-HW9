"""Command-line interface for DeepFake Detector."""

import json
import logging
import sys
import time
from typing import Optional

import click

from deepfake_detector.analyzers.face_analyzer import FaceAnalyzer
from deepfake_detector.analyzers.video_analyzer import VideoAnalyzer
from deepfake_detector.models.detector import DeepFakeDetector, ResultAggregator
from deepfake_detector.utils.config import load_config
from deepfake_detector.utils.logging_config import setup_logging
from deepfake_detector.utils.validators import (
    ValidationError,
    validate_device,
    validate_num_frames,
    validate_output_format,
    validate_threshold,
    validate_video_path,
)

logger = logging.getLogger(__name__)


def print_banner() -> None:
    """Print application banner."""
    click.echo("=" * 50)
    click.echo("DeepFake Video Detector")
    click.echo("=" * 50)


def print_result_text(result, video_path: str, processing_time: float) -> None:
    """Print detection result in text format with detailed explanations."""
    click.echo("")
    click.echo("=" * 60)
    click.echo("                    DETECTION RESULTS")
    click.echo("=" * 60)

    # Verdict with color
    if result.verdict == "FAKE":
        click.secho(f"  Verdict: {result.verdict}", fg="red", bold=True)
        click.echo("")
        click.secho(
            "  This video shows signs of AI manipulation or deepfake generation.",
            fg="red",
        )
    else:
        click.secho(f"  Verdict: {result.verdict}", fg="green", bold=True)
        click.echo("")
        click.secho(
            "  This video appears to be authentic with no manipulation detected.",
            fg="green",
        )

    click.echo("")
    click.echo(f"  Confidence: {result.confidence:.1%}")
    click.echo("=" * 60)
    click.echo("")

    # Detailed Evidence Section
    click.secho("EVIDENCE ANALYSIS:", bold=True)
    click.echo("-" * 60)

    for indicator in result.indicators:
        click.echo("")
        if indicator.detected:
            click.secho(
                f"  [DETECTED] {indicator.name.upper()}", fg="yellow", bold=True
            )
        else:
            click.secho(f"  [OK] {indicator.name.upper()}", fg="green")

        click.echo(f"    Score: {indicator.score:.1%}")
        click.echo(f"    {indicator.description}")

        # Add detailed explanation for each indicator
        _print_indicator_explanation(indicator, result)

    click.echo("")
    click.echo("-" * 60)

    # Summary section
    click.secho("ANALYSIS SUMMARY:", bold=True)
    click.echo(f"  - Video analyzed: {video_path}")
    click.echo(f"  - Frames processed: {len(result.frame_results)}")
    click.echo(f"  - Processing time: {processing_time:.2f} seconds")
    click.echo(f"  - Model: vit-deepfake (ViT-based HuggingFace detector)")
    click.echo("")

    # Interpretation guide
    click.secho("HOW TO INTERPRET:", bold=True)
    click.echo("  - Confidence 0-30%:   Likely AUTHENTIC")
    click.echo("  - Confidence 30-50%:  UNCERTAIN, manual review recommended")
    click.echo("  - Confidence 50-70%:  Likely MANIPULATED")
    click.echo("  - Confidence 70-100%: High confidence DEEPFAKE")
    click.echo("")


def _print_indicator_explanation(indicator, result) -> None:
    """Print detailed explanation for each indicator."""
    if indicator.name == "face_manipulation":
        total_frames = len(result.frame_results)
        fake_frames = sum(1 for f in result.frame_results if f.confidence > 0.5)
        click.echo("")
        click.echo("    EXPLANATION:")
        click.echo(
            f"    The ViT (Vision Transformer) model analyzed {total_frames} frames"
        )
        click.echo(f"    and detected manipulation artifacts in {fake_frames} frames.")
        if indicator.score > 0.7:
            click.echo("    High detection rate across frames indicates systematic")
            click.echo("    face manipulation consistent with deepfake generation.")
        elif indicator.score > 0.3:
            click.echo("    Moderate detection suggests possible manipulation.")
            click.echo("    Manual review of flagged frames is recommended.")
        else:
            click.echo("    Low detection rate suggests authentic facial content.")

    elif indicator.name == "temporal_consistency":
        click.echo("")
        click.echo("    EXPLANATION:")
        if indicator.detected:
            click.echo("    Frame-to-frame predictions show HIGH VARIANCE, indicating")
            click.echo("    inconsistent manipulation or detection uncertainty.")
            click.echo("    This may suggest partial manipulation or edge cases.")
        else:
            click.echo("    Frame-to-frame predictions are CONSISTENT, indicating")
            click.echo("    the model has high agreement across the video.")
            if any(f.confidence > 0.5 for f in result.frame_results):
                click.echo("    Consistent high scores strongly suggest deepfake.")
            else:
                click.echo("    Consistent low scores suggest authentic video.")

    elif indicator.name == "overall_confidence":
        click.echo("")
        click.echo("    EXPLANATION:")
        click.echo(f"    Combined score from all frames: {indicator.score:.1%}")
        click.echo("    Formula: 70% mean score + 30% max score across frames.")
        if indicator.detected:
            click.echo("    Score EXCEEDS threshold - classified as FAKE.")
        else:
            click.echo("    Score BELOW threshold - classified as NOT FAKE.")


def print_result_json(result, video_path: str, processing_time: float) -> None:
    """Print detection result in JSON format."""
    output = {
        "verdict": result.verdict,
        "confidence": result.confidence,
        "reasoning": [
            {
                "indicator": ind.name,
                "detected": ind.detected,
                "score": ind.score,
                "description": ind.description,
            }
            for ind in result.indicators
        ],
        "metadata": {
            "video_path": video_path,
            "frames_analyzed": len(result.frame_results),
            "processing_time_seconds": round(processing_time, 3),
        },
    }
    click.echo(json.dumps(output, indent=2))


@click.group()
@click.version_option(version="0.1.0", prog_name="deepfake-detector")
def main() -> None:
    """DeepFake Video Detector - Analyze videos for AI-generated content."""


@main.command()
@click.argument("video_path", type=click.Path(exists=False))
@click.option(
    "-t",
    "--threshold",
    type=float,
    default=None,
    help="Confidence threshold for fake detection (0.0-1.0).",
)
@click.option(
    "-n",
    "--num-frames",
    type=int,
    default=None,
    help="Number of frames to analyze.",
)
@click.option(
    "-d",
    "--device",
    type=str,
    default=None,
    help="Compute device (cpu/cuda/cuda:N/auto).",
)
@click.option(
    "-o",
    "--output",
    "output_format",
    type=click.Choice(["text", "json"]),
    default=None,
    help="Output format.",
)
@click.option(
    "--json",
    "json_output",
    is_flag=True,
    help="Output results as JSON (shorthand for -o json).",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output.",
)
@click.option(
    "-c",
    "--config",
    "config_path",
    type=click.Path(exists=True),
    default=None,
    help="Path to custom configuration file.",
)
def analyze(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    video_path: str,
    threshold: Optional[float],
    num_frames: Optional[int],
    device: Optional[str],
    output_format: Optional[str],
    json_output: bool,
    verbose: bool,
    config_path: Optional[str],
) -> None:
    """
    Analyze a video for deepfake content.

    VIDEO_PATH: Path to the video file to analyze.
    """
    start_time = time.time()

    # Load configuration
    config = load_config(config_path)

    # Setup logging
    log_level = "DEBUG" if verbose else config.logging.level
    setup_logging(level=log_level, log_file=config.logging.log_file)

    # Apply CLI overrides
    if threshold is not None:
        config.detection.confidence_threshold = threshold
    if num_frames is not None:
        config.detection.num_frames = num_frames
    if device is not None:
        config.device = device
    if output_format is not None:
        config.output.output_format = output_format
    if json_output:
        config.output.output_format = "json"

    # Validate inputs
    try:
        video_path = str(validate_video_path(video_path))
        validate_threshold(config.detection.confidence_threshold)
        validate_num_frames(config.detection.num_frames)
        validate_device(config.device)
        validate_output_format(config.output.output_format)
    except ValidationError as exc:
        click.secho(f"Error: {exc}", fg="red", err=True)
        sys.exit(1)

    # Print banner for text output
    if config.output.output_format == "text":
        print_banner()
        click.echo(f"Analyzing: {video_path}")
        click.echo("")

    try:
        # Run analysis pipeline
        result = run_analysis_pipeline(video_path, config, verbose)

        processing_time = time.time() - start_time

        # Output results
        if config.output.output_format == "json":
            print_result_json(result, video_path, processing_time)
        else:
            print_result_text(result, video_path, processing_time)

        sys.exit(0)

    except ValidationError as exc:
        click.secho(f"Input error: {exc}", fg="red", err=True)
        sys.exit(1)
    except RuntimeError as exc:
        click.secho(f"Processing error: {exc}", fg="red", err=True)
        sys.exit(2)
    except Exception as exc:  # pylint: disable=broad-exception-caught
        logger.exception("Unexpected error during analysis")
        click.secho(f"Unexpected error: {exc}", fg="red", err=True)
        sys.exit(2)


def run_analysis_pipeline(video_path: str, config, verbose: bool):
    """
    Run the complete analysis pipeline.

    Args:
        video_path: Path to video file.
        config: Configuration object.
        verbose: Enable verbose output.

    Returns:
        AggregatedResult with detection results.
    """
    # Step 1: Load and extract frames
    if verbose:
        click.echo("Step 1/4: Loading video...")

    with VideoAnalyzer(max_duration=config.video.max_duration) as video:
        video_info = video.load(video_path)

        if verbose:
            click.echo(f"  Video: {video_info.width}x{video_info.height}")
            click.echo(f"  Duration: {video_info.duration:.1f}s")
            click.echo(f"  Frames: {video_info.frame_count}")

        if verbose:
            click.echo("Step 2/4: Extracting frames...")

        frames = video.extract_frames(
            num_frames=config.detection.num_frames,
            sample_rate=config.detection.sample_rate,
        )

        if verbose:
            click.echo(f"  Extracted {len(frames)} frames")

    # Step 2: Detect and extract faces
    if verbose:
        click.echo("Step 3/4: Detecting faces...")

    face_analyzer = FaceAnalyzer(
        target_size=config.video.frame_size,
        min_confidence=0.5,
    )

    face_crops = face_analyzer.extract_faces_from_frames(frames)

    if verbose:
        click.echo(f"  Found {len(face_crops)} face crops")

    if not face_crops:
        logger.warning("No faces detected in video")
        aggregator = ResultAggregator(threshold=config.detection.confidence_threshold)
        return aggregator.aggregate([], [], [])

    # Step 3: Run deepfake detection
    if verbose:
        click.echo("Step 4/4: Running detection model...")

    detector = DeepFakeDetector(
        model_name=config.detection.model,
        device=config.device,
        cache_dir=config.model_cache_dir,
    )
    detector.load_model()

    scores = detector.predict(face_crops)

    if verbose:
        click.echo(f"  Analyzed {len(scores)} faces")

    # Step 4: Aggregate results
    frame_indices = [crop.frame_index for crop in face_crops]
    faces_per_frame = [1] * len(face_crops)  # One face per crop

    aggregator = ResultAggregator(threshold=config.detection.confidence_threshold)
    result = aggregator.aggregate(scores, frame_indices, faces_per_frame)

    return result


@main.command()
@click.option("--validate", is_flag=True, help="Validate configuration.")
@click.option("--show", is_flag=True, help="Show effective configuration.")
@click.option(
    "-c",
    "--config",
    "config_path",
    type=click.Path(exists=True),
    default=None,
    help="Path to configuration file.",
)
def config_cmd(validate: bool, show: bool, config_path: Optional[str]) -> None:
    """Manage configuration settings."""
    try:
        cfg = load_config(config_path)

        if validate:
            click.secho("Configuration is valid.", fg="green")

        if show:
            click.echo("Effective configuration:")
            click.echo(f"  Model: {cfg.detection.model}")
            click.echo(f"  Threshold: {cfg.detection.confidence_threshold}")
            click.echo(f"  Num frames: {cfg.detection.num_frames}")
            click.echo(f"  Device: {cfg.device}")
            click.echo(f"  Output format: {cfg.output.output_format}")
            click.echo(f"  Log level: {cfg.logging.level}")

    except Exception as exc:  # pylint: disable=broad-exception-caught
        click.secho(f"Configuration error: {exc}", fg="red", err=True)
        sys.exit(1)


# Alias for backwards compatibility
main.add_command(config_cmd, name="config")


if __name__ == "__main__":
    main()
