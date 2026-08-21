#!/usr/bin/env python3
"""Exp02: sensitivity of disease underestimation to observable field of view."""
from __future__ import annotations

import csv, importlib.util, json
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
WORKSPACE = HERE.parents[2]
OUT = HERE
BASE = WORKSPACE / "7hao" / "experiments" / "exp01_quality_fov_baseline" / "run_baseline.py"
spec = importlib.util.spec_from_file_location("baseline", BASE)
if spec is None or spec.loader is None:
    raise RuntimeError(BASE)
baseline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(baseline)

FRACTIONS = [0.35, 0.45, 0.55, 0.65, 0.75, 0.90]

def main() -> None:
    image_map = baseline.find_uwf_image_map()
    records = []
    for split in ("train", "val", "test"):
        p, y = baseline.read_split(split, image_map)
        records.extend(zip(p, y.tolist()))
    splits = baseline.make_patient_level_splits(records, seed=42)
    rows = []
    detailed = []
    for frac in FRACTIONS:
        X = {}
        for split, data in splits.items():
            feats = []
            for i, path in enumerate(data["paths"], 1):
                f, _ = baseline.feature_vector(baseline.central_view(baseline.read_image(path), frac))
                feats.append(f)
                if i % 300 == 0:
                    print(f"fraction={frac:.2f} {split} {i}/{len(data['paths'])}", flush=True)
            X[split] = np.vstack(feats)
        Xtr, others, _, _ = baseline.standardize(X["train"], [X["val"], X["test"]])
        X["train"], X["val"], X["test"] = Xtr, others[0], others[1]
        W = baseline.fit_multiclass(X["train"], splits["train"]["y"])
        for split in ("train", "val", "test"):
            y = splits[split]["y"]
            p = baseline.predict_multi(W, X[split])
            pred = p.argmax(axis=1)
            rec = {
                "fraction": frac,
                "split": split,
                "n": int(len(y)),
                "accuracy": float(np.mean(pred == y)),
                "macro_f1": baseline.macro_f1(y, pred),
                "severity_mae": float(np.mean(np.abs(pred - y))),
                "underestimate_rate": float(np.mean(pred < y)),
                "underestimate_count": int(np.sum(pred < y)),
                "mean_entropy": float(np.mean(-np.sum(p * np.log(np.clip(p, 1e-8, 1.0)), axis=1))),
            }
            rows.append(rec)
            if split == "test":
                detailed.extend({"fraction": frac, "image": path.name, "true_label": int(y[i]), "pred": int(pred[i]), "underestimate": int(pred[i] < y[i])} for i, path in enumerate(splits[split]["paths"]))
        print(json.dumps(rows[-3:], ensure_ascii=False), flush=True)
    with (OUT / "results.json").open("w", encoding="utf-8") as f:
        json.dump({"fractions": FRACTIONS, "rows": rows, "split_strategy": "patient-level grouped split, seed=42", "notes": ["Central views are geometric crops from UWF, not paired 45-degree acquisitions.", "The experiment measures field-of-view sensitivity, not clinical image quality ground truth."]}, f, ensure_ascii=False, indent=2)
    with (OUT / "metrics.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    with (OUT / "test_predictions_by_fraction.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(detailed[0])); w.writeheader(); w.writerows(detailed)
    lines = ["# Exp02：视野比例敏感性实验", "", "目的：改变可见视野比例，观察 DR 严重程度误差和低估率如何变化。", "", "## 设置", "", "- UWF-DR 1630 张；patient-level grouped split，与 Exp01 相同。", "- 中心视野比例：0.35 / 0.45 / 0.55 / 0.65 / 0.75 / 0.90。", "- 每个视野比例单独训练轻量多分类逻辑回归。", "", "## 解释边界", "", "这个实验只能说明‘视野被限制后，模型和严重度估计如何变化’，不能把几何裁剪等同于真实普通眼底相机采集。", "", "## 文件", "", "- `results.json`：完整结果。", "- `metrics.csv`：可直接画图。", "- `test_predictions_by_fraction.csv`：测试集逐图预测。"]
    (OUT / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"saved={OUT}")

if __name__ == "__main__":
    main()
