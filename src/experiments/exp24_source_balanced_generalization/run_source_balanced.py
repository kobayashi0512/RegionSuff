#!/usr/bin/env python3
"""Exp24: source-balanced leave-one-source-out quality generalization."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import openpyxl
import timm
import torch
from PIL import Image
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HERE.mkdir(parents=True, exist_ok=True)
DATA = ROOT / "7hao/datasets/MSHF_IQA/extracted/MSHF dataset 2.0"
MODEL = ROOT / "7hao/models/retinaradar/efficientnet_b0_retinaradar_model.ckpt"
MEAN = np.asarray([.485, .456, .406], np.float32)
STD = np.asarray([.229, .224, .225], np.float32)
NAMES = ("clarity", "illumination", "contrast", "overall")


def load_label_map():
    wb = openpyxl.load_workbook(DATA / "Individual_scores.xlsx.xlsx", read_only=True, data_only=True)
    out = {}
    for row in wb.active.iter_rows(min_row=3, values_only=True):
        if not row or not row[0]:
            continue
        groups = ((1, 2, 3, 4), (6, 7, 8, 9), (11, 12, 13, 14))
        vals = []
        for cols in zip(*groups):
            v = [row[i] for i in cols]
            vals.append(None if any(x is None for x in v) else int(sum(int(x) for x in v) >= 2))
        if all(x is not None for x in vals):
            out[str(row[0])] = [vals[1], vals[0], vals[2], vals[3]]
    return out


def load_model():
    ckpt = torch.load(MODEL, map_location="cpu")
    model = timm.create_model("efficientnet_b0", pretrained=False, num_classes=17)
    model.load_state_dict({k.replace("model.", "", 1): v for k, v in ckpt["state_dict"].items()}, strict=True)
    model.eval()
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    return model.to(device), device


def prep(paths):
    xs = []
    for p in paths:
        with Image.open(p) as im:
            im = im.convert("RGB").resize((256, 256), Image.Resampling.BILINEAR).crop((16, 16, 240, 240))
        x = np.asarray(im, np.float32) / 255.0
        x = (x - MEAN) / STD
        xs.append(np.transpose(x, (2, 0, 1)))
    return torch.from_numpy(np.stack(xs)).float()


def extract(model, device, paths):
    out = []
    for st in range(0, len(paths), 32):
        with torch.no_grad():
            z = model.global_pool(model.forward_features(prep(paths[st:st + 32]).to(device))).flatten(1)
        out.append(z.cpu().numpy().astype(np.float32))
        if st % 256 == 0:
            print(f"features: {min(st + 32, len(paths))}/{len(paths)}", flush=True)
    return np.vstack(out)


def metric(y, score):
    if len(np.unique(y)) < 2:
        return None
    return {"auroc": float(roc_auc_score(y, score)), "average_precision": float(average_precision_score(y, score)), "positive_rate": float(y.mean()), "n": int(len(y))}


def source_weights(src, y, mode):
    if mode == "unweighted":
        return np.ones(len(y), dtype=float)
    if mode == "source_balanced":
        return np.asarray([1.0 / max(1, np.sum(src == s)) for s in src], dtype=float) * len(y)
    # Give each source/label cell equal total weight. This protects a target
    # source from a training source whose label prevalence is very different.
    w = np.zeros(len(y), dtype=float)
    for s in sorted(set(src)):
        for c in (0, 1):
            m = (src == s) & (y == c)
            if np.any(m):
                w[m] = 1.0 / m.sum()
    return w * len(y) / max(1e-12, w.sum())


def main():
    labels = load_label_map()
    paths = sorted([p for split in ("train", "test") for p in (DATA / "AI-use" / split).glob("*.jpg") if p.name in labels])
    y = np.asarray([labels[p.name] for p in paths], dtype=int)
    sources = np.asarray([p.name.rsplit("-", 1)[0] for p in paths])
    model, device = load_model()
    print(f"device={device}; n={len(paths)}; sources={sorted(set(sources))}", flush=True)
    X = extract(model, device, paths)
    result = {
        "dataset": {"n": int(len(paths)), "sources": {s: int(np.sum(sources == s)) for s in sorted(set(sources))}, "labels": list(NAMES), "patient_id_available": False},
        "leave_one_source_out": {},
        "aggregate": {},
        "notes": [
            "Source-balanced training gives each source equal total contribution; source_label_balanced additionally equalizes the two binary label cells within each source when present.",
            "All probes use frozen RetinaRadar EfficientNet-B0 features. This is a domain-generalization audit for image quality, not a clinical endpoint validation.",
            "The release has no patient identifier field, so source holdout is the conservative reproducible split available here.",
        ],
    }
    modes = ("unweighted", "source_balanced", "source_label_balanced")
    aggregate = {mode: [] for mode in modes}
    for hold in sorted(set(sources)):
        tr, te = sources != hold, sources == hold
        result["leave_one_source_out"][hold] = {"n_test": int(te.sum()), "metrics": {mode: {} for mode in modes}}
        mu, sd = X[tr].mean(0), X[tr].std(0)
        sd[sd < 1e-8] = 1.0
        xtr, xte = (X[tr] - mu) / sd, (X[te] - mu) / sd
        for mode in modes:
            weights = source_weights(sources[tr], y[tr, 0], mode)
            for j, name in enumerate(NAMES):
                if len(np.unique(y[tr, j])) < 2 or len(np.unique(y[te, j])) < 2:
                    continue
                # Use the same weighting definition for each quality target.
                weights = source_weights(sources[tr], y[tr, j], mode)
                clf = LogisticRegression(max_iter=800, C=.1, solver="liblinear", random_state=42)
                clf.fit(xtr, y[tr, j], sample_weight=weights)
                score = clf.predict_proba(xte)[:, 1]
                m = metric(y[te, j], score)
                result["leave_one_source_out"][hold]["metrics"][mode][name] = m
                if m is not None:
                    aggregate[mode].append((hold, name, m["auroc"], m["average_precision"]))
    for mode in modes:
        rows = aggregate[mode]
        result["aggregate"][mode] = {
            "mean_auroc": float(np.mean([r[2] for r in rows])) if rows else None,
            "mean_average_precision": float(np.mean([r[3] for r in rows])) if rows else None,
            "n_source_label_cells": len(rows),
            "cells": [{"source": r[0], "label": r[1], "auroc": r[2], "average_precision": r[3]} for r in rows],
        }
    (HERE / "results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    report = [
        "# Exp24：来源均衡的域泛化实验",
        "",
        "## 设计",
        "MSHF中UWF-mosaic来源的跨来源AUROC最弱。Exp24在每次留出一个来源时，比较普通训练、来源均衡和来源×标签均衡三种权重，测试模型是否只是依赖某个数据来源的采集风格。",
        "",
        "## 结果",
        "```json",
        json.dumps({"aggregate": result["aggregate"], "UWF-mosaic": result["leave_one_source_out"].get("UWF-mosaic")}, ensure_ascii=False, indent=2),
        "```",
        "",
        "## 注意",
        "MSHF公开包没有患者ID；这里没有把来源留出夸大成患者级外部验证。若未来能取得患者级ID或独立医院数据，应再做真正的外部验证。",
    ]
    (HERE / "REPORT.md").write_text("\n".join(report), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
