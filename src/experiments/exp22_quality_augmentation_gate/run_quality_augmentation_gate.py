#!/usr/bin/env python3
"""Exp22: quality-augmentation training plus a validation-calibrated gate."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HERE.mkdir(parents=True, exist_ok=True)
BASE = ROOT / "7hao/experiments/exp01_quality_fov_baseline/run_baseline.py"
spec = importlib.util.spec_from_file_location("baseline", BASE)
baseline = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(baseline)


def corrupt(arr: np.ndarray, kind: str, level: int) -> np.ndarray:
    im = Image.fromarray(np.clip(arr * 255, 0, 255).astype("uint8"))
    if kind == "blur":
        im = im.filter(ImageFilter.GaussianBlur([1, 2, 3][level - 1]))
    elif kind == "brightness":
        im = ImageEnhance.Brightness(im).enhance([.8, .6, .4][level - 1])
    elif kind == "contrast":
        im = ImageEnhance.Contrast(im).enhance([.8, .6, .4][level - 1])
    return np.asarray(im, dtype=np.float32) / 255.0


def train_augments(arr: np.ndarray):
    """Moderate perturbations used during training, not the strongest test stress."""
    return [
        corrupt(arr, "blur", 1),
        ImageEnhance.Brightness(Image.fromarray(np.clip(arr * 255, 0, 255).astype("uint8"))).enhance(.85),
        ImageEnhance.Contrast(Image.fromarray(np.clip(arr * 255, 0, 255).astype("uint8"))).enhance(.85),
        ImageEnhance.Brightness(Image.fromarray(np.clip(arr * 255, 0, 255).astype("uint8"))).enhance(1.15),
        ImageEnhance.Contrast(Image.fromarray(np.clip(arr * 255, 0, 255).astype("uint8"))).enhance(1.15),
    ]


def as_array(x):
    if isinstance(x, Image.Image):
        return np.asarray(x, dtype=np.float32) / 255.0
    return x


def feature_batch(arrs):
    xs, metas = [], []
    for arr in arrs:
        f, meta = baseline.feature_vector(as_array(arr))
        xs.append(f)
        metas.append(meta)
    return np.vstack(xs), metas


def model_metrics(y, probs):
    pred = probs.argmax(1)
    return {
        "accuracy": float(np.mean(pred == y)),
        "macro_f1": baseline.macro_f1(y, pred),
        "severity_mae": float(np.mean(np.abs(pred - y))),
        "underestimation_rate": float(np.mean(pred < y)),
        "predicted_class_counts": np.bincount(pred, minlength=3).tolist(),
    }


def quality_score(metas, ref):
    """A label-free image quality proxy, standardized against clean training data."""
    cols = np.asarray([[m["sharpness"], m["contrast"], m["brightness"], m["nonblack_coverage"]] for m in metas], dtype=float)
    mu, sd = ref
    z = (cols - mu) / sd
    # Brightness is best near the clean-training distribution, while sharpness,
    # contrast and retinal coverage are better when larger.
    return .35 * z[:, 0] + .35 * z[:, 1] - .15 * np.abs(z[:, 2]) + .15 * z[:, 3]


def gated_metrics(y, probs, q, threshold):
    pred = probs.argmax(1)
    keep = q >= threshold
    if not np.any(keep):
        return {"threshold": float(threshold), "coverage": 0.0, "accepted_accuracy": None, "accepted_underestimation_rate": None}
    return {
        "threshold": float(threshold),
        "coverage": float(keep.mean()),
        "accepted_accuracy": float(np.mean(pred[keep] == y[keep])),
        "accepted_underestimation_rate": float(np.mean(pred[keep] < y[keep])),
        "rejected_n": int((~keep).sum()),
    }


def choose_threshold(y, probs, q):
    # Calibration is performed once on validation data; the test set is never
    # used to choose the threshold. Requiring >=50% coverage avoids a trivial
    # gate that rejects nearly every image.
    candidates = np.unique(np.quantile(q, np.linspace(.05, .85, 81)))
    valid = []
    for t in candidates:
        g = gated_metrics(y, probs, q, t)
        if g["coverage"] >= .50:
            valid.append((g["accepted_accuracy"], g["coverage"], float(t)))
    valid.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return valid[0][2] if valid else float(np.quantile(q, .5))


def main():
    image_map = baseline.find_uwf_image_map()
    records = []
    for split in ("train", "val", "test"):
        paths, y = baseline.read_split(split, image_map)
        records.extend(zip(paths, y.tolist()))
    splits = baseline.make_patient_level_splits(records, seed=42)
    arrays = {s: [baseline.read_image(p) for p in splits[s]["paths"]] for s in splits}
    # Build clean and moderate-augmentation training matrices.
    clean_tr, clean_meta_tr = feature_batch(arrays["train"])
    aug_arrs = []
    for i, arr in enumerate(arrays["train"], 1):
        aug_arrs.extend(train_augments(arr))
        if i % 250 == 0:
            print(f"training augmentations: {i}/{len(arrays['train'])}", flush=True)
    aug_tr, _ = feature_batch(aug_arrs)
    robust_tr = np.vstack([clean_tr, aug_tr])
    robust_y = np.tile(splits["train"]["y"], 6)
    clean_tr_z, [_, _], clean_mu, clean_sd = baseline.standardize(clean_tr, [clean_tr, clean_tr])
    robust_tr_z, _, robust_mu, robust_sd = baseline.standardize(robust_tr, [])
    W_clean = baseline.fit_multiclass(clean_tr_z, splits["train"]["y"])
    W_robust = baseline.fit_multiclass(robust_tr_z, robust_y)
    quality_ref = (np.asarray([[m["sharpness"], m["contrast"], m["brightness"], m["nonblack_coverage"]] for m in clean_meta_tr]).mean(0),
                   np.asarray([[m["sharpness"], m["contrast"], m["brightness"], m["nonblack_coverage"]] for m in clean_meta_tr]).std(0))
    quality_ref[1][quality_ref[1] < 1e-8] = 1.0

    def evaluate(arrs, y, W, mu, sd, name):
        X, metas = feature_batch(arrs)
        probs = baseline.predict_multi(W, (X - mu) / sd)
        q = quality_score(metas, quality_ref)
        return model_metrics(y, probs), probs, q

    result = {
        "dataset": {"n": len(records), "split_counts": {s: np.bincount(splits[s]["y"], minlength=3).tolist() for s in splits}},
        "training": {
            "clean_training_n": int(len(clean_tr)),
            "augmented_training_n": int(len(robust_tr)),
            "augmentation_copies_per_clean": 5,
            "augmentation_policy": ["GaussianBlur(radius=1)", "brightness x .85/.15", "contrast x .85/1.15"],
        },
        "models": {"clean_only": {}, "quality_augmented": {}},
        "quality_gate": {},
        "notes": [
            "Quality stress tests use the same synthetic corruptions as Exp06 for direct comparison.",
            "The quality gate is a label-free proxy calibrated on validation labels only and constrained to retain at least 50% of validation images.",
            "Synthetic corruption cannot replace real-world low-quality images or a clinician quality gold standard.",
        ],
    }
    conditions = [("clean", arrays["test"])]
    for kind in ("blur", "brightness", "contrast"):
        for level in (1, 2, 3):
            conditions.append((f"{kind}_L{level}", [corrupt(a, kind, level) for a in arrays["test"]]))
    # Calibrate the single gate threshold on a validation mixture.
    val_arrs = arrays["val"]
    val_cal_arrs = val_arrs + [corrupt(a, "brightness", 2) for a in val_arrs] + [corrupt(a, "contrast", 2) for a in val_arrs]
    val_cal_y = np.tile(splits["val"]["y"], 3)
    val_clean_metrics, val_clean_probs, val_clean_q = evaluate(val_arrs, splits["val"]["y"], W_robust, robust_mu, robust_sd, "val")
    _, val_cal_probs, val_cal_q = evaluate(val_cal_arrs, val_cal_y, W_robust, robust_mu, robust_sd, "calibration")
    threshold = choose_threshold(val_cal_y, val_cal_probs, val_cal_q)
    result["quality_gate"] = {"calibration": {"n": len(val_cal_y), "threshold": threshold, "calibration_metrics": gated_metrics(val_cal_y, val_cal_probs, val_cal_q, threshold)}}
    for cond, arrs in conditions:
        for model_name, W, mu, sd in (("clean_only", W_clean, clean_mu, clean_sd), ("quality_augmented", W_robust, robust_mu, robust_sd)):
            met, probs, q = evaluate(arrs, splits["test"]["y"], W, mu, sd, cond)
            result["models"][model_name][cond] = met
            if model_name == "quality_augmented":
                result["quality_gate"][cond] = gated_metrics(splits["test"]["y"], probs, q, threshold)
    (HERE / "results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    report = [
        "# Exp22：质量增强训练与拒识机制",
        "",
        "## 设计",
        "在原始训练图像上加入中等强度的模糊、亮度和对比度扰动，训练一个质量增强模型；测试阶段沿用Exp06的三档合成退化。另用验证集校准一个不依赖疾病标签的质量门控分数，低于阈值的图像进入拒识/人工复核。",
        "",
        "## 结果",
        "```json",
        json.dumps({"models": result["models"], "quality_gate": result["quality_gate"]}, ensure_ascii=False, indent=2),
        "```",
        "",
        "## 注意",
        "门控的价值不是让模型‘强行给出答案’，而是在图像质量明显不足时降低自动判读覆盖率、提高保留样本的可靠性。该门控仍需真实低质量临床样本验证。",
    ]
    (HERE / "REPORT.md").write_text("\n".join(report), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
