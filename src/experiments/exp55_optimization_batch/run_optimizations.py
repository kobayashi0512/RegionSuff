#!/usr/bin/env python3
"""Exp55+: controlled optimization batch for RegionSufficiency.

This file deliberately creates a new experiment family.  It never edits Exp01--Exp54.
All variants use the frozen g3 feature cache, the original patient-grouped split,
the same optimizer budget, and five seeds.  A second checkpoint-selection rule is
reported because the manuscript registry and the historical training code used
different validation masks.
"""
from __future__ import annotations

import copy
import json
import math
import random
import time
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import accuracy_score, f1_score, recall_score
from torch import nn


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CACHE = ROOT / "7hao/experiments/exp34_shared_uwf_region_cache"
HERE.mkdir(parents=True, exist_ok=True)

SEEDS = (0, 1, 2, 3, 4)
VIEWS = ("full", "center", "cross")
DEVICE = torch.device("mps" if torch.backends.mps.is_available() else "cpu")


def read_inputs():
    meta = json.loads((CACHE / "split_meta.json").read_text())
    y = {s: np.asarray(meta[s]["y"], dtype=np.int64) for s in ("train", "val", "test")}
    z = np.load(CACHE / "region_features_g3.npz")
    raw = {s: z[f"{s}_features"].astype(np.float32) for s in y}
    mu = raw["train"].reshape(-1, raw["train"].shape[-1]).mean(0)
    sd = raw["train"].reshape(-1, raw["train"].shape[-1]).std(0)
    sd[sd < 1e-8] = 1.0
    x = {s: ((raw[s] - mu) / sd).astype(np.float32) for s in y}
    return meta, y, x


def view_mask(name: str, n: int, g: int = 3) -> np.ndarray:
    m = np.ones((n, g * g), dtype=np.float32)
    if name == "full":
        return m
    m[:] = 0
    center = (g - 1) / 2
    for r in range(g):
        for c in range(g):
            if name == "center" and abs(r - center) <= 0.51 and abs(c - center) <= 0.51:
                m[:, r * g + c] = 1
            if name == "cross" and (abs(r - center) <= 0.51 or abs(c - center) <= 0.51):
                m[:, r * g + c] = 1
    return m


def random_bernoulli(n: int, r: int, ratio: float, rng: np.random.Generator) -> np.ndarray:
    m = (rng.random((n, r)) > ratio).astype(np.float32)
    empty = m.sum(1) == 0
    m[empty, 4] = 1
    return m


def random_connected(n: int, ratio: float, rng: np.random.Generator) -> np.ndarray:
    """Remove a connected local block/line, while retaining at least one token.

    This is a region-space proxy for contiguous acquisition loss.  It is not
    presented as a physical camera model.
    """
    out = np.ones((n, 9), dtype=np.float32)
    for i in range(n):
        # The nominal removed area is close to the Bernoulli ratio, but the
        # connected shapes are intentionally discrete on the 3x3 bank.
        u = rng.random()
        if u < 0.50:
            r, c = int(rng.integers(0, 3)), int(rng.integers(0, 0 + 3))
            out[i, r * 3 + c] = 0
            # Extend from a seed along a random cardinal direction.
            if rng.random() < 0.75:
                dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                dr, dc = dirs[int(rng.integers(0, len(dirs)))]
                rr, cc = r + dr, c + dc
                if 0 <= rr < 3 and 0 <= cc < 3:
                    out[i, rr * 3 + cc] = 0
        elif u < 0.80:
            r = int(rng.integers(0, 2)); c = int(rng.integers(0, 2))
            out[i, r * 3 + c] = 0
            out[i, (r + 1) * 3 + c] = 0
        else:
            # Random row/column removal exposes the head to field-edge loss.
            if rng.random() < 0.5:
                r = int(rng.integers(0, 3))
                out[i, r * 3 : r * 3 + 3] = 0
            else:
                c = int(rng.integers(0, 3)); out[i, c::3] = 0
        if out[i].sum() == 0:
            out[i, 4] = 1
    return out


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


class RegionNet(nn.Module):
    def __init__(self, feature_dim: int, variant: str):
        super().__init__()
        self.variant = variant
        self.use_coord = variant in {"coord", "coord_connected", "coord_connected_under"}
        in_dim = feature_dim + (8 if self.use_coord else 0)
        self.embed = nn.Sequential(nn.Linear(in_dim, 128), nn.LayerNorm(128), nn.ReLU())
        self.att = nn.Sequential(nn.Linear(128, 48), nn.Tanh(), nn.Linear(48, 1))
        self.cls = nn.Linear(128, 3)
        if self.use_coord:
            coords = []
            for r in range(3):
                for c in range(3):
                    coords.append((2 * r / 2 - 1, 2 * c / 2 - 1))
            coords = torch.tensor(coords, dtype=torch.float32)
            self.register_buffer("coords", coords)
            self.coord_proj = nn.Sequential(nn.Linear(2, 8), nn.Tanh())

    def forward(self, x: torch.Tensor, mask: torch.Tensor):
        if self.use_coord:
            ce = self.coord_proj(self.coords).unsqueeze(0).expand(x.shape[0], -1, -1)
            x = torch.cat([x, ce], dim=-1)
        h = self.embed(x)
        score = self.att(h).squeeze(-1).masked_fill(mask <= 0, -1e4)
        weight = torch.softmax(score, dim=1)
        z = (weight.unsqueeze(-1) * h).sum(1)
        return self.cls(z), weight


def train_one(xtr, ytr, xval, yval, variant: str, seed: int):
    set_seed(seed)
    rng = np.random.default_rng(seed + 100_000)
    model = RegionNet(xtr.shape[-1], variant).to(DEVICE)
    xt = torch.from_numpy(xtr).float().to(DEVICE)
    yt = torch.from_numpy(ytr).long().to(DEVICE)
    xv = torch.from_numpy(xval).float().to(DEVICE)
    opt = torch.optim.AdamW(model.parameters(), lr=1.5e-3, weight_decay=3e-4)
    best = {"full": None, "cross": None}
    best_score = {"full": -1.0, "cross": -1.0}
    patience = {"full": 0, "cross": 0}
    last_epoch = 0

    for ep in range(180):
        last_epoch = ep + 1
        if variant in {"coord_connected", "coord_connected_under"}:
            mask_np = random_connected(len(xtr), 0.30, rng)
        else:
            mask_np = random_bernoulli(len(xtr), 9, 0.30, rng)
        mask = torch.from_numpy(mask_np).float().to(DEVICE)
        logits, _ = model(xt, mask)
        loss = nn.functional.cross_entropy(logits, yt)
        if variant == "coord_connected_under":
            prob = torch.softmax(logits, dim=1)
            expected = (prob * torch.arange(3, device=DEVICE).float()).sum(1)
            # A soft penalty discourages severe underestimation while allowing
            # the classifier to trade off false over-calls in a measurable way.
            loss = loss + 0.20 * torch.relu(yt.float() - expected).pow(2).mean()
        opt.zero_grad(); loss.backward(); opt.step()

        with torch.no_grad():
            pred_full = model(xv, torch.from_numpy(view_mask("full", len(xval))).float().to(DEVICE))[0].argmax(1).cpu().numpy()
            pred_cross = model(xv, torch.from_numpy(view_mask("cross", len(xval))).float().to(DEVICE))[0].argmax(1).cpu().numpy()
        scores = {
            "full": f1_score(yval, pred_full, average="macro", zero_division=0),
            "cross": f1_score(yval, pred_cross, average="macro", zero_division=0),
        }
        for criterion in ("full", "cross"):
            if scores[criterion] > best_score[criterion]:
                best_score[criterion] = float(scores[criterion])
                best[criterion] = copy.deepcopy({k: v.detach().cpu() for k, v in model.state_dict().items()})
                patience[criterion] = 0
            else:
                patience[criterion] += 1
        if min(patience.values()) >= 25:
            break
    return model, best, best_score, last_epoch


def metric_dict(y, prob):
    pred = prob.argmax(1)
    return {
        "accuracy": float(accuracy_score(y, pred)),
        "macro_f1": float(f1_score(y, pred, average="macro", zero_division=0)),
        "severity_mae": float(np.mean(np.abs(pred - y))),
        "underestimation_rate": float(np.mean(pred < y)),
        "normal_recall": float(recall_score(y, pred, labels=[0], average=None, zero_division=0)[0]),
        "npdr_recall": float(recall_score(y, pred, labels=[1], average=None, zero_division=0)[0]),
        "pdr_recall": float(recall_score(y, pred, labels=[2], average=None, zero_division=0)[0]),
    }


def predict(model, state, x, mask):
    model.load_state_dict(state)
    model.eval()
    with torch.no_grad():
        logits, weight = model(torch.from_numpy(x).float().to(DEVICE), torch.from_numpy(mask).float().to(DEVICE))
        prob = torch.softmax(logits, 1).cpu().numpy()
        weight = weight.cpu().numpy()
    return prob, weight


def paired_bootstrap(y, a, b, n_boot=1000, seed=20260812):
    rng = np.random.default_rng(seed)
    n = len(y)
    values = {"macro_f1": [], "severity_mae": [], "underestimation_rate": []}
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        ma = metric_dict(y[idx], a[idx]); mb = metric_dict(y[idx], b[idx])
        for k in values:
            values[k].append(mb[k] - ma[k])
    return {k: {"mean": float(np.mean(v)), "ci95": [float(np.quantile(v, .025)), float(np.quantile(v, .975))]} for k, v in values.items()}


def main():
    t0 = time.time()
    _, y, x = read_inputs()
    variants = ("baseline", "coord", "coord_connected", "coord_connected_under")
    all_rows = []
    aggregate = {}
    predictions = {}
    print(f"device={DEVICE}; n_train={len(y['train'])}; n_val={len(y['val'])}; n_test={len(y['test'])}", flush=True)

    for variant in variants:
        aggregate[variant] = {}
        for criterion in ("full", "cross"):
            aggregate[variant][criterion] = {}
        predictions[variant] = {}
        for seed in SEEDS:
            print(f"START variant={variant} seed={seed}", flush=True)
            _, best, best_score, epochs = train_one(x["train"], y["train"], x["val"], y["val"], variant, seed)
            for criterion in ("full", "cross"):
                model = RegionNet(x["train"].shape[-1], variant).to(DEVICE)
                predictions[variant][f"{criterion}_{seed}"] = {}
                for view in VIEWS:
                    prob, weight = predict(model, best[criterion], x["test"], view_mask(view, len(y["test"])))
                    predictions[variant][f"{criterion}_{seed}"][view] = prob.tolist()
                    row = {
                        "variant": variant, "criterion": criterion, "seed": seed,
                        "view": view, "best_val_score": best_score[criterion], "epochs": epochs,
                        **metric_dict(y["test"], prob),
                    }
                    all_rows.append(row)
                    aggregate[variant][criterion].setdefault(view, []).append(row)
            print(f"DONE variant={variant} seed={seed} epochs={epochs} val_full={best_score['full']:.4f} val_cross={best_score['cross']:.4f}", flush=True)

    agg_out = {}
    for variant in aggregate:
        agg_out[variant] = {}
        for criterion in aggregate[variant]:
            agg_out[variant][criterion] = {}
            for view, rows in aggregate[variant][criterion].items():
                keys = ("accuracy", "macro_f1", "severity_mae", "underestimation_rate", "normal_recall", "npdr_recall", "pdr_recall")
                agg_out[variant][criterion][view] = {k: {"mean": float(np.mean([r[k] for r in rows])), "std": float(np.std([r[k] for r in rows], ddof=1))} for k in keys}

    # Paired test comparison against the baseline trained under the same
    # selection criterion and seed.  Positive macro-F1 and negative MAE/risk
    # are improvements.
    paired = {}
    for variant in variants[1:]:
        paired[variant] = {}
        for criterion in ("full", "cross"):
            paired[variant][criterion] = {}
            for view in VIEWS:
                paired[variant][criterion][view] = {}
                for seed in SEEDS:
                    key = f"{criterion}_{seed}"
                    a = np.asarray(predictions["baseline"][key][view], dtype=np.float32)
                    b = np.asarray(predictions[variant][key][view], dtype=np.float32)
                    paired[variant][criterion][view][str(seed)] = paired_bootstrap(y["test"], a, b)

    result = {
        "experiment": "Exp55-58 controlled optimization batch",
        "dataset": {"development": 1630, "split": "reused patient-grouped UWF split", "test_n": int(len(y["test"]))},
        "device": str(DEVICE), "seeds": list(SEEDS), "variants": list(variants),
        "variant_definitions": {
            "baseline": "original 3x3 masked attention, Bernoulli region removal p=0.30",
            "coord": "baseline plus learnable 2D region-coordinate embedding",
            "coord_connected": "coordinate embedding plus connected region-loss masks",
            "coord_connected_under": "coord_connected plus soft underestimation penalty lambda=0.20",
        },
        "selection_criteria": "validation macro-F1 under full or center-plus-cross mask; both are reported",
        "aggregate": agg_out, "paired_vs_baseline": paired, "rows": all_rows,
        "notes": [
            "No original Exp01-Exp54 result was overwritten.",
            "All synthetic masks are geometric proxies, not real paired acquisitions.",
            "Paired bootstrap uses the same held-out images for each compared model.",
            "A variant is eligible for manuscript insertion only if its cross-view macro-F1 improves with a CI excluding zero and does not worsen MAE or underestimation in the prespecified direction.",
        ],
        "elapsed_seconds": time.time() - t0,
    }
    (HERE / "results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    report = [
        "# Exp55–Exp58：RegionSufficiency 优化实验批次",
        "",
        "本批次在新的实验目录中测试位置编码、连通视野遮罩和低估惩罚。只有 paired bootstrap 的主要终点明确改善且安全指标不恶化的变体才进入论文。",
        "",
        "```json",
        json.dumps({"aggregate": agg_out, "paired_vs_baseline": paired}, ensure_ascii=False, indent=2),
        "```",
    ]
    (HERE / "REPORT.md").write_text("\n".join(report), encoding="utf-8")
    print(json.dumps(agg_out, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
