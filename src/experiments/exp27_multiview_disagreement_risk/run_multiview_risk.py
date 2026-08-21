#!/usr/bin/env python3
"""Exp27: use multi-view prediction disagreement to predict underestimation."""
from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.model_selection import GroupKFold

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HERE.mkdir(parents=True, exist_ok=True)
BASE = ROOT / "7hao/experiments/exp01_quality_fov_baseline/run_baseline.py"
spec = importlib.util.spec_from_file_location("baseline", BASE)
baseline = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(baseline)


def crop_at(arr, fraction=.55, dx=0.0, dy=0.0):
    x0, y0, x1, y1, _ = baseline.retinal_bbox(arr)
    roi = arr[y0:y1, x0:x1]
    h, w = roi.shape[:2]
    ch, cw = max(8, int(h * fraction)), max(8, int(w * fraction))
    xx = int((w - cw) * (.5 + .35 * dx)); yy = int((h - ch) * (.5 + .35 * dy))
    xx, yy = max(0, min(w - cw, xx)), max(0, min(h - ch, yy))
    return roi[yy:yy + ch, xx:xx + cw]


def circle45(arr, ratio=45 / 200):
    x0, y0, x1, y1, _ = baseline.retinal_bbox(arr); roi = arr[y0:y1, x0:x1]
    h, w = roi.shape[:2]; r = max(8, int(min(h, w) * ratio)); cx, cy = w // 2, h // 2
    xa, xb, ya, yb = max(0, cx-r), min(w, cx+r), max(0, cy-r), min(h, cy+r)
    z = roi[ya:yb, xa:xb].copy(); yy, xx = np.ogrid[:z.shape[0], :z.shape[1]]
    mask = (xx - z.shape[1]/2.)**2 + (yy - z.shape[0]/2.)**2 <= r*r; z[~mask] = 0
    return z


VIEWS = ("full", "center", "circle45", "left", "right", "up", "down")


def make_view(arr, view):
    if view == "full": return arr
    if view == "center": return crop_at(arr, .55, 0, 0)
    if view == "circle45": return circle45(arr)
    return crop_at(arr, .55, {"left": -1, "right": 1, "up": 0, "down": 0}[view], {"left": 0, "right": 0, "up": -1, "down": 1}[view])


def extract(arrs, view):
    return np.vstack([baseline.feature_vector(make_view(a, view))[0] for a in arrs])


def fit_probe(X, y):
    Xz, _, mu, sd = baseline.standardize(X, [])
    return baseline.fit_multiclass(Xz, y), mu, sd


def predict_probe(model, X):
    W, mu, sd = model
    return baseline.predict_multi(W, (X - mu) / sd)


def entropy(p):
    return -np.sum(np.clip(p, 1e-8, 1) * np.log(np.clip(p, 1e-8, 1)), axis=1)


def risk_features(probs, quality=None, mode="multiview"):
    keys = list(VIEWS); A = np.stack([probs[k] for k in keys], axis=1)
    mean, sd, lo, hi = A.mean(1), A.std(1), A.min(1), A.max(1)
    ent, expected = entropy(A.reshape(-1, 3)).reshape(len(A), -1), A @ np.asarray([0., 1., 2.])
    center, full = probs["center"], probs["full"]
    gaps = np.c_[center - full, np.abs(center - full), expected[:, [0]] - expected[:, 1:], expected.std(1), expected.max(1) - expected.min(1)]
    # Average symmetric KL between full view and each restricted view.
    kl = []
    for k in keys[1:]:
        a, b = np.clip(probs["full"], 1e-8, 1), np.clip(probs[k], 1e-8, 1)
        kl.append(.5 * np.sum(a*np.log(a/b) + b*np.log(b/a), axis=1))
    base = np.c_[center, ent[:, 1], expected[:, 1], mean, sd, lo, hi, ent, expected, gaps, np.mean(np.vstack(kl), axis=0), np.max(np.vstack(kl), axis=0)]
    if mode == "central_uncertainty":
        base = np.c_[center, ent[:, 1], expected[:, 1], quality if quality is not None else np.zeros((len(A), 4))]
    elif mode == "multiview_disagreement":
        base = np.c_[mean, sd, lo, hi, ent, expected, gaps, np.mean(np.vstack(kl), axis=0), np.max(np.vstack(kl), axis=0)]
    elif mode == "multiview_plus_quality":
        base = np.c_[base, quality if quality is not None else np.zeros((len(A), 4))]
    return base


def standardize(Xtr, Xv, Xt):
    mu, sd = Xtr.mean(0), Xtr.std(0); sd[sd < 1e-8] = 1
    return (Xtr-mu)/sd, (Xv-mu)/sd, (Xt-mu)/sd


def metrics(y, p):
    return {"auroc": float(roc_auc_score(y, p)), "average_precision": float(average_precision_score(y, p)), "brier": float(brier_score_loss(y, p)), "positive_rate": float(y.mean())}


def quality_matrix(arrs):
    rows = []
    for a in arrs:
        _, m = baseline.feature_vector(crop_at(a, .55, 0, 0))
        rows.append([m["sharpness"], m["contrast"], m["brightness"], m["nonblack_coverage"]])
    return np.asarray(rows, dtype=float)


def main():
    mp = baseline.find_uwf_image_map(); records=[]
    for s in ("train", "val", "test"):
        p,y=baseline.read_split(s,mp); records.extend(zip(p,y.tolist()))
    splits=baseline.make_patient_level_splits(records,seed=42)
    arrays={s:[baseline.read_image(p) for p in splits[s]["paths"]] for s in splits}
    y={s:splits[s]["y"] for s in splits}
    X={v:{s:extract(arrays[s],v) for s in splits} for v in VIEWS}
    groups=np.asarray(splits["train"]["patient_keys"])
    # patient_keys is unique per split, so use the path-derived key for OOF.
    groups=np.asarray([baseline.patient_key(p) for p in splits["train"]["paths"]])
    oof={v:np.zeros((len(y["train"]),3)) for v in VIEWS}
    for tr,va in GroupKFold(n_splits=5).split(X["full"]["train"],y["train"],groups):
        for v in VIEWS:
            mdl=fit_probe(X[v]["train"][tr],y["train"][tr]); oof[v][va]=predict_probe(mdl,X[v]["train"][va])
    full_models={v:fit_probe(X[v]["train"],y["train"]) for v in VIEWS}
    probs={"train":oof,"val":{v:predict_probe(full_models[v],X[v]["val"]) for v in VIEWS},"test":{v:predict_probe(full_models[v],X[v]["test"]) for v in VIEWS}}
    quality={s:quality_matrix(arrays[s]) for s in splits}
    risk_y={s:(probs[s]["center"].argmax(1)<y[s]).astype(int) for s in splits}
    result={"dataset":{"n":len(records),"views":list(VIEWS),"split_counts":{s:np.bincount(y[s],minlength=3).tolist() for s in splits}},"models":{},"notes":["Training risk labels use patient-grouped out-of-fold view probes; validation/test view probes are fit only on the training split.","Multi-view disagreement features include probability spread, expected severity spread, entropy, full-vs-restricted gaps and symmetric KL divergence.","Views are geometric UWF proxies, not real same-eye camera pairs."]}
    csvrows=[]
    for mode in ("central_uncertainty","multiview_disagreement","multiview_plus_quality"):
        Ftr=risk_features(probs["train"],quality["train"],mode); Fv=risk_features(probs["val"],quality["val"],mode); Ft=risk_features(probs["test"],quality["test"],mode)
        Ftr,Fv,Ft=standardize(Ftr,Fv,Ft)
        clf=LogisticRegression(C=.1,class_weight="balanced",max_iter=1000,solver="liblinear",random_state=42); clf.fit(Ftr,risk_y["train"])
        pval=clf.predict_proba(Fv)[:,1]; ptest=clf.predict_proba(Ft)[:,1]
        result["models"][mode]={"n_features":int(Ftr.shape[1]),"val":metrics(risk_y["val"],pval),"test":metrics(risk_y["test"],ptest)}
        for s,sc in (("val",pval),("test",ptest)):
            for i,pth in enumerate(splits[s]["paths"]): csvrows.append([s,mode,pth.name,int(y[s][i]),int(risk_y[s][i]),float(sc[i])])
    with (HERE/"risk_predictions.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(["split","model","image","severity","risk_target","risk_score"]); w.writerows(csvrows)
    (HERE/"results.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    (HERE/"REPORT.md").write_text("# Exp27：多视野分歧低估风险\n\n使用完整、中心、圆形和四个偏移视野的预测概率、熵、严重度跨度、完整-局部差异和KL分歧预测中心视野低估风险。\n\n```json\n"+json.dumps(result,ensure_ascii=False,indent=2)+"\n```\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
