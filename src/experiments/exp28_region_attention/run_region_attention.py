#!/usr/bin/env python3
"""Exp28: region-bank attention for evidence coverage analysis."""
from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path

import numpy as np
import torch
from torch import nn

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HERE.mkdir(parents=True, exist_ok=True)
BASE = ROOT / "7hao/experiments/exp01_quality_fov_baseline/run_baseline.py"
spec = importlib.util.spec_from_file_location("baseline", BASE)
baseline = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(baseline)


def regions(arr):
    x0, y0, x1, y1, _ = baseline.retinal_bbox(arr)
    roi = arr[y0:y1, x0:x1]
    h, w = roi.shape[:2]
    out = []
    for r in range(3):
        for c in range(3):
            ya, yb = int(r*h/3), int((r+1)*h/3)
            xa, xb = int(c*w/3), int((c+1)*w/3)
            out.append(baseline.feature_vector(roi[ya:yb, xa:xb])[0])
    return np.vstack(out)


def extract(arrs):
    return np.stack([regions(a) for a in arrs]).astype(np.float32)


class AttentionMIL(nn.Module):
    def __init__(self, fdim, hidden=48):
        super().__init__()
        self.embed = nn.Sequential(nn.Linear(fdim, hidden), nn.LayerNorm(hidden), nn.ReLU())
        self.att = nn.Sequential(nn.Linear(hidden, 24), nn.Tanh(), nn.Linear(24, 1))
        self.cls = nn.Linear(hidden, 3)

    def forward(self, x, mask):
        h = self.embed(x)
        logits = self.att(h).squeeze(-1)
        logits = logits.masked_fill(mask <= 0, -1e4)
        a = torch.softmax(logits, dim=1)
        pooled = (a.unsqueeze(-1) * h).sum(1)
        return self.cls(pooled), a


class MeanMIL(nn.Module):
    def __init__(self, fdim):
        super().__init__(); self.cls = nn.Linear(fdim, 3)

    def forward(self, x, mask):
        z = (x * mask.unsqueeze(-1)).sum(1) / mask.sum(1, keepdim=True).clamp_min(1)
        return self.cls(z), mask / mask.sum(1, keepdim=True).clamp_min(1)


def masks_for(name, n):
    base = np.ones((n, 9), dtype=np.float32)
    if name == "full": return base
    if name == "center":
        base[:] = 0; base[:, 4] = 1; return base
    if name == "center_plus_cross":
        base[:] = 0; base[:, [1, 3, 4, 5, 7]] = 1; return base
    if name == "left_half":
        base[:] = 0; base[:, [0, 3, 6, 1, 4, 7]] = 1; return base
    if name == "right_half":
        base[:] = 0; base[:, [1, 2, 4, 5, 7, 8]] = 1; return base
    if name == "top_half":
        base[:] = 0; base[:, [0, 1, 2, 3, 4, 5]] = 1; return base
    if name == "bottom_half":
        base[:] = 0; base[:, [3, 4, 5, 6, 7, 8]] = 1; return base
    raise ValueError(name)


def random_mask(n, p=.30, rng=None):
    rng = rng or np.random.default_rng(42); m = (rng.random((n, 9)) > p).astype(np.float32)
    for i in range(n):
        if not m[i].any(): m[i, 4] = 1
    return m


def train_model(model, X, y, augmented=False, seed=42):
    torch.manual_seed(seed); rng = np.random.default_rng(seed); device = torch.device("cpu")
    model.to(device); xt = torch.from_numpy(X).float(); yt = torch.from_numpy(y).long(); opt = torch.optim.AdamW(model.parameters(), lr=2e-3, weight_decay=2e-4)
    for epoch in range(320):
        mask = random_mask(len(X), .30, rng) if augmented else np.ones((len(X), 9), np.float32)
        mt = torch.from_numpy(mask).float()
        logits, _ = model(xt, mt); loss = nn.functional.cross_entropy(logits, yt)
        opt.zero_grad(); loss.backward(); opt.step()
    return model


def eval_model(model, X, y, mask_name):
    mask = torch.from_numpy(masks_for(mask_name, len(X))).float()
    with torch.no_grad(): logits, att = model(torch.from_numpy(X).float(), mask)
    p = torch.softmax(logits, 1).numpy(); pred = p.argmax(1)
    return {"accuracy": float(np.mean(pred == y)), "macro_f1": baseline.macro_f1(y, pred), "severity_mae": float(np.mean(abs(pred-y))), "underestimation_rate": float(np.mean(pred<y))}, p, att.numpy()


def main():
    mp=baseline.find_uwf_image_map(); records=[]
    for s in ("train","val","test"):
        p,y=baseline.read_split(s,mp); records.extend(zip(p,y.tolist()))
    splits=baseline.make_patient_level_splits(records,seed=42); arrays={s:[baseline.read_image(p) for p in splits[s]["paths"]] for s in splits}; ys={s:splits[s]["y"] for s in splits}
    raw={s:extract(arrays[s]) for s in splits}; mu=raw["train"].reshape(-1,raw["train"].shape[-1]).mean(0); sd=raw["train"].reshape(-1,raw["train"].shape[-1]).std(0); sd[sd<1e-8]=1
    X={s:(raw[s]-mu)/sd for s in splits}; fdim=X["train"].shape[-1]
    result={"dataset":{"n":len(records),"regions":9,"region_layout":"3x3 retinal bounding-box tiles","split_counts":{s:np.bincount(ys[s],minlength=3).tolist() for s in splits}},"models":{},"attention_summary":{},"notes":["The region bank is a geometric 3x3 partition of the retinal bounding box; it is an evidence-localization proxy, not lesion-level annotation.","Attention-mask-augmented training randomly hides 30% of regions during training and keeps the center tile if all regions would be hidden.","Features are 67-dimensional image statistics; this is a low-cost proof-of-concept before replacing the region encoder with a deep frozen encoder."]}
    rows=[]
    for name,augmented in (("attention_full_only",False),("attention_mask_augmented",True),("mean_pool_baseline",False)):
        model=MeanMIL(fdim) if name.startswith("mean") else AttentionMIL(fdim)
        model=train_model(model,X["train"],ys["train"],augmented=augmented,seed=42)
        result["models"][name]={}
        for view in ("full","center","center_plus_cross","left_half","right_half","top_half","bottom_half"):
            met,p,a=eval_model(model,X["test"],ys["test"],view); result["models"][name][view]=met
            if view=="full":
                for i in range(len(ys["test"])):
                    rows.append([name,splits["test"]["paths"][i].name,int(ys["test"][i]),int(p[i].argmax()),*a[i].tolist()])
        # Validation is reported for model selection transparency.
        met,_,_=eval_model(model,X["val"],ys["val"],"full"); result["models"][name]["val_full"]=met
    with (HERE/"attention_test.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(["model","image","true_label","pred_label"]+[f"attention_region_{i}" for i in range(9)]); w.writerows(rows)
    # Attention averages by true severity for the mask-augmented model.
    aug_rows=[r for r in rows if r[0]=="attention_mask_augmented"]
    if aug_rows:
        aa=np.asarray([r[4:13] for r in aug_rows],float); yy=np.asarray([r[2] for r in aug_rows],int)
        result["attention_summary"]={"overall_mean_attention":aa.mean(0).tolist(),"by_severity":{str(c):aa[yy==c].mean(0).tolist() for c in (0,1,2)}}
    (HERE/"results.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    (HERE/"REPORT.md").write_text("# Exp28：区域证据注意力与视野覆盖\n\n把UWF视网膜包围盒划分为3×3区域，使用注意力池化判断不同区域对严重度预测的贡献，并在中心/半视野遮罩下评估证据缺失。\n\n```json\n"+json.dumps(result,ensure_ascii=False,indent=2)+"\n```\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
