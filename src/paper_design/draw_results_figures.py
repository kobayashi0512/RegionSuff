#!/usr/bin/env python3
"""Create exact manuscript figures from the locked experiment registry.

All plotted numbers are read from experiment results.json/CSV files.  The
palette is derived from the Chinese RMB 20 note used by the project artwork.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.axes_grid1.inset_locator import inset_axes


ROOT = Path("/Users/tongyue/Documents/77f /7hao")
EXP = ROOT / "experiments"
OUT = ROOT / "paper_design/figures"
OUT.mkdir(parents=True, exist_ok=True)

# RMB 20 publication palette: warm paper, seal brown, orange, olive and rose.
INK = "#3F3027"
BROWN = "#704C2B"
UMBER = "#965E4A"
ORANGE = "#E49F5D"
OLIVE = "#8B9A7C"
ROSE = "#C74282"
PALE = "#F7ECE6"
PALE_OLIVE = "#E5E8D9"
PAPER = "#FFFDFC"
GRID = "#D9C9BA"
VIEW_COLORS = [BROWN, ORANGE, OLIVE]

mpl.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 8.5,
        "axes.titlesize": 9.5,
        "axes.titleweight": "bold",
        "axes.labelsize": 8.5,
        "axes.edgecolor": INK,
        "axes.labelcolor": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "text.color": INK,
        "figure.facecolor": PAPER,
        "axes.facecolor": PAPER,
        "axes.grid": False,
        "savefig.facecolor": PAPER,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.04,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
    }
)


def load(name: str) -> dict:
    return json.loads((EXP / name / "results.json").read_text(encoding="utf-8"))


def panel(ax, letter: str, title: str):
    ax.text(-0.12, 1.08, letter, transform=ax.transAxes, fontsize=12, fontweight="bold", color=BROWN, va="top")
    ax.set_title(title, loc="left", pad=8)


def clean(ax, grid_axis: str | None = "y"):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if grid_axis:
        ax.grid(axis=grid_axis, color=GRID, linewidth=0.6, alpha=0.55, zorder=0)
    ax.set_axisbelow(True)


def save(fig, stem: str):
    for ext in ("png", "pdf", "svg"):
        dpi = 420 if ext == "png" else None
        fig.savefig(OUT / f"{stem}.{ext}", dpi=dpi)
    plt.close(fig)


def mean_sd(item: dict, metric: str):
    return item[metric]["mean"], item[metric]["std"]


def figure3():
    fov = load("exp48b_pixel_fov_geometry")["aggregate"]
    multi = load("exp36_multiseed_deep_region")
    fig, axs = plt.subplots(2, 2, figsize=(10.7, 7.2), constrained_layout=True)

    # A: visible-fraction sensitivity.
    ax = axs[0, 0]
    panel(ax, "A", "Continuous visible fraction")
    fractions = [0.35, 0.45, 0.55, 0.65, 0.75, 0.90]
    for shape, color, marker in [("rect", BROWN, "o"), ("circle", ROSE, "s")]:
        means = [fov[f"{shape}_center_{v:.2f}"]["macro_f1"]["mean"] for v in fractions]
        sds = [fov[f"{shape}_center_{v:.2f}"]["macro_f1"]["std"] for v in fractions]
        ax.errorbar(fractions, means, yerr=sds, marker=marker, color=color, lw=1.8, ms=5, capsize=2.5,
                    label="Rectangle" if shape == "rect" else "Circle")
    ax.set_xlabel("Visible linear fraction")
    ax.set_ylabel("Macro-F1")
    ax.set_ylim(0.42, 0.87)
    ax.legend(frameon=False, ncol=2, loc="lower right")
    clean(ax)

    # B: matched size, translated windows.
    ax = axs[0, 1]
    panel(ax, "B", "Same size, different retinal location")
    locs = ["center", "left", "right", "up", "down"]
    labels = ["Center", "Left", "Right", "Superior", "Inferior"]
    vals = [fov[f"rect_{x}_0.55"]["macro_f1"]["mean"] for x in locs]
    errs = [fov[f"rect_{x}_0.55"]["macro_f1"]["std"] for x in locs]
    bars = ax.bar(np.arange(5), vals, yerr=errs, capsize=2.5, color=[ORANGE, OLIVE, OLIVE, UMBER, UMBER],
                  edgecolor=BROWN, linewidth=0.7, zorder=3)
    ax.set_xticks(np.arange(5), labels, rotation=18, ha="right")
    ax.set_ylabel("Macro-F1")
    ax.set_ylim(0.52, 0.80)
    for b, v in zip(bars, vals):
        ax.text(b.get_x()+b.get_width()/2, v+0.006, f"{v:.3f}", ha="center", va="bottom", fontsize=7)
    clean(ax)

    # C: matched linear fraction, shape changes both topology and pixel area.
    ax = axs[1, 0]
    panel(ax, "C", "Window shape at fraction 0.55")
    metrics = ["macro_f1", "underestimation_rate"]
    metric_labels = ["Macro-F1", "Underestimation"]
    x = np.arange(2)
    width = 0.34
    for j, (shape, color) in enumerate([("rect", BROWN), ("circle", ORANGE)]):
        vals = [fov[f"{shape}_center_0.55"][m]["mean"] for m in metrics]
        errs = [fov[f"{shape}_center_0.55"][m]["std"] for m in metrics]
        ax.bar(x+(j-0.5)*width, vals, width, yerr=errs, capsize=2.5, color=color, edgecolor=BROWN,
               linewidth=0.7, label=shape.capitalize(), zorder=3)
    ax.set_xticks(x, metric_labels)
    ax.set_ylim(0, 0.86)
    ax.set_ylabel("Metric value")
    ax.legend(frameon=False, ncol=2, loc="upper right")
    ax.text(0.02, 0.04, "Same linear fraction ≠ same topology\nor visible pixel area", transform=ax.transAxes,
            fontsize=7.5, color=UMBER)
    clean(ax)

    # D: exact five-seed region-mask results.
    ax = axs[1, 1]
    panel(ax, "D", "Regional evidence topology (internal test)")
    views = ["full", "center", "cross"]
    labels = ["Full", "Center", "Center + cross"]
    rows = multi["rows"]
    for seed in range(5):
        ys = [next(r["macro_f1"] for r in rows if r["seed"] == seed and r["view"] == v) for v in views]
        ax.plot(np.arange(3), ys, color=GRID, lw=1, alpha=0.9, zorder=1)
        ax.scatter(np.arange(3), ys, s=22, facecolor=PAPER, edgecolor=BROWN, linewidth=0.8, zorder=3)
    means = [multi["aggregate"][v]["macro_f1"]["mean"] for v in views]
    sds = [multi["aggregate"][v]["macro_f1"]["std"] for v in views]
    ax.errorbar(np.arange(3), means, yerr=sds, fmt="D", ms=6, lw=0, ecolor=INK, capsize=3,
                markerfacecolor=ORANGE, markeredgecolor=BROWN, zorder=4, label="Mean ± SD")
    ax.set_xticks(np.arange(3), labels)
    ax.set_ylabel("Macro-F1")
    ax.set_ylim(0.74, 0.87)
    ax.legend(frameon=False, loc="lower left")
    clean(ax)

    fig.suptitle("Controlled visibility tests: area alone does not determine diagnostic sufficiency",
                 fontsize=12.5, fontweight="bold", color=BROWN)
    save(fig, "Figure3_Controlled_Visibility_RMB20")


def figure4():
    abl = load("exp35_region_mask_pool_ablation")
    enc = load("exp37_encoder_ablation")["representations"]
    pair = load("exp45_grid_paired_bootstrap")["rows"]
    fig, axs = plt.subplots(2, 2, figsize=(10.7, 7.2), constrained_layout=True)

    ax = axs[0, 0]
    panel(ax, "A", "Regional encoder control")
    order = ["retinaradar_region", "imagenet_resnet50_region", "handcrafted_region", "random_resnet50_region"]
    labels = ["RetinaRadar\n(frozen)", "ImageNet\nResNet-50", "Handcrafted", "Random\nResNet-50"]
    vals = [enc[k]["cross"]["macro_f1"] for k in order]
    bars = ax.bar(np.arange(4), vals, color=[ROSE, ORANGE, OLIVE, PALE], edgecolor=BROWN, linewidth=0.8, zorder=3)
    ax.set_xticks(np.arange(4), labels)
    ax.set_ylim(0, 0.92)
    ax.set_ylabel("Center + cross macro-F1")
    for b, v in zip(bars, vals): ax.text(b.get_x()+b.get_width()/2, v+0.018, f"{v:.3f}", ha="center", fontsize=7.5)
    clean(ax)

    ax = axs[0, 1]
    panel(ax, "B", "Aggregation operator")
    pools = ["mean", "max", "attention"]
    p_labels = ["Mean", "Max", "Attention"]
    x = np.arange(3); w = 0.23
    for j, (view, color, label) in enumerate(zip(["full", "center", "cross"], VIEW_COLORS, ["Full", "Center", "Center + cross"])):
        vals = [abl["pooling"][p][view]["macro_f1"] for p in pools]
        ax.bar(x+(j-1)*w, vals, w, color=color, edgecolor=BROWN, linewidth=0.6, label=label, zorder=3)
    ax.set_xticks(x, p_labels)
    ax.set_ylim(0.70, 0.88)
    ax.set_ylabel("Macro-F1")
    ax.legend(frameon=False, ncol=3, fontsize=7, loc="lower right")
    clean(ax)

    ax = axs[1, 0]
    panel(ax, "C", "Training mask-ratio sensitivity")
    ratios = [0, 0.15, 0.30, 0.45, 0.60]
    for view, color, marker, label in zip(["full", "center", "cross"], VIEW_COLORS, ["o", "s", "^"], ["Full", "Center", "Center + cross"]):
        vals = [abl["mask_ratio"][str(r) if r else "0"][view]["macro_f1"] for r in ratios]
        ax.plot(ratios, vals, marker=marker, color=color, lw=1.6, ms=5, label=label)
    ax.axvline(0.30, color=ROSE, linestyle="--", lw=1.2)
    ax.text(0.305, 0.804, "prespecified final", rotation=90, va="bottom", color=ROSE, fontsize=7)
    ax.set_xlabel("Random region mask ratio")
    ax.set_ylabel("Macro-F1")
    ax.set_ylim(0.77, 0.88)
    ax.legend(frameon=False, ncol=3, fontsize=7, loc="lower right")
    clean(ax)

    ax = axs[1, 1]
    panel(ax, "D", "Does 4×4 consistently beat 3×3?")
    rows = [r for r in pair if r["view"] == "cross"]
    y = np.arange(5)
    est = [r["delta_4x4_minus_3x3"]["macro_f1"]["mean"] for r in rows]
    lo = [r["delta_4x4_minus_3x3"]["macro_f1"]["ci95"][0] for r in rows]
    hi = [r["delta_4x4_minus_3x3"]["macro_f1"]["ci95"][1] for r in rows]
    xerr = np.array([[e-l for e,l in zip(est,lo)], [h-e for e,h in zip(est,hi)]])
    ax.errorbar(est, y, xerr=xerr, fmt="o", ms=5, color=BROWN, ecolor=ORANGE, capsize=2.5, lw=1.3)
    ax.axvline(0, color=INK, lw=0.9)
    ax.set_yticks(y, [f"Seed {r['seed']}" for r in rows])
    ax.set_xlabel("Paired Δ macro-F1 (4×4 − 3×3)")
    ax.set_xlim(-0.075, 0.09)
    ax.text(0.02, 0.03, "Every 95% CI crosses zero", transform=ax.transAxes, color=UMBER, fontsize=7.5)
    clean(ax, "x")

    fig.suptitle("Ablations and controls for the regional evidence model", fontsize=12.5, fontweight="bold", color=BROWN)
    save(fig, "Figure4_Ablations_RMB20")


def figure5():
    occ = load("exp39_attention_occlusion_validation")
    rows = occ["rows"]
    att = np.array([r["mean_attention"] for r in rows]).reshape(3, 3)
    drop = np.array([r["performance_drop_macro_f1"] for r in rows]).reshape(3, 3)
    cmap = LinearSegmentedColormap.from_list("rmb20", [PALE, ORANGE, ROSE, BROWN])
    fig, axs = plt.subplots(2, 2, figsize=(10.7, 7.2), constrained_layout=True)

    ax = axs[0, 0]
    panel(ax, "A", "Mean learned attention")
    im = ax.imshow(att, cmap=cmap, vmin=0, vmax=max(0.42, att.max()))
    for (i, j), v in np.ndenumerate(att): ax.text(j, i, f"{v:.3f}", ha="center", va="center", fontsize=8, color="white" if v > 0.22 else INK)
    ax.set_xticks([0,1,2], ["Left", "Center", "Right"]); ax.set_yticks([0,1,2], ["Superior", "Middle", "Inferior"])
    fig.colorbar(im, ax=ax, fraction=0.045, pad=0.02, label="Attention weight")

    ax = axs[0, 1]
    panel(ax, "B", "Causal one-region occlusion")
    vmax = max(abs(drop.min()), abs(drop.max()))
    im = ax.imshow(drop, cmap=LinearSegmentedColormap.from_list("drop", [OLIVE, PAPER, ROSE]), vmin=-vmax, vmax=vmax)
    for (i, j), v in np.ndenumerate(drop): ax.text(j, i, f"{v:+.3f}", ha="center", va="center", fontsize=8, color=INK)
    ax.set_xticks([0,1,2], ["Left", "Center", "Right"]); ax.set_yticks([0,1,2], ["Superior", "Middle", "Inferior"])
    fig.colorbar(im, ax=ax, fraction=0.045, pad=0.02, label="Macro-F1 drop")

    ax = axs[1, 0]
    panel(ax, "C", "Attention versus performance loss")
    x = np.array([r["mean_attention"] for r in rows]); y = np.array([r["performance_drop_macro_f1"] for r in rows])
    ax.scatter(x, y, s=45, color=ORANGE, edgecolor=BROWN, linewidth=0.8, zorder=3)
    coef = np.polyfit(x, y, 1); xx = np.linspace(0, x.max()*1.04, 100)
    ax.plot(xx, np.polyval(coef, xx), color=ROSE, lw=1.5)
    for r in rows:
        if r["region"] in (3,4,5): ax.annotate(f"R{r['region']+1}", (r["mean_attention"], r["performance_drop_macro_f1"]), xytext=(4,4), textcoords="offset points", fontsize=7)
    rho = occ["attention_occlusion_spearman"]
    ax.text(0.04, 0.92, f"Spearman ρ = {rho['rho']:.2f}\np = {rho['p_value']:.3f}", transform=ax.transAxes, va="top", fontsize=8,
            bbox=dict(boxstyle="round,pad=.25", facecolor=PALE, edgecolor=GRID))
    ax.set_xlabel("Mean attention weight")
    ax.set_ylabel("Macro-F1 drop after occlusion")
    clean(ax)

    # D: class-stratified attention, derived from saved held-out predictions.
    ax = axs[1, 1]
    panel(ax, "D", "Attention by true DR class")
    ax.axis("off")
    csv_path = EXP / "exp30_deep_region_attention" / "attention_test.csv"
    values = {0: [], 1: [], 2: []}
    with csv_path.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["model"] != "deep_attention_mask_augmented":
                continue
            values[int(r["true_label"])].append([float(r[f"attention_region_{i}"]) for i in range(9)])
    class_names = ["Normal", "NPDR", "PDR"]
    for idx, cls in enumerate([0,1,2]):
        iax = inset_axes(ax, width="29%", height="66%", loc="lower left",
                        bbox_to_anchor=(0.02+idx*0.33, 0.10, 1, 1), bbox_transform=ax.transAxes, borderpad=0)
        mat = np.mean(np.asarray(values[cls]), axis=0).reshape(3,3)
        iax.imshow(mat, cmap=cmap, vmin=0, vmax=0.42)
        iax.set_xticks([]); iax.set_yticks([])
        iax.set_title(class_names[idx], fontsize=8.5, color=UMBER, pad=3)
        for (i,j), v in np.ndenumerate(mat): iax.text(j,i,f"{v:.2f}",ha="center",va="center",fontsize=6.5,color="white" if v>0.22 else INK)
        for sp in iax.spines.values(): sp.set_color(BROWN); sp.set_linewidth(0.7)
    ax.text(0.02, 0.02, "Held-out images; class labels used only for stratified visualization", transform=ax.transAxes, fontsize=7, color=UMBER)

    fig.suptitle("Attention is tested against intervention, not treated as explanation by itself", fontsize=12.5, fontweight="bold", color=BROWN)
    save(fig, "Figure5_Attention_Occlusion_RMB20")


def figure6():
    internal = load("exp36_multiseed_deep_region")["aggregate"]
    ext_all = load("exp53_mmrdr_uwf_external_fov")
    external = ext_all["summary"]
    boot = load("exp54_mmrdr_paired_bootstrap")["per_seed"]
    fig, axs = plt.subplots(2, 2, figsize=(10.7, 7.2), constrained_layout=True)

    ax = axs[0, 0]
    panel(ax, "A", "Internal and external UWF performance")
    views_i = ["full", "center", "cross"]
    views_e = ["full", "center", "center_plus_cross"]
    labels = ["Full", "Center", "Center + cross"]
    x = np.arange(3); w=.34
    vals_i=[internal[v]["macro_f1"]["mean"] for v in views_i]; err_i=[internal[v]["macro_f1"]["std"] for v in views_i]
    vals_e=[external[v]["macro_f1"]["mean"] for v in views_e]; err_e=[external[v]["macro_f1"]["std"] for v in views_e]
    ax.bar(x-w/2, vals_i, w, yerr=err_i, capsize=2.5, color=ORANGE, edgecolor=BROWN, linewidth=.7, label="UWF-DR internal", zorder=3)
    ax.bar(x+w/2, vals_e, w, yerr=err_e, capsize=2.5, color=OLIVE, edgecolor=BROWN, linewidth=.7, label="MMRDR-UWF external", zorder=3)
    ax.set_xticks(x,labels); ax.set_ylim(.52,.88); ax.set_ylabel("Macro-F1")
    ax.legend(frameon=False, fontsize=7.5, loc="lower left")
    clean(ax)

    ax = axs[0, 1]
    panel(ax, "B", "External error burden by view")
    x=np.arange(2); w=.23
    for j,(v,c,l) in enumerate(zip(views_e,VIEW_COLORS,labels)):
        vals=[external[v]["severity_mae"]["mean"], external[v]["underestimation_rate"]["mean"]]
        errs=[external[v]["severity_mae"]["std"], external[v]["underestimation_rate"]["std"]]
        ax.bar(x+(j-1)*w,vals,w,yerr=errs,capsize=2.5,color=c,edgecolor=BROWN,linewidth=.6,label=l,zorder=3)
    ax.set_xticks(x,["Severity MAE","Underestimation"]); ax.set_ylim(0,.48); ax.set_ylabel("Error metric")
    ax.legend(frameon=False,ncol=3,fontsize=7,loc="upper right")
    clean(ax)

    ax = axs[1, 0]
    panel(ax, "C", "Paired external Δ macro-F1 versus full view")
    y=[]; est=[]; lo=[]; hi=[]; colors=[]; labels_y=[]
    pos=0
    for seedrec in boot:
        for view,label,color in [("center","Center",UMBER),("center_plus_cross","Center + cross",OLIVE)]:
            d=seedrec["bootstrap"]["paired_delta_vs_full"][view]["macro_f1"]
            y.append(pos); est.append(d["estimate"]); lo.append(d["ci95"][0]); hi.append(d["ci95"][1]); colors.append(color)
            labels_y.append(f"S{seedrec['seed']} · {label}"); pos+=1
    xerr=np.array([[e-l for e,l in zip(est,lo)],[h-e for e,h in zip(est,hi)]])
    for yi,e,xe,c in zip(y,est,xerr.T,colors): ax.errorbar(e,yi,xerr=np.asarray(xe).reshape(2,1),fmt="o",ms=4,color=c,ecolor=c,capsize=2,lw=1)
    ax.axvline(0,color=INK,lw=.9); ax.set_yticks(y,labels_y,fontsize=6.5); ax.invert_yaxis(); ax.set_xlim(-.055,.055)
    ax.set_xlabel("Paired Δ macro-F1"); clean(ax,"x")

    ax = axs[1, 1]
    panel(ax, "D", "Exploratory external quality-proxy strata")
    lows=[]; highs=[]
    for s in ext_all["records"]:
        q=s["views"]["full"]["quality_proxy_quartiles"]
        lows.append(q["lowest"]["macro_f1"]); highs.append(q["highest"]["macro_f1"])
    for i,(a,b) in enumerate(zip(lows,highs)):
        ax.plot([0,1],[a,b],color=GRID,lw=1.2); ax.scatter([0,1],[a,b],color=[UMBER,OLIVE],edgecolor=BROWN,s=28,zorder=3)
        ax.text(1.04,b,f"S{i}",fontsize=6.5,va="center")
    ax.set_xticks([0,1],["Lowest proxy quartile","Highest proxy quartile"]); ax.set_xlim(-.2,1.25); ax.set_ylim(.53,.65)
    ax.set_ylabel("Full-view macro-F1")
    ax.text(.02,.03,"Unlabeled coverage/contrast/sharpness proxy",transform=ax.transAxes,fontsize=7,color=UMBER)
    clean(ax)

    fig.suptitle("Independent same-modality UWF replication without target-label training", fontsize=12.5, fontweight="bold", color=BROWN)
    save(fig, "Figure6_External_Replication_RMB20")


def figure7():
    fixed=load("exp40_final_region_selective_risk")
    nested=load("exp47_nested_risk_calibration")
    fig,axs=plt.subplots(2,2,figsize=(10.7,7.2),constrained_layout=True)

    ax=axs[0,0]; panel(ax,"A","Underestimation-risk discrimination")
    labels=["Paired risk\nhead","Severity gap","Symmetric KL","Nested grouped\nrisk head"]
    vals=[fixed["risk_head"]["test"]["auroc"],fixed["direct_scores"]["severity_gap"]["test"]["auroc"],fixed["direct_scores"]["student_teacher_kl"]["test"]["auroc"],nested["aggregate"]["risk_auroc"]["mean"]]
    errs=[0,0,0,nested["aggregate"]["risk_auroc"]["std"]]
    bars=ax.bar(np.arange(4),vals,yerr=errs,capsize=3,color=[ROSE,ORANGE,PALE_OLIVE,OLIVE],edgecolor=BROWN,linewidth=.7,zorder=3)
    ax.axhline(.5,color=GRID,lw=1,linestyle="--"); ax.set_xticks(np.arange(4),labels); ax.set_ylim(.45,.80); ax.set_ylabel("AUROC")
    for b,v in zip(bars,vals): ax.text(b.get_x()+b.get_width()/2,v+.012,f"{v:.3f}",ha="center",fontsize=7)
    clean(ax)

    targets=np.array([.05,.10,.20]); fixed_keys=["0.05","0.1","0.2"]; nested_keys=["target_0.05","target_0.10","target_0.20"]
    ax=axs[0,1]; panel(ax,"B","Coverage retained under a risk constraint")
    fv=np.array([fixed["selective"][k]["test"]["coverage"] for k in fixed_keys])
    nv=np.array([nested["aggregate"][k]["test_coverage"]["mean"] for k in nested_keys]); ne=np.array([nested["aggregate"][k]["test_coverage"]["std"] for k in nested_keys])
    ax.plot(targets,fv,"o-",color=ROSE,lw=1.7,label="Fixed held-out")
    ax.errorbar(targets,nv,yerr=ne,fmt="s-",color=OLIVE,lw=1.7,capsize=3,label="Nested grouped")
    ax.set_xticks(targets,["5%","10%","20%"]); ax.set_xlabel("Target underestimation risk"); ax.set_ylabel("Accepted coverage")
    ax.set_ylim(.20,1.08); ax.legend(frameon=False); clean(ax)

    ax=axs[1,0]; panel(ax,"C","Observed risk among accepted cases")
    fr=np.array([fixed["selective"][k]["test"]["accepted_risk"] for k in fixed_keys])
    nr=np.array([nested["aggregate"][k]["test_accepted_risk"]["mean"] for k in nested_keys]); nre=np.array([nested["aggregate"][k]["test_accepted_risk"]["std"] for k in nested_keys])
    ax.plot([0,.22],[0,.22],color=GRID,lw=1,linestyle="--",label="Observed = target")
    ax.plot(targets,fr,"o-",color=ROSE,lw=1.7,label="Fixed held-out")
    ax.errorbar(targets,nr,yerr=nre,fmt="s-",color=OLIVE,lw=1.7,capsize=3,label="Nested grouped")
    ax.set_xticks(targets,["5%","10%","20%"]); ax.set_xlabel("Target underestimation risk"); ax.set_ylabel("Accepted underestimation risk")
    ax.set_xlim(.035,.215); ax.set_ylim(0,.22); ax.legend(frameon=False,fontsize=7.5); clean(ax)

    ax=axs[1,1]; panel(ax,"D","Nested threshold transport across patient groups")
    markers={"0.05":"o","0.10":"s","0.20":"^"}; colors={"0.05":ROSE,"0.10":ORANGE,"0.20":OLIVE}
    for fold in nested["folds"]:
        for k in ["0.05","0.10","0.20"]:
            s=fold["selective"][k]
            ax.scatter(s["test_coverage"],s["test_accepted_risk"],marker=markers[k],s=38,color=colors[k],edgecolor=BROWN,linewidth=.5,
                       label=f"Target {k}" if fold["fold"]==0 else None)
    ax.set_xlabel("Accepted coverage"); ax.set_ylabel("Accepted underestimation risk"); ax.set_xlim(.3,1.03); ax.set_ylim(0,.18)
    ax.legend(frameon=False,ncol=3,fontsize=7,loc="upper left"); clean(ax)

    fig.suptitle("Selective prediction reveals both promise and threshold-transport uncertainty", fontsize=12.5,fontweight="bold",color=BROWN)
    save(fig,"Figure7_Selective_Risk_RMB20")


if __name__ == "__main__":
    figure3()
    figure4()
    figure5()
    figure6()
    figure7()
    print("Created:")
    for p in sorted(OUT.glob("Figure[3-7]_*.png")):
        print(p)
