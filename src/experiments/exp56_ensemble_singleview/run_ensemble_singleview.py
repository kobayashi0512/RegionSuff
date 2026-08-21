#!/usr/bin/env python3
"""Exp56-57: seed ensembles and single-view limited-evidence risk heads.

The ensemble is evaluated on the same held-out images.  The risk task is
single-view by construction: the candidate score only receives the limited
view's probability vector, entropy, margin, and visible-token count.  It does
not use the full-view teacher at inference time.
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
from sklearn.metrics import average_precision_score, brier_score_loss, f1_score, roc_auc_score


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CACHE = ROOT / "7hao/experiments/exp34_shared_uwf_region_cache"
HERE.mkdir(parents=True, exist_ok=True)
DEVICE = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
SEEDS = (0, 1, 2, 3, 4)

sp = importlib.util.spec_from_file_location("ab", ROOT / "7hao/experiments/exp35_region_mask_pool_ablation/run_ablation.py")
ab = importlib.util.module_from_spec(sp); assert sp.loader; sp.loader.exec_module(ab)

meta = json.loads((CACHE / "split_meta.json").read_text())
y = {s: np.asarray(meta[s]["y"], dtype=np.int64) for s in ("train", "val", "test")}
z = np.load(CACHE / "region_features_g3.npz")
raw = {s: z[f"{s}_features"].astype(np.float32) for s in y}
mu = raw["train"].reshape(-1, raw["train"].shape[-1]).mean(0)
sd = raw["train"].reshape(-1, raw["train"].shape[-1]).std(0); sd[sd < 1e-8] = 1
X = {s: ((raw[s] - mu) / sd).astype(np.float32) for s in y}


def set_seed(seed):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)


def fit_heads():
    heads = {}
    for seed in SEEDS:
        model, dev, val_score, epochs = ab.train(X["train"], y["train"], X["val"], y["val"], "attention", .30, seed)
        heads[seed] = (model, dev, float(val_score), int(epochs))
    return heads


def probs(head, view, split):
    model, dev, _, _ = head
    with torch.no_grad():
        mask = torch.from_numpy(ab.eval_mask(view, len(X[split]), 3)).float().to(dev)
        p = torch.softmax(model(torch.from_numpy(X[split]).float().to(dev), mask)[0], 1).cpu().numpy()
    return p


def score_metrics(yy, p):
    pred = p.argmax(1)
    return {
        "accuracy": float(np.mean(pred == yy)),
        "macro_f1": float(f1_score(yy, pred, average="macro", zero_division=0)),
        "severity_mae": float(np.mean(np.abs(pred - yy))),
        "underestimation_rate": float(np.mean(pred < yy)),
    }


def risk_features(p, visible_count):
    entropy = -np.sum(np.clip(p, 1e-8, 1) * np.log(np.clip(p, 1e-8, 1)), axis=1)
    top = np.sort(p, axis=1)
    margin = top[:, -1] - top[:, -2]
    expected = p @ np.arange(3.0)
    return np.c_[p, expected, entropy, margin, np.full(len(p), visible_count / 9.0)]


def cp_upper(k, n):
    if n == 0 or k == n: return 1.0
    return float(beta.ppf(.95, k + 1, n - k))


def calibrate(scores, yy, target):
    options = []
    for t in np.unique(scores):
        accepted = scores <= t; n = int(accepted.sum()); k = int(yy[accepted].sum())
        if n and cp_upper(k, n) <= target: options.append((n, float(t), k, cp_upper(k, n)))
    if not options:
        i = int(np.argmin(scores)); return {"threshold": float(scores[i]), "validation_coverage": 1 / len(yy), "validation_cp_upper": cp_upper(int(yy[i]), 1), "feasible": False}
    n, t, k, u = max(options, key=lambda q: q[0])
    return {"threshold": t, "validation_coverage": n / len(yy), "validation_risk": k / n, "validation_cp_upper": u, "feasible": True}


def main():
    t0 = time.time()
    heads = fit_heads()
    per_seed = []
    for seed in SEEDS:
        full = probs(heads[seed], "full", "test")
        cross = probs(heads[seed], "cross", "test")
        per_seed.append({"seed": seed, "full": score_metrics(y["test"], full), "cross": score_metrics(y["test"], cross)})

    ensemble = {}
    for view in ("full", "cross"):
        pv = np.stack([probs(heads[s], view, "val") for s in SEEDS])
        pt = np.stack([probs(heads[s], view, "test") for s in SEEDS])
        pva = pv.mean(0); pta = pt.mean(0)
        ensemble[view] = {"validation": score_metrics(y["val"], pva), "test": score_metrics(y["test"], pta)}

    # Single-view risk: train on cross-view predictions from each training
    # seed's validation split, with leave-one-seed-out aggregation at test.
    # The score never reads full-view probabilities.
    risk = {}
    for mode in ("single_seed", "ensemble"):
        risk[mode] = {"risk_head": {}, "selective": {}}
        vals, yvals = [], []
        for seed in SEEDS:
            pval = probs(heads[seed], "cross", "val")
            vals.append(risk_features(pval, 5)); yvals.append((pval.argmax(1) < y["val"]).astype(int))
        Fv = np.vstack(vals); yv = np.concatenate(yvals)
        # For ensemble mode, collapse duplicated labels to image level.  For
        # single_seed mode, seed predictions are retained but the exact same
        # image is repeated only on the calibration side; test stays external.
        if mode == "ensemble":
            pval_ens = np.stack([probs(heads[s], "cross", "val") for s in SEEDS]).mean(0)
            Fv = risk_features(pval_ens, 5); yv = (pval_ens.argmax(1) < y["val"]).astype(int)
        mu2 = Fv.mean(0); sd2 = Fv.std(0); sd2[sd2 < 1e-8] = 1
        clf = LogisticRegression(C=.1, class_weight="balanced", solver="liblinear", max_iter=1000, random_state=0).fit((Fv - mu2) / sd2, yv)
        if mode == "ensemble":
            ptest = np.stack([probs(heads[s], "cross", "test") for s in SEEDS]).mean(0)
            Ft = risk_features(ptest, 5); yt = (ptest.argmax(1) < y["test"]).astype(int)
            st = clf.predict_proba((Ft - mu2) / sd2)[:, 1]
            sv = clf.predict_proba((Fv - mu2) / sd2)[:, 1]
            yv_event = (pval_ens.argmax(1) < y["val"]).astype(int)
        else:
            # Average the risk score of the five single-view heads, but do
            # not feed a full-view prediction to any head.
            test_scores = []
            for seed in SEEDS:
                ptest_seed = probs(heads[seed], "cross", "test")
                Ft_seed = risk_features(ptest_seed, 5)
                test_scores.append(clf.predict_proba((Ft_seed - mu2) / sd2)[:, 1])
            st = np.stack(test_scores).mean(0)
            ptest = np.stack([probs(heads[s], "cross", "test") for s in SEEDS]).mean(0)
            yt = (ptest.argmax(1) < y["test"]).astype(int)
            val_scores = []
            for seed in SEEDS:
                pval_seed = probs(heads[seed], "cross", "val")
                val_scores.append(clf.predict_proba((risk_features(pval_seed, 5) - mu2) / sd2)[:, 1])
            sv = np.stack(val_scores).mean(0)
            pval_ens = np.stack([probs(heads[s], "cross", "val") for s in SEEDS]).mean(0)
            yv_event = (pval_ens.argmax(1) < y["val"]).astype(int)
        risk[mode]["risk_head"] = {"test": {"auroc": float(roc_auc_score(yt, st)), "average_precision": float(average_precision_score(yt, st)), "brier": float(brier_score_loss(yt, st)), "positive_rate": float(yt.mean())}}
        for a in (.05, .10, .20):
            cal = calibrate(sv, yv_event, a); accepted = st <= cal["threshold"]
            risk[mode]["selective"][str(a)] = {"calibration": cal, "test_coverage": float(accepted.mean()), "test_accepted_risk": float(yt[accepted].mean()) if accepted.any() else None}

    result = {
        "experiment": "Exp56 ensemble and Exp57 single-view risk",
        "protocol": "same patient-grouped split; five existing seed heads; no original result overwritten",
        "per_seed": per_seed, "ensemble": ensemble, "risk": risk,
        "notes": [
            "Ensemble averages probability vectors across the five trained heads.",
            "Single-view risk receives only center-plus-cross probabilities, entropy, margin, expected severity and visible fraction.",
            "The single-view risk experiment is a research audit; synthetic center-plus-cross is still not a real paired acquisition.",
        ], "elapsed_seconds": time.time() - t0,
    }
    (HERE / "results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    (HERE / "REPORT.md").write_text("# Exp56–57：五种子集成与单视图风险头\n\n" + json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ensemble": ensemble, "risk": risk}, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__": main()
