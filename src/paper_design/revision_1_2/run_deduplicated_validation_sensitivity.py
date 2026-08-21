#!/usr/bin/env python3
"""Sensitivity analysis for duplicate/conflicting validation-list entries.

The locked image-level test set and cached features are not changed.  For each
validation filename, one row is retained; when duplicate rows disagree, the
majority label is used (ties resolve to the more severe label).  The five
prespecified seeds are retrained with the corrected all-empty mask fallback to
the geometric centre token.  Outputs are written only under revision_1_2.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import random
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import f1_score


ROOT = Path("/Users/tongyue/Documents/77f /7hao")
HERE = ROOT / "paper_design/revision_1_2/deduplicated_validation_sensitivity"
CACHE = ROOT / "experiments/exp34_shared_uwf_region_cache"
HERE.mkdir(parents=True, exist_ok=True)

spec = importlib.util.spec_from_file_location("ab", ROOT / "experiments/exp35_region_mask_pool_ablation/run_ablation.py")
ab = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(ab)

meta = json.loads((CACHE / "split_meta.json").read_text())
z = np.load(CACHE / "region_features_g3.npz")
raw = {s: z[f"{s}_features"].astype(np.float32) for s in ("train", "val", "test")}
y = {s: np.asarray(meta[s]["y"], dtype=np.int64) for s in raw}
mu = raw["train"].reshape(-1, raw["train"].shape[-1]).mean(0)
sd = raw["train"].reshape(-1, raw["train"].shape[-1]).std(0)
sd[sd < 1e-8] = 1
X = {s: ((raw[s] - mu) / sd).astype(np.float32) for s in raw}


def deduplicate_validation():
    grouped = {}
    for idx, (name, label) in enumerate(zip(meta["val"]["paths"], y["val"])):
        grouped.setdefault(Path(name).name, []).append((idx, int(label)))
    keep, labels, conflicts = [], [], []
    for name, rows in grouped.items():
        counts = np.bincount([label for _, label in rows], minlength=3)
        label = int(np.flatnonzero(counts == counts.max())[-1])
        keep.append(rows[0][0])
        labels.append(label)
        if len(set(v for _, v in rows)) > 1:
            conflicts.append({"filename": name, "listed_labels": [v for _, v in rows], "resolved_label": label})
    order = np.argsort(keep)
    keep = np.asarray(keep, dtype=int)[order]
    labels = np.asarray(labels, dtype=np.int64)[order]
    return X["val"][keep], labels, grouped, conflicts


def train(xtr, ytr, xv, yv, seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    dev = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    model = ab.PoolNet(xtr.shape[-1], "attention").to(dev)
    xt = torch.from_numpy(xtr).float().to(dev)
    yt = torch.from_numpy(ytr).long().to(dev)
    xvt = torch.from_numpy(xv).float().to(dev)
    rng = np.random.default_rng(seed)
    opt = torch.optim.AdamW(model.parameters(), lr=1.5e-3, weight_decay=3e-4)
    best_state, best_score, patience = None, -1.0, 0
    for ep in range(180):
        mask = (rng.random((len(xtr), 9)) > 0.30).astype(np.float32)
        mask[mask.sum(1) == 0, 4] = 1.0
        logits, _ = model(xt, torch.from_numpy(mask).float().to(dev))
        loss = torch.nn.functional.cross_entropy(logits, yt)
        opt.zero_grad(); loss.backward(); opt.step()
        with torch.no_grad():
            pred = model(xvt, torch.ones((len(xv), 9), device=dev))[0].argmax(1).cpu().numpy()
        score = float(f1_score(yv, pred, average="macro", zero_division=0))
        if score > best_score:
            best_score = score
            best_state = copy.deepcopy({k: v.detach().cpu() for k, v in model.state_dict().items()})
            patience = 0
        else:
            patience += 1
        if patience >= 25:
            break
    model.load_state_dict(best_state)
    return model, dev, best_score, ep + 1


def aggregate(rows):
    out = {}
    for view in ("full", "center", "cross"):
        rr = [r[view] for r in rows]
        out[view] = {
            metric: {"mean": float(np.mean([q[metric] for q in rr])), "std": float(np.std([q[metric] for q in rr], ddof=1))}
            for metric in rr[0]
        }
    return out


def main():
    xv, yv, grouped, conflicts = deduplicate_validation()
    rows = []
    for seed in range(5):
        model, dev, val, epochs = train(X["train"], y["train"], xv, yv, seed)
        row = {"seed": seed, "best_deduplicated_val_full_macro_f1": val, "epochs": epochs}
        for view in ("full", "center", "cross"):
            row[view] = ab.evaluate(model, dev, X["test"], y["test"], ab.eval_mask(view, len(y["test"]), 3))
        rows.append(row)
        print(f"seed={seed} done", flush=True)
    result = {
        "purpose": "Sensitivity to duplicate/conflicting UWF-DR list entries used for early stopping",
        "original_validation_records": int(len(y["val"])),
        "unique_validation_filenames": int(len(grouped)),
        "duplicate_extra_rows_removed": int(len(y["val"]) - len(grouped)),
        "conflicting_validation_filenames": conflicts,
        "test_set_unchanged": True,
        "all_empty_mask_fallback": "geometric centre token (index 4)",
        "rows": rows,
        "aggregate": aggregate(rows),
    }
    (HERE / "results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    (HERE / "REPORT.md").write_text(
        "# Deduplicated-validation sensitivity\n\nThe original test set is unchanged. Duplicate validation filenames are retained once; conflicting labels use majority vote with severe-class tie-breaking.\n\n```json\n"
        + json.dumps(result, ensure_ascii=False, indent=2) + "\n```\n",
        encoding="utf-8",
    )
    print(json.dumps(result["aggregate"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
