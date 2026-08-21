#!/usr/bin/env python3
"""Exp60: train with pixel-space continuous aperture augmentation.

One masked copy per training image is generated in the original retinal
bounding box and re-encoded by the frozen RetinaRadar encoder.  The trained
head is then evaluated on held-out geometric views and held-out pixel-space
apertures.  Exp01--Exp59 are untouched.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import random
import time
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import accuracy_score, f1_score

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CACHE = ROOT / "7hao/experiments/exp34_shared_uwf_region_cache"
HERE.mkdir(parents=True, exist_ok=True)
SEEDS = (0, 1, 2, 3, 4)

sp = importlib.util.spec_from_file_location("ab", ROOT / "7hao/experiments/exp35_region_mask_pool_ablation/run_ablation.py")
ab = importlib.util.module_from_spec(sp); assert sp.loader; sp.loader.exec_module(ab)
sp2 = importlib.util.spec_from_file_location("m30", ROOT / "7hao/experiments/exp30_deep_region_attention/run_deep_region_attention.py")
m30 = importlib.util.module_from_spec(sp2); assert sp2.loader; sp2.loader.exec_module(m30)
DEVICE = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

meta = json.loads((CACHE / "split_meta.json").read_text())
z = np.load(CACHE / "region_features_g3.npz")
raw = {s: z[f"{s}_features"].astype(np.float32) for s in ("train", "val", "test")}
y = {s: np.asarray(meta[s]["y"], dtype=np.int64) for s in raw}
mu = raw["train"].reshape(-1, raw["train"].shape[-1]).mean(0)
sd = raw["train"].reshape(-1, raw["train"].shape[-1]).std(0); sd[sd < 1e-8] = 1
X = {s: ((raw[s] - mu) / sd).astype(np.float32) for s in raw}


def aperture(arr, bbox, shape, fraction, dx=0.0, dy=0.0):
    x0, y0, x1, y1, _ = bbox
    h, w = y1 - y0, x1 - x0
    cx = x0 + w * (0.5 + dx * (1 - fraction) / 2)
    cy = y0 + h * (0.5 + dy * (1 - fraction) / 2)
    yy, xx = np.ogrid[:arr.shape[0], :arr.shape[1]]
    if shape == "rect":
        keep = (np.abs(xx - cx) <= w * fraction / 2) & (np.abs(yy - cy) <= h * fraction / 2)
    else:
        keep = ((xx - cx) / (w + 1e-8)) ** 2 + ((yy - cy) / (h + 1e-8)) ** 2 <= (fraction / np.sqrt(np.pi)) ** 2
    out = np.zeros_like(arr); out[keep] = arr[keep]
    return out


def fixed_grid_crops(arr, bbox):
    x0, y0, x1, y1, _ = bbox
    roi = arr[y0:y1, x0:x1]; h, w = roi.shape[:2]
    return [roi[int(r * h / 3):int((r + 1) * h / 3), int(c * w / 3):int((c + 1) * w / 3)] for r in range(3) for c in range(3)]


def extract_arrays(model, device, arrays, bboxes, batch=32):
    crops = []
    for arr, bbox in zip(arrays, bboxes): crops.extend(fixed_grid_crops(arr, bbox))
    out = []
    for st in range(0, len(crops), batch):
        with torch.no_grad():
            out.append(model.global_pool(model.forward_features(m30.tensor_batch(crops[st:st + batch]).to(device))).flatten(1).cpu().numpy().astype(np.float32))
        if st % 1024 == 0: print(f"extract {min(st + batch, len(crops))}/{len(crops)}", flush=True)
    return np.vstack(out).reshape(len(arrays), 9, -1)


def make_pixel_cache():
    out_path = HERE / "pixel_aug_train_features.npz"
    if out_path.exists(): return np.load(out_path)["features"]
    image_map = m30.baseline.find_uwf_image_map()
    paths = [image_map[Path(p).name] for p in meta["train"]["paths"]]
    arrays = [m30.baseline.read_image(p) for p in paths]
    bboxes = [m30.baseline.retinal_bbox(a) for a in arrays]
    rng = np.random.default_rng(20260812)
    masked = []
    for arr, bbox in zip(arrays, bboxes):
        shape = "circle" if rng.random() < .5 else "rect"
        fraction = float(rng.uniform(.45, .80))
        direction = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)][int(rng.integers(0, 5))]
        masked.append(aperture(arr, bbox, shape, fraction, direction[0], direction[1]))
    model, dev = m30.load_model()
    feat = extract_arrays(model, dev, masked, bboxes)
    np.savez_compressed(out_path, features=feat)
    return feat


def eval_mask(name, n):
    return ab.eval_mask(name, n, 3)


def train(xtr, ytr, xv, yv, seed, use_pixel):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    model = ab.PoolNet(xtr.shape[-1], "attention").to(DEVICE)
    xt = torch.from_numpy(xtr).float().to(DEVICE); yt = torch.from_numpy(ytr).long().to(DEVICE); xvt = torch.from_numpy(xv).float().to(DEVICE)
    rng = np.random.default_rng(seed + 300000)
    opt = torch.optim.AdamW(model.parameters(), lr=1.5e-3, weight_decay=3e-4)
    best_state = None; best_score = -1; patience = 0
    for ep in range(180):
        if use_pixel:
            # Pixel-augmented rows are present in every epoch and token-level
            # masking remains active, so the two robustness mechanisms compose.
            xx = xtr
            yy = ytr
        else:
            xx = xtr[:len(ytr)]; yy = ytr
        mask = (rng.random((len(xx), 9)) > .30).astype(np.float32); empty = mask.sum(1) == 0; mask[empty, 4] = 1
        logits, _ = model(torch.from_numpy(xx).float().to(DEVICE), torch.from_numpy(mask).float().to(DEVICE)); loss = torch.nn.functional.cross_entropy(logits, torch.from_numpy(yy).long().to(DEVICE))
        opt.zero_grad(); loss.backward(); opt.step()
        with torch.no_grad():
            p = model(xvt, torch.ones((len(xv), 9), device=DEVICE))[0].argmax(1).cpu().numpy()
        score = f1_score(yv, p, average="macro", zero_division=0)
        if score > best_score: best_score = float(score); best_state = copy.deepcopy({k: v.detach().cpu() for k, v in model.state_dict().items()}); patience = 0
        else: patience += 1
        if patience >= 25: break
    model.load_state_dict(best_state); return model, best_score, ep + 1


def metrics(yy, prob):
    pred = prob.argmax(1)
    return {"accuracy": float(accuracy_score(yy, pred)), "macro_f1": float(f1_score(yy, pred, average="macro", zero_division=0)), "severity_mae": float(np.mean(np.abs(pred - yy))), "underestimation_rate": float(np.mean(pred < yy))}


def predict(model, xx, mask):
    model.eval()
    with torch.no_grad():
        p = torch.softmax(model(torch.from_numpy(xx).float().to(DEVICE), torch.from_numpy(mask).float().to(DEVICE))[0], 1).cpu().numpy()
    return p


def main():
    t0 = time.time()
    pixel_aug = make_pixel_cache()
    # Normalization uses source unmasked training moments only.
    pixel_aug = ((pixel_aug - mu) / sd).astype(np.float32)
    x_aug = np.concatenate([X["train"], pixel_aug], axis=0)
    y_aug = np.concatenate([y["train"], y["train"]], axis=0)
    image_map = m30.baseline.find_uwf_image_map()
    test_paths = [image_map[Path(p).name] for p in meta["test"]["paths"]]
    test_arr = [m30.baseline.read_image(p) for p in test_paths]
    test_bbox = [m30.baseline.retinal_bbox(a) for a in test_arr]
    pixel_scenarios = [("rect_center_0.35", "rect", .35, 0, 0), ("rect_center_0.55", "rect", .55, 0, 0), ("rect_center_0.75", "rect", .75, 0, 0), ("circle_center_0.55", "circle", .55, 0, 0)]
    encoder, enc_dev = m30.load_model()
    pixel_test = {}
    for name, shape, frac, dx, dy in pixel_scenarios:
        arrs = [aperture(a, b, shape, frac, dx, dy) for a, b in zip(test_arr, test_bbox)]
        pixel_test[name] = ((extract_arrays(encoder, enc_dev, arrs, test_bbox) - mu) / sd).astype(np.float32)
    results = {"experiment": "Exp60 pixel-space continuous aperture training", "seeds": list(SEEDS), "variants": {"baseline": {}, "pixel_augmented": {}}, "pixel_scenarios": [s[0] for s in pixel_scenarios]}
    for variant, train_x, train_y, use_pixel in (("baseline", X["train"], y["train"], False), ("pixel_augmented", x_aug, y_aug, True)):
        rows = []
        for seed in SEEDS:
            model, val_score, epochs = train(train_x, train_y, X["val"], y["val"], seed, use_pixel)
            row = {"seed": seed, "best_val_full_macro_f1": val_score, "epochs": epochs, "geometric": {}}
            for view in ("full", "center", "cross"):
                row["geometric"][view] = metrics(y["test"], predict(model, X["test"], eval_mask(view, len(y["test"]))))
            row["pixel"] = {name: metrics(y["test"], predict(model, xx, np.ones((len(y["test"]), 9), np.float32))) for name, xx in pixel_test.items()}
            rows.append(row)
        results["variants"][variant]["rows"] = rows
        results["variants"][variant]["aggregate"] = {}
        for group in ("geometric", "pixel"):
            keys = ("full", "center", "cross") if group == "geometric" else [s[0] for s in pixel_scenarios]
            results["variants"][variant]["aggregate"][group] = {}
            for key in keys:
                q = [r[group][key] for r in rows]
                results["variants"][variant]["aggregate"][group][key] = {k: {"mean": float(np.mean([v[k] for v in q])), "std": float(np.std([v[k] for v in q], ddof=1))} for k in q[0]}
    results["notes"] = ["Pixel augmentation uses one unlabeled geometric aperture per training image and re-extracts frozen RetinaRadar features.", "All apertures are geometric proxies; no real paired 45-degree acquisition is implied.", "The augmentation is promoted only if it improves the held-out pixel-space stress endpoints without worsening geometric underestimation."]
    results["elapsed_seconds"] = time.time() - t0
    (HERE / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    (HERE / "REPORT.md").write_text("# Exp60：连续像素视野增强训练\n\n" + json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(results["variants"], ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__": main()
