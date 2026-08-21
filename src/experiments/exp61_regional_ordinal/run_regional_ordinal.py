#!/usr/bin/env python3
"""Exp61: ordinal regional attention heads.

This tests whether the Normal < NPDR < PDR ordering improves the regional
model's MAE and underestimation rate without sacrificing macro-F1.  The
comparison uses the same source cache, patient split, masks, five seeds and
validation selection as Exp55.
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
from torch import nn

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CACHE = ROOT / "7hao/experiments/exp34_shared_uwf_region_cache"
HERE.mkdir(parents=True, exist_ok=True)
SEEDS = (0, 1, 2, 3, 4)
DEVICE = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

sp = importlib.util.spec_from_file_location("ab", ROOT / "7hao/experiments/exp35_region_mask_pool_ablation/run_ablation.py")
ab = importlib.util.module_from_spec(sp); assert sp.loader; sp.loader.exec_module(ab)
meta = json.loads((CACHE / "split_meta.json").read_text())
y = {s: np.asarray(meta[s]["y"], dtype=np.int64) for s in ("train", "val", "test")}
z = np.load(CACHE / "region_features_g3.npz")
raw = {s: z[f"{s}_features"].astype(np.float32) for s in y}
mu = raw["train"].reshape(-1, raw["train"].shape[-1]).mean(0)
sd = raw["train"].reshape(-1, raw["train"].shape[-1]).std(0); sd[sd < 1e-8] = 1
X = {s: ((raw[s] - mu) / sd).astype(np.float32) for s in y}


class OrdinalNet(nn.Module):
    def __init__(self, feature_dim):
        super().__init__()
        self.e = nn.Sequential(nn.Linear(feature_dim, 128), nn.LayerNorm(128), nn.ReLU())
        self.a = nn.Sequential(nn.Linear(128, 48), nn.Tanh(), nn.Linear(48, 1))
        self.c = nn.Linear(128, 2)

    def forward(self, x, mask):
        h = self.e(x); s = self.a(h).squeeze(-1).masked_fill(mask <= 0, -1e4); w = torch.softmax(s, 1); z = (w.unsqueeze(-1) * h).sum(1)
        return self.c(z), w


def decode(logits):
    # logits represent P(y>0) and P(y>1); thresholding then clips invalid
    # cumulative combinations to the valid 0/1/2 ordinal label set.
    q = torch.sigmoid(logits)
    return (q > .5).sum(1)


def train_one(seed, under_penalty):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    rng = np.random.default_rng(seed + 500000)
    model = OrdinalNet(X["train"].shape[-1]).to(DEVICE)
    xt = torch.from_numpy(X["train"]).float().to(DEVICE); yt = torch.from_numpy(y["train"]).long().to(DEVICE); xv = torch.from_numpy(X["val"]).float().to(DEVICE)
    targets = torch.stack([(yt > 0).float(), (yt > 1).float()], 1)
    opt = torch.optim.AdamW(model.parameters(), lr=1.5e-3, weight_decay=3e-4)
    best_state = None; best_score = -1; patience = 0
    for ep in range(180):
        mask_np = (rng.random((len(yt), 9)) > .30).astype(np.float32); empty = mask_np.sum(1) == 0; mask_np[empty, 4] = 1
        logits, _ = model(xt, torch.from_numpy(mask_np).float().to(DEVICE))
        loss = nn.functional.binary_cross_entropy_with_logits(logits, targets)
        if under_penalty:
            prob = torch.sigmoid(logits)
            expected = prob.sum(1)
            loss = loss + .20 * torch.relu(yt.float() - expected).pow(2).mean()
        opt.zero_grad(); loss.backward(); opt.step()
        with torch.no_grad():
            val_logits, _ = model(xv, torch.ones((len(xv), 9), device=DEVICE)); pred = decode(val_logits).cpu().numpy()
        score = f1_score(y["val"], pred, average="macro", zero_division=0)
        if score > best_score:
            best_score = float(score); best_state = copy.deepcopy({k: v.detach().cpu() for k, v in model.state_dict().items()}); patience = 0
        else: patience += 1
        if patience >= 25: break
    model.load_state_dict(best_state); return model, best_score, ep + 1


def masks(name, n): return ab.eval_mask(name, n, 3)


def metrics(yy, p):
    pred = p.argmax(1)
    return {"accuracy": float(accuracy_score(yy, pred)), "macro_f1": float(f1_score(yy, pred, average="macro", zero_division=0)), "severity_mae": float(np.mean(np.abs(pred - yy))), "underestimation_rate": float(np.mean(pred < yy))}


def train_baseline_cross(seed):
    """Reproduce Exp55 baseline while retaining the cross-selected state."""
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    rng = np.random.default_rng(seed + 100000)
    model = ab.PoolNet(X["train"].shape[-1], "attention").to(DEVICE)
    xt = torch.from_numpy(X["train"]).float().to(DEVICE); yt = torch.from_numpy(y["train"]).long().to(DEVICE); xv = torch.from_numpy(X["val"]).float().to(DEVICE)
    opt = torch.optim.AdamW(model.parameters(), lr=1.5e-3, weight_decay=3e-4)
    best_state = None; best_score = -1.0; patience = 0
    for ep in range(180):
        mask_np = (rng.random((len(y["train"]), 9)) > .30).astype(np.float32); empty = mask_np.sum(1) == 0; mask_np[empty, 4] = 1
        logits, _ = model(xt, torch.from_numpy(mask_np).float().to(DEVICE)); loss = nn.functional.cross_entropy(logits, yt)
        opt.zero_grad(); loss.backward(); opt.step()
        with torch.no_grad():
            pred = model(xv, torch.from_numpy(masks("cross", len(y["val"]))).float().to(DEVICE))[0].argmax(1).cpu().numpy()
        score = f1_score(y["val"], pred, average="macro", zero_division=0)
        if score > best_score:
            best_score = float(score); best_state = copy.deepcopy({k: v.detach().cpu() for k, v in model.state_dict().items()}); patience = 0
        else:
            patience += 1
        if patience >= 25: break
    model.load_state_dict(best_state); return model


def main():
    t0 = time.time(); results = {"experiment": "Exp61 regional ordinal attention", "variants": {}, "seeds": list(SEEDS)}
    for name, under in (("ordinal", False), ("ordinal_under", True)):
        rows = []; pred_store = {}
        for seed in SEEDS:
            model, val_score, epochs = train_one(seed, under)
            row = {"seed": seed, "best_val_macro_f1": val_score, "epochs": epochs, "views": {}}
            for view in ("full", "center", "cross"):
                with torch.no_grad():
                    logits, _ = model(torch.from_numpy(X["test"]).float().to(DEVICE), torch.from_numpy(masks(view, len(y["test"]))).float().to(DEVICE))
                    p = torch.sigmoid(logits).cpu().numpy(); pred = (p > .5).sum(1)
                probs = np.zeros((len(pred), 3), np.float32)
                probs[:, 0] = 1 - p[:, 0]; probs[:, 1] = p[:, 0] - p[:, 1]; probs[:, 2] = p[:, 1]
                probs = np.clip(probs, 1e-6, 1); probs /= probs.sum(1, keepdims=True)
                pred_store[f"{view}_{seed}"] = probs.tolist(); row["views"][view] = metrics(y["test"], probs)
            rows.append(row)
        results["variants"][name] = {"rows": rows, "aggregate": {}}
        for view in ("full", "center", "cross"):
            q = [r["views"][view] for r in rows]
            results["variants"][name]["aggregate"][view] = {k: {"mean": float(np.mean([v[k] for v in q])), "std": float(np.std([v[k] for v in q], ddof=1))} for k in q[0]}
        results["variants"][name]["predictions"] = pred_store
    # Reproduce a fresh cross-selected baseline so the paired comparison does
    # not depend on a missing cache field or on a different checkpoint rule.
    base_probs = {}
    for seed in SEEDS:
        model = train_baseline_cross(seed)
        base_probs[f"cross_{seed}"] = {}
        for view in ("full", "center", "cross"):
            with torch.no_grad():
                logits, _ = model(torch.from_numpy(X["test"]).float().to(DEVICE), torch.from_numpy(masks(view, len(y["test"]))).float().to(DEVICE))
                probs = torch.softmax(logits, 1).cpu().numpy()
            base_probs[f"cross_{seed}"][view] = probs.tolist()
    rng = np.random.default_rng(20260812)
    paired = {}
    for name in ("ordinal", "ordinal_under"):
        paired[name] = {}
        for view in ("full", "center", "cross"):
            paired[name][view] = {}
            for seed in SEEDS:
                a = np.asarray(base_probs[f"cross_{seed}"][view]); b = np.asarray(results["variants"][name]["predictions"][f"{view}_{seed}"])
                vals = {k: [] for k in ("macro_f1", "severity_mae", "underestimation_rate")}
                for _ in range(1000):
                    idx = rng.integers(0, len(y["test"]), len(y["test"])); ma = metrics(y["test"][idx], a[idx]); mb = metrics(y["test"][idx], b[idx])
                    for k in vals: vals[k].append(mb[k] - ma[k])
                paired[name][view][str(seed)] = {k: {"mean": float(np.mean(v)), "ci95": [float(np.quantile(v, .025)), float(np.quantile(v, .975))]} for k, v in vals.items()}
    results["paired_vs_exp55_cross_selection_baseline"] = paired
    results["notes"] = ["Ordinal outputs encode P(y>0) and P(y>1).", "Only validation macro-F1 selects checkpoints; the held-out test is used once.", "Candidate is promoted only if cross-view macro-F1 and safety metrics improve with reproducible paired evidence."]
    results["elapsed_seconds"] = time.time() - t0
    # Do not save predictions to the main report after the comparison; they
    # remain in results.json to make the audit reproducible.
    (HERE / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    (HERE / "REPORT.md").write_text("# Exp61：区域严重度 ordinal head\n\n" + json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"aggregate": {k: v["aggregate"] for k, v in results["variants"].items()}, "paired": paired}, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__": main()
