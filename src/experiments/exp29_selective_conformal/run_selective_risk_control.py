#!/usr/bin/env python3
"""Exp29: split-calibrated selective prediction for underestimation risk."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
from scipy.stats import beta

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HERE.mkdir(parents=True, exist_ok=True)
PRED = ROOT / "7hao/experiments/exp27_multiview_disagreement_risk/risk_predictions.csv"


def cp_upper(k, n, conf=.95):
    if n == 0: return 1.0
    if k == n: return 1.0
    return float(beta.ppf(conf, k + 1, n - k))


def calibrate(score, y, alpha):
    # Accept low predicted-risk images. Choose the largest validation coverage
    # whose one-sided Clopper-Pearson upper bound is <= alpha.
    candidates = np.unique(np.r_[score, np.inf])
    choices=[]
    for t in candidates:
        keep=score<=t; n=int(keep.sum())
        if n==0: continue
        k=int(y[keep].sum()); ub=cp_upper(k,n)
        if ub<=alpha: choices.append((n, float(t), k, ub))
    if not choices:
        # A transparent fallback: accept the lowest-risk sample only.
        i=int(np.argmin(score)); return {"threshold":float(score[i]),"validation_n":1,"validation_coverage":float(1/len(y)),"validation_risk":float(y[i]),"validation_cp_upper":cp_upper(int(y[i]),1),"feasible":False}
    n,t,k,ub=max(choices,key=lambda z:z[0])
    keep=score<=t
    return {"threshold":t,"validation_n":n,"validation_coverage":float(n/len(y)),"validation_risk":float(k/n),"validation_cp_upper":float(ub),"feasible":True}


def evaluate(score,y,severity,cal):
    keep=score<=cal["threshold"]
    out={"coverage":float(keep.mean()),"accepted_n":int(keep.sum()),"accepted_underestimation_risk":float(y[keep].mean()) if keep.any() else None,"accepted_accuracy":float(1-y[keep].mean()) if keep.any() else None,"rejected_n":int((~keep).sum())}
    if keep.any():
        pdr=severity==2
        out["accepted_pdr_n"] = int((pdr&keep).sum()); out["accepted_pdr_underestimation_risk"] = float(y[pdr&keep].mean()) if np.any(pdr&keep) else None
    return out


def main():
    rows=list(csv.DictReader(PRED.open(encoding="utf-8")))
    result={"source":"Exp27 multi-view risk scores","models":{},"notes":["Thresholds are selected only on validation risk labels.","The one-sided Clopper-Pearson upper bound is used as a finite-sample calibration audit; test results are independent of threshold selection.","Geometric views and synthetic masks are proxies, so this is algorithmic risk control rather than clinical certification."]}
    for model in sorted({r["model"] for r in rows}):
        val=[r for r in rows if r["model"]==model and r["split"]=="val"]; test=[r for r in rows if r["model"]==model and r["split"]=="test"]
        vs=np.asarray([float(r["risk_score"]) for r in val]); vy=np.asarray([int(r["risk_target"]) for r in val]); ts=np.asarray([float(r["risk_score"]) for r in test]); ty=np.asarray([int(r["risk_target"]) for r in test]); sev=np.asarray([int(r["severity"]) for r in test])
        result["models"][model]={"uncalibrated_test":{"coverage":1.0,"risk":float(ty.mean()),"n":len(ty)},"alphas":{}}
        for alpha in (.05,.10,.20):
            cal=calibrate(vs,vy,alpha); result["models"][model]["alphas"][str(alpha)]={"calibration":cal,"test":evaluate(ts,ty,sev,cal)}
        # A compact risk-coverage curve for visualization.
        curve=[]
        for cov in (.20,.40,.60,.80,1.00):
            n=max(1,int(len(ts)*cov)); idx=np.argsort(ts)[:n]; curve.append({"coverage":float(n/len(ts)),"risk":float(ty[idx].mean()),"threshold":float(ts[idx[-1]])})
        result["models"][model]["test_risk_coverage_curve"]=curve
    (HERE/"results.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    (HERE/"REPORT.md").write_text("# Exp29：选择性预测与风险—覆盖率控制\n\n对Exp27的低估风险分数进行验证集校准：只自动接受低风险图像，对高风险图像转人工复核。使用Clopper–Pearson上置信界做有限样本审计。\n\n```json\n"+json.dumps(result,ensure_ascii=False,indent=2)+"\n```\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
