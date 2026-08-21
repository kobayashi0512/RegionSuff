#!/usr/bin/env python3
"""First reproducible baseline for disease-conditional retinal observability.

This script intentionally uses only Pillow and NumPy. It compares a full UWF
view with a simulated central field and predicts whether the central field
underestimates the UWF disease severity.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image


WORKSPACE = Path(__file__).resolve().parents[3]
DATA_ROOT = WORKSPACE / "7hao" / "datasets"
UWF_ROOT = DATA_ROOT / "UWF_DR_1630" / "extracted"
OUT_ROOT = WORKSPACE / "7hao" / "experiments" / "exp01_quality_fov_baseline"
OUT_ROOT.mkdir(parents=True, exist_ok=True)


def find_uwf_image_map() -> dict[str, Path]:
    result: dict[str, Path] = {}
    for p in UWF_ROOT.rglob("*"):
        if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg"}:
            result[p.name] = p
            # One released filename contains a duplicated underscore while
            # the corresponding CSV contains the normalized spelling.
            result.setdefault(p.name.replace("__", "_"), p)
    return result


def read_split(split: str, image_map: dict[str, Path]) -> tuple[list[Path], np.ndarray]:
    csv_paths = list(UWF_ROOT.rglob(f"{split}.csv"))
    if len(csv_paths) != 1:
        raise RuntimeError(f"Expected one {split}.csv, found {csv_paths}")
    paths: list[Path] = []
    labels: list[int] = []
    with csv_paths[0].open(newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            name = row["Image Name"].strip()
            if name not in image_map:
                raise FileNotFoundError(name)
            paths.append(image_map[name])
            labels.append(int(row["Label"]))
    return paths, np.asarray(labels, dtype=np.int64)


def patient_key(path: Path) -> str:
    # The released filenames use the first two underscore-separated fields as
    # the patient identifier, e.g. 5_155_2022-02-13_1_L.png.
    parts = path.stem.split("_")
    return "_".join(parts[:2]) if len(parts) >= 2 else path.stem


def make_patient_level_splits(records: list[tuple[Path, int]], seed: int = 42) -> dict[str, dict[str, object]]:
    groups: dict[str, list[tuple[Path, int]]] = {}
    for path, label in records:
        groups.setdefault(patient_key(path), []).append((path, int(label)))

    split_names = ["train", "val", "test"]
    ratios = np.asarray([0.70, 0.15, 0.15], dtype=np.float64)
    total_n = len(records)
    total_groups = len(groups)
    total_class = np.bincount([label for _, label in records], minlength=3).astype(np.float64)
    target_n = ratios * total_n
    target_groups = ratios * total_groups
    target_class = ratios[:, None] * total_class[None, :]
    current_n = np.zeros(3, dtype=np.float64)
    current_groups = np.zeros(3, dtype=np.float64)
    current_class = np.zeros((3, 3), dtype=np.float64)
    assigned: list[list[tuple[Path, int]]] = [[], [], []]

    rng = np.random.default_rng(seed)
    keys = list(groups)
    rng.shuffle(keys)
    keys.sort(key=lambda k: len(groups[k]), reverse=True)

    for key in keys:
        rows = groups[key]
        g_n = len(rows)
        g_class = np.bincount([label for _, label in rows], minlength=3).astype(np.float64)
        scores = []
        for j in range(3):
            size_after = current_n[j] + g_n
            class_after = current_class[j] + g_class
            size_term = ((size_after - target_n[j]) / max(1.0, target_n[j])) ** 2
            ratio_after = class_after / max(1.0, size_after)
            global_ratio = total_class / max(1.0, total_n)
            class_term = float(np.mean((ratio_after - global_ratio) ** 2))
            overflow = max(0.0, size_after - target_n[j]) / max(1.0, target_n[j])
            group_term = ((current_groups[j] + 1.0 - target_groups[j]) / max(1.0, target_groups[j])) ** 2
            scores.append(group_term + 0.25 * size_term + 0.5 * class_term + 2.0 * overflow)
        j = int(np.argmin(scores))
        assigned[j].extend(rows)
        current_n[j] += g_n
        current_groups[j] += 1
        current_class[j] += g_class

    result: dict[str, dict[str, object]] = {}
    for j, name in enumerate(split_names):
        rows = assigned[j]
        result[name] = {
            "paths": [p for p, _ in rows],
            "y": np.asarray([y for _, y in rows], dtype=np.int64),
            "patient_keys": sorted({patient_key(p) for p, _ in rows}),
        }
    return result


def read_image(path: Path) -> np.ndarray:
    with Image.open(path) as im:
        im = im.convert("RGB")
        return np.asarray(im, dtype=np.float32) / 255.0


def retinal_bbox(arr: np.ndarray) -> tuple[int, int, int, int, float]:
    gray = arr.mean(axis=2)
    mask = gray > 0.035
    if mask.sum() < 0.08 * mask.size:
        h, w = gray.shape
        return 0, 0, w, h, float(mask.mean())
    ys, xs = np.where(mask)
    x0, x1 = int(xs.min()), int(xs.max()) + 1
    y0, y1 = int(ys.min()), int(ys.max()) + 1
    return x0, y0, x1, y1, float(mask.mean())


def central_view(arr: np.ndarray, fraction: float = 0.55) -> np.ndarray:
    x0, y0, x1, y1, _ = retinal_bbox(arr)
    roi = arr[y0:y1, x0:x1]
    h, w = roi.shape[:2]
    ch = max(8, int(h * fraction))
    cw = max(8, int(w * fraction))
    yy = max(0, (h - ch) // 2)
    xx = max(0, (w - cw) // 2)
    return roi[yy : yy + ch, xx : xx + cw]


def resize_array(arr: np.ndarray, size: int = 64) -> np.ndarray:
    im = Image.fromarray(np.clip(arr * 255.0, 0, 255).astype(np.uint8))
    im = im.resize((size, size), Image.Resampling.BILINEAR)
    return np.asarray(im, dtype=np.float32) / 255.0


def safe_stats(x: np.ndarray) -> list[float]:
    return [float(np.mean(x)), float(np.std(x)), float(np.percentile(x, 5)), float(np.percentile(x, 95))]


def feature_vector(arr: np.ndarray) -> tuple[np.ndarray, dict[str, float]]:
    x0, y0, x1, y1, coverage = retinal_bbox(arr)
    h0, w0 = arr.shape[:2]
    z = resize_array(arr)
    gray = z.mean(axis=2)
    gx = np.diff(gray, axis=1)
    gy = np.diff(gray, axis=0)
    grad = np.sqrt(gx[:-1, :] ** 2 + gy[:, :-1] ** 2)
    yy, xx = np.mgrid[:64, :64]
    rr = np.sqrt((xx - 31.5) ** 2 + (yy - 31.5) ** 2) / 31.5

    feats: list[float] = []
    for c in range(3):
        feats.extend(safe_stats(z[:, :, c]))
    feats.extend(safe_stats(gray))
    feats.extend(safe_stats(grad))
    feats.extend([
        float(np.mean(gray < 0.035)),
        float(np.mean(gray > 0.90)),
        float(np.mean(grad > np.percentile(grad, 95))),
    ])

    # Concentric spatial summaries: useful for differentiating central and
    # peripheral information without claiming lesion localization.
    for lo, hi in [(0.0, 0.25), (0.25, 0.50), (0.50, 0.75), (0.75, 1.25)]:
        m = (rr >= lo) & (rr < hi)
        feats.extend([float(gray[m].mean()), float(gray[m].std()), float(z[:, :, 0][m].mean())])

    # Coarse spatial layout.
    for gy0 in range(4):
        for gx0 in range(4):
            patch = gray[gy0 * 16 : (gy0 + 1) * 16, gx0 * 16 : (gx0 + 1) * 16]
            feats.extend([float(patch.mean()), float(patch.std())])

    bbox_w = max(1, x1 - x0)
    bbox_h = max(1, y1 - y0)
    meta = {
        "nonblack_coverage": float(coverage),
        "bbox_width_ratio": float(bbox_w / max(1, w0)),
        "bbox_height_ratio": float(bbox_h / max(1, h0)),
        "bbox_aspect": float(bbox_w / bbox_h),
        "sharpness": float(np.mean(grad)),
        "contrast": float(np.std(gray)),
        "brightness": float(np.mean(gray)),
    }
    return np.asarray(feats, dtype=np.float64), meta


def load_features(paths: list[Path]) -> tuple[np.ndarray, list[dict[str, float]]]:
    xs: list[np.ndarray] = []
    metas: list[dict[str, float]] = []
    for i, path in enumerate(paths, 1):
        arr = read_image(path)
        f, meta = feature_vector(arr)
        xs.append(f)
        metas.append(meta)
        if i % 250 == 0:
            print(f"  extracted {i}/{len(paths)}", flush=True)
    return np.vstack(xs), metas


def standardize(train: np.ndarray, other: list[np.ndarray]) -> tuple[np.ndarray, list[np.ndarray], np.ndarray, np.ndarray]:
    mu = train.mean(axis=0)
    sd = train.std(axis=0)
    sd[sd < 1e-8] = 1.0
    return (train - mu) / sd, [(x - mu) / sd for x in other], mu, sd


def softmax(logits: np.ndarray) -> np.ndarray:
    x = logits - logits.max(axis=1, keepdims=True)
    ex = np.exp(np.clip(x, -40, 40))
    return ex / ex.sum(axis=1, keepdims=True)


def fit_multiclass(X: np.ndarray, y: np.ndarray, classes: int = 3, epochs: int = 700, lr: float = 0.06, l2: float = 1e-3) -> np.ndarray:
    Xb = np.c_[np.ones(len(X)), X]
    W = np.zeros((Xb.shape[1], classes), dtype=np.float64)
    Y = np.eye(classes)[y]
    for epoch in range(epochs):
        p = softmax(Xb @ W)
        grad = (Xb.T @ (p - Y)) / len(Xb)
        grad[1:] += l2 * W[1:]
        step = lr / (1.0 + 0.002 * epoch)
        W -= step * grad
    return W


def fit_binary(X: np.ndarray, y: np.ndarray, epochs: int = 600, lr: float = 0.08, l2: float = 1e-3) -> np.ndarray:
    Xb = np.c_[np.ones(len(X)), X]
    w = np.zeros(Xb.shape[1], dtype=np.float64)
    for epoch in range(epochs):
        logits = np.clip(Xb @ w, -30, 30)
        p = 1.0 / (1.0 + np.exp(-logits))
        grad = (Xb.T @ (p - y)) / len(Xb)
        grad[1:] += l2 * w[1:]
        w -= (lr / (1.0 + 0.002 * epoch)) * grad
    return w


def predict_multi(W: np.ndarray, X: np.ndarray) -> np.ndarray:
    return softmax(np.c_[np.ones(len(X)), X] @ W)


def predict_binary(w: np.ndarray, X: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.c_[np.ones(len(X)), X] @ w, -30, 30)))


def macro_f1(y: np.ndarray, pred: np.ndarray, classes: int = 3) -> float:
    vals = []
    for c in range(classes):
        tp = np.sum((y == c) & (pred == c))
        fp = np.sum((y != c) & (pred == c))
        fn = np.sum((y == c) & (pred != c))
        precision = tp / max(1, tp + fp)
        recall = tp / max(1, tp + fn)
        vals.append(2 * precision * recall / max(1e-12, precision + recall))
    return float(np.mean(vals))


def auc_pr(y: np.ndarray, score: np.ndarray) -> tuple[float, float]:
    order = np.argsort(-score, kind="mergesort")
    yy = y[order].astype(np.int64)
    positives = max(1, int(yy.sum()))
    tp = np.cumsum(yy)
    fp = np.cumsum(1 - yy)
    tpr = tp / positives
    fpr = fp / max(1, int((1 - yy).sum()))
    auc = float(np.sum((fpr[1:] - fpr[:-1]) * (tpr[1:] + tpr[:-1]) * 0.5)) if len(y) > 1 else 0.0
    precision = tp / np.maximum(1, tp + fp)
    ap = float(np.sum((tpr[1:] - tpr[:-1]) * precision[1:])) if len(y) > 1 else float(precision[-1])
    return auc, ap


def quality_proxy(meta: dict[str, float]) -> float:
    # This is a descriptive proxy only, not a clinical ground-truth label.
    sharp = min(1.0, meta["sharpness"] / 0.08)
    contrast = min(1.0, meta["contrast"] / 0.22)
    coverage = min(1.0, meta["nonblack_coverage"] / 0.55)
    return float(0.45 * sharp + 0.35 * contrast + 0.20 * coverage)


def main() -> None:
    print(f"workspace={WORKSPACE}")
    image_map = find_uwf_image_map()
    official_records: list[tuple[Path, int]] = []
    official_counts = {}
    for split in ("train", "val", "test"):
        paths, y = read_split(split, image_map)
        official_records.extend(zip(paths, y.tolist()))
        official_counts[split] = np.bincount(y, minlength=3).tolist()
    splits = make_patient_level_splits(official_records)
    print(f"official image-level counts={official_counts}")
    for split in ("train", "val", "test"):
        y = splits[split]["y"]
        print(f"patient-level {split}: n={len(y)}, patients={len(splits[split]['patient_keys'])}, counts={np.bincount(y, minlength=3).tolist()}")

    print("Extracting full-view features")
    full = {}
    full_meta = {}
    for split, data in splits.items():
        full[split], full_meta[split] = load_features(data["paths"])

    print("Extracting central-view features")
    central = {}
    central_meta = {}
    for split, data in splits.items():
        xs: list[np.ndarray] = []
        metas: list[dict[str, float]] = []
        for i, path in enumerate(data["paths"], 1):
            f, meta = feature_vector(central_view(read_image(path), fraction=0.55))
            xs.append(f)
            metas.append(meta)
            if i % 250 == 0:
                print(f"  extracted {i}/{len(data['paths'])}", flush=True)
        central[split] = np.vstack(xs)
        central_meta[split] = metas

    # Full-view classifier and central-view classifier.
    full_train, full_others, _, _ = standardize(full["train"], [full["val"], full["test"]])
    central_train, central_others, _, _ = standardize(central["train"], [central["val"], central["test"]])
    full["train"], full["val"], full["test"] = full_train, full_others[0], full_others[1]
    central["train"], central["val"], central["test"] = central_train, central_others[0], central_others[1]

    print("Fitting full-view classifier")
    W_full = fit_multiclass(full["train"], splits["train"]["y"])
    print("Fitting central-view classifier")
    W_central = fit_multiclass(central["train"], splits["train"]["y"])

    probs_full = {s: predict_multi(W_full, full[s]) for s in splits}
    probs_central = {s: predict_multi(W_central, central[s]) for s in splits}
    preds_full = {s: p.argmax(axis=1) for s, p in probs_full.items()}
    preds_central = {s: p.argmax(axis=1) for s, p in probs_central.items()}

    results: dict[str, object] = {"dataset": {}, "models": {}, "notes": []}
    for split in splits:
        y = splits[split]["y"]
        results["models"][split] = {
            "full_accuracy": float(np.mean(preds_full[split] == y)),
            "full_macro_f1": macro_f1(y, preds_full[split]),
            "central_accuracy": float(np.mean(preds_central[split] == y)),
            "central_macro_f1": macro_f1(y, preds_central[split]),
            "full_severity_mae": float(np.mean(np.abs(preds_full[split] - y))),
            "central_severity_mae": float(np.mean(np.abs(preds_central[split] - y))),
            "central_underestimation_rate": float(np.mean(preds_central[split] < y)),
        }

    # Risk head: predict whether the central view will underestimate severity.
    def risk_features(split: str) -> np.ndarray:
        p = probs_central[split]
        entropy = -np.sum(p * np.log(np.clip(p, 1e-8, 1.0)), axis=1, keepdims=True)
        sorted_p = np.sort(p, axis=1)
        margin = (sorted_p[:, -1] - sorted_p[:, -2])[:, None]
        q = np.asarray([quality_proxy(m) for m in central_meta[split]], dtype=np.float64)[:, None]
        return np.c_[central[split], p, entropy, margin, q]

    risk_train_X = risk_features("train")
    risk_val_X = risk_features("val")
    risk_test_X = risk_features("test")
    risk_train_X, [risk_val_X, risk_test_X], _, _ = standardize(risk_train_X, [risk_val_X, risk_test_X])
    risk_y_train = (preds_central["train"] < splits["train"]["y"]).astype(np.int64)
    risk_y_val = (preds_central["val"] < splits["val"]["y"]).astype(np.int64)
    risk_y_test = (preds_central["test"] < splits["test"]["y"]).astype(np.int64)
    w_risk = fit_binary(risk_train_X, risk_y_train)
    risk_score_val = predict_binary(w_risk, risk_val_X)
    risk_score_test = predict_binary(w_risk, risk_test_X)
    val_auc, val_ap = auc_pr(risk_y_val, risk_score_val)
    test_auc, test_ap = auc_pr(risk_y_test, risk_score_test)
    val_quality_risk = np.asarray([1.0 - quality_proxy(m) for m in central_meta["val"]])
    test_quality_risk = np.asarray([1.0 - quality_proxy(m) for m in central_meta["test"]])
    val_entropy = -np.sum(probs_central["val"] * np.log(np.clip(probs_central["val"], 1e-8, 1.0)), axis=1)
    test_entropy = -np.sum(probs_central["test"] * np.log(np.clip(probs_central["test"], 1e-8, 1.0)), axis=1)
    val_quality_auc, val_quality_ap = auc_pr(risk_y_val, val_quality_risk)
    test_quality_auc, test_quality_ap = auc_pr(risk_y_test, test_quality_risk)
    val_entropy_auc, val_entropy_ap = auc_pr(risk_y_val, val_entropy)
    test_entropy_auc, test_entropy_ap = auc_pr(risk_y_test, test_entropy)
    results["models"]["risk_head"] = {
        "train_underestimation_count": int(risk_y_train.sum()),
        "val_underestimation_count": int(risk_y_val.sum()),
        "test_underestimation_count": int(risk_y_test.sum()),
        "val_auroc": val_auc,
        "val_average_precision": val_ap,
        "test_auroc": test_auc,
        "test_average_precision": test_ap,
        "quality_proxy_val_auroc": val_quality_auc,
        "quality_proxy_val_average_precision": val_quality_ap,
        "quality_proxy_test_auroc": test_quality_auc,
        "quality_proxy_test_average_precision": test_quality_ap,
        "entropy_val_auroc": val_entropy_auc,
        "entropy_val_average_precision": val_entropy_ap,
        "entropy_test_auroc": test_entropy_auc,
        "entropy_test_average_precision": test_entropy_ap,
    }
    results["dataset"] = {
        "full_images": int(sum(len(v["paths"]) for v in splits.values())),
        "feature_dimension": int(full["train"].shape[1]),
        "central_crop_fraction": 0.55,
        "split_counts": {s: np.bincount(splits[s]["y"], minlength=3).tolist() for s in splits},
        "patient_counts": {s: len(splits[s]["patient_keys"]) for s in splits},
        "split_strategy": "patient-level grouped split, seed=42, target patient ratio 70/15/15",
    }
    results["notes"] = [
        "This is a lightweight feature baseline, not the final neural architecture.",
        "Central view is a geometric crop from UWF and is not a real paired 45-degree acquisition.",
        "All reported train/val/test results use a patient-level grouped split to prevent patient leakage.",
        "quality_proxy is descriptive only because the downloaded UWF-DR dataset has disease labels but no ophthalmologist quality labels.",
        "The main feasibility signal is whether central-view severity error and underestimation are non-trivial and predictable.",
    ]

    predictions_path = OUT_ROOT / "test_predictions.csv"
    with predictions_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["image", "true_label", "full_pred", "central_pred", "central_underestimate", "risk_score", "quality_proxy"])
        for i, path in enumerate(splits["test"]["paths"]):
            writer.writerow([
                path.name,
                int(splits["test"]["y"][i]),
                int(preds_full["test"][i]),
                int(preds_central["test"][i]),
                int(risk_y_test[i]),
                float(risk_score_test[i]),
                quality_proxy(central_meta["test"][i]),
            ])

    with (OUT_ROOT / "results.json").open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    with (OUT_ROOT / "feature_meta_summary.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["split", "view", "image", "nonblack_coverage", "sharpness", "contrast", "brightness", "quality_proxy"])
        for split in splits:
            for view, metas in (("full", full_meta[split]), ("central", central_meta[split])):
                for path, meta in zip(splits[split]["paths"], metas):
                    writer.writerow([split, view, path.name, meta["nonblack_coverage"], meta["sharpness"], meta["contrast"], meta["brightness"], quality_proxy(meta)])

    print(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"saved={OUT_ROOT}")


if __name__ == "__main__":
    main()
