#!/usr/bin/env python3
"""Exp26: tune quality robustness rather than committing to naive augmentation."""
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


def corrupt(arr, kind, level):
    im = Image.fromarray(np.clip(arr * 255, 0, 255).astype("uint8"))
    if kind == "blur":
        im = im.filter(ImageFilter.GaussianBlur([1, 2, 3][level - 1]))
    elif kind == "brightness":
        im = ImageEnhance.Brightness(im).enhance([.8, .6, .4][level - 1])
    elif kind == "contrast":
        im = ImageEnhance.Contrast(im).enhance([.8, .6, .4][level - 1])
    return np.asarray(im, dtype=np.float32) / 255.0


def moderate(arr, kind):
    im = Image.fromarray(np.clip(arr * 255, 0, 255).astype("uint8"))
    if kind == "blur":
        im = im.filter(ImageFilter.GaussianBlur(1))
    elif kind == "brightness":
        im = ImageEnhance.Brightness(im).enhance(.85)
    elif kind == "contrast":
        im = ImageEnhance.Contrast(im).enhance(.85)
    return np.asarray(im, dtype=np.float32) / 255.0


def photo_normalize(arr):
    """Normalize per-image photometry inside the retinal foreground mask."""
    gray = arr.mean(2)
    m = gray > .035
    if np.sum(m) < .08 * m.size:
        return arr
    out = arr.copy()
    for c in range(3):
        vals = arr[:, :, c][m]
        mean, sd = float(vals.mean()), float(vals.std())
        out[:, :, c][m] = np.clip(.50 + .18 * (vals - mean) / max(sd, 1e-5), 0, 1)
    out[~m] = 0
    return out


def feats(arrs, normalized=False):
    return np.vstack([baseline.feature_vector(photo_normalize(a) if normalized else a)[0] for a in arrs])


def fit(X, y):
    mu, sd = X.mean(0), X.std(0)
    sd[sd < 1e-8] = 1
    return baseline.fit_multiclass((X - mu) / sd, y), mu, sd


def score(W, X, mu, sd, y):
    p = baseline.predict_multi(W, (X - mu) / sd)
    pred = p.argmax(1)
    return p, {"accuracy": float(np.mean(pred == y)), "macro_f1": baseline.macro_f1(y, pred), "severity_mae": float(np.mean(abs(pred - y))), "underestimation_rate": float(np.mean(pred < y))}


def qproxy(arrs, ref):
    rows = []
    for a in arrs:
        _, m = baseline.feature_vector(a)
        rows.append([m["sharpness"], m["contrast"], m["brightness"], m["nonblack_coverage"]])
    z = (np.asarray(rows) - ref[0]) / ref[1]
    return .35 * z[:, 0] + .35 * z[:, 1] - .15 * abs(z[:, 2]) + .15 * z[:, 3]


def gate_threshold(y, p, q):
    vals = []
    for t in np.unique(np.quantile(q, np.linspace(.05, .85, 81))):
        keep = q >= t
        if keep.mean() >= .5:
            vals.append((float(np.mean(p[keep].argmax(1) == y[keep])), float(keep.mean()), float(t)))
    vals.sort(reverse=True)
    return vals[0][2]


def gated(y, p, q, t):
    keep = q >= t
    return {"threshold": float(t), "coverage": float(keep.mean()), "accepted_accuracy": float(np.mean(p[keep].argmax(1) == y[keep])) if np.any(keep) else None, "accepted_underestimation_rate": float(np.mean(p[keep].argmax(1) < y[keep])) if np.any(keep) else None, "rejected_n": int((~keep).sum())}


def main():
    mp = baseline.find_uwf_image_map(); records = []
    for s in ("train", "val", "test"):
        p, y = baseline.read_split(s, mp); records.extend(zip(p, y.tolist()))
    splits = baseline.make_patient_level_splits(records, seed=42)
    arrays = {s: [baseline.read_image(p) for p in splits[s]["paths"]] for s in splits}
    ytr, yv, yt = splits["train"]["y"], splits["val"]["y"], splits["test"]["y"]
    clean_tr = feats(arrays["train"]); ref_rows = []
    for a in arrays["train"]:
        _, m = baseline.feature_vector(a); ref_rows.append([m["sharpness"], m["contrast"], m["brightness"], m["nonblack_coverage"]])
    ref = (np.asarray(ref_rows).mean(0), np.asarray(ref_rows).std(0)); ref[1][ref[1] < 1e-8] = 1
    candidates = {}
    # Raw feature model with only one moderate copy per corruption and clean
    # images duplicated twice, preventing augmented data from dominating.
    aug = np.vstack([feats([moderate(a, k) for a in arrays["train"]]) for k in ("blur", "brightness", "contrast")])
    candidates["raw_clean"] = (clean_tr, ytr)
    candidates["raw_weighted_moderate_aug"] = (np.vstack([clean_tr, clean_tr, aug]), np.tile(ytr, 5))
    # Per-image photometric normalization tests invariance to illumination and
    # contrast changes without pretending that blur can be recovered.
    norm_tr = feats(arrays["train"], normalized=True)
    candidates["photometric_normalized"] = (norm_tr, ytr)
    result = {"dataset": {"n": len(records), "split_counts": {s: np.bincount(splits[s]["y"], minlength=3).tolist() for s in splits}}, "candidate_selection": {}, "models": {}, "quality_gate": {}, "notes": ["Candidate selected on a validation mixture of clean and L1/L2 synthetic stress, not on the test set.", "Photometric normalization operates only on foreground pixels; it is designed for brightness/contrast shifts, not blur.", "Synthetic stress is not a clinical quality ground truth."]}
    val_conditions = [("clean", arrays["val"])] + [(f"{k}_L{l}", [corrupt(a, k, l) for a in arrays["val"]]) for k in ("blur", "brightness", "contrast") for l in (1, 2)]
    test_conditions = [("clean", arrays["test"])] + [(f"{k}_L{l}", [corrupt(a, k, l) for a in arrays["test"]]) for k in ("blur", "brightness", "contrast") for l in (1, 2, 3)]
    fitted = {}
    for name, (train_X, train_y) in candidates.items():
        W, mu, sd = fit(train_X, train_y); fitted[name] = (W, mu, sd)
        val_rows = []
        for cond, arrs in val_conditions:
            X = feats(arrs, normalized=(name == "photometric_normalized")); _, met = score(W, X, mu, sd, yv); val_rows.append(met)
        result["candidate_selection"][name] = {"validation_mean_accuracy": float(np.mean([m["accuracy"] for m in val_rows])), "validation_clean_accuracy": val_rows[0]["accuracy"], "validation_stress_mean_accuracy": float(np.mean([m["accuracy"] for m in val_rows[1:]])), "validation_rows": {cond: met for (cond, _), met in zip(val_conditions, val_rows)}}
    chosen = max(result["candidate_selection"], key=lambda n: .4 * result["candidate_selection"][n]["validation_clean_accuracy"] + .6 * result["candidate_selection"][n]["validation_stress_mean_accuracy"])
    result["chosen_model"] = chosen
    W, mu, sd = fitted[chosen]
    val_cal_arrs = sum(([a] + [corrupt(a, k, l) for k in ("blur", "brightness", "contrast") for l in (1, 2)] for a in arrays["val"]), [])
    val_cal_y = np.tile(yv, 7)
    _, val_cal_p = score(W, feats(val_cal_arrs, normalized=(chosen == "photometric_normalized")), mu, sd, val_cal_y)
    # score() returns metrics, so recompute probabilities for gate calibration.
    val_cal_X = feats(val_cal_arrs, normalized=(chosen == "photometric_normalized")); val_cal_p = baseline.predict_multi(W, (val_cal_X - mu) / sd)
    t = gate_threshold(val_cal_y, val_cal_p, qproxy(val_cal_arrs, ref)); result["quality_gate"]["threshold"] = t
    for cond, arrs in test_conditions:
        X = feats(arrs, normalized=(chosen == "photometric_normalized")); p, met = score(W, X, mu, sd, yt); result["models"][cond] = met; result["quality_gate"][cond] = gated(yt, p, qproxy(arrs, ref), t)
    (HERE / "results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    (HERE / "REPORT.md").write_text("# Exp26：质量鲁棒性策略选择\n\n对简单增强、clean加权增强和前景光度归一化进行验证集选择，再在测试集做全量压力测试；门控阈值只用验证混合集确定。\n\n```json\n" + json.dumps(result, ensure_ascii=False, indent=2) + "\n```\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__": main()
