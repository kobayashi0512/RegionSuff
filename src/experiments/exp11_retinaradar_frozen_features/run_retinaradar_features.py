#!/usr/bin/env python3
"""Experiment 11: frozen retinal quality-model features for FOV risk.

This experiment does not claim RetinaRadar is a disease model.  It uses the
released multi-label image-quality model as a frozen encoder and asks whether
its representations/quality outputs help predict when a central view
underestimates the UWF disease grade.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np
import torch
import timm
from PIL import Image
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, average_precision_score, f1_score, mean_absolute_error, roc_auc_score
from sklearn.model_selection import GroupKFold

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "7hao" / "datasets" / "UWF_DR_1630" / "extracted"
OUT = ROOT / "7hao" / "experiments" / "exp11_retinaradar_frozen_features"
MODEL_PATH = ROOT / "7hao" / "models" / "retinaradar" / "efficientnet_b0_retinaradar_model.ckpt"
OUT.mkdir(parents=True, exist_ok=True)


def patient_key(path: Path) -> str:
    parts = path.stem.split("_")
    return "_".join(parts[:2]) if len(parts) >= 2 else path.stem


def find_images() -> dict[str, Path]:
    out = {}
    for p in DATA.rglob("*"):
        if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg"}:
            out[p.name] = p
            out.setdefault(p.name.replace("__", "_"), p)
    return out


def read_csv(split: str, image_map: dict[str, Path]):
    paths, labels = [], []
    csv_path = next(DATA.rglob(f"{split}.csv"))
    with csv_path.open(newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            name = row["Image Name"].strip()
            paths.append(image_map[name])
            labels.append(int(row["Label"]))
    return paths, np.asarray(labels, dtype=np.int64)


def grouped_split(records: list[tuple[Path, int]], seed: int = 42):
    groups: dict[str, list[tuple[Path, int]]] = {}
    for p, y in records:
        groups.setdefault(patient_key(p), []).append((p, int(y)))
    ratios = np.array([.70, .15, .15])
    total_n, total_g = len(records), len(groups)
    total_c = np.bincount([y for _, y in records], minlength=3).astype(float)
    target_n, target_g, target_c = ratios * total_n, ratios * total_g, ratios[:, None] * total_c[None, :]
    cur_n, cur_g, cur_c = np.zeros(3), np.zeros(3), np.zeros((3, 3))
    assigned = [[], [], []]
    rng = np.random.default_rng(seed)
    keys = list(groups); rng.shuffle(keys); keys.sort(key=lambda k: len(groups[k]), reverse=True)
    for k in keys:
        rows = groups[k]; n = len(rows); c = np.bincount([y for _, y in rows], minlength=3).astype(float)
        scores = []
        for j in range(3):
            size_after = cur_n[j] + n
            ratio_after = (cur_c[j] + c) / max(1.0, size_after)
            global_ratio = total_c / max(1.0, total_n)
            size_term = ((size_after - target_n[j]) / max(1., target_n[j])) ** 2
            class_term = np.mean((ratio_after - global_ratio) ** 2)
            overflow = max(0., size_after - target_n[j]) / max(1., target_n[j])
            group_term = ((cur_g[j] + 1 - target_g[j]) / max(1., target_g[j])) ** 2
            scores.append(group_term + .25 * size_term + .5 * class_term + 2 * overflow)
        j = int(np.argmin(scores)); assigned[j].extend(rows)
        cur_n[j] += n; cur_g[j] += 1; cur_c[j] += c
    names = ["train", "val", "test"]
    return {name: {"paths": [p for p, _ in assigned[i]], "y": np.asarray([y for _, y in assigned[i]], dtype=np.int64), "patients": sorted({patient_key(p) for p, _ in assigned[i]})} for i, name in enumerate(names)}


def retinal_bbox(arr: np.ndarray):
    gray = arr.mean(2); mask = gray > .035
    if mask.sum() < .08 * mask.size:
        h, w = gray.shape; return 0, 0, w, h
    ys, xs = np.where(mask)
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def central_view(arr: np.ndarray, fraction: float = .55):
    x0, y0, x1, y1 = retinal_bbox(arr); roi = arr[y0:y1, x0:x1]
    h, w = roi.shape[:2]; ch, cw = max(8, int(h * fraction)), max(8, int(w * fraction))
    yy, xx = max(0, (h - ch) // 2), max(0, (w - cw) // 2)
    return roi[yy:yy + ch, xx:xx + cw]


def load_model():
    ckpt = torch.load(MODEL_PATH, map_location="cpu")
    model = timm.create_model("efficientnet_b0", pretrained=False, num_classes=17)
    state = {k.replace("model.", "", 1): v for k, v in ckpt["state_dict"].items()}
    model.load_state_dict(state, strict=True)
    model.eval()
    if torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")
    return model.to(device), device


MEAN = np.asarray([.485, .456, .406], dtype=np.float32)
STD = np.asarray([.229, .224, .225], dtype=np.float32)


def batch_tensor(paths: list[Path], view: str):
    xs = []
    for p in paths:
        with Image.open(p) as im:
            arr = np.asarray(im.convert("RGB"), dtype=np.float32) / 255.
        if view == "central": arr = central_view(arr)
        im = Image.fromarray(np.clip(arr * 255, 0, 255).astype(np.uint8)).resize((256, 256), Image.Resampling.BILINEAR)
        im = im.crop((16, 16, 240, 240))
        x = np.asarray(im, dtype=np.float32) / 255.
        x = (x - MEAN) / STD
        xs.append(np.transpose(x, (2, 0, 1)))
    return torch.from_numpy(np.stack(xs)).float()


def extract(model, device, paths, view, batch_size=32):
    feats, logits = [], []
    for start in range(0, len(paths), batch_size):
        x = batch_tensor(paths[start:start + batch_size], view).to(device)
        with torch.no_grad():
            z = model.forward_features(x)
            z = model.global_pool(z).flatten(1)
            y = model(x)
        feats.append(z.detach().cpu().numpy().astype(np.float32))
        logits.append(y.detach().cpu().numpy().astype(np.float32))
        if (start + len(x)) % 256 < batch_size or start + len(x) == len(paths):
            print(f"  {view}: {min(start + batch_size, len(paths))}/{len(paths)}", flush=True)
    return np.vstack(feats), np.vstack(logits)


def standardize(train, others):
    mu, sd = train.mean(0), train.std(0); sd[sd < 1e-8] = 1.
    return (train - mu) / sd, [(x - mu) / sd for x in others]


def metrics(y, pred):
    return {"accuracy": float(accuracy_score(y, pred)), "macro_f1": float(f1_score(y, pred, average="macro")), "severity_mae": float(mean_absolute_error(y, pred)), "underestimation_rate": float(np.mean(pred < y))}


def binary_metrics(y, score):
    return {"auroc": float(roc_auc_score(y, score)) if len(np.unique(y)) == 2 else None, "average_precision": float(average_precision_score(y, score)) if y.sum() else None}


def main():
    image_map = find_images(); records = []
    for split in ("train", "val", "test"):
        p, y = read_csv(split, image_map); records.extend(zip(p, y.tolist()))
    splits = grouped_split(records)
    model, device = load_model()
    print(f"device={device}; images={len(records)}")
    raw = {}
    for view in ("full", "central"):
        raw[view] = {}
        for split in splits:
            raw[view][split] = extract(model, device, splits[split]["paths"], view)
    # Save reusable frozen embeddings and the model's 17 quality logits.
    np.savez_compressed(OUT / "frozen_features.npz", **{f"{view}_{split}_{kind}": raw[view][split][0 if kind == 'features' else 1] for view in raw for split in splits for kind in ("features", "quality_logits")})

    results = {"dataset": {"n": len(records), "device": str(device), "split_counts": {s: np.bincount(splits[s]["y"], minlength=3).tolist() for s in splits}, "patient_counts": {s: len(splits[s]["patients"]) for s in splits}, "central_crop_fraction": .55}, "models": {}, "notes": []}
    classifiers = {}
    for view in ("full", "central"):
        Xtr = raw[view]["train"][0]; Xv, Xt = raw[view]["val"][0], raw[view]["test"][0]
        Xtr, [Xv, Xt] = standardize(Xtr, [Xv, Xt])
        clf = LogisticRegression(max_iter=500, C=.1, solver="lbfgs", random_state=42)
        clf.fit(Xtr, splits["train"]["y"]); classifiers[view] = clf
        results["models"][view] = {}
        for s, X in (("train", Xtr), ("val", Xv), ("test", Xt)):
            pred = clf.predict(X); results["models"][view][s] = metrics(splits[s]["y"], pred)
        print(view, results["models"][view], flush=True)

    # Compare frozen 17-dimensional quality logits alone versus full embedding.
    qresults = {}
    for view in ("full", "central"):
        Xtr = raw[view]["train"][1]; Xv, Xt = raw[view]["val"][1], raw[view]["test"][1]
        Xtr, [Xv, Xt] = standardize(Xtr, [Xv, Xt])
        clf = LogisticRegression(max_iter=500, C=.5, solver="lbfgs", random_state=42)
        clf.fit(Xtr, splits["train"]["y"]); qresults[view] = {}
        for s, X in (("train", Xtr), ("val", Xv), ("test", Xt)):
            qresults[view][s] = metrics(splits[s]["y"], clf.predict(X))
    results["models"]["quality_logits_only"] = qresults

    # Risk head: quality logits + frozen feature representation, target is
    # central linear-probe prediction below the true UWF grade.
    Xfull_tr, Xfull_v, Xfull_t = [raw["central"][s][0] for s in ("train", "val", "test")]
    Qtr, Qv, Qt = [raw["central"][s][1] for s in ("train", "val", "test")]
    # Recompute with the same training moments used above for val/test. For
    # the training risk labels use patient-grouped out-of-fold predictions;
    # in-sample labels would be almost all zero because the probe can fit the
    # training set very well.
    mu, sd = Xfull_tr.mean(0), Xfull_tr.std(0); sd[sd < 1e-8] = 1.
    Xby_split = {"train": Xfull_tr, "val": Xfull_v, "test": Xfull_t}
    groups_train = np.asarray([patient_key(p) for p in splits["train"]["paths"]])
    oof_pred = np.zeros(len(Xfull_tr), dtype=np.int64)
    for tr_idx, va_idx in GroupKFold(n_splits=5).split(Xfull_tr, splits["train"]["y"], groups_train):
        fold_mu, fold_sd = Xfull_tr[tr_idx].mean(0), Xfull_tr[tr_idx].std(0); fold_sd[fold_sd < 1e-8] = 1.
        fold_clf = LogisticRegression(max_iter=500, C=.1, solver="lbfgs", random_state=42)
        fold_clf.fit((Xfull_tr[tr_idx] - fold_mu) / fold_sd, splits["train"]["y"][tr_idx])
        oof_pred[va_idx] = fold_clf.predict((Xfull_tr[va_idx] - fold_mu) / fold_sd)
    c_pred = {"train": oof_pred, "val": classifiers["central"].predict((Xfull_v - mu) / sd), "test": classifiers["central"].predict((Xfull_t - mu) / sd)}
    risk_y = {s: (c_pred[s] < splits[s]["y"]).astype(np.int64) for s in splits}
    risk_Xtr = np.c_[Qtr, Xfull_tr]; risk_Xv = np.c_[Qv, Xfull_v]; risk_Xt = np.c_[Qt, Xfull_t]
    risk_Xtr, [risk_Xv, risk_Xt] = standardize(risk_Xtr, [risk_Xv, risk_Xt])
    risk_clf = LogisticRegression(max_iter=500, C=.1, solver="liblinear", random_state=42)
    risk_clf.fit(risk_Xtr, risk_y["train"])
    risk_scores = {"val": risk_clf.predict_proba(risk_Xv)[:, 1], "test": risk_clf.predict_proba(risk_Xt)[:, 1]}
    results["models"]["risk_head"] = {"train_positive": int(risk_y["train"].sum()), "val_positive": int(risk_y["val"].sum()), "test_positive": int(risk_y["test"].sum()), "val": binary_metrics(risk_y["val"], risk_scores["val"]), "test": binary_metrics(risk_y["test"], risk_scores["test"])}

    with (OUT / "test_predictions.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["image", "true_label", "full_pred", "central_pred", "underestimate", "risk_score"])
        full_tr = classifiers["full"]
        # full classifier test preprocessing moments
        ftr = raw["full"]["train"][0]; fmu, fsd = ftr.mean(0), ftr.std(0); fsd[fsd < 1e-8] = 1.
        fp = full_tr.predict((raw["full"]["test"][0] - fmu) / fsd)
        for i, p in enumerate(splits["test"]["paths"]): w.writerow([p.name, int(splits["test"]["y"][i]), int(fp[i]), int(c_pred["test"][i]), int(risk_y["test"][i]), float(risk_scores["test"][i])])
    results["notes"] = ["RetinaRadar EfficientNet-B0 weights are used frozen; this is a quality-assessment model, not a disease foundation model.", "Central view is a geometric 55% crop of UWF and is not a real paired 45-degree acquisition.", "Disease classifiers are linear probes trained on frozen representations under patient-level splits.", "The underestimation target is defined relative to the UWF dataset's clinical severity label and the central-view linear probe prediction."]
    with (OUT / "results.json").open("w", encoding="utf-8") as f: json.dump(results, f, ensure_ascii=False, indent=2)
    report = ["# Exp11：RetinaRadar 冻结特征与质量输出实验", "", "## 目的", "验证一个公开的眼底图像质量模型的冻结表征和 17 维质量输出，是否能帮助判断中心视野是否低估 UWF 的糖网分级。", "", "## 关键结果", "```json", json.dumps(results["models"], ensure_ascii=False, indent=2), "```", "", "## 解释", "- `frozen_feature`：不更新 RetinaRadar 参数，只训练线性分类器，避免把诊断任务误称为大模型微调。", "- `quality_logits_only`：只使用清晰度、照明、对比度、视野、可用性等质量输出。", "- `risk_head`：预测中心视野分类结果是否低于 UWF 临床标签。", "", "## 限制", "本实验的中心视野仍是 UWF 的几何裁剪，不能替代真实同眼 45°/UWF 配对；当前数据没有医生逐图质量金标准。"]
    (OUT / "REPORT.md").write_text("\n".join(report), encoding="utf-8")
    print(json.dumps(results, ensure_ascii=False, indent=2)); print(f"saved={OUT}")


if __name__ == "__main__": main()
