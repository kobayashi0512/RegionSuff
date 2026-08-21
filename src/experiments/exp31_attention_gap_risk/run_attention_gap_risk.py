#!/usr/bin/env python3
"""Exp31: turn deep-region attention into an evidence-missingness risk score."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HERE.mkdir(parents=True, exist_ok=True)
ATT = ROOT / "7hao/experiments/exp30_deep_region_attention/attention_test.csv"
RISK = ROOT / "7hao/experiments/exp27_multiview_disagreement_risk/risk_predictions.csv"


def metric(y, score):
    if len(np.unique(y)) < 2:
        return {"auroc": None, "average_precision": None, "n": int(len(y)), "positive_rate": float(y.mean())}
    return {"auroc": float(roc_auc_score(y, score)), "average_precision": float(average_precision_score(y, score)), "n": int(len(y)), "positive_rate": float(y.mean())}


def main():
    att_rows = [r for r in csv.DictReader(ATT.open(encoding="utf-8")) if r["model"] == "deep_attention_mask_augmented"]
    risk_rows = [r for r in csv.DictReader(RISK.open(encoding="utf-8")) if r["split"] == "test" and r["model"] == "multiview_plus_quality"]
    att_by = {r["image"]: r for r in att_rows}; risk_by = {r["image"]: r for r in risk_rows}
    images = sorted(set(att_by) & set(risk_by))
    attention = np.asarray([[float(att_by[i][f"attention_region_{j}"]) for j in range(9)] for i in images])
    y = np.asarray([int(risk_by[i]["risk_target"]) for i in images])
    severity = np.asarray([int(att_by[i]["true_label"]) for i in images])
    # Visible regions: center+cross. The other four corners and side regions
    # are the counterfactual evidence that the partial view did not observe.
    visible = np.asarray([1, 3, 4, 5, 7])
    missing_cross = 1.0 - attention[:, visible].sum(1)
    missing_center = 1.0 - attention[:, 4]
    peripheral_max = attention[:, [0, 2, 6, 8]].max(1)
    att_entropy = -np.sum(np.clip(attention, 1e-8, 1) * np.log(np.clip(attention, 1e-8, 1)), axis=1)
    scores = {"missing_center_attention": missing_center, "missing_center_cross_attention": missing_cross, "peripheral_max_attention": peripheral_max, "attention_entropy": att_entropy}
    result = {"dataset": {"n": len(images), "risk_target": "center-view severity underestimation from Exp27", "visible_regions_for_center_cross": visible.tolist()}, "scores": {}, "by_severity": {}, "notes": ["This is a post-hoc mechanistic audit: attention is learned in Exp30 and evaluated on the held-out Exp30 test images.", "The target comes from Exp27's geometric center-view underestimation definition; it is not a true paired 45-degree acquisition label.", "A high missingness score means the full-view attention allocates more evidence to regions absent from the center+cross view."]}
    for name, score in scores.items():
        result["scores"][name] = metric(y, score)
        result["scores"][name]["top20_percent_risk"] = metric(y[np.argsort(-score)[:max(1, int(.2*len(score)))]], score[np.argsort(-score)[:max(1, int(.2*len(score)))]])
    for c in (0, 1, 2):
        m = severity == c
        result["by_severity"][str(c)] = {"n": int(m.sum()), "mean_missing_center_cross": float(missing_cross[m].mean()), "mean_missing_center": float(missing_center[m].mean()), "underestimation_rate": float(y[m].mean())}
    with (HERE / "attention_gap_scores.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["image", "severity", "risk_target", *scores.keys()]); w.writerows([[i, int(severity[k]), int(y[k]), *[float(v[k]) for v in scores.values()]] for k, i in enumerate(images)])
    (HERE / "results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    (HERE / "REPORT.md").write_text("# Exp31：区域证据缺失风险\n\n把Exp30的3×3区域注意力转化为‘当前中心+十字视野没有看到多少全图证据’的机制分数，并在测试集上检验其对中心视野低估风险的排序能力。\n\n```json\n" + json.dumps(result, ensure_ascii=False, indent=2) + "\n```\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__": main()
