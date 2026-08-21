#!/usr/bin/env python3
"""Exp23: class-balanced and ordinal severity models, focused on PDR."""
from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, precision_score, recall_score, roc_auc_score

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HERE.mkdir(parents=True, exist_ok=True)
BASE = ROOT / "7hao/experiments/exp01_quality_fov_baseline/run_baseline.py"
spec = importlib.util.spec_from_file_location("baseline", BASE)
baseline = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(baseline)
CACHE = ROOT / "7hao/experiments/exp11_retinaradar_frozen_features/frozen_features.npz"


def standardize_fit(Xtr, Xv, Xt):
    mu = Xtr.mean(0)
    sd = Xtr.std(0)
    sd[sd < 1e-8] = 1.0
    return (Xtr - mu) / sd, (Xv - mu) / sd, (Xt - mu) / sd, mu, sd


def ordinal_fit(X, y, C):
    # Two cumulative logits: P(Y>0) and P(Y>1). The final probabilities are
    # the differences between adjacent cumulative probabilities.
    models = []
    for threshold in (0, 1):
        clf = LogisticRegression(C=C, class_weight="balanced", max_iter=1200, solver="lbfgs", random_state=42)
        clf.fit(X, (y > threshold).astype(int))
        models.append(clf)
    return models


def ordinal_predict(models, X):
    p0 = models[0].predict_proba(X)[:, 1]
    p1 = models[1].predict_proba(X)[:, 1]
    # Enforce the monotonicity expected from cumulative probabilities.
    hi = np.maximum(p0, p1)
    lo = np.minimum(p0, p1)
    probs = np.c_[1.0 - hi, hi - lo, lo]
    probs = np.clip(probs, 1e-8, 1.0)
    return probs / probs.sum(1, keepdims=True)


def metrics(y, probs):
    pred = probs.argmax(1)
    pdr = (y == 2).astype(int)
    result = {
        "accuracy": float(np.mean(pred == y)),
        "macro_f1": baseline.macro_f1(y, pred),
        "severity_mae": float(np.mean(np.abs(pred - y))),
        "underestimation_rate": float(np.mean(pred < y)),
        "pdr_n": int(pdr.sum()),
        "pdr_recall": float(recall_score(pdr, pred == 2, zero_division=0)),
        "pdr_precision": float(precision_score(pdr, pred == 2, zero_division=0)),
        "pdr_predicted_rate": float(np.mean(pred == 2)),
        "predicted_class_counts": np.bincount(pred, minlength=3).tolist(),
    }
    if len(np.unique(pdr)) == 2:
        score = probs[:, 2]
        result["pdr_auroc"] = float(roc_auc_score(pdr, score))
        result["pdr_average_precision"] = float(average_precision_score(pdr, score))
    else:
        result["pdr_auroc"] = None
        result["pdr_average_precision"] = None
    for c, name in enumerate(("normal", "npdr", "pdr")):
        m = y == c
        result[f"{name}_n"] = int(m.sum())
        result[f"{name}_accuracy"] = float(np.mean(pred[m] == y[m])) if np.any(m) else None
        result[f"{name}_underestimation_rate"] = float(np.mean(pred[m] < y[m])) if np.any(m) else None
    return result


def select_c(Xtr, ytr, Xv, yv, ordinal=False):
    candidates = (0.01, 0.03, 0.1, 0.3, 1.0)
    scores = []
    for C in candidates:
        if ordinal:
            model = ordinal_fit(Xtr, ytr, C)
            p = ordinal_predict(model, Xv)
        else:
            model = LogisticRegression(C=C, class_weight="balanced", max_iter=1200, solver="lbfgs", random_state=42)
            model.fit(Xtr, ytr)
            p = model.predict_proba(Xv)
        scores.append((baseline.macro_f1(yv, p.argmax(1)), C))
    scores.sort(reverse=True)
    return float(scores[0][1]), [{"C": float(c), "val_macro_f1": float(s)} for s, c in scores]


def main():
    image_map = baseline.find_uwf_image_map()
    records = []
    for split in ("train", "val", "test"):
        paths, y = baseline.read_split(split, image_map)
        records.extend(zip(paths, y.tolist()))
    splits = baseline.make_patient_level_splits(records, seed=42)
    cache = np.load(CACHE)
    # Match the cached embeddings to the exact patient-grouped split used by
    # all UWF experiments (same seed and grouping implementation).
    hand = {}
    for s in splits:
        hand[s] = np.vstack([baseline.feature_vector(baseline.read_image(p))[0] for p in splits[s]["paths"]])
    result = {
        "dataset": {"n": len(records), "split_counts": {s: np.bincount(splits[s]["y"], minlength=3).tolist() for s in splits}, "patient_counts": {s: len(splits[s]["patient_keys"]) for s in splits}},
        "models": {},
        "notes": [
            "Class-balanced logistic probes and ordinal cumulative logits are fit on frozen RetinaRadar features; the RetinaRadar checkpoint is not a disease model and is not updated.",
            "C is selected on the patient-level validation split by macro-F1, then the selected model is evaluated once on the held-out test split.",
            "PDR metrics are one-vs-rest; PDR is the highest UWF clinical grade (label 2).",
        ],
    }
    test_rows = []
    representations = []
    for view in ("full", "central"):
        representations.append((f"{view}_frozen_balanced", cache[f"{view}_train_features"], cache[f"{view}_val_features"], cache[f"{view}_test_features"], False))
        representations.append((f"{view}_frozen_ordinal", cache[f"{view}_train_features"], cache[f"{view}_val_features"], cache[f"{view}_test_features"], True))
        representations.append((f"{view}_fusion_balanced", np.c_[cache[f"{view}_train_features"], cache[f"{view}_train_quality_logits"], hand["train"]], np.c_[cache[f"{view}_val_features"], cache[f"{view}_val_quality_logits"], hand["val"]], np.c_[cache[f"{view}_test_features"], cache[f"{view}_test_quality_logits"], hand["test"]], False))
    ytr, yv, yt = splits["train"]["y"], splits["val"]["y"], splits["test"]["y"]
    for name, Xt0, Xv0, Xte0, is_ordinal in representations:
        Xtr, Xv, Xte, mu, sd = standardize_fit(Xt0, Xv0, Xte0)
        C, tuning = select_c(Xtr, ytr, Xv, yv, ordinal=is_ordinal)
        if is_ordinal:
            model = ordinal_fit(Xtr, ytr, C)
            p_tr, p_v, p_te = ordinal_predict(model, Xtr), ordinal_predict(model, Xv), ordinal_predict(model, Xte)
        else:
            model = LogisticRegression(C=C, class_weight="balanced", max_iter=1200, solver="lbfgs", random_state=42)
            model.fit(Xtr, ytr)
            p_tr, p_v, p_te = model.predict_proba(Xtr), model.predict_proba(Xv), model.predict_proba(Xte)
        result["models"][name] = {"selected_C": C, "tuning": tuning, "train": metrics(ytr, p_tr), "val": metrics(yv, p_v), "test": metrics(yt, p_te)}
        for i, p in enumerate(splits["test"]["paths"]):
            test_rows.append([name, p.name, int(yt[i]), int(p_te[i].argmax()), float(p_te[i, 2])])
    with (HERE / "test_predictions.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["model", "image", "true_label", "pred_label", "pdr_score"])
        w.writerows(test_rows)
    (HERE / "results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    report = [
        "# Exp23：序数严重度与PDR优化",
        "",
        "## 设计",
        "原始严重度预测对最高级PDR的召回和区分能力偏弱。这里比较三类表征（冻结特征、质量输出+冻结特征+手工统计融合）以及两种学习方式：类别均衡多分类和两个累计阈值的序数回归。序数模型显式利用Normal < NPDR < PDR的等级关系。",
        "",
        "## 结果",
        "```json",
        json.dumps(result["models"], ensure_ascii=False, indent=2),
        "```",
        "",
        "## 重点读法",
        "PDR AUROC/AP反映把PDR与非PDR区分开的能力；PDR recall反映真正PDR中被识别出来的比例；underestimation_rate反映模型把严重度报低的风险。不能只看总体accuracy。",
    ]
    (HERE / "REPORT.md").write_text("\n".join(report), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
