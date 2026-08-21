#!/usr/bin/env python3
"""Redraw RegionSuff Figures 1 and 2 for manuscript version 1.2.

The diagrams keep the RMB-20 palette and use only straight horizontal or
vertical connectors.  Claims are intentionally limited to model auditing
under controlled evidence loss; no clinician-adjudicated sufficiency label or
deployable single-view triage head is implied.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Rectangle


ROOT = Path("/Users/tongyue/Documents/77f /7hao")
BASE_PATH = ROOT / "paper_design/draw_framework_and_method.py"
OUT = ROOT / "paper_design/revision_1_2/figures"
OUT.mkdir(parents=True, exist_ok=True)

spec = importlib.util.spec_from_file_location("basefig", BASE_PATH)
base = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(base)

COL = base.COL
rounded = base.rounded
txt = base.txt
arrow = base.arrow
stage_panel = base.stage_panel
show_img = base.show_img
load_fundus = base.load_fundus
masked_view = base.masked_view
mask_matrix = base.mask_matrix


def save(fig, stem: str):
    for ext in ("png", "pdf", "svg"):
        fig.savefig(
            OUT / f"{stem}.{ext}",
            dpi=420 if ext == "png" else None,
            bbox_inches="tight",
            pad_inches=0.04,
        )
    plt.close(fig)


def aperture_thumb(ax, x, y, shape, fraction, label):
    rounded(ax, x, y, 8.4, 8.4, fc=COL["gray2"], ec=COL["orange"], lw=0.8, radius=0.8)
    if shape == "rect":
        side = 6.0 * fraction
        ax.add_patch(Rectangle((x + 4.2 - side / 2, y + 4.2 - side / 2), side, side,
                               fc=COL["orange2"], ec=COL["umber"], lw=0.7, zorder=4))
    else:
        ax.add_patch(Circle((x + 4.2, y + 4.2), 3.0 * fraction,
                            fc=COL["orange2"], ec=COL["umber"], lw=0.7, zorder=4))
    txt(ax, x + 4.2, y - 1.2, label, size=6.7, weight="bold")


def draw_overview():
    img = load_fundus()
    center = masked_view(img, "center")
    cross = masked_view(img, "cross")

    fig, ax = plt.subplots(figsize=(16, 9))
    ax.set_xlim(0, 160)
    ax.set_ylim(0, 90)
    ax.axis("off")
    txt(ax, 4, 86.2, "RegionSuff: auditing retinal evidence availability under limited fields of view",
        size=16.2, weight="bold", color=COL["brown"], ha="left")
    txt(ax, 4, 82.8, "Study rationale, controlled perturbations, model, and evidence chain",
        size=9.2, color=COL["umber"], ha="left")

    xs = [3, 42.5, 82, 121.5]
    y, w, h = 9.0, 35.5, 70.0
    stage_panel(ax, xs[0], y, w, h, "A", "Hidden evidence gap", COL["peach"], COL["umber"])
    stage_panel(ax, xs[1], y, w, h, "B", "Controlled evidence loss", COL["apricot"], COL["ochre"])
    stage_panel(ax, xs[2], y, w, h, "C", "RegionSuff model", COL["olive2"], COL["olive"])
    stage_panel(ax, xs[3], y, w, h, "D", "Evidence and boundary", COL["peach"], COL["umber"])
    for i in range(3):
        arrow(ax, xs[i] + w + 0.9, 45.0, xs[i + 1] - 0.9, 45.0,
              color=COL["brown"], lw=1.7, head=11)

    # A: quality versus evidence availability.
    show_img(ax, img, xs[0] + 2.7, 49.0, 13.7, 16.2, border=COL["olive"])
    show_img(ax, center, xs[0] + 19.0, 49.0, 13.7, 16.2, border=COL["rose"])
    txt(ax, xs[0] + 9.55, 67.1, "Nominal full field", size=7.8, weight="bold")
    txt(ax, xs[0] + 25.85, 67.1, "Sharp but restricted", size=7.8, weight="bold")
    rounded(ax, xs[0] + 2.7, 35.5, 30.0, 9.0, fc=COL["paper"], ec=COL["gray"], lw=0.9, radius=1.1)
    txt(ax, xs[0] + 5.0, 41.7, "Technical gradability", size=7.7, weight="bold", ha="left")
    txt(ax, xs[0] + 30.4, 41.7, "may pass", size=7.7, weight="bold", color=COL["olive"], ha="right")
    txt(ax, xs[0] + 5.0, 38.2, "Task-relevant evidence", size=7.7, weight="bold", ha="left")
    txt(ax, xs[0] + 30.4, 38.2, "may be absent", size=7.7, weight="bold", color=COL["rose"], ha="right")
    rounded(ax, xs[0] + 3.4, 16.0, 28.6, 13.2, fc=COL["peach"], ec=COL["umber"], lw=1.0, radius=1.2)
    txt(ax, xs[0] + 17.7, 25.2, "Question", size=8.4, weight="bold", color=COL["umber"])
    txt(ax, xs[0] + 17.7, 20.6, "How does a fixed DR model behave\nwhen retinal evidence is removed\nin a controlled, traceable way?", size=7.8)

    # B: region and pixel perturbation families.
    show_img(ax, img, xs[1] + 2.7, 52.0, 8.8, 10.6, grid=True, border=COL["olive"])
    show_img(ax, center, xs[1] + 13.4, 52.0, 8.8, 10.6, border=COL["rose"])
    show_img(ax, cross, xs[1] + 24.1, 52.0, 8.8, 10.6, border=COL["orange"])
    txt(ax, xs[1] + 7.1, 49.7, "Full", size=7.0, weight="bold")
    txt(ax, xs[1] + 17.8, 49.7, "Center", size=7.0, weight="bold")
    txt(ax, xs[1] + 28.5, 49.7, "Center + cross", size=7.0, weight="bold")
    rounded(ax, xs[1] + 2.8, 39.0, 29.7, 6.5, fc=COL["paper"], ec=COL["ochre"], lw=0.9, radius=1.0)
    txt(ax, xs[1] + 17.65, 42.25, "Region topology: which 3×3 tokens are visible?", size=7.5, weight="bold")
    aperture_thumb(ax, xs[1] + 4.0, 24.0, "rect", 0.55, "Rectangle")
    aperture_thumb(ax, xs[1] + 13.7, 24.0, "circle", 0.73, "Area-matched circle")
    aperture_thumb(ax, xs[1] + 23.4, 24.0, "rect", 0.35, "Severe aperture")
    rounded(ax, xs[1] + 3.0, 14.2, 29.2, 5.8, fc=COL["apricot"], ec=COL["ochre"], lw=0.9, radius=0.9)
    txt(ax, xs[1] + 17.6, 17.1, "Area · location · shape · topology", size=7.7, weight="bold")

    # C: compact architecture.
    show_img(ax, img, xs[2] + 3.0, 55.0, 9.2, 11.0, grid=True, border=COL["olive"])
    rounded(ax, xs[2] + 17.2, 55.4, 14.7, 10.2, fc=COL["paper"], ec=COL["olive"], lw=1.0, radius=1.0)
    txt(ax, xs[2] + 24.55, 62.0, "3×3 evidence bank", size=8.0, weight="bold")
    txt(ax, xs[2] + 24.55, 58.2, "visible mask  m", size=7.4, color=COL["umber"])
    arrow(ax, xs[2] + 13.0, 60.5, xs[2] + 16.2, 60.5, color=COL["olive"], lw=1.3)
    rounded(ax, xs[2] + 4.0, 42.0, 27.6, 7.8, fc=COL["gray2"], ec=COL["umber"], lw=1.0, radius=1.0)
    txt(ax, xs[2] + 17.8, 47.0, "Frozen retinal-quality encoder", size=8.2, weight="bold")
    txt(ax, xs[2] + 17.8, 44.2, "shared across regions", size=7.0, color=COL["umber"])
    arrow(ax, xs[2] + 17.8, 54.3, xs[2] + 17.8, 50.8, color=COL["umber"], lw=1.3)
    rounded(ax, xs[2] + 4.0, 29.6, 27.6, 7.8, fc=COL["olive2"], ec=COL["olive"], lw=1.0, radius=1.0)
    txt(ax, xs[2] + 17.8, 34.5, "Masked attention over visible tokens", size=8.1, weight="bold")
    txt(ax, xs[2] + 17.8, 31.8, "unavailable regions receive zero weight", size=6.9, color=COL["umber"])
    arrow(ax, xs[2] + 17.8, 41.0, xs[2] + 17.8, 38.4, color=COL["olive"], lw=1.3)
    rounded(ax, xs[2] + 4.0, 17.2, 12.7, 7.2, fc=COL["paper"], ec=COL["olive"], lw=1.0, radius=1.0)
    rounded(ax, xs[2] + 18.9, 17.2, 12.7, 7.2, fc=COL["paper"], ec=COL["rose"], lw=1.0, radius=1.0)
    txt(ax, xs[2] + 10.35, 20.8, "DR severity\nNormal · NPDR · PDR", size=7.1, weight="bold")
    txt(ax, xs[2] + 25.25, 20.8, "Paired-view\nrisk audit", size=7.1, weight="bold", color=COL["rose"])
    arrow(ax, xs[2] + 10.35, 28.6, xs[2] + 10.35, 25.3, color=COL["olive"], lw=1.2)
    arrow(ax, xs[2] + 25.25, 28.6, xs[2] + 25.25, 25.3, color=COL["rose"], lw=1.2)

    # D: evidence chain, without deployment language.
    evidence = [
        ("Internal robustness", "390 held-out images · five seeds", COL["orange"]),
        ("Model intervention", "one-region occlusion vs attention", COL["ochre"]),
        ("External severity audit", "2,597 MMRDR-UWF images · no adaptation", COL["olive"]),
        ("Paired-view risk analysis", "fixed split is exploratory; nested audit is stricter", COL["rose"]),
    ]
    yy = 61.0
    for title, sub, edge in evidence:
        rounded(ax, xs[3] + 2.8, yy - 5.2, 29.8, 9.2, fc=COL["paper"], ec=edge, lw=1.0, radius=1.0)
        txt(ax, xs[3] + 5.0, yy + 0.8, title, size=7.9, weight="bold", color=edge, ha="left")
        txt(ax, xs[3] + 5.0, yy - 2.4, sub, size=6.8, ha="left")
        yy -= 11.2
    rounded(ax, xs[3] + 2.8, 12.6, 29.8, 7.8, fc=COL["peach"], ec=COL["umber"], lw=1.0, radius=1.0)
    txt(ax, xs[3] + 17.7, 16.5,
        "Boundary: synthetic evidence-loss audit,\nnot clinician-labelled sufficiency or single-view triage",
        size=6.6, weight="bold", color=COL["umber"])

    txt(ax, 80, 3.6,
        "Core claim: the composition and topology of visible retinal evidence change model behaviour beyond photographic quality or nominal field area alone.",
        size=8.6, weight="bold", color=COL["brown"])
    save(fig, "Figure1_Study_Overview_RMB20_v1_2")


def draw_method():
    img = load_fundus()
    fig, ax = plt.subplots(figsize=(16, 9))
    ax.set_xlim(0, 160)
    ax.set_ylim(0, 90)
    ax.axis("off")
    txt(ax, 4, 86.2, "RegionSuff model and evaluation protocols", size=16.4, weight="bold",
        color=COL["brown"], ha="left")
    txt(ax, 4, 82.9,
        "Consistent notation for visibility-conditioned severity inference and the paired-view exploratory risk audit",
        size=9.0, color=COL["umber"], ha="left")

    xs = [3, 40.7, 78.4, 116.1]
    y, w, h = 22.0, 34.8, 57.0
    stage_panel(ax, xs[0], y, w, h, "A", "Evidence construction", COL["peach"], COL["umber"])
    stage_panel(ax, xs[1], y, w, h, "B", "Regional tokens", COL["apricot"], COL["ochre"])
    stage_panel(ax, xs[2], y, w, h, "C", "Visibility-conditioned pooling", COL["olive2"], COL["olive"])
    stage_panel(ax, xs[3], y, w, h, "D", "Outputs and audit", COL["peach"], COL["umber"])
    for i in range(3):
        arrow(ax, xs[i] + w + 0.8, 51.0, xs[i + 1] - 0.8, 51.0,
              color=COL["brown"], lw=1.7, head=11)

    # A
    show_img(ax, img, xs[0] + 3.1, 51.0, 13.7, 16.2, grid=True, border=COL["umber"])
    rounded(ax, xs[0] + 20.1, 52.8, 11.0, 12.4, fc=COL["paper"], ec=COL["umber"], lw=1.0, radius=1.0)
    txt(ax, xs[0] + 25.6, 61.3, "Retinal ROI", size=7.9, weight="bold")
    txt(ax, xs[0] + 25.6, 57.6, r"$\mathcal{R}(x)=\{r_1,\ldots,r_9\}$", size=8.2, color=COL["brown"])
    txt(ax, xs[0] + 25.6, 54.8, "row-major regions", size=6.8)
    arrow(ax, xs[0] + 17.5, 59.0, xs[0] + 19.2, 59.0, color=COL["umber"], lw=1.2)
    mask_matrix(ax, xs[0] + 3.0, 36.8, "full", COL["olive"], "Full")
    mask_matrix(ax, xs[0] + 13.9, 36.8, "center", COL["rose"], "Center")
    mask_matrix(ax, xs[0] + 24.8, 36.8, "cross", COL["orange"], "Center + cross")
    rounded(ax, xs[0] + 3.0, 25.6, 29.0, 6.2, fc=COL["apricot"], ec=COL["orange"], lw=0.9, radius=0.9)
    txt(ax, xs[0] + 17.5, 28.7,
        "Training: independent token masking, ρ=0.30\nall-empty draw → region 1 restored",
        size=6.9, weight="bold")

    # B
    rounded(ax, xs[1] + 3.4, 55.0, 10.5, 8.6, fc=COL["paper"], ec=COL["umber"], lw=1.0, radius=1.0)
    txt(ax, xs[1] + 8.65, 59.3, r"Region $r_i$", size=8.2, weight="bold")
    rounded(ax, xs[1] + 17.0, 52.4, 14.0, 13.8, fc=COL["gray2"], ec=COL["umber"], lw=1.1, radius=1.1)
    txt(ax, xs[1] + 24.0, 62.3, "Frozen encoder E", size=8.2, weight="bold", color=COL["umber"])
    txt(ax, xs[1] + 24.0, 58.8, "RetinaRadar", size=7.8, weight="bold")
    txt(ax, xs[1] + 24.0, 55.4, "EfficientNet-B0", size=6.9)
    arrow(ax, xs[1] + 14.8, 59.3, xs[1] + 16.1, 59.3, color=COL["umber"], lw=1.2)
    rounded(ax, xs[1] + 6.2, 39.4, 22.4, 7.8, fc=COL["apricot"], ec=COL["orange"], lw=1.0, radius=1.0)
    txt(ax, xs[1] + 17.4, 44.3, "Trainable projection P", size=8.0, weight="bold")
    txt(ax, xs[1] + 17.4, 41.5, r"$z_i=P(E(r_i))\in\mathbb{R}^{128}$", size=8.2, color=COL["brown"])
    arrow(ax, xs[1] + 24.0, 51.4, xs[1] + 24.0, 48.2, color=COL["orange"], lw=1.3)
    rounded(ax, xs[1] + 6.2, 27.5, 22.4, 6.8, fc=COL["olive2"], ec=COL["olive"], lw=1.0, radius=1.0)
    txt(ax, xs[1] + 17.4, 30.9, r"Token bank $Z=[z_1,\ldots,z_9]$", size=7.8, weight="bold")
    arrow(ax, xs[1] + 17.4, 38.4, xs[1] + 17.4, 35.2, color=COL["olive"], lw=1.3)

    # C
    rounded(ax, xs[2] + 3.0, 56.0, 28.8, 8.7, fc=COL["paper"], ec=COL["olive"], lw=1.0, radius=1.0)
    txt(ax, xs[2] + 5.0, 61.8, "Evidence score", size=7.6, weight="bold", color=COL["olive"], ha="left")
    txt(ax, xs[2] + 5.0, 58.6, r"$e_i=w_a^{\mathsf{T}}\tanh(W_a z_i+b_a)+b_s$", size=8.2, ha="left")
    rounded(ax, xs[2] + 3.0, 43.2, 28.8, 8.7, fc=COL["paper"], ec=COL["orange"], lw=1.0, radius=1.0)
    txt(ax, xs[2] + 5.0, 49.0, "Masked normalization", size=7.6, weight="bold", color=COL["orange"], ha="left")
    txt(ax, xs[2] + 5.0, 45.8, r"$a_i(m)=m_i e^{e_i}/\sum_j m_j e^{e_j}$", size=8.2, ha="left")
    rounded(ax, xs[2] + 3.0, 30.4, 28.8, 8.7, fc=COL["paper"], ec=COL["olive"], lw=1.0, radius=1.0)
    txt(ax, xs[2] + 5.0, 36.2, "Visible evidence aggregation", size=7.6, weight="bold", color=COL["olive"], ha="left")
    txt(ax, xs[2] + 5.0, 33.0, r"$h(m)=\sum_i a_i(m)z_i\;\longrightarrow\;p(m)$", size=8.2, ha="left")
    arrow(ax, xs[2] + 17.4, 55.0, xs[2] + 17.4, 52.8, color=COL["olive"], lw=1.2)
    arrow(ax, xs[2] + 17.4, 42.2, xs[2] + 17.4, 40.0, color=COL["orange"], lw=1.2)
    rounded(ax, xs[2] + 5.4, 24.9, 24.0, 3.3, fc=COL["olive2"], ec=COL["olive"], lw=0.8, radius=0.7)
    txt(ax, xs[2] + 17.4, 26.55, "Same trainable head for every visibility mask", size=6.8, weight="bold")

    # D
    rounded(ax, xs[3] + 3.0, 55.0, 28.8, 9.5, fc=COL["olive2"], ec=COL["olive"], lw=1.0, radius=1.0)
    txt(ax, xs[3] + 17.4, 61.3, "Severity prediction", size=8.3, weight="bold", color=COL["olive"])
    txt(ax, xs[3] + 17.4, 57.5, r"$\widehat{y}(m)=\arg\max_c p_c(m)$", size=8.3)
    rounded(ax, xs[3] + 3.0, 41.1, 28.8, 9.5, fc=COL["peach"], ec=COL["umber"], lw=1.0, radius=1.0)
    txt(ax, xs[3] + 17.4, 47.4, r"Paired full/limited feature $g\in\mathbb{R}^{18}$", size=7.8, weight="bold", color=COL["umber"])
    txt(ax, xs[3] + 17.4, 43.7, "probabilities · gaps · entropy · symmetric KL", size=6.8)
    rounded(ax, xs[3] + 3.0, 29.0, 28.8, 7.5, fc=COL["apricot"], ec=COL["orange"], lw=1.0, radius=1.0)
    txt(ax, xs[3] + 17.4, 33.8, r"$q(g)=\sigma(\beta^{\mathsf{T}}\widetilde{g}+b)$", size=8.2, weight="bold")
    txt(ax, xs[3] + 17.4, 31.2, "event: limited prediction < reference label", size=6.6, color=COL["rose"])
    rounded(ax, xs[3] + 4.5, 24.0, 25.8, 3.1, fc=COL["paper"], ec=COL["rose"], lw=0.8, radius=0.7)
    txt(ax, xs[3] + 17.4, 25.55, "Audit requires both full and limited views", size=6.8, weight="bold", color=COL["rose"])

    # Bottom protocol strip.
    txt(ax, 4.0, 17.8, "Protocol separation", size=8.8, weight="bold", color=COL["brown"], ha="left")
    items = [
        (4.0, 35.0, "SEVERITY FIT", "UWF-DR train; full-view validation macro-F1 selects epoch", COL["orange"]),
        (41.0, 35.0, "INTERNAL TEST", "390 held-out images; seeds 0–4; descriptive seed dispersion", COL["ochre"]),
        (78.0, 38.0, "PAIRED RISK", "Fixed split = exploratory; nested grouped folds = stricter audit", COL["rose"]),
        (118.0, 38.0, "EXTERNAL TEST", "MMRDR severity only; no target training, calibration, or selection", COL["olive"]),
    ]
    for xx, ww, head, body, edge in items:
        rounded(ax, xx, 6.0, ww, 8.0, fc=COL["paper"], ec=edge, lw=1.0, radius=0.9)
        txt(ax, xx + 2.5, 11.4, head, size=6.9, weight="bold", color=edge, ha="left")
        txt(ax, xx + 2.5, 8.2, body, size=6.2, ha="left")
    save(fig, "Figure2_Method_Architecture_RMB20_v1_2")


if __name__ == "__main__":
    draw_overview()
    draw_method()
    print(OUT)
