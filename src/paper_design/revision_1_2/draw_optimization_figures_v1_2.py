#!/usr/bin/env python3
"""Draw the promoted continuous-aperture robustness figure from Exp60."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path("/Users/tongyue/Documents/77f /7hao")
EXP = ROOT / "experiments/exp60_pixel_aperture_training/results.json"
OUT = ROOT / "paper_design/revision_1_2/figures"
OUT.mkdir(parents=True, exist_ok=True)

INK = "#3F3027"
BROWN = "#704C2B"
UMBER = "#965E4A"
ORANGE = "#E49F5D"
OLIVE = "#8B9A7C"
ROSE = "#C74282"
PAPER = "#FFFDFC"
GRID = "#D9C9BA"

mpl.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 8.3,
        "axes.titlesize": 9.5,
        "axes.titleweight": "bold",
        "axes.labelsize": 8.3,
        "axes.edgecolor": INK,
        "axes.labelcolor": INK,
        "text.color": INK,
        "figure.facecolor": PAPER,
        "axes.facecolor": PAPER,
        "savefig.facecolor": PAPER,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.04,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
    }
)


def clean(ax, axis="y"):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis=axis, color=GRID, linewidth=0.6, alpha=0.55)
    ax.set_axisbelow(True)


def panel(ax, letter, title):
    ax.text(-0.13, 1.08, letter, transform=ax.transAxes, fontsize=12, fontweight="bold", color=BROWN, va="top")
    ax.set_title(title, loc="left", pad=8)


def main():
    result = json.loads(EXP.read_text(encoding="utf-8"))
    base = result["variants"]["baseline"]["aggregate"]["pixel"]
    aug = result["variants"]["pixel_augmented"]["aggregate"]["pixel"]
    scenarios = ["rect_center_0.35", "rect_center_0.55", "rect_center_0.75", "circle_center_0.55"]
    labels = ["Rect 0.35", "Rect 0.55", "Rect 0.75", "Circle 0.55"]
    x = np.arange(len(scenarios))
    width = 0.34
    fig, axs = plt.subplots(1, 3, figsize=(11.0, 3.9), constrained_layout=True)

    configs = [
        ("A", "Held-out macro-F1", "macro_f1", "Macro-F1", (0.35, 0.86)),
        ("B", "Held-out ordinal error", "severity_mae", "Severity MAE", (0.12, 0.55)),
        ("C", "Held-out underestimation", "underestimation_rate", "Underestimation rate", (0.00, 0.38)),
    ]
    for ax, (letter, title, metric, ylabel, ylim) in zip(axs, configs):
        panel(ax, letter, title)
        bmean = np.array([base[s][metric]["mean"] for s in scenarios])
        bsd = np.array([base[s][metric]["std"] for s in scenarios])
        amean = np.array([aug[s][metric]["mean"] for s in scenarios])
        asd = np.array([aug[s][metric]["std"] for s in scenarios])
        ax.bar(x - width / 2, bmean, width, yerr=bsd, capsize=2.5, color=OLIVE, edgecolor=BROWN, linewidth=0.7, label="Baseline", zorder=3)
        ax.bar(x + width / 2, amean, width, yerr=asd, capsize=2.5, color=ROSE, edgecolor=BROWN, linewidth=0.7, label="Pixel-aperture training", zorder=3)
        ax.set_xticks(x, labels, rotation=18, ha="right")
        ax.set_ylabel(ylabel)
        ax.set_ylim(*ylim)
        clean(ax)
        for i, (bv, av) in enumerate(zip(bmean, amean)):
            if metric == "underestimation_rate":
                text = f"Δ {av-bv:+.3f}"
            else:
                text = f"Δ {av-bv:+.3f}"
            ax.text(i, max(bv, av) + (ylim[1] - ylim[0]) * 0.035, text, ha="center", va="bottom", fontsize=7, color=UMBER)
    handles, legend_labels = axs[0].get_legend_handles_labels()
    fig.legend(handles, legend_labels, frameon=False, loc="upper center", bbox_to_anchor=(0.50, 0.925), ncol=2, fontsize=7.5)
    fig.suptitle("Pixel-aperture training improves F1 and MAE but shifts underestimation asymmetrically", fontsize=12.5, fontweight="bold", color=BROWN)
    for ext in ("png", "pdf", "svg"):
        fig.savefig(OUT / f"Figure8_Continuous_Aperture_Optimization_RMB20_v1_2.{ext}", dpi=420 if ext == "png" else None)
    plt.close(fig)


if __name__ == "__main__":
    main()
