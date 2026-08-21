#!/usr/bin/env python3
"""Exp25: bootstrap and stratified audit of the optimized severity model."""
from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path

import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HERE.mkdir(parents=True, exist_ok=True)
BASE = ROOT / "7hao/experiments/exp01_quality_fov_baseline/run_baseline.py"
spec = importlib.util.spec_from_file_location("baseline", BASE)
baseline = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(baseline)
CACHE = ROOT / "7hao/experiments/exp11_retinaradar_frozen_features/frozen_features.npz"


def ordinal_fit(X, y, C=.01):
    from sklearn.linear_model import LogisticRegression
    return [LogisticRegression(C=C, class_weight="balanced", max_iter=1200, solver="lbfgs", random_state=42).fit(X, (y > t).astype(int)) for t in (0, 1)]


def ordinal_predict(models, X):
    p0 = models[0].predict_proba(X)[:, 1]
    p1 = models[1].predict_proba(X)[:, 1]
    hi, lo = np.maximum(p0, p1), np.minimum(p0, p1)
    p = np.c_[1 - hi, hi - lo, lo]
    p = np.clip(p, 1e-8, 1.0)
    return p / p.sum(1, keepdims=True)


def f1(y, pred):
    return baseline.macro_f1(y, pred)


def point_metrics(y, p):
    pred = p.argmax(1)
    pdr = (y == 2).astype(int)
    out = {
        "accuracy": float(np.mean(pred == y)),
        "macro_f1": float(f1(y, pred)),
        "severity_mae": float(np.mean(np.abs(pred - y))),
        "underestimation_rate": float(np.mean(pred < y)),
        "pdr_prevalence": float(pdr.mean()),
    }
    if len(np.unique(pdr)) == 2:
        out["pdr_auroc"] = float(roc_auc_score(pdr, p[:, 2]))
        out["pdr_average_precision"] = float(average_precision_score(pdr, p[:, 2]))
    else:
        out["pdr_auroc"] = None
        out["pdr_average_precision"] = None
    return out


def bootstrap(y, p, rng, n_boot=2000):
    n = len(y)
    keys = ("accuracy", "macro_f1", "severity_mae", "underestimation_rate", "pdr_auroc", "pdr_average_precision")
    vals = {k: [] for k in keys}
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        m = point_metrics(y[idx], p[idx])
        for k in keys:
            if m[k] is not None:
                vals[k].append(m[k])
    return {k: {"estimate": float(point_metrics(y, p)[k]) if point_metrics(y, p)[k] is not None else None,
                "ci95": [float(np.quantile(v, .025)), float(np.quantile(v, .975))] if v else None} for k, v in vals.items()}


def main():
    image_map = baseline.find_uwf_image_map()
    records = []
    for split in ("train", "val", "test"):
        paths, y = baseline.read_split(split, image_map)
        records.extend(zip(paths, y.tolist()))
    splits = baseline.make_patient_level_splits(records, seed=42)
    cache = np.load(CACHE)
    Xtr, Xv, Xt = cache["central_train_features"], cache["central_val_features"], cache["central_test_features"]
    mu, sd = Xtr.mean(0), Xtr.std(0)
    sd[sd < 1e-8] = 1.0
    Xtr, Xv, Xt = (Xtr - mu) / sd, (Xv - mu) / sd, (Xt - mu) / sd
    ytr, yv, yt = splits["train"]["y"], splits["val"]["y"], splits["test"]["y"]
    ordinal = ordinal_fit(Xtr, ytr, C=.01)
    p_ordinal = ordinal_predict(ordinal, Xt)
    # The class-balanced non-ordinal model is included because it had the best
    # held-out accuracy, while ordinal is the safety-focused model selected by
    # validation macro-F1/PDR behavior.
    from sklearn.linear_model import LogisticRegression
    balanced = LogisticRegression(C=.01, class_weight="balanced", max_iter=1200, solver="lbfgs", random_state=42).fit(Xtr, ytr)
    p_balanced = balanced.predict_proba(Xt)
    result = {
        "dataset": {"n_test": int(len(yt)), "test_class_counts": np.bincount(yt, minlength=3).tolist(), "bootstrap_replicates": 2000},
        "models": {
            "central_frozen_ordinal": {"point": point_metrics(yt, p_ordinal), "bootstrap": bootstrap(yt, p_ordinal, np.random.default_rng(20260810))},
            "central_frozen_balanced": {"point": point_metrics(yt, p_balanced), "bootstrap": bootstrap(yt, p_balanced, np.random.default_rng(20260811))},
        },
        "paired_comparison": {},
        "stratified": {},
        "notes": [
            "Bootstrap resamples the held-out test images with replacement; it quantifies sampling uncertainty but is not a substitute for an independent external cohort.",
            "Ordinal is selected by validation macro-F1 in Exp23; balanced is shown as an accuracy-oriented companion.",
        ],
    }
    # Paired comparison against the previously released frozen-feature central
    # probe, aligned by image name.
    old_rows = {r["image"]: r for r in csv.DictReader((ROOT / "7hao/experiments/exp11_retinaradar_frozen_features/test_predictions.csv").open(encoding="utf-8"))}
    old_pred = np.asarray([int(old_rows[p.name]["central_pred"]) for p in splits["test"]["paths"]])
    rng = np.random.default_rng(20260812)
    opt_pred = p_balanced.argmax(1)
    diffs_acc, diffs_under = [], []
    for _ in range(2000):
        idx = rng.integers(0, len(yt), size=len(yt))
        diffs_acc.append(float(np.mean(opt_pred[idx] == yt[idx]) - np.mean(old_pred[idx] == yt[idx])))
        diffs_under.append(float(np.mean(opt_pred[idx] < yt[idx]) - np.mean(old_pred[idx] < yt[idx])))
    result["paired_comparison"] = {
        "optimized": "central_frozen_balanced",
        "reference": "Exp11 central frozen linear probe",
        "optimized_point": point_metrics(yt, p_balanced),
        "reference_accuracy": float(np.mean(old_pred == yt)),
        "reference_underestimation_rate": float(np.mean(old_pred < yt)),
        "accuracy_delta_optimized_minus_reference": {"estimate": float(np.mean(opt_pred == yt) - np.mean(old_pred == yt)), "ci95": [float(np.quantile(diffs_acc, .025)), float(np.quantile(diffs_acc, .975))]},
        "underestimation_delta_optimized_minus_reference": {"estimate": float(np.mean(opt_pred < yt) - np.mean(old_pred < yt)), "ci95": [float(np.quantile(diffs_under, .025)), float(np.quantile(diffs_under, .975))]},
    }
    # Quality and severity strata use the already computed central quality proxy.
    meta_rows = [r for r in csv.DictReader((ROOT / "7hao/experiments/exp01_quality_fov_baseline/feature_meta_summary.csv").open(encoding="utf-8")) if r["split"] == "test" and r["view"] == "central"]
    meta_by_image = {r["image"]: float(r["quality_proxy"]) for r in meta_rows}
    q = np.asarray([meta_by_image[p.name] for p in splits["test"]["paths"]])
    for grade in (0, 1, 2):
        m = yt == grade
        result["stratified"][f"severity_{grade}"] = {"n": int(m.sum()), "accuracy": float(np.mean(p_balanced.argmax(1)[m] == yt[m])), "underestimation_rate": float(np.mean(p_balanced.argmax(1)[m] < yt[m]))}
    edges = np.quantile(q, [0, 1/3, 2/3, 1]); edges[0] -= 1e-9; edges[-1] += 1e-9
    for i, name in enumerate(("low", "middle", "high")):
        m = (q >= edges[i]) & (q < edges[i + 1])
        result["stratified"][f"quality_{name}"] = {"n": int(m.sum()), "quality_proxy_range": [float(edges[i]), float(edges[i + 1])], "accuracy": float(np.mean(p_balanced.argmax(1)[m] == yt[m])), "underestimation_rate": float(np.mean(p_balanced.argmax(1)[m] < yt[m]))}
    (HERE / "results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    report = [
        "# Exp25：优化模型的Bootstrap与分层审计",
        "",
        "对Exp23的两个候选模型进行2000次测试集bootstrap，并与Exp11原中心视野冻结线性探针做同图配对比较；另外按UWF严重度和中心图像质量代理分层。",
        "",
        "```json",
        json.dumps(result, ensure_ascii=False, indent=2),
        "```",
    ]
    (HERE / "REPORT.md").write_text("\n".join(report), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
