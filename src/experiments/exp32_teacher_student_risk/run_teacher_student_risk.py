#!/usr/bin/env python3
"""Exp32: teacher-student evidence gap risk head on deep region features."""
from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HERE.mkdir(parents=True, exist_ok=True)
M30_PATH = ROOT / "7hao/experiments/exp30_deep_region_attention/run_deep_region_attention.py"
spec = importlib.util.spec_from_file_location("m30", M30_PATH)
m30 = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(m30)
baseline = m30.baseline


def predict_pair(model, X, y, device):
    import torch
    x = torch.from_numpy(X).float().to(device)
    full_mask = torch.from_numpy(m30.mask_named("full", len(X))).float().to(device)
    partial_mask = torch.from_numpy(m30.mask_named("center_plus_cross", len(X))).float().to(device)
    with torch.no_grad():
        lf, af = model(x, full_mask); lp, ap = model(x, partial_mask)
        pf, pp = torch.softmax(lf, 1).cpu().numpy(), torch.softmax(lp, 1).cpu().numpy()
        af, ap = af.cpu().numpy(), ap.cpu().numpy()
    ef, ep = pf @ np.asarray([0., 1., 2.]), pp @ np.asarray([0., 1., 2.])
    entf = -np.sum(np.clip(pf, 1e-8, 1)*np.log(np.clip(pf, 1e-8, 1)), 1)
    entp = -np.sum(np.clip(pp, 1e-8, 1)*np.log(np.clip(pp, 1e-8, 1)), 1)
    kl = .5*np.sum(np.clip(pf,1e-8,1)*np.log(np.clip(pf,1e-8,1)/np.clip(pp,1e-8,1)) + np.clip(pp,1e-8,1)*np.log(np.clip(pp,1e-8,1)/np.clip(pf,1e-8,1)), 1)
    visible = np.asarray([1,3,4,5,7])
    missing = 1. - af[:, visible].sum(1)
    F = np.c_[pf, pp, pf-pp, np.abs(pf-pp), ef, ep, ef-ep, entf, entp, kl, missing]
    risk = (pp.argmax(1) < y).astype(int)
    return F, risk, {"full_probs":pf,"partial_probs":pp,"expected_gap":ef-ep,"kl":kl,"missing_attention":missing}


def metric(y, p, probabilistic=False):
    out = {"auroc":float(roc_auc_score(y,p)),"average_precision":float(average_precision_score(y,p)),"positive_rate":float(y.mean())}
    if probabilistic:
        out["brier"] = float(brier_score_loss(y, np.clip(p, 0, 1)))
    return out


def main():
    mp=baseline.find_uwf_image_map(); records=[]
    for s in ("train","val","test"):
        p,y=baseline.read_split(s,mp); records.extend(zip(p,y.tolist()))
    splits=baseline.make_patient_level_splits(records,seed=42); arr={s:[baseline.read_image(p) for p in splits[s]["paths"]] for s in splits}; y={s:splits[s]["y"] for s in splits}
    encoder,device=m30.load_model(); print(f"device={device}",flush=True); raw={s:m30.extract(encoder,device,arr[s]) for s in splits}; mu=raw["train"].reshape(-1,raw["train"].shape[-1]).mean(0); sd=raw["train"].reshape(-1,raw["train"].shape[-1]).std(0); sd[sd<1e-8]=1; X={s:(raw[s]-mu)/sd for s in splits}; fdim=X["train"].shape[-1]
    model, val_score, epochs, device=m30.train(m30.AttentionMIL(fdim),X["train"],y["train"],X["val"],y["val"],augmented=True)
    pairs={s:predict_pair(model,X[s],y[s],device) for s in ("val","test")}
    result={"dataset":{"n":len(records),"regions":9,"teacher":"full-region attention","student":"center+cross masked attention","device":str(device),"best_val_full_macro_f1":float(val_score),"epochs":int(epochs)},"direct_scores":{},"risk_head":{},"notes":["The attention model is trained only on the training split; the independent risk head is fitted on validation teacher-student features and evaluated on the held-out test split.","Risk target is whether the masked student predicts a grade below the UWF label.","This is still a geometric partial-view proxy, not a real paired 45-degree acquisition."]}
    yv,yt=pairs["val"][1],pairs["test"][1]
    for name,sv in (("expected_severity_gap",pairs["val"][2]["expected_gap"]),("student_teacher_kl",pairs["val"][2]["kl"]),("missing_attention",pairs["val"][2]["missing_attention"])):
        st=pairs["test"][2][{"expected_severity_gap":"expected_gap","student_teacher_kl":"kl","missing_attention":"missing_attention"}[name]]
        # Larger gap/KL/missingness is interpreted as greater risk.
        result["direct_scores"][name]={"val":metric(yv,sv),"test":metric(yt,st)}
    Fv,Ft=pairs["val"][0],pairs["test"][0]
    fmu,fsd=Fv.mean(0),Fv.std(0); fsd[fsd<1e-8]=1
    clf=LogisticRegression(C=.1,class_weight="balanced",max_iter=1000,solver="liblinear",random_state=42)
    clf.fit((Fv-fmu)/fsd,yv); ptest=clf.predict_proba((Ft-fmu)/fsd)[:,1]
    result["risk_head"]={"n_features":int(Fv.shape[1]),"calibration_n":int(len(yv)),"test":metric(yt,ptest,probabilistic=True)}
    with (HERE/"risk_predictions.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(["image","severity","risk_target","risk_head_score","expected_gap","student_teacher_kl","missing_attention"])
        for i,p in enumerate(splits["test"]["paths"]): w.writerow([p.name,int(y["test"][i]),int(yt[i]),float(ptest[i]),float(pairs["test"][2]["expected_gap"][i]),float(pairs["test"][2]["kl"][i]),float(pairs["test"][2]["missing_attention"][i])])
    (HERE/"results.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    (HERE/"REPORT.md").write_text("# Exp32：Teacher–Student证据差异风险头\n\n训练完整区域模型作为teacher，再用中心+十字视野作为student；用两者预测概率差、期望严重度差、KL和注意力缺失量训练独立低估风险头。风险头只在验证集拟合，测试集仅用于最终评估。\n\n```json\n"+json.dumps(result,ensure_ascii=False,indent=2)+"\n```\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__': main()
