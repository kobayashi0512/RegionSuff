#!/usr/bin/env python3
"""Exp62: fair comparison of paired-view and single-view risk heads.

Both heads use the same five-seed probability ensemble and the same held-out
event target: the center-plus-cross prediction underestimates the UWF label.
The paired head additionally receives the full-view probabilities; the
single-view head receives only the restricted-view probabilities and derived
uncertainty features.  All thresholds are calibrated on validation only.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import random
import time
from pathlib import Path

import numpy as np
import torch
from scipy.stats import beta
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CACHE = ROOT / "7hao/experiments/exp34_shared_uwf_region_cache"
HERE.mkdir(parents=True, exist_ok=True)
SEEDS = (0, 1, 2, 3, 4)

sp = importlib.util.spec_from_file_location(
    "ab", ROOT / "7hao/experiments/exp35_region_mask_pool_ablation/run_ablation.py"
)
ab = importlib.util.module_from_spec(sp)
assert sp.loader
sp.loader.exec_module(ab)

meta = json.loads((CACHE / "split_meta.json").read_text())
y = {s: np.asarray(meta[s]["y"], dtype=np.int64) for s in ("train", "val", "test")}
z = np.load(CACHE / "region_features_g3.npz")
raw = {s: z[f"{s}_features"].astype(np.float32) for s in y}
mu = raw["train"].reshape(-1, raw["train"].shape[-1]).mean(0)
sd = raw["train"].reshape(-1, raw["train"].shape[-1]).std(0)
sd[sd < 1e-8] = 1
X = {s: ((raw[s] - mu) / sd).astype(np.float32) for s in y}


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def probs(model, dev, split: str, view: str) -> np.ndarray:
    with torch.no_grad():
        mask = torch.from_numpy(ab.eval_mask(view, len(X[split]), 3)).float().to(dev)
        xt = torch.from_numpy(X[split]).float().to(dev)
        return torch.softmax(model(xt, mask)[0], 1).cpu().numpy()


def single_features(p: np.ndarray, visible_fraction: float = 5 / 9) -> np.ndarray:
    ent = -np.sum(np.clip(p, 1e-8, 1) * np.log(np.clip(p, 1e-8, 1)), axis=1)
    top = np.sort(p, axis=1)
    margin = top[:, -1] - top[:, -2]
    expected = p @ np.arange(3.0)
    return np.c_[p, expected, ent, margin, np.full(len(p), visible_fraction)]


def paired_features(pf: np.ndarray, pc: np.ndarray) -> np.ndarray:
    ef = pf @ np.arange(3.0)
    ec = pc @ np.arange(3.0)
    entf = -np.sum(np.clip(pf, 1e-8, 1) * np.log(np.clip(pf, 1e-8, 1)), axis=1)
    entc = -np.sum(np.clip(pc, 1e-8, 1) * np.log(np.clip(pc, 1e-8, 1)), axis=1)
    kl = 0.5 * np.sum(
        pf * np.log(np.clip(pf, 1e-8, 1) / np.clip(pc, 1e-8, 1))
        + pc * np.log(np.clip(pc, 1e-8, 1) / np.clip(pf, 1e-8, 1)),
        axis=1,
    )
    return np.c_[
        pf,
        pc,
        pf - pc,
        np.abs(pf - pc),
        ef,
        ec,
        ef - ec,
        entf,
        entc,
        kl,
    ]


def metric(yy: np.ndarray, score: np.ndarray) -> dict:
    return {
        "auroc": float(roc_auc_score(yy, score)),
        "average_precision": float(average_precision_score(yy, score)),
        "brier": float(brier_score_loss(yy, np.clip(score, 0, 1))),
        "positive_rate": float(yy.mean()),
    }


def cp_upper(k: int, n: int) -> float:
    if n == 0 or k == n:
        return 1.0
    return float(beta.ppf(0.95, k + 1, n - k))


def calibrate(score: np.ndarray, yy: np.ndarray, target: float) -> dict:
    options = []
    for t in np.unique(score):
        accepted = score <= t
        n = int(accepted.sum())
        k = int(yy[accepted].sum())
        if n and cp_upper(k, n) <= target:
            options.append((n, float(t), k, cp_upper(k, n)))
    if not options:
        i = int(np.argmin(score))
        return {
            "threshold": float(score[i]),
            "validation_coverage": 1 / len(yy),
            "validation_cp_upper": cp_upper(int(yy[i]), 1),
            "feasible": False,
        }
    n, t, k, upper = max(options, key=lambda q: q[0])
    return {
        "threshold": t,
        "validation_coverage": n / len(yy),
        "validation_risk": k / n,
        "validation_cp_upper": upper,
        "feasible": True,
    }


def bootstrap_delta(ytest: np.ndarray, single: np.ndarray, paired: np.ndarray, n_boot: int = 5000) -> dict:
    rng = np.random.default_rng(6200)
    n = len(ytest)
    deltas = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        if len(np.unique(ytest[idx])) < 2:
            continue
        deltas.append(
            roc_auc_score(ytest[idx], single[idx]) - roc_auc_score(ytest[idx], paired[idx])
        )
    arr = np.asarray(deltas)
    point = roc_auc_score(ytest, single) - roc_auc_score(ytest, paired)
    return {
        "single_minus_paired_auroc": float(point),
        "bootstrap_replicates": int(len(arr)),
        "95ci": [float(np.percentile(arr, 2.5)), float(np.percentile(arr, 97.5))],
        "probability_single_better": float(np.mean(arr > 0)),
    }


def selective(score_v, yv, score_t, yt):
    out = {}
    for target in (0.05, 0.10, 0.20):
        c = calibrate(score_v, yv, target)
        accepted = score_t <= c["threshold"]
        out[str(target)] = {
            "calibration": c,
            "test_coverage": float(accepted.mean()),
            "test_accepted_n": int(accepted.sum()),
            "test_accepted_risk": float(yt[accepted].mean()) if accepted.any() else None,
        }
    return out


def main() -> None:
    t0 = time.time()
    heads = {}
    for seed in SEEDS:
        set_seed(seed)
        heads[seed] = ab.train(X["train"], y["train"], X["val"], y["val"], "attention", 0.30, seed)

    view_prob = {}
    for split in ("val", "test"):
        view_prob[split] = {
            view: np.mean([probs(heads[s][0], heads[s][1], split, view) for s in SEEDS], axis=0)
            for view in ("full", "cross")
        }
    pfv, pcv = view_prob["val"]["full"], view_prob["val"]["cross"]
    pft, pct = view_prob["test"]["full"], view_prob["test"]["cross"]
    yv = (pcv.argmax(1) < y["val"]).astype(np.int64)
    yt = (pct.argmax(1) < y["test"]).astype(np.int64)

    feature_sets = {
        "paired_full_plus_cross": (paired_features(pfv, pcv), paired_features(pft, pct)),
        "single_cross_only": (single_features(pcv), single_features(pct)),
    }
    fitted = {}
    for name, (fv, ft) in feature_sets.items():
        m = fv.mean(0)
        s = fv.std(0)
        s[s < 1e-8] = 1
        clf = LogisticRegression(C=0.1, class_weight="balanced", solver="liblinear", max_iter=1000, random_state=0)
        clf.fit((fv - m) / s, yv)
        sv = clf.predict_proba((fv - m) / s)[:, 1]
        st = clf.predict_proba((ft - m) / s)[:, 1]
        fitted[name] = {
            "test": metric(yt, st),
            "validation": metric(yv, sv),
            "selective": selective(sv, yv, st, yt),
            "validation_score": sv,
            "test_score": st,
        }

    single = fitted["single_cross_only"]["test_score"]
    paired = fitted["paired_full_plus_cross"]["test_score"]
    result = {
        "experiment": "Exp62 fair single-view versus paired-view risk head",
        "protocol": "five-seed probability ensemble; same validation/test event target; test labels used only for final evaluation; one-sided Clopper-Pearson calibration on validation",
        "event_definition": "center-plus-cross predicted severity is lower than the UWF clinical severity label",
        "models": {
            name: {k: v for k, v in values.items() if k not in ("validation_score", "test_score")}
            for name, values in fitted.items()
        },
        "paired_bootstrap": bootstrap_delta(yt, single, paired),
        "notes": [
            "The paired-view head receives full-view and center-plus-cross probabilities.",
            "The single-view head receives only center-plus-cross probabilities and derived uncertainty features.",
            "Center-plus-cross is a geometric proxy and not a real same-eye paired acquisition.",
        ],
        "elapsed_seconds": time.time() - t0,
    }
    np.savez_compressed(HERE / "risk_scores.npz", y_test=yt, paired=paired, single=single)
    (HERE / "results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    (HERE / "REPORT.md").write_text(
        "# Exp62：单视图与配对视图风险头的同测试集比较\n\n"
        "本实验固定同一五种子集成、同一低估事件标签和同一测试集，比较部署时需要完整视图的配对风险头与只使用受限视图输出的单视图风险头。\n\n"
        "```json\n" + json.dumps(result, ensure_ascii=False, indent=2) + "\n```\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
