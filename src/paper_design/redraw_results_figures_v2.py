#!/usr/bin/env python3
"""Publication redraw of RegionSuff Figures 3–8.

All values are loaded from the locked experiment registry.  This revision
keeps the RMB-20 palette while separating labels from error bars and replacing
unlabelled black reference lines with light, explicitly labelled references.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
from mpl_toolkits.axes_grid1.inset_locator import inset_axes


ROOT = Path('/Users/tongyue/Documents/77f /7hao')
EXP = ROOT / 'experiments'
OUT = ROOT / 'paper_design' / 'figures_v2'
OUT.mkdir(parents=True, exist_ok=True)

# Warm palette derived from the RMB-20 paper-note treatment used throughout
# the manuscript figures. Colours carry the same meaning in all panels.
INK = '#3F3027'
BROWN = '#704C2B'       # Full view / rectangle
ORANGE = '#E49F5D'      # Center view / augmented condition
OLIVE = '#8B9A7C'       # Center-plus-cross / external condition
ROSE = '#C74282'        # Critical contrast / circle / risk head
UMBER = '#965E4A'
PAPER = '#FFFDFC'
PALE = '#F7ECE6'
PALE_OLIVE = '#E5E8D9'
GRID = '#E5D8CD'
REFERENCE = '#9B928A'
ERROR = '#8E8176'
VIEW_COLORS = [BROWN, ORANGE, OLIVE]

mpl.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 9.3,
    'axes.titlesize': 10.6,
    'axes.titleweight': 'bold',
    'axes.labelsize': 9.2,
    'axes.edgecolor': INK,
    'axes.labelcolor': INK,
    'xtick.color': INK,
    'ytick.color': INK,
    'text.color': INK,
    'figure.facecolor': PAPER,
    'axes.facecolor': PAPER,
    'savefig.facecolor': PAPER,
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
    'svg.fonttype': 'none',
})


def load(name: str) -> dict:
    return json.loads((EXP / name / 'results.json').read_text(encoding='utf-8'))


def clean(ax, grid_axis: str | None = 'y') -> None:
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(0.8)
    ax.spines['bottom'].set_linewidth(0.8)
    ax.tick_params(length=3, width=0.7, labelsize=8.4)
    if grid_axis:
        ax.grid(axis=grid_axis, color=GRID, linewidth=0.65, alpha=0.9, zorder=0)
    ax.set_axisbelow(True)


def panel(ax, letter: str, title: str) -> None:
    ax.text(-0.13, 1.13, letter, transform=ax.transAxes, fontsize=11.8,
            fontweight='bold', color=BROWN, va='top', ha='left')
    ax.set_title(title, loc='left', pad=8, fontsize=10.4, fontweight='bold')


def err_style(color: str) -> dict:
    return {
        'ecolor': color,
        'elinewidth': 1.2,
        'capthick': 1.2,
        'capsize': 3.2,
    }


def refline(ax, x: float, label: str = 'No difference') -> None:
    """A semantic neutral reference, deliberately not a heavy black line."""
    ax.axvline(x, color=REFERENCE, linestyle=(0, (3, 3)), linewidth=1.05, zorder=1)
    ax.annotate(label, xy=(x, 1), xycoords=('data', 'axes fraction'), xytext=(4, -4),
                textcoords='offset points', ha='left', va='top', fontsize=7.2, color=REFERENCE,
                bbox=dict(facecolor=PAPER, edgecolor='none', pad=0.7))


def figure_base(rows: int = 2, cols: int = 2, *, figsize=(12.3, 7.45)):
    fig, axs = plt.subplots(rows, cols, figsize=figsize)
    fig.subplots_adjust(left=0.075, right=0.985, top=0.865, bottom=0.105,
                        wspace=0.33, hspace=0.56)
    return fig, axs


def save(fig, stem: str) -> None:
    for ext in ('png', 'pdf', 'svg'):
        fig.savefig(OUT / f'{stem}.{ext}', dpi=450 if ext == 'png' else None,
                    facecolor=PAPER, bbox_inches=None)
    plt.close(fig)


def figure3() -> None:
    """Area, location, shape, and topology without overprinted labels."""
    fov = load('exp48b_pixel_fov_geometry')['aggregate']
    multi = load('exp36_multiseed_deep_region')
    fig, axs = figure_base()

    # A — continuous fraction.
    ax = axs[0, 0]
    panel(ax, 'A', 'Visible fraction changes performance')
    fractions = [0.35, 0.45, 0.55, 0.65, 0.75, 0.90]
    for shape, color, marker, label in [
        ('rect', BROWN, 'o', 'Rectangle'),
        ('circle', ROSE, 's', 'Area-matched circle'),
    ]:
        mean = [fov[f'{shape}_center_{f:.2f}']['macro_f1']['mean'] for f in fractions]
        sd = [fov[f'{shape}_center_{f:.2f}']['macro_f1']['std'] for f in fractions]
        ax.errorbar(fractions, mean, yerr=sd, fmt=f'{marker}-', color=color, markersize=5.8,
                    linewidth=1.75, markeredgecolor=PAPER, markeredgewidth=0.8,
                    label=label, zorder=3, **err_style(color))
    ax.set_xlabel('Visible linear fraction')
    ax.set_ylabel('Macro-F1')
    ax.set_ylim(0.42, 0.87)
    ax.legend(frameon=False, fontsize=8.0, loc='lower right')
    clean(ax)

    # B — location. Underestimation gets its own clean panel rather than
    # competing with F1 bars and their error bars.
    ax = axs[0, 1]
    panel(ax, 'B', 'Same fraction, different retinal location')
    locs = ['center', 'left', 'right', 'up', 'down']
    labels = ['Center', 'Left', 'Right', 'Superior', 'Inferior']
    colors = [ORANGE, OLIVE, OLIVE, UMBER, UMBER]
    mean = [fov[f'rect_{x}_0.55']['underestimation_rate']['mean'] for x in locs]
    sd = [fov[f'rect_{x}_0.55']['underestimation_rate']['std'] for x in locs]
    for i, (m, s, c) in enumerate(zip(mean, sd, colors)):
        ax.errorbar(i, m, yerr=s, fmt='o', color=c, markersize=7, markeredgecolor=PAPER,
                    markeredgewidth=1.0, zorder=3, **err_style(c))
    ax.plot(np.arange(5), mean, color=GRID, linewidth=1.1, zorder=1)
    ax.set_xticks(np.arange(5), labels, rotation=0)
    ax.set_ylabel('Underestimation rate')
    ax.set_ylim(0, 0.30)
    ax.text(0.01, 0.94, 'Centered rectangular aperture: f = 0.55', transform=ax.transAxes,
            fontsize=7.6, color=UMBER, va='top')
    clean(ax)

    # C — shape at matched nominal area. It gives the exact shape contrast,
    # leaving no numerical annotation inside error-bar space.
    ax = axs[1, 0]
    panel(ax, 'C', 'Matched nominal area, different shape')
    shapes = [('rect', BROWN, 'Rectangle'), ('circle', ORANGE, 'Area-matched circle')]
    vals = [fov[f'{shape}_center_0.55']['macro_f1']['mean'] for shape, _, _ in shapes]
    errs = [fov[f'{shape}_center_0.55']['macro_f1']['std'] for shape, _, _ in shapes]
    bars = ax.bar(np.arange(2), vals, width=0.58, color=[x[1] for x in shapes],
                  edgecolor=INK, linewidth=0.65, zorder=3)
    for b, v, e, (_, c, _) in zip(bars, vals, errs, shapes):
        ax.errorbar(b.get_x() + b.get_width() / 2, v, yerr=e, fmt='none', zorder=4, **err_style(c))
        ax.text(b.get_x() + b.get_width() / 2, v + e + 0.012, f'{v:.3f}', ha='center', va='bottom', fontsize=8.2)
    ax.set_xticks(np.arange(2), [x[2] for x in shapes])
    ax.set_ylabel('Macro-F1')
    ax.set_ylim(0.54, 0.86)
    ax.text(0.5, 0.05, 'Both apertures use f = 0.55 (nominal area = f²).', transform=ax.transAxes,
            ha='center', fontsize=7.4, color=UMBER)
    clean(ax)

    # D — topology. Individual trajectories remain legible behind the mean.
    ax = axs[1, 1]
    panel(ax, 'D', 'Regional evidence topology (internal test)')
    views = ['full', 'center', 'cross']
    labels = ['Full', 'Center', 'Center + cross']
    rows = multi['rows']
    for seed in range(5):
        ys = [next(r['macro_f1'] for r in rows if r['seed'] == seed and r['view'] == view) for view in views]
        ax.plot(np.arange(3), ys, color='#D8CEC5', linewidth=1.0, marker='o', markersize=4.2,
                markerfacecolor=PAPER, markeredgecolor='#A8927F', zorder=2)
    mean = [multi['aggregate'][view]['macro_f1']['mean'] for view in views]
    sd = [multi['aggregate'][view]['macro_f1']['std'] for view in views]
    ax.errorbar(np.arange(3), mean, yerr=sd, fmt='D', markersize=6.1, color=BROWN,
                markerfacecolor=ORANGE, markeredgecolor=BROWN, zorder=4, label='Mean ± SD', **err_style(BROWN))
    ax.set_xticks(np.arange(3), labels)
    ax.set_ylabel('Macro-F1')
    ax.set_ylim(0.74, 0.87)
    ax.legend(frameon=False, fontsize=7.8, loc='lower left')
    clean(ax)

    fig.suptitle('Controlled evidence-loss tests: area, location, shape, and topology are not interchangeable',
                 fontsize=13.2, fontweight='bold', color=BROWN, y=0.972)
    save(fig, 'Figure3_Controlled_Visibility_RMB20_v2')


def figure4() -> None:
    abl = load('exp35_region_mask_pool_ablation')
    enc = load('exp37_encoder_ablation')['representations']
    pair = load('exp45_grid_paired_bootstrap')['rows']
    fig, axs = figure_base()

    ax = axs[0, 0]
    panel(ax, 'A', 'Regional encoder control')
    order = ['retinaradar_region', 'imagenet_resnet50_region', 'handcrafted_region', 'random_resnet50_region']
    labels = ['RetinaRadar\n(frozen)', 'ImageNet\nResNet-50', 'Handcrafted', 'Random\nResNet-50']
    vals = [enc[k]['cross']['macro_f1'] for k in order]
    colors = [ROSE, ORANGE, OLIVE, PALE]
    bars = ax.bar(np.arange(4), vals, color=colors, edgecolor=INK, linewidth=0.65, zorder=3)
    for bar, value in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.015, f'{value:.3f}', ha='center', va='bottom', fontsize=8)
    ax.set_xticks(np.arange(4), labels)
    ax.set_ylabel('Center + cross macro-F1')
    ax.set_ylim(0, 0.92)
    clean(ax)

    ax = axs[0, 1]
    panel(ax, 'B', 'Aggregation operator')
    pools = ['mean', 'max', 'attention']
    x = np.arange(3)
    width = 0.22
    for j, (view, color, label) in enumerate(zip(['full', 'center', 'cross'], VIEW_COLORS,
                                                  ['Full', 'Center', 'Center + cross'])):
        vals = [abl['pooling'][pool][view]['macro_f1'] for pool in pools]
        ax.bar(x + (j - 1) * width, vals, width, color=color, edgecolor=INK,
               linewidth=0.55, label=label, zorder=3)
    ax.set_xticks(x, ['Mean', 'Max', 'Attention'])
    ax.set_ylabel('Macro-F1')
    ax.set_ylim(0.70, 0.88)
    ax.legend(frameon=False, fontsize=7.6, ncol=3, loc='lower center', bbox_to_anchor=(0.5, 0.01))
    clean(ax)

    ax = axs[1, 0]
    panel(ax, 'C', 'Training mask-ratio sensitivity')
    ratios = [0, 0.15, 0.30, 0.45, 0.60]
    for view, color, marker, label in zip(['full', 'center', 'cross'], VIEW_COLORS, ['o', 's', '^'],
                                          ['Full', 'Center', 'Center + cross']):
        vals = [abl['mask_ratio'][str(r) if r else '0'][view]['macro_f1'] for r in ratios]
        ax.plot(ratios, vals, marker=marker, color=color, linewidth=1.65, markersize=5.4, label=label, zorder=3)
    ax.axvline(0.30, color=ROSE, linestyle=(0, (3, 3)), linewidth=1.05, zorder=1)
    ax.annotate('Reference ratio 0.30', xy=(0.30, 0.878), xytext=(4, -2), textcoords='offset points',
                fontsize=7.3, color=ROSE, va='top', ha='left', bbox=dict(facecolor=PAPER, edgecolor='none', pad=0.5))
    ax.set_xlabel('Random region mask ratio')
    ax.set_ylabel('Macro-F1')
    ax.set_ylim(0.77, 0.88)
    ax.legend(frameon=False, fontsize=7.6, ncol=3, loc='lower right')
    clean(ax)

    ax = axs[1, 1]
    panel(ax, 'D', 'Five-seed paired bootstrap: 4×4 minus 3×3')
    rows = [row for row in pair if row['view'] == 'cross']
    y = np.arange(len(rows))
    est = [row['delta_4x4_minus_3x3']['macro_f1']['mean'] for row in rows]
    lo = [row['delta_4x4_minus_3x3']['macro_f1']['ci95'][0] for row in rows]
    hi = [row['delta_4x4_minus_3x3']['macro_f1']['ci95'][1] for row in rows]
    xerr = np.array([[e - l for e, l in zip(est, lo)], [h - e for e, h in zip(est, hi)]])
    refline(ax, 0)
    ax.errorbar(est, y, xerr=xerr, fmt='o', markersize=5.2, color=BROWN, ecolor=ORANGE,
                elinewidth=1.2, capsize=3, zorder=3)
    ax.set_yticks(y, [f'Seed {row["seed"]}' for row in rows])
    ax.invert_yaxis()
    ax.set_xlabel('Paired Δ macro-F1 (4×4 − 3×3)')
    ax.set_xlim(-0.075, 0.09)
    ax.text(0.98, 0.06, 'All 95% CIs cross zero', transform=ax.transAxes, ha='right',
            fontsize=7.5, color=UMBER, bbox=dict(facecolor=PALE, edgecolor='none', pad=1.8))
    clean(ax, 'x')

    fig.suptitle('Component ablations: retinal representations help; selected controls are not unique optima',
                 fontsize=13.2, fontweight='bold', color=BROWN, y=0.972)
    save(fig, 'Figure4_Ablations_RMB20_v2')


def figure5() -> None:
    occ = load('exp39_attention_occlusion_validation')
    rows = occ['rows']
    att = np.array([r['mean_attention'] for r in rows]).reshape(3, 3)
    drop = np.array([r['performance_drop_macro_f1'] for r in rows]).reshape(3, 3)
    att_cmap = LinearSegmentedColormap.from_list('attention', [PALE, ORANGE, ROSE, BROWN])
    drop_cmap = LinearSegmentedColormap.from_list('drop', [OLIVE, PAPER, ROSE])
    fig, axs = figure_base(figsize=(12.3, 7.65))

    ax = axs[0, 0]
    panel(ax, 'A', 'Mean learned regional attention')
    im = ax.imshow(att, cmap=att_cmap, vmin=0, vmax=0.42)
    for (i, j), value in np.ndenumerate(att):
        ax.text(j, i, f'{value:.3f}', ha='center', va='center', fontsize=8.4,
                color='white' if value > 0.22 else INK)
    ax.set_xticks([0, 1, 2], ['Left', 'Center', 'Right'])
    ax.set_yticks([0, 1, 2], ['Superior', 'Middle', 'Inferior'])
    cb = fig.colorbar(im, ax=ax, fraction=0.045, pad=0.02)
    cb.set_label('Attention weight', fontsize=8.0)
    cb.ax.tick_params(labelsize=7.4)

    ax = axs[0, 1]
    panel(ax, 'B', 'One-region occlusion loss')
    vmax = max(abs(drop.min()), abs(drop.max()))
    im = ax.imshow(drop, cmap=drop_cmap, vmin=-vmax, vmax=vmax)
    for (i, j), value in np.ndenumerate(drop):
        ax.text(j, i, f'{value:+.3f}', ha='center', va='center', fontsize=8.4, color=INK)
    ax.set_xticks([0, 1, 2], ['Left', 'Center', 'Right'])
    ax.set_yticks([0, 1, 2], ['Superior', 'Middle', 'Inferior'])
    cb = fig.colorbar(im, ax=ax, fraction=0.045, pad=0.02)
    cb.set_label('Macro-F1 loss', fontsize=8.0)
    cb.ax.tick_params(labelsize=7.4)

    ax = axs[1, 0]
    panel(ax, 'C', 'Attention versus occlusion loss')
    x = np.array([r['mean_attention'] for r in rows])
    y = np.array([r['performance_drop_macro_f1'] for r in rows])
    ax.scatter(x, y, s=46, color=ORANGE, edgecolor=BROWN, linewidth=0.75, zorder=3)
    coef = np.polyfit(x, y, 1)
    xx = np.linspace(0, x.max() * 1.05, 100)
    ax.plot(xx, np.polyval(coef, xx), color=ROSE, linewidth=1.5, zorder=2)
    center_row = next(r for r in rows if r['region'] == 4)
    ax.annotate('Middle-center', (center_row['mean_attention'], center_row['performance_drop_macro_f1']),
                xytext=(-48, 8), textcoords='offset points', fontsize=7.5, color=UMBER,
                arrowprops=dict(arrowstyle='-', color=UMBER, linewidth=0.65))
    rho = occ['attention_occlusion_spearman']
    ax.text(0.04, 0.94, f'Spearman ρ = {rho["rho"]:.2f}\np = {rho["p_value"]:.3f}; n = 9 regions',
            transform=ax.transAxes, va='top', fontsize=8.0,
            bbox=dict(boxstyle='round,pad=.3', facecolor=PALE, edgecolor=GRID))
    ax.set_xlabel('Mean attention weight')
    ax.set_ylabel('Macro-F1 loss after occlusion')
    clean(ax)

    ax = axs[1, 1]
    panel(ax, 'D', 'Attention stratified by true DR class')
    ax.axis('off')
    csv_path = EXP / 'exp30_deep_region_attention' / 'attention_test.csv'
    values = {0: [], 1: [], 2: []}
    with csv_path.open(encoding='utf-8') as file:
        for row in csv.DictReader(file):
            if row['model'] == 'deep_attention_mask_augmented':
                values[int(row['true_label'])].append([float(row[f'attention_region_{i}']) for i in range(9)])
    class_names = ['Normal', 'NPDR', 'PDR']
    for idx, cls in enumerate([0, 1, 2]):
        iax = inset_axes(ax, width='28%', height='73%', loc='lower left',
                         bbox_to_anchor=(0.035 + idx * 0.323, 0.15, 1, 1),
                         bbox_transform=ax.transAxes, borderpad=0)
        mat = np.mean(np.asarray(values[cls]), axis=0).reshape(3, 3)
        iax.imshow(mat, cmap=att_cmap, vmin=0, vmax=0.42)
        iax.set_xticks([])
        iax.set_yticks([])
        iax.set_title(class_names[idx], fontsize=8.8, color=UMBER, pad=5, fontweight='bold')
        for (i, j), value in np.ndenumerate(mat):
            iax.text(j, i, f'{value:.2f}', ha='center', va='center', fontsize=7.0,
                     color='white' if value > 0.22 else INK)
        for spine in iax.spines.values():
            spine.set_color(BROWN)
            spine.set_linewidth(0.65)
    ax.text(0.5, 0.02, 'Held-out images; displayed only as class-stratified model behavior.',
            transform=ax.transAxes, ha='center', fontsize=7.2, color=UMBER)

    fig.suptitle('Attention is assessed against a controlled intervention, not treated as explanation by itself',
                 fontsize=13.2, fontweight='bold', color=BROWN, y=0.972)
    save(fig, 'Figure5_Attention_Occlusion_RMB20_v2')


def figure6() -> None:
    internal = load('exp36_multiseed_deep_region')['aggregate']
    ext_all = load('exp53_mmrdr_uwf_external_fov')
    external = ext_all['summary']
    boot = load('exp54_mmrdr_paired_bootstrap')['per_seed']
    fig, axs = figure_base()

    views_i = ['full', 'center', 'cross']
    views_e = ['full', 'center', 'center_plus_cross']
    labels = ['Full', 'Center', 'Center + cross']

    ax = axs[0, 0]
    panel(ax, 'A', 'Internal and external UWF performance')
    x = np.arange(3)
    width = 0.32
    int_vals = [internal[v]['macro_f1']['mean'] for v in views_i]
    int_err = [internal[v]['macro_f1']['std'] for v in views_i]
    ext_vals = [external[v]['macro_f1']['mean'] for v in views_e]
    ext_err = [external[v]['macro_f1']['std'] for v in views_e]
    for xpos, vals, errs, color, label in [
        (x - width / 2, int_vals, int_err, ORANGE, 'UWF-DR internal'),
        (x + width / 2, ext_vals, ext_err, OLIVE, 'MMRDR-UWF external'),
    ]:
        bars = ax.bar(xpos, vals, width, color=color, edgecolor=INK, linewidth=0.6, label=label, zorder=3)
        for bar, value, error in zip(bars, vals, errs):
            ax.errorbar(bar.get_x() + bar.get_width() / 2, value, yerr=error, fmt='none', zorder=4, **err_style(color))
    ax.set_xticks(x, labels)
    ax.set_ylabel('Macro-F1')
    ax.set_ylim(0.52, 0.88)
    ax.legend(frameon=False, fontsize=7.8, loc='lower left')
    clean(ax)

    ax = axs[0, 1]
    panel(ax, 'B', 'External error burden by view')
    metrics = ['Severity MAE', 'Underestimation']
    x = np.arange(2)
    width = 0.21
    for j, (view, color, label) in enumerate(zip(views_e, VIEW_COLORS, labels)):
        vals = [external[view]['severity_mae']['mean'], external[view]['underestimation_rate']['mean']]
        errs = [external[view]['severity_mae']['std'], external[view]['underestimation_rate']['std']]
        bars = ax.bar(x + (j - 1) * width, vals, width, color=color, edgecolor=INK, linewidth=0.55,
                      label=label, zorder=3)
        for bar, value, error in zip(bars, vals, errs):
            ax.errorbar(bar.get_x() + bar.get_width() / 2, value, yerr=error, fmt='none', zorder=4, **err_style(color))
    ax.set_xticks(x, metrics)
    ax.set_ylabel('Error metric')
    ax.set_ylim(0, 0.48)
    ax.legend(frameon=False, fontsize=7.4, ncol=3, loc='upper right')
    clean(ax)

    ax = axs[1, 0]
    panel(ax, 'C', 'Paired external Δ macro-F1 versus full view')
    y, estimate, lo, hi, colors, labels_y = [], [], [], [], [], []
    position = 0
    for seed_record in boot:
        for view, label, color in [('center', 'Center', UMBER), ('center_plus_cross', 'Center + cross', OLIVE)]:
            value = seed_record['bootstrap']['paired_delta_vs_full'][view]['macro_f1']
            y.append(position)
            estimate.append(value['estimate'])
            lo.append(value['ci95'][0])
            hi.append(value['ci95'][1])
            colors.append(color)
            labels_y.append(f'Seed {seed_record["seed"]} · {label}')
            position += 1
    xerr = np.array([[e - l for e, l in zip(estimate, lo)], [h - e for e, h in zip(estimate, hi)]])
    refline(ax, 0)
    for yi, est, error, color in zip(y, estimate, xerr.T, colors):
        ax.errorbar(est, yi, xerr=np.asarray(error).reshape(2, 1), fmt='o', markersize=4.5,
                    color=color, ecolor=color, elinewidth=1.15, capsize=2.7, zorder=3)
    ax.set_yticks(y, labels_y, fontsize=7.2)
    ax.invert_yaxis()
    ax.set_xlim(-0.055, 0.055)
    ax.set_xlabel('Paired Δ macro-F1')
    clean(ax, 'x')

    ax = axs[1, 1]
    panel(ax, 'D', 'Exploratory external quality-proxy strata')
    low, high = [], []
    for record in ext_all['records']:
        quartiles = record['views']['full']['quality_proxy_quartiles']
        low.append(quartiles['lowest']['macro_f1'])
        high.append(quartiles['highest']['macro_f1'])
    for i, (left, right) in enumerate(zip(low, high)):
        ax.plot([0, 1], [left, right], color=GRID, linewidth=1.2, zorder=1)
        ax.scatter(0, left, color=UMBER, edgecolor=BROWN, s=32, linewidth=0.55, zorder=3,
                   label='Lowest proxy quartile' if i == 0 else None)
        ax.scatter(1, right, color=OLIVE, edgecolor=BROWN, s=32, linewidth=0.55, zorder=3,
                   label='Highest proxy quartile' if i == 0 else None)
    ax.set_xticks([0, 1], ['Lowest proxy\nquartile', 'Highest proxy\nquartile'])
    ax.set_xlim(-0.22, 1.22)
    ax.set_ylim(0.53, 0.65)
    ax.set_ylabel('Full-view macro-F1')
    ax.legend(frameon=False, fontsize=7.2, loc='lower left')
    ax.text(0.5, 0.04, 'Unlabeled coverage / contrast / sharpness proxy', transform=ax.transAxes,
            ha='center', fontsize=7.0, color=UMBER)
    clean(ax)

    fig.suptitle('Independent same-modality UWF evaluation: topology ordering persists under domain shift',
                 fontsize=13.2, fontweight='bold', color=BROWN, y=0.972)
    save(fig, 'Figure6_External_Replication_RMB20_v2')


def figure7() -> None:
    fixed = load('exp40_final_region_selective_risk')
    nested = load('exp47_nested_risk_calibration')
    fig, axs = figure_base()
    targets = np.array([0.05, 0.10, 0.20])
    fixed_keys = ['0.05', '0.1', '0.2']
    nested_keys = ['target_0.05', 'target_0.10', 'target_0.20']

    ax = axs[0, 0]
    panel(ax, 'A', 'Risk ranking under distinct protocols')
    labels = ['Paired risk\nhead', 'Severity\ngap', 'Symmetric\nKL', 'Nested grouped\nrisk head']
    vals = [
        fixed['risk_head']['test']['auroc'],
        fixed['direct_scores']['severity_gap']['test']['auroc'],
        fixed['direct_scores']['student_teacher_kl']['test']['auroc'],
        nested['aggregate']['risk_auroc']['mean'],
    ]
    errs = [0, 0, 0, nested['aggregate']['risk_auroc']['std']]
    colors = [ROSE, ORANGE, PALE_OLIVE, OLIVE]
    bars = ax.bar(np.arange(4), vals, color=colors, edgecolor=INK, linewidth=0.65, zorder=3)
    for bar, value, error, color in zip(bars, vals, errs, colors):
        if error:
            ax.errorbar(bar.get_x() + bar.get_width() / 2, value, yerr=error, fmt='none', zorder=4, **err_style(color))
        ax.text(bar.get_x() + bar.get_width() / 2, value + error + 0.011, f'{value:.3f}',
                ha='center', va='bottom', fontsize=8)
    ax.axhline(0.5, color=REFERENCE, linestyle=(0, (3, 3)), linewidth=1.0, zorder=1)
    ax.text(3.48, 0.505, 'Chance', ha='right', va='bottom', fontsize=7.0, color=REFERENCE)
    ax.set_xticks(np.arange(4), labels)
    ax.set_ylabel('AUROC')
    ax.set_ylim(0.45, 0.80)
    clean(ax)

    ax = axs[0, 1]
    panel(ax, 'B', 'Exploratory fixed-split coverage')
    coverage = np.array([fixed['selective'][key]['test']['coverage'] for key in fixed_keys])
    ax.plot(targets, coverage, marker='o', color=ROSE, linewidth=1.8, markersize=6.0, zorder=3)
    for x, value in zip(targets, coverage):
        ax.text(x, value + 0.035, f'{value:.3f}', ha='center', va='bottom', fontsize=8.0, color=ROSE)
    ax.set_xticks(targets, ['5%', '10%', '20%'])
    ax.set_xlabel('Nominal underestimation-risk target')
    ax.set_ylabel('Accepted coverage')
    ax.set_ylim(0.20, 1.08)
    ax.text(0.04, 0.07, 'Shared validation predictions were used for risk fitting\nand threshold selection; this panel is exploratory.',
            transform=ax.transAxes, fontsize=7.2, color=UMBER,
            bbox=dict(facecolor=PALE, edgecolor='none', pad=2.2))
    clean(ax)

    ax = axs[1, 0]
    panel(ax, 'C', 'Nested grouped threshold transport')
    nested_risk = np.array([nested['aggregate'][key]['test_accepted_risk']['mean'] for key in nested_keys])
    nested_err = np.array([nested['aggregate'][key]['test_accepted_risk']['std'] for key in nested_keys])
    ax.plot([0, 0.22], [0, 0.22], color=REFERENCE, linestyle=(0, (3, 3)), linewidth=1.0, label='Observed = target')
    ax.errorbar(targets, nested_risk, yerr=nested_err, fmt='s-', color=OLIVE, markersize=5.6,
                linewidth=1.7, label='Nested grouped', zorder=3, **err_style(OLIVE))
    ax.set_xticks(targets, ['5%', '10%', '20%'])
    ax.set_xlabel('Nominal underestimation-risk target')
    ax.set_ylabel('Observed accepted risk')
    ax.set_xlim(0.035, 0.215)
    ax.set_ylim(0, 0.22)
    ax.legend(frameon=False, fontsize=7.5, loc='upper left')
    clean(ax)

    ax = axs[1, 1]
    panel(ax, 'D', 'Nested outer-fold coverage–risk points')
    marker = {'0.05': 'o', '0.10': 's', '0.20': '^'}
    color = {'0.05': ROSE, '0.10': ORANGE, '0.20': OLIVE}
    for fold in nested['folds']:
        for target in ['0.05', '0.10', '0.20']:
            record = fold['selective'][target]
            ax.scatter(record['test_coverage'], record['test_accepted_risk'], marker=marker[target], s=42,
                       color=color[target], edgecolor=BROWN, linewidth=0.55,
                       label=f'Target {target}' if fold['fold'] == 0 else None, zorder=3)
    ax.set_xlabel('Accepted coverage')
    ax.set_ylabel('Observed accepted risk')
    ax.set_xlim(0.30, 1.03)
    ax.set_ylim(0, 0.18)
    ax.legend(frameon=False, fontsize=7.2, ncol=3, loc='upper left')
    clean(ax)

    fig.suptitle('Paired-view underestimation audit: useful ranking, but unstable threshold transport',
                 fontsize=13.2, fontweight='bold', color=BROWN, y=0.972)
    save(fig, 'Figure7_Selective_Risk_RMB20_v2')


def figure8() -> None:
    result = load('exp60_pixel_aperture_training')
    base = result['variants']['baseline']['aggregate']['pixel']
    augmented = result['variants']['pixel_augmented']['aggregate']['pixel']
    scenarios = ['rect_center_0.35', 'rect_center_0.55', 'rect_center_0.75', 'circle_center_0.55']
    labels = ['Rect.\n0.35', 'Rect.\n0.55', 'Rect.\n0.75', 'Circle\n0.55']
    fig, axs = plt.subplots(1, 3, figsize=(12.3, 5.25))
    fig.subplots_adjust(left=0.065, right=0.99, top=0.79, bottom=0.31, wspace=0.38)
    x = np.arange(len(scenarios))
    width = 0.31
    configs = [
        ('A', 'Held-out macro-F1', 'macro_f1', 'Macro-F1', (0.35, 0.88)),
        ('B', 'Held-out ordinal error', 'severity_mae', 'Severity MAE', (0.12, 0.58)),
        ('C', 'Held-out underestimation', 'underestimation_rate', 'Underestimation rate', (0.00, 0.40)),
    ]
    for ax, (letter, title, metric, ylabel, ylim) in zip(axs, configs):
        panel(ax, letter, title)
        base_mean = np.array([base[item][metric]['mean'] for item in scenarios])
        base_sd = np.array([base[item][metric]['std'] for item in scenarios])
        aug_mean = np.array([augmented[item][metric]['mean'] for item in scenarios])
        aug_sd = np.array([augmented[item][metric]['std'] for item in scenarios])
        left = ax.bar(x - width / 2, base_mean, width, color=OLIVE, edgecolor=INK, linewidth=0.58,
                      label='Protocol-matched baseline', zorder=3)
        right = ax.bar(x + width / 2, aug_mean, width, color=ROSE, edgecolor=INK, linewidth=0.58,
                       label='Pixel-aperture training', zorder=3)
        for bar, value, error, color in list(zip(left, base_mean, base_sd, [OLIVE] * len(x))) + list(zip(right, aug_mean, aug_sd, [ROSE] * len(x))):
            ax.errorbar(bar.get_x() + bar.get_width() / 2, value, yerr=error, fmt='none', zorder=4, **err_style(color))
        ax.set_xticks(x, labels)
        ax.set_ylabel(ylabel)
        ax.set_ylim(*ylim)
        for i, delta in enumerate(aug_mean - base_mean):
            sign_color = OLIVE if ((metric != 'underestimation_rate' and delta > 0) or (metric == 'underestimation_rate' and delta < 0)) else ROSE
            ax.text(i, -0.30, f'Δ {delta:+.3f}', transform=ax.get_xaxis_transform(), ha='center', va='top',
                    fontsize=8.0, fontweight='bold', color=sign_color, clip_on=False)
        ax.text(0.5, -0.58, 'Augmented − baseline', transform=ax.transAxes, ha='center', va='top',
                fontsize=7.2, color=UMBER, clip_on=False)
        clean(ax)
    handles, legend_labels = axs[0].get_legend_handles_labels()
    fig.legend(handles, legend_labels, frameon=False, fontsize=8.0, ncol=2,
               loc='upper center', bbox_to_anchor=(0.5, 0.875))
    fig.suptitle('Pixel-aperture training improves F1 and MAE; underestimation changes are aperture-specific',
                 fontsize=13.2, fontweight='bold', color=BROWN, y=0.975)
    save(fig, 'Figure8_Continuous_Aperture_Optimization_RMB20_v2')


def main() -> None:
    figure3()
    figure4()
    figure5()
    figure6()
    figure7()
    figure8()
    print('Created:')
    for file in sorted(OUT.glob('Figure[3-8]*_v2.png')):
        print(file)


if __name__ == '__main__':
    main()
