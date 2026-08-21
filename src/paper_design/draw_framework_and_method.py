#!/usr/bin/env python3
"""Draw the first two RegionSufficiency manuscript figures locally.

The layout deliberately uses only single-segment horizontal or vertical
connectors.  Quantitative panels will be generated separately from trusted
results.json files; this script creates the conceptual study and method figures.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
from PIL import Image


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "figures"
OUT.mkdir(parents=True, exist_ok=True)

FUNDUS = (
    ROOT
    / "7hao/datasets/UWF_DR_1630/extracted/Ultra-wide-field (SLO) fundus image dataset for intelligent diabetic retinopathy system/diabetic retinopathy/PDR512/5_313_2020-10-21_1_L.png"
)

COL = {
    "paper": "#FFFDFC",
    "paper2": "#FBF7F1",
    "peach": "#F7ECE6",
    "apricot": "#F5CFAA",
    "orange": "#E49F5D",
    "orange2": "#F1C89A",
    "ochre": "#C58B47",
    "umber": "#965E4A",
    "brown": "#704C2B",
    "olive": "#8B9A7C",
    "olive2": "#E5E8D9",
    "rose": "#B95372",
    "gray": "#D8D0C8",
    "gray2": "#EEE9E3",
    "ink": "#3F3027",
    "white": "#FFFFFF",
}


mpl.rcParams.update(
    {
        "font.family": "Arial",
        "font.size": 9,
        "text.color": COL["ink"],
        "axes.labelcolor": COL["ink"],
        "figure.facecolor": COL["paper"],
        "savefig.facecolor": COL["paper"],
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
        "mathtext.fontset": "stixsans",
    }
)


def rounded(
    ax,
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    fc: str,
    ec: str = COL["umber"],
    lw: float = 1.2,
    radius: float = 1.7,
    shadow: bool = False,
    z: int = 2,
):
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle=f"round,pad=0.35,rounding_size={radius}",
        facecolor=fc,
        edgecolor=ec,
        linewidth=lw,
        zorder=z,
    )
    if shadow:
        patch.set_path_effects(
            [pe.SimplePatchShadow(offset=(1.2, -1.2), alpha=0.12), pe.Normal()]
        )
    ax.add_patch(patch)
    return patch


def txt(
    ax,
    x: float,
    y: float,
    s: str,
    *,
    size: float = 8,
    weight: str = "normal",
    color: str = COL["ink"],
    ha: str = "center",
    va: str = "center",
    style: str = "normal",
    z: int = 6,
    linespacing: float = 1.12,
):
    return ax.text(
        x,
        y,
        s,
        fontsize=size,
        fontweight=weight,
        color=color,
        ha=ha,
        va=va,
        fontstyle=style,
        zorder=z,
        linespacing=linespacing,
    )


def arrow(
    ax,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    *,
    color: str = COL["umber"],
    lw: float = 1.4,
    head: float = 9,
    z: int = 4,
):
    if not (abs(x1 - x2) < 1e-9 or abs(y1 - y2) < 1e-9):
        raise ValueError(f"Connector must be horizontal or vertical: {(x1,y1,x2,y2)}")
    a = FancyArrowPatch(
        (x1, y1),
        (x2, y2),
        arrowstyle="-|>",
        mutation_scale=head,
        linewidth=lw,
        color=color,
        shrinkA=0,
        shrinkB=0,
        zorder=z,
    )
    ax.add_patch(a)
    return a


def stage_panel(ax, x, y, w, h, letter, title, fill, edge):
    rounded(ax, x, y, w, h, fc=COL["paper2"], ec=edge, lw=1.4, radius=2.2, shadow=True)
    rounded(ax, x + 1.1, y + h - 8.3, w - 2.2, 6.6, fc=fill, ec=edge, lw=1.0, radius=1.4)
    txt(ax, x + 2.3, y + h - 5.0, letter, size=10.5, weight="bold", color=edge, ha="left")
    txt(ax, x + w / 2 + 1.0, y + h - 5.0, title, size=10.3, weight="bold", color=COL["ink"])


def load_fundus() -> np.ndarray:
    return np.asarray(Image.open(FUNDUS).convert("RGB"))


def masked_view(img: np.ndarray, mode: str) -> np.ndarray:
    h, w = img.shape[:2]
    out = np.zeros_like(img)
    if mode == "full":
        return img.copy()
    cells: Iterable[tuple[int, int]]
    if mode == "center":
        cells = [(1, 1)]
    elif mode == "cross":
        cells = [(0, 1), (1, 0), (1, 1), (1, 2), (2, 1)]
    else:
        raise ValueError(mode)
    for r, c in cells:
        y0, y1 = int(r * h / 3), int((r + 1) * h / 3)
        x0, x1 = int(c * w / 3), int((c + 1) * w / 3)
        out[y0:y1, x0:x1] = img[y0:y1, x0:x1]
    return out


def show_img(ax, img, x, y, w, h, *, grid=False, border=COL["brown"], lw=0.9):
    ax.imshow(img, extent=(x, x + w, y, y + h), zorder=3, interpolation="lanczos")
    ax.add_patch(Rectangle((x, y), w, h, fill=False, ec=border, lw=lw, zorder=5))
    if grid:
        for k in (1, 2):
            ax.plot([x + k * w / 3] * 2, [y, y + h], color=COL["paper"], lw=0.9, zorder=5)
            ax.plot([x, x + w], [y + k * h / 3] * 2, color=COL["paper"], lw=0.9, zorder=5)


def save(fig, stem):
    for ext in ("svg", "pdf", "png"):
        kwargs = {"dpi": 360} if ext == "png" else {}
        fig.savefig(OUT / f"{stem}.{ext}", bbox_inches="tight", pad_inches=0.04, **kwargs)


def draw_palette():
    fig, ax = plt.subplots(figsize=(11, 1.8))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 1.8)
    ax.axis("off")
    items = [
        ("Paper", COL["paper"]),
        ("Peach", COL["peach"]),
        ("Apricot", COL["apricot"]),
        ("Orange", COL["orange"]),
        ("Umber", COL["umber"]),
        ("Brown", COL["brown"]),
        ("Olive", COL["olive"]),
        ("Risk", COL["rose"]),
    ]
    for i, (name, color) in enumerate(items):
        x = 0.2 + i * 1.34
        rounded(ax, x, 0.62, 1.08, 0.72, fc=color, ec=COL["brown"], lw=0.7, radius=0.12)
        txt(ax, x + 0.54, 0.38, name, size=7.6, weight="bold")
        txt(ax, x + 0.54, 0.17, color, size=6.7, color=COL["umber"])
    save(fig, "RMB20_Publication_Palette")
    plt.close(fig)


def draw_overview():
    img = load_fundus()
    full, center, cross = img, masked_view(img, "center"), masked_view(img, "cross")

    fig, ax = plt.subplots(figsize=(16, 9))
    ax.set_xlim(0, 160)
    ax.set_ylim(0, 90)
    ax.axis("off")
    txt(ax, 4, 86.2, "RegionSufficiency: from hidden evidence gaps to evidence-aware retinal assessment", size=17, weight="bold", color=COL["brown"], ha="left")
    txt(ax, 4, 82.8, "Study overview and validation logic", size=9.5, color=COL["umber"], ha="left")

    xs = [3, 42.5, 82, 121.5]
    y, w, h = 8, 35.5, 71.5
    stage_panel(ax, xs[0], y, w, h, "A", "Hidden diagnostic gap", COL["peach"], COL["umber"])
    stage_panel(ax, xs[1], y, w, h, "B", "Study cohorts & views", COL["apricot"], COL["ochre"])
    stage_panel(ax, xs[2], y, w, h, "C", "RegionSufficiency", COL["olive2"], COL["olive"])
    stage_panel(ax, xs[3], y, w, h, "D", "Evidence & action", COL["peach"], COL["umber"])
    for i in range(3):
        arrow(ax, xs[i] + w + 1.0, 44, xs[i + 1] - 1.0, 44, color=COL["brown"], lw=1.8, head=12)

    # Panel A
    show_img(ax, full, xs[0] + 3.0, 48.0, 13.4, 16.5, border=COL["olive"])
    show_img(ax, center, xs[0] + 19.1, 48.0, 13.4, 16.5, border=COL["rose"])
    txt(ax, xs[0] + 9.7, 66.4, "Complete view", size=8.4, weight="bold")
    txt(ax, xs[0] + 25.8, 66.4, "Clear but incomplete", size=8.4, weight="bold")
    rounded(ax, xs[0] + 2.6, 36.5, 30.4, 8.3, fc=COL["paper"], ec=COL["gray"], lw=0.9, radius=1.1)
    txt(ax, xs[0] + 5.0, 42.0, "Image quality", size=7.8, weight="bold", ha="left")
    txt(ax, xs[0] + 29.8, 42.0, "PASS", size=7.8, weight="bold", color=COL["olive"], ha="right")
    txt(ax, xs[0] + 5.0, 39.0, "Diagnostic evidence", size=7.8, weight="bold", ha="left")
    txt(ax, xs[0] + 29.8, 39.0, "MAY FAIL", size=7.8, weight="bold", color=COL["rose"], ha="right")
    rounded(ax, xs[0] + 3.2, 15.2, 29.2, 15.5, fc=COL["peach"], ec=COL["umber"], lw=1.0, radius=1.4)
    txt(ax, xs[0] + 17.8, 25.4, "Hidden assumption", size=8.8, weight="bold", color=COL["umber"])
    txt(ax, xs[0] + 17.8, 20.7, "A fundus AI model is usually forced\nto predict even when key retinal\nevidence was never captured.", size=8.0)

    # Panel B
    rounded(ax, xs[1] + 3.0, 56.0, 29.5, 10.0, fc=COL["paper"], ec=COL["ochre"], lw=1.0, radius=1.2)
    txt(ax, xs[1] + 6.0, 62.7, "Development", size=7.5, weight="bold", color=COL["ochre"], ha="left")
    txt(ax, xs[1] + 6.0, 59.0, "UWF-DR   n = 1,630   patient-grouped", size=8.3, weight="bold", ha="left")
    rounded(ax, xs[1] + 3.0, 43.4, 29.5, 10.0, fc=COL["paper"], ec=COL["olive"], lw=1.0, radius=1.2)
    txt(ax, xs[1] + 6.0, 50.1, "Independent external test", size=7.5, weight="bold", color=COL["olive"], ha="left")
    txt(ax, xs[1] + 6.0, 46.4, "MMRDR-UWF   n = 2,597   test only", size=8.3, weight="bold", ha="left")
    thumb_y = 25.0
    for k, (name, view, edge) in enumerate(
        [("Full", full, COL["olive"]), ("Center", center, COL["rose"]), ("Center + cross", cross, COL["orange"])]
    ):
        xx = xs[1] + 2.8 + k * 10.7
        show_img(ax, view, xx, thumb_y, 8.8, 10.8, border=edge)
        txt(ax, xx + 4.4, 22.8, name, size=7.4, weight="bold")
    rounded(ax, xs[1] + 4.0, 13.0, 27.5, 6.4, fc=COL["apricot"], ec=COL["ochre"], lw=0.9, radius=1.0)
    txt(ax, xs[1] + 17.75, 16.2, "Area  |  Location  |  Shape  |  Region set", size=7.9, weight="bold")

    # Panel C
    show_img(ax, full, xs[2] + 3.0, 54.5, 9.8, 12.0, grid=True, border=COL["olive"])
    rounded(ax, xs[2] + 17.0, 55.3, 15.0, 10.4, fc=COL["paper"], ec=COL["olive"], lw=1.0, radius=1.1)
    txt(ax, xs[2] + 24.5, 62.3, "3 × 3 region bank", size=8.3, weight="bold")
    txt(ax, xs[2] + 24.5, 58.6, r"visible tokens  $h_i$", size=8.0, color=COL["umber"])
    arrow(ax, xs[2] + 13.5, 60.5, xs[2] + 16.0, 60.5, color=COL["olive"], lw=1.4)
    rounded(ax, xs[2] + 4.0, 41.0, 27.5, 8.0, fc=COL["olive2"], ec=COL["olive"], lw=1.1, radius=1.2)
    txt(ax, xs[2] + 17.75, 46.2, "Shared retinal encoder", size=8.5, weight="bold")
    txt(ax, xs[2] + 17.75, 43.3, "frozen representation + trainable projection", size=7.2, color=COL["umber"])
    arrow(ax, xs[2] + 17.75, 54.0, xs[2] + 17.75, 50.0, color=COL["olive"], lw=1.4)
    rounded(ax, xs[2] + 4.0, 28.2, 27.5, 8.0, fc=COL["apricot"], ec=COL["orange"], lw=1.1, radius=1.2)
    txt(ax, xs[2] + 17.75, 33.4, "Visibility-conditioned attention", size=8.5, weight="bold")
    txt(ax, xs[2] + 17.75, 30.5, "masked regions receive zero weight", size=7.2, color=COL["umber"])
    arrow(ax, xs[2] + 17.75, 40.0, xs[2] + 17.75, 37.2, color=COL["orange"], lw=1.4)
    rounded(ax, xs[2] + 3.2, 14.0, 13.8, 8.5, fc=COL["paper"], ec=COL["olive"], lw=1.0, radius=1.1)
    rounded(ax, xs[2] + 18.5, 14.0, 13.8, 8.5, fc=COL["paper"], ec=COL["rose"], lw=1.0, radius=1.1)
    txt(ax, xs[2] + 10.1, 18.3, "DR severity\nNormal · NPDR · PDR", size=7.7, weight="bold")
    txt(ax, xs[2] + 25.4, 18.3, "Underestimation\nrisk audit", size=7.7, weight="bold", color=COL["rose"])
    arrow(ax, xs[2] + 10.1, 27.2, xs[2] + 10.1, 23.5, color=COL["olive"], lw=1.3)
    arrow(ax, xs[2] + 25.4, 27.2, xs[2] + 25.4, 23.5, color=COL["rose"], lw=1.3)

    # Panel D
    rows = [
        ("Controlled evidence topology", "How much, where, and how distributed?", COL["orange"]),
        ("Internal model evidence", "Multi-seed performance and matched ablations", COL["ochre"]),
        ("Independent UWF replication", "MMRDR view comparison and paired bootstrap", COL["olive"]),
        ("Selective decision", "Risk–coverage and subgroup boundary audit", COL["rose"]),
    ]
    yy = 60.0
    for title, sub, edge in rows:
        rounded(ax, xs[3] + 3.0, yy - 5.0, 29.3, 9.1, fc=COL["paper"], ec=edge, lw=1.0, radius=1.1)
        txt(ax, xs[3] + 5.2, yy + 1.0, title, size=8.1, weight="bold", color=edge, ha="left")
        txt(ax, xs[3] + 5.2, yy - 2.2, sub, size=7.1, ha="left")
        yy -= 11.2
    rounded(ax, xs[3] + 4.0, 12.8, 12.8, 7.0, fc=COL["olive2"], ec=COL["olive"], lw=1.1, radius=1.2)
    rounded(ax, xs[3] + 18.7, 12.8, 12.8, 7.0, fc=COL["peach"], ec=COL["rose"], lw=1.1, radius=1.2)
    txt(ax, xs[3] + 10.4, 16.3, "ACCEPT", size=8.8, weight="bold", color=COL["olive"])
    txt(ax, xs[3] + 25.1, 16.3, "DEFER", size=8.8, weight="bold", color=COL["rose"])

    txt(ax, 80, 3.0, "A clear image can still be diagnostically insufficient when the visible retinal evidence is incomplete.", size=9.2, weight="bold", color=COL["brown"])
    save(fig, "Figure1_Study_Overview_RMB20")
    plt.close(fig)


def mask_matrix(ax, x, y, mode, edge, title):
    if mode == "full":
        m = np.ones((3, 3), int)
    elif mode == "center":
        m = np.zeros((3, 3), int); m[1, 1] = 1
    elif mode == "cross":
        m = np.zeros((3, 3), int); m[1, :] = 1; m[:, 1] = 1
    else:
        raise ValueError(mode)
    cell = 2.0
    for r in range(3):
        for c in range(3):
            fc = COL["olive"] if m[r, c] else COL["gray2"]
            ax.add_patch(Rectangle((x + c * cell, y + (2-r) * cell), cell, cell, fc=fc, ec=COL["paper"], lw=0.8, zorder=4))
    ax.add_patch(Rectangle((x, y), 3*cell, 3*cell, fill=False, ec=edge, lw=1.0, zorder=5))
    txt(ax, x + 3.0, y - 1.6, title, size=7.1, weight="bold")


def draw_method():
    img = load_fundus()
    fig, ax = plt.subplots(figsize=(16, 9))
    ax.set_xlim(0, 160)
    ax.set_ylim(0, 90)
    ax.axis("off")
    txt(ax, 4, 86.0, "RegionSufficiency architecture and leakage-controlled evaluation", size=17, weight="bold", color=COL["brown"], ha="left")
    txt(ax, 4, 82.7, "Current implementation: visibility-conditioned severity model + paired-view underestimation risk audit", size=9.3, color=COL["umber"], ha="left")

    xs = [3, 40.7, 78.4, 116.1]
    y, w, h = 18.0, 34.8, 61.0
    stage_panel(ax, xs[0], y, w, h, "A", "View construction", COL["peach"], COL["umber"])
    stage_panel(ax, xs[1], y, w, h, "B", "Regional representation", COL["apricot"], COL["ochre"])
    stage_panel(ax, xs[2], y, w, h, "C", "Masked evidence aggregation", COL["olive2"], COL["olive"])
    stage_panel(ax, xs[3], y, w, h, "D", "Severity & risk decision", COL["peach"], COL["umber"])
    for i in range(3):
        arrow(ax, xs[i] + w + 0.8, 48.5, xs[i+1] - 0.8, 48.5, color=COL["brown"], lw=1.7, head=11)

    # A: image and masks
    show_img(ax, img, xs[0] + 3.4, 47.0, 14.5, 17.8, grid=True, border=COL["umber"])
    rounded(ax, xs[0] + 20.5, 49.0, 10.8, 14.0, fc=COL["paper"], ec=COL["umber"], lw=1.0, radius=1.1)
    txt(ax, xs[0] + 25.9, 59.2, "Retinal ROI", size=8.1, weight="bold")
    txt(ax, xs[0] + 25.9, 55.5, r"$x=\{x_1,\ldots,x_9\}$", size=9.1, color=COL["brown"])
    txt(ax, xs[0] + 25.9, 51.7, "3 × 3 region bank", size=7.2)
    arrow(ax, xs[0] + 18.8, 56.0, xs[0] + 19.7, 56.0, color=COL["umber"], lw=1.3)
    mask_matrix(ax, xs[0] + 3.5, 31.5, "full", COL["olive"], "Full")
    mask_matrix(ax, xs[0] + 13.9, 31.5, "center", COL["rose"], "Center")
    mask_matrix(ax, xs[0] + 24.3, 31.5, "cross", COL["orange"], "Center + cross")
    rounded(ax, xs[0] + 4.0, 21.6, 26.8, 5.8, fc=COL["apricot"], ec=COL["orange"], lw=0.9, radius=1.0)
    txt(ax, xs[0] + 17.4, 24.5, "Training only: random region masking  ρ = 0.30", size=7.4, weight="bold")

    # B: encoder and projection
    rounded(ax, xs[1] + 3.4, 53.0, 10.2, 9.0, fc=COL["paper"], ec=COL["umber"], lw=1.0, radius=1.0)
    txt(ax, xs[1] + 8.5, 58.5, r"Region $x_i$", size=8.2, weight="bold")
    txt(ax, xs[1] + 8.5, 55.0, "shared input", size=7.0, color=COL["umber"])
    rounded(ax, xs[1] + 17.0, 50.0, 14.0, 15.0, fc=COL["gray2"], ec=COL["umber"], lw=1.2, radius=1.2)
    txt(ax, xs[1] + 24.0, 61.2, "Frozen encoder", size=8.4, weight="bold", color=COL["umber"])
    txt(ax, xs[1] + 24.0, 57.5, "RetinaRadar", size=8.0, weight="bold")
    txt(ax, xs[1] + 24.0, 54.5, "EfficientNet-B0", size=7.2)
    txt(ax, xs[1] + 24.0, 51.8, r"$E(x_i)$", size=9.0, color=COL["brown"])
    arrow(ax, xs[1] + 14.4, 57.5, xs[1] + 16.1, 57.5, color=COL["umber"], lw=1.4)
    rounded(ax, xs[1] + 7.0, 37.0, 20.7, 8.0, fc=COL["apricot"], ec=COL["orange"], lw=1.1, radius=1.1)
    txt(ax, xs[1] + 17.35, 42.1, r"Trainable projection $\phi$", size=8.3, weight="bold")
    txt(ax, xs[1] + 17.35, 39.1, r"$h_i=\phi(E(x_i))$", size=9.1, color=COL["brown"])
    arrow(ax, xs[1] + 24.0, 49.0, xs[1] + 24.0, 46.0, color=COL["orange"], lw=1.4)
    rounded(ax, xs[1] + 6.0, 24.0, 22.7, 7.5, fc=COL["olive2"], ec=COL["olive"], lw=1.0, radius=1.1)
    txt(ax, xs[1] + 17.35, 28.7, "Regional token matrix", size=8.0, weight="bold")
    txt(ax, xs[1] + 17.35, 25.8, r"$H=[h_1,\ldots,h_9]$", size=9.0, color=COL["brown"])
    arrow(ax, xs[1] + 17.35, 36.0, xs[1] + 17.35, 32.5, color=COL["olive"], lw=1.4)

    # C: full and limited lanes
    rounded(ax, xs[2] + 3.0, 51.0, 28.8, 13.5, fc=COL["paper"], ec=COL["olive"], lw=1.1, radius=1.2)
    txt(ax, xs[2] + 5.0, 61.3, "Full-view lane", size=8.0, weight="bold", color=COL["olive"], ha="left")
    txt(ax, xs[2] + 5.0, 57.6, r"$a_i^{(F)}=\frac{m_i^{(F)}e^{e_i}}{\sum_j m_j^{(F)}e^{e_j}}$", size=8.5, ha="left")
    txt(ax, xs[2] + 5.0, 53.7, r"$z^{(F)}=\sum_i a_i^{(F)}h_i\;\;\rightarrow\;\;p^{(F)}$", size=8.5, ha="left")
    rounded(ax, xs[2] + 3.0, 33.0, 28.8, 13.5, fc=COL["paper"], ec=COL["orange"], lw=1.1, radius=1.2)
    txt(ax, xs[2] + 5.0, 43.3, "Limited-view lane", size=8.0, weight="bold", color=COL["orange"], ha="left")
    txt(ax, xs[2] + 5.0, 39.6, r"$a_i^{(L)}=\frac{m_i^{(L)}e^{e_i}}{\sum_j m_j^{(L)}e^{e_j}}$", size=8.5, ha="left")
    txt(ax, xs[2] + 5.0, 35.7, r"$z^{(L)}=\sum_i a_i^{(L)}h_i\;\;\rightarrow\;\;p^{(L)}$", size=8.5, ha="left")
    rounded(ax, xs[2] + 6.0, 22.0, 22.8, 6.7, fc=COL["olive2"], ec=COL["olive"], lw=0.9, radius=1.0)
    txt(ax, xs[2] + 17.4, 26.6, "Shared attention and classifier weights", size=7.2, weight="bold")
    txt(ax, xs[2] + 17.4, 24.2, r"$p^{(v)}=\mathrm{softmax}(W_cz^{(v)}+b_c)$", size=7.5, color=COL["brown"])
    arrow(ax, xs[2] + 17.4, 32.0, xs[2] + 17.4, 29.7, color=COL["olive"], lw=1.2)

    # D: severity and risk
    rounded(ax, xs[3] + 3.0, 54.0, 28.7, 10.8, fc=COL["olive2"], ec=COL["olive"], lw=1.1, radius=1.2)
    txt(ax, xs[3] + 17.35, 61.2, "Severity prediction", size=8.5, weight="bold", color=COL["olive"])
    txt(ax, xs[3] + 17.35, 57.8, r"$\hat y^{(L)}=\arg\max_c p_c^{(L)}$", size=8.8)
    txt(ax, xs[3] + 17.35, 55.5, "Normal  ·  NPDR  ·  PDR", size=7.4, weight="bold")
    rounded(ax, xs[3] + 3.0, 39.0, 28.7, 10.7, fc=COL["peach"], ec=COL["umber"], lw=1.0, radius=1.2)
    txt(ax, xs[3] + 17.35, 46.6, "18-D paired evidence-gap vector", size=8.1, weight="bold", color=COL["umber"])
    txt(ax, xs[3] + 17.35, 42.8, r"$[p^{(F)},p^{(L)},\Delta p,|\Delta p|,\mu_F,\mu_L,\Delta\mu,H_F,H_L,D_{SKL}]$", size=7.3)
    rounded(ax, xs[3] + 3.0, 28.0, 28.7, 6.8, fc=COL["apricot"], ec=COL["orange"], lw=1.0, radius=1.0)
    txt(ax, xs[3] + 17.35, 32.1, r"Risk estimator  $r=\sigma(\beta^T\tilde F+b)$", size=8.0, weight="bold")
    txt(ax, xs[3] + 17.35, 29.8, r"training target: $u=\mathbb{1}[\hat y^{(L)}<y]$", size=6.9, color=COL["rose"])
    rounded(ax, xs[3] + 3.0, 20.0, 28.7, 5.2, fc=COL["paper"], ec=COL["umber"], lw=0.9, radius=0.9)
    ax.add_patch(Rectangle((xs[3] + 17.35, 20.0), 0.08, 5.2, fc=COL["gray"], ec="none", zorder=5))
    txt(ax, xs[3] + 10.0, 22.6, r"$r\leq\tau$  ACCEPT", size=7.6, weight="bold", color=COL["olive"])
    txt(ax, xs[3] + 24.5, 22.6, r"$r>\tau$  DEFER", size=7.6, weight="bold", color=COL["rose"])
    arrow(ax, xs[3] + 17.35, 53.0, xs[3] + 17.35, 50.7, color=COL["umber"], lw=1.2)
    arrow(ax, xs[3] + 17.35, 38.0, xs[3] + 17.35, 35.8, color=COL["orange"], lw=1.2)
    arrow(ax, xs[3] + 17.35, 27.0, xs[3] + 17.35, 26.2, color=COL["umber"], lw=1.2)

    # Protocol strip
    txt(ax, 4.0, 13.9, "Protocol separation", size=9.2, weight="bold", color=COL["brown"], ha="left")
    strip_y = 5.0
    strip = [
        (4.0, 46.0, "TRAIN", "Fit severity model with stochastic region masks", COL["orange"]),
        (57.0, 46.0, "VALIDATION", r"Fit logistic risk estimator and freeze $\tau$", COL["ochre"]),
        (110.0, 46.0, "TEST / EXTERNAL", "Freeze all parameters; report paired uncertainty", COL["olive"]),
    ]
    for xx, ww, head, body, edge in strip:
        rounded(ax, xx, strip_y, ww, 7.0, fc=COL["paper"], ec=edge, lw=1.0, radius=1.0)
        txt(ax, xx + 3.0, strip_y + 4.7, head, size=7.4, weight="bold", color=edge, ha="left")
        txt(ax, xx + ww - 2.5, strip_y + 3.2, body, size=7.2, ha="right")
    arrow(ax, 51.0, 8.5, 56.0, 8.5, color=COL["brown"], lw=1.4)
    arrow(ax, 104.0, 8.5, 109.0, 8.5, color=COL["brown"], lw=1.4)

    save(fig, "Figure2_Method_Architecture_RMB20")
    plt.close(fig)


if __name__ == "__main__":
    draw_palette()
    draw_overview()
    draw_method()
    print(f"Wrote figures to {OUT}")
