#!/usr/bin/env python3
"""Exp58: region-wise source/target moment normalization on external cohorts.

This is an unlabeled target-domain audit.  Target labels are loaded only after
features have been transformed and predictions generated.  The experiment
compares global source normalization, region-wise source normalization, and
region-wise unlabeled target normalization.
"""
from __future__ import annotations

import csv
import importlib.util
import json
import time
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CACHE = ROOT / "7hao/experiments/exp34_shared_uwf_region_cache"
HERE.mkdir(parents=True, exist_ok=True)

sp = importlib.util.spec_from_file_location("ab", ROOT / "7hao/experiments/exp35_region_mask_pool_ablation/run_ablation.py")
ab = importlib.util.module_from_spec(sp); assert sp.loader; sp.loader.exec_module(ab)
sp2 = importlib.util.spec_from_file_location("m30", ROOT / "7hao/experiments/exp30_deep_region_attention/run_deep_region_attention.py")
m30 = importlib.util.module_from_spec(sp2); assert sp2.loader; sp2.loader.exec_module(m30)

meta = json.loads((CACHE / "split_meta.json").read_text())
source_raw = np.load(CACHE / "region_features_g3.npz")
raw_source = source_raw["train_features"].astype(np.float32)
y_source = np.asarray(meta["train"]["y"], dtype=np.int64)
raw_val = source_raw["val_features"].astype(np.float32)
y_val = np.asarray(meta["val"]["y"], dtype=np.int64)


def source_stats():
    gm = raw_source.reshape(-1, raw_source.shape[-1]).mean(0)
    gs = raw_source.reshape(-1, raw_source.shape[-1]).std(0); gs[gs < 1e-8] = 1
    rm = raw_source.mean(0); rs = raw_source.std(0); rs[rs < 1e-8] = 1
    return gm, gs, rm, rs


GM, GS, RM, RS = source_stats()


def normalize(raw, mode):
    if mode == "global_source": return (raw - GM) / GS
    if mode == "region_source": return (raw - RM) / RS
    if mode == "region_target":
        tm = raw.mean(0); ts = raw.std(0); ts[ts < 1e-8] = 1
        return (raw - tm) / ts
    raise ValueError(mode)


def metrics(y, pred):
    return {
        "accuracy": float(np.mean(pred == y)),
        "macro_f1": float(ab.m30.baseline.macro_f1(y, pred)),
        "severity_mae": float(np.mean(np.abs(pred - y))),
        "underestimation_rate": float(np.mean(pred < y)),
    }


def load_external():
    out = {}
    # IDRiD and SUSTech feature caches were generated without using labels.
    for name in ("IDRiD_test", "SUSTech_SYSU"):
        p = ROOT / f"7hao/experiments/exp52_unlabeled_moment_adaptation/{name}_raw_region_features.npz"
        if name == "IDRiD_test":
            base = ROOT / "7hao/datasets/IDRiD_Zenodo/extracted/B. Disease Grading"
            csvp = base / "2. Groundtruths/b. IDRiD_Disease Grading_Testing Labels.csv"
            idir = base / "1. Original Images/b. Testing Set"
            rows = []
            with csvp.open(newline="", encoding="utf-8-sig") as f:
                for r in csv.DictReader(f):
                    image = idir / (r["Image name"].strip() + ".jpg")
                    if image.exists(): rows.append((int(r["Retinopathy grade"]), 0 if int(r["Retinopathy grade"]) == 0 else 1 if int(r["Retinopathy grade"]) <= 3 else 2))
        else:
            base = ROOT / "7hao/datasets/SUSTech_SYSU_Figshare/extracted/originalImages"
            rows = []
            with (base / "drLabels.csv").open(newline="", encoding="utf-8-sig") as f:
                for r in csv.DictReader(f):
                    g = int(r["DR_grade(International_Clinical_DR_Severity_Scale)"])
                    rows.append((g, 0 if g == 0 else 1 if g <= 3 else 2))
        if p.exists(): out[name] = {"raw": np.load(p)["features"].astype(np.float32), "y": np.asarray([r[1] for r in rows], dtype=np.int64)}
    mm = ROOT / "7hao/experiments/exp53_mmrdr_uwf_external_fov/mmrdr_test_raw_region_features.npz"
    mr = ROOT / "7hao/datasets/MMRDR_figshare/extracted/MMRDR-UWF/UWF.csv"
    base = ROOT / "7hao/datasets/MMRDR_figshare/extracted/MMRDR-UWF"
    rows = []
    with mr.open(newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r["image"].startswith("img/ts") and (base / r["image"]).exists():
                g = int(r["grade"]); rows.append(0 if g == 0 else 1 if g <= 3 else 2)
    if mm.exists(): out["MMRDR_UWF"] = {"raw": np.load(mm)["features"].astype(np.float32), "y": np.asarray(rows, dtype=np.int64)}
    return out


def main():
    t0 = time.time()
    results = {"experiment": "Exp58 region-wise external normalization", "targets": {}, "protocol": "source labels only train the source head; target moments are estimated without target labels"}
    external = load_external()
    for target_name, item in external.items():
        raw = item["raw"]; yy = item["y"]
        results["targets"][target_name] = {"n": int(len(yy)), "methods": {}}
        for method in ("global_source", "region_source", "region_target"):
            results["targets"][target_name]["methods"][method] = {"full": [], "cross": []}
        for seed in range(5):
            heads = {}
            for train_method in ("global_source", "region_source"):
                xtr = normalize(raw_source, train_method); xv = normalize(raw_val, train_method)
                heads[train_method] = ab.train(xtr, y_source, xv, y_val, "attention", .30, seed)
            # global_source uses the historical head; the other two use the
            # same architecture trained on region-wise source statistics.
            for method, train_method, eval_method in (("global_source", "global_source", "global_source"), ("region_source", "region_source", "region_source"), ("region_target", "region_source", "region_target")):
                head, dev, _, _ = heads[train_method]
                xx = normalize(raw, eval_method)
                with torch.no_grad():
                    xt = torch.from_numpy(xx).float().to(dev)
                    for view in ("full", "cross"):
                        mask = torch.from_numpy(ab.eval_mask(view, len(yy), 3)).float().to(dev)
                        pred = head(xt, mask)[0].argmax(1).cpu().numpy()
                        results["targets"][target_name]["methods"][method][view].append(metrics(yy, pred))
        for method, views in results["targets"][target_name]["methods"].items():
            for view, rows in views.items():
                keys = tuple(rows[0])
                views[view] = {k: {"mean": float(np.mean([r[k] for r in rows])), "std": float(np.std([r[k] for r in rows], ddof=1))} for k in keys}
    results["notes"] = [
        "All geometric views are the same 3x3 masks used in the source model.",
        "Region-wise target normalization is transductive and unlabeled; it is not a clinical calibration procedure.",
        "A method is not promoted solely because macro-F1 improves if underestimation or MAE worsens materially.",
    ]
    results["elapsed_seconds"] = time.time() - t0
    (HERE / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    (HERE / "REPORT.md").write_text("# Exp58：区域级无标签外部域标准化\n\n" + json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(results["targets"], ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__": main()
