"""
Generate visualizations for research results.
"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Create output directory
output_dir = Path("results/figures")
output_dir.mkdir(parents=True, exist_ok=True)

# Data from experiments
models = ["Baseline\n(EfficientNet)", "ViT Detector v2", "CLIP Zero-Shot"]
video1_confidence = [49.4, 83.6, 86.2]
video2_confidence = [51.0, 83.1, 81.7]
avg_confidence = [50.2, 83.4, 84.0]

# Colors
colors = ["#ff6b6b", "#4ecdc4", "#45b7d1"]

# Figure 1: Model Comparison Bar Chart
fig, ax = plt.subplots(figsize=(10, 6))

x = np.arange(len(models))
width = 0.25

bars1 = ax.bar(x - width, video1_confidence, width, label="man_hair.1.mp4", color="#4ecdc4", alpha=0.8)
bars2 = ax.bar(x, video2_confidence, width, label="man_hair.2.mp4", color="#45b7d1", alpha=0.8)
bars3 = ax.bar(x + width, avg_confidence, width, label="Average", color="#96ceb4", alpha=0.8)

# Add threshold line
ax.axhline(y=50, color="#ff6b6b", linestyle="--", linewidth=2, label="Random (50%)")
ax.axhline(y=85, color="#2ecc71", linestyle="--", linewidth=2, label="Target (85%)")

# Labels
ax.set_ylabel("Confidence (%)", fontsize=12)
ax.set_title("DeepFake Detection: Model Comparison", fontsize=14, fontweight="bold")
ax.set_xticks(x)
ax.set_xticklabels(models, fontsize=11)
ax.set_ylim(0, 100)
ax.legend(loc="upper left")
ax.grid(axis="y", alpha=0.3)

# Add value labels on bars
for bars in [bars1, bars2, bars3]:
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f"{height:.1f}%",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha="center", va="bottom", fontsize=9)

plt.tight_layout()
plt.savefig(output_dir / "model_comparison.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"Saved: {output_dir / 'model_comparison.png'}")

# Figure 2: Improvement Chart
fig, ax = plt.subplots(figsize=(8, 5))

improvement = [0, 33.2, 33.8]
bars = ax.bar(models, improvement, color=colors, alpha=0.8, edgecolor="black", linewidth=1)

ax.set_ylabel("Improvement over Baseline (%)", fontsize=12)
ax.set_title("DeepFake Detection: Improvement from Baseline", fontsize=14, fontweight="bold")
ax.set_ylim(0, 50)
ax.grid(axis="y", alpha=0.3)

# Add value labels
for bar, val in zip(bars, improvement):
    ax.annotate(f"+{val:.1f}%" if val > 0 else "Baseline",
                xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center", va="bottom", fontsize=11, fontweight="bold")

plt.tight_layout()
plt.savefig(output_dir / "improvement_chart.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"Saved: {output_dir / 'improvement_chart.png'}")

# Figure 3: Fake Frame Ratio
fig, ax = plt.subplots(figsize=(8, 5))

models_exp = ["ViT Detector v2", "CLIP Zero-Shot"]
fake_ratio_v1 = [100, 93.8]
fake_ratio_v2 = [100, 93.8]

x = np.arange(len(models_exp))
width = 0.35

bars1 = ax.bar(x - width/2, fake_ratio_v1, width, label="man_hair.1.mp4", color="#4ecdc4", alpha=0.8)
bars2 = ax.bar(x + width/2, fake_ratio_v2, width, label="man_hair.2.mp4", color="#45b7d1", alpha=0.8)

ax.set_ylabel("Fake Frame Detection Rate (%)", fontsize=12)
ax.set_title("Frame-Level Detection Consistency", fontsize=14, fontweight="bold")
ax.set_xticks(x)
ax.set_xticklabels(models_exp, fontsize=11)
ax.set_ylim(0, 110)
ax.legend()
ax.grid(axis="y", alpha=0.3)

for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f"{height:.1f}%",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha="center", va="bottom", fontsize=10)

plt.tight_layout()
plt.savefig(output_dir / "fake_frame_ratio.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"Saved: {output_dir / 'fake_frame_ratio.png'}")

# Figure 4: Summary Dashboard
fig, axes = plt.subplots(1, 3, figsize=(14, 4))

# Subplot 1: Before/After
ax1 = axes[0]
categories = ["Before", "After"]
values = [50.2, 83.4]
colors_ba = ["#ff6b6b", "#2ecc71"]
bars = ax1.bar(categories, values, color=colors_ba, alpha=0.8, edgecolor="black", linewidth=1)
ax1.set_ylabel("Confidence (%)")
ax1.set_title("Detection Confidence")
ax1.set_ylim(0, 100)
for bar, val in zip(bars, values):
    ax1.annotate(f"{val:.1f}%",
                xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center", va="bottom", fontsize=12, fontweight="bold")

# Subplot 2: Detection Rate
ax2 = axes[1]
categories = ["Before", "After"]
values = [50, 100]
bars = ax2.bar(categories, values, color=colors_ba, alpha=0.8, edgecolor="black", linewidth=1)
ax2.set_ylabel("Detection Rate (%)")
ax2.set_title("Fake Detection Rate")
ax2.set_ylim(0, 110)
for bar, val in zip(bars, values):
    ax2.annotate(f"{val}%",
                xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center", va="bottom", fontsize=12, fontweight="bold")

# Subplot 3: Improvement
ax3 = axes[2]
ax3.pie([33.2, 66.8], labels=["Improvement\n+33.2%", ""], colors=["#2ecc71", "#ecf0f1"],
        autopct="", startangle=90, explode=(0.05, 0))
ax3.set_title("Overall Improvement")

plt.suptitle("DeepFake Detection Research Summary", fontsize=14, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig(output_dir / "research_summary.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"Saved: {output_dir / 'research_summary.png'}")

print("\nAll figures generated successfully!")
