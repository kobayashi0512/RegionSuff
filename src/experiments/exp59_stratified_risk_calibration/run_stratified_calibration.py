#!/usr/bin/env python3
"""Exp59: predicted-severity-stratified calibration of a single-view risk head.

The candidate score observes only the limited-view prediction.  Thresholds are
calibrated inside predicted severity strata using one-sided Clopper–Pearson
upper bounds.  The test set is used only after thresholds are fixed.
"""
from __future__ import annotations

import copy
import importlib.util
import json
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


def features(p):
    ent = -np.sum(np.clip(p, 1e-8, 1) * np.log(np.clip(p, 1e-8, 1)), axis=1)
    sortp = np.sort(p, axis=1)
    margin = sortp[:, -1] - sortp[:, -2]
    expected = p @ np.arange(3.0)
    return np.c_[p, expected, ent, margin, np.ones(len(p)) * (5 / 9)]


def cp_upper(k, n):
    if n == 0 or k == n: return 1.0
    return float(beta.ppf(.95, k + 1, n - k))


def select_threshold(score, event, target):
    best = None
    for t in np.unique(score):
        acc = score <= t; n = int(acc.sum()); k = int(event[acc].sum())
        if n and cp_upper(k, n) <= target and (best is None or n > best[0]): best = (n, float(t), k, cp_upper(k, n))
    if best is None:
        idx = int(np.argmin(score)); return {"threshold": float(score[idx]), "coverage": 1 / len(event), "accepted_risk": float(event[idx]), "cp_upper": cp_upper(int(event[idx]), 1), "feasible": False}
    n, t, k, u = best
    return {"threshold": t, "coverage": n / len(event), "accepted_risk": k / n, "cp_upper": u, "feasible": True}


def score_model(heads, split):
    all_p = []
    for seed in SEEDS:
        head, dev, _, _ = heads[seed]
        with torch.no_grad():
            mask = torch.from_numpy(ab.eval_mask("cross", len(X[split]), 3)).float().to(dev)
            p = torch.softmax(head(torch.from_numpy(X[split]).float().to(dev), mask)[0], 1).cpu().numpy()
        all_p.append(p)
    return np.stack(all_p).mean(0)


def evaluate(yt, p, score, thresholds, mode):
    pred = p.argmax(1)
    accepted = np.zeros(len(yt), dtype=bool)
    for group in (0, 1, 2):
        idx = pred == group
        accepted[idx] = score[idx] <= thresholds[str(group)]["threshold"]
    out = {"coverage": float(accepted.mean()), "accepted_n": int(accepted.sum()), "accepted_risk": float(np.mean(pred[accepted] < yt[accepted])) if accepted.any() else None}
    out["by_predicted_severity"] = {}
    for group in (0, 1, 2):
        idx = accepted & (pred == group)
        out["by_predicted_severity"][str(group)] = {"n": int(idx.sum()), "coverage_within_group": float(idx.sum() / max(1, (pred == group).sum())), "accepted_risk": float(np.mean(pred[idx] < yt[idx])) if idx.any() else None}
    return out


def main():
    t0 = time.time()
    heads = {}
    for seed in SEEDS:
        heads[seed] = ab.train(X["train"], y["train"], X["val"], y["val"], "attention", .30, seed)
    pval = score_model(heads, "val"); ptest = score_model(heads, "test")
    yval_event = (pval.argmax(1) < y["val"]).astype(int)
    ytest_event = (ptest.argmax(1) < y["test"]).astype(int)
    Fv = features(pval); Ft = features(ptest)
    fm = Fv.mean(0); fs = Fv.std(0); fs[fs < 1e-8] = 1
    clf = LogisticRegression(C=.1, class_weight="balanced", solver="liblinear", max_iter=1000).fit((Fv - fm) / fs, yval_event)
    sv = clf.predict_proba((Fv - fm) / fs)[:, 1]; st = clf.predict_proba((Ft - fm) / fs)[:, 1]
    result = {"experiment": "Exp59 stratified single-view risk calibration", "protocol": "ensemble limited-view risk score; severity stratum is predicted limited-view severity; target labels are used only for validation calibration", "risk_head": {"test": {"auroc": float(roc_auc_score(ytest_event, st)), "average_precision": float(average_precision_score(ytest_event, st)), "brier": float(brier_score_loss(ytest_event, st)), "positive_rate": float(ytest_event.mean())}}, "targets": {}}
    for alpha in (.05, .10, .20):
        global_threshold = {}
        for group in (0, 1, 2):
            idx = pval.argmax(1) == group
            global_threshold[str(group)] = select_threshold(sv[idx], yval_event[idx], alpha)
        result["targets"][str(alpha)] = {"global": {}, "stratified": {"calibration": global_threshold}}
        # Global calibration from all validation images, then applied to all test images.
        gcal = select_threshold(sv, yval_event, alpha)
        gacc = st <= gcal["threshold"]
        result["targets"][str(alpha)]["global"] = {"calibration": gcal, "test_coverage": float(gacc.mean()), "test_accepted_risk": float(ytest_event[gacc].mean()) if gacc.any() else None}
        result["targets"][str(alpha)]["stratified"]["test"] = evaluate(y["test"], ptest, st, global_threshold, "predicted_severity")
    result["notes"] = [
        "The full-view output is not used by the risk head.",
        "Stratification improves safety only if it lowers accepted risk without an unacceptable coverage collapse.",
        "The limited-view mask is a geometric proxy, not a real paired camera acquisition.",
    ]
    result["elapsed_seconds"] = time.time() - t0
    (HERE / "results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    (HERE / "REPORT.md").write_text("# Exp59：按预测严重度分层的单视图风险校准\n\n" + json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__": main()
