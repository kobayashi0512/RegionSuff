#!/usr/bin/env python3
"""Exp21: fair field-of-view comparison with one shared classifier.

The earlier FOV experiments trained a separate classifier for each view.  That
mixes the effect of the view with the learnability of the classifier.  Here a
single model is evaluated on paired views of exactly the same test images.
"""
from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HERE.mkdir(parents=True, exist_ok=True)
BASE = ROOT / "7hao/experiments/exp01_quality_fov_baseline/run_baseline.py"
spec = importlib.util.spec_from_file_location("baseline", BASE)
baseline = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(baseline)


def circle45(arr: np.ndarray, ratio: float = 45 / 200) -> np.ndarray:
    x0, y0, x1, y1, _ = baseline.retinal_bbox(arr)
    roi = arr[y0:y1, x0:x1]
    h, w = roi.shape[:2]
    r = max(8, int(min(h, w) * ratio))
    cx, cy = w // 2, h // 2
    xa, xb = max(0, cx - r), min(w, cx + r)
    ya, yb = max(0, cy - r), min(h, cy + r)
    z = roi[ya:yb, xa:xb].copy()
    yy, xx = np.ogrid[:z.shape[0], :z.shape[1]]
    mask = (xx - z.shape[1] / 2.0) ** 2 + (yy - z.shape[0] / 2.0) ** 2 <= r * r
    z[~mask] = 0.0
    return z


def extract(paths, view):
    xs = []
    for i, p in enumerate(paths, 1):
        arr = baseline.read_image(p)
        if view == "square55":
            arr = baseline.central_view(arr, 0.55)
        elif view == "circle45":
            arr = circle45(arr)
        xs.append(baseline.feature_vector(arr)[0])
        if i % 250 == 0:
            print(f"{view}: {i}/{len(paths)}", flush=True)
    return np.vstack(xs)


def metrics(y, p):
    pred = p.argmax(1)
    return {
        "accuracy": float(np.mean(pred == y)),
        "macro_f1": baseline.macro_f1(y, pred),
        "severity_mae": float(np.mean(np.abs(pred - y))),
        "underestimation_rate": float(np.mean(pred < y)),
        "predicted_class_counts": np.bincount(pred, minlength=3).tolist(),
    }


def paired_view_stats(y, pred_full, pred_view):
    d = (pred_view == y).astype(float) - (pred_full == y).astype(float)
    return {
        "paired_accuracy_delta_vs_full": float(d.mean()),
        "paired_win_rate": float(np.mean(d > 0)),
        "paired_tie_rate": float(np.mean(d == 0)),
        "paired_loss_rate": float(np.mean(d < 0)),
        "paired_underestimation_delta_vs_full": float(np.mean(pred_view < y) - np.mean(pred_full < y)),
    }


def main():
    image_map = baseline.find_uwf_image_map()
    records = []
    for split in ("train", "val", "test"):
        paths, y = baseline.read_split(split, image_map)
        records.extend(zip(paths, y.tolist()))
    splits = baseline.make_patient_level_splits(records, seed=42)
    views = ("full", "square55", "circle45")
    X = {view: {s: extract(splits[s]["paths"], view) for s in splits} for view in views}
    result = {
        "dataset": {
            "n": len(records),
            "split_counts": {s: np.bincount(splits[s]["y"], minlength=3).tolist() for s in splits},
            "patient_counts": {s: len(splits[s]["patient_keys"]) for s in splits},
            "paired_test_images": len(splits["test"]["paths"]),
        },
        "protocols": {},
        "notes": [
            "Each protocol uses one shared classifier and evaluates full, square55 and circle45 views of the same test images.",
            "full_only_shared trains only on full-view training images; view_augmented_shared trains on full plus square55 plus circle45 training views with identical labels.",
            "The square/circle views are geometric proxies and are not real same-eye 45-degree acquisitions.",
        ],
    }
    prediction_rows = []
    for protocol in ("full_only_shared", "view_augmented_shared"):
        train_views = ("full",) if protocol == "full_only_shared" else views
        train_x = np.vstack([X[v]["train"] for v in train_views])
        train_y = np.tile(splits["train"]["y"], len(train_views))
        train_x, _, mu, sd = baseline.standardize(train_x, [])
        W = baseline.fit_multiclass(train_x, train_y)
        result["protocols"][protocol] = {"train_views": list(train_views), "views": {}}
        full_pred = None
        for view in views:
            view_metrics = {}
            pred_by_split = {}
            for split in ("train", "val", "test"):
                z = (X[view][split] - mu) / sd
                probs = baseline.predict_multi(W, z)
                pred = probs.argmax(1)
                pred_by_split[split] = pred
                view_metrics[split] = metrics(splits[split]["y"], probs)
            if view == "full":
                full_pred = pred_by_split["test"]
            if view != "full":
                view_metrics["test"].update(paired_view_stats(splits["test"]["y"], full_pred, pred_by_split["test"]))
            result["protocols"][protocol]["views"][view] = view_metrics
            if split == "test":
                pass
            for i, p in enumerate(splits["test"]["paths"]):
                prediction_rows.append([protocol, view, p.name, int(splits["test"]["y"][i]), int(pred_by_split["test"][i])])
    with (HERE / "test_predictions.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["protocol", "view", "image", "true_label", "pred_label"])
        w.writerows(prediction_rows)
    (HERE / "results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    report = [
        "# Exp21：共享模型的公平视野比较",
        "",
        "## 为什么重做",
        "早期实验为每个视野单独训练分类器，视野差异和模型可学习性混在一起。Exp21固定同一个分类器，在同一批测试图像上比较完整视野、55%中心方形和近似45°圆形视野。",
        "",
        "## 主要结果",
        "```json",
        json.dumps(result["protocols"], ensure_ascii=False, indent=2),
        "```",
        "",
        "## 解释",
        "paired_accuracy_delta_vs_full是同一张图上局部视野相对完整视野的准确率变化；paired_win/loss/tie把每张测试图作为配对单位，避免仅比较总体准确率。",
        "",
        "## 限制",
        "几何裁剪仍然不能替代真实同眼配对的45°眼底照相；结果用于检验‘视野缩小是否导致低估’这一机制，而不是估计临床设备之间的绝对差异。",
    ]
    (HERE / "REPORT.md").write_text("\n".join(report), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
