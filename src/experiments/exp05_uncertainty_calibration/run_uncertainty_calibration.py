#!/usr/bin/env python3
"""Exp05: bootstrap uncertainty and calibration for the existing experiments."""
from __future__ import annotations
import csv, json
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent; WORKSPACE=HERE.parents[2]
EXP01=WORKSPACE/"7hao/experiments/exp01_quality_fov_baseline"
EXP02=WORKSPACE/"7hao/experiments/exp02_fov_sensitivity"

def auroc(y,s):
    y=np.asarray(y).astype(int); s=np.asarray(s,float); pos=s[y==1]; neg=s[y==0]
    if len(pos)==0 or len(neg)==0: return float('nan')
    # Tie-aware rank statistic.
    ranks=np.argsort(np.argsort(s))+1
    return float((ranks[y==1].sum()-len(pos)*(len(pos)+1)/2)/(len(pos)*len(neg)))
def brier(y,s): return float(np.mean((np.asarray(s)-np.asarray(y))**2))
def ece(y,s,bins=10):
    y=np.asarray(y); s=np.asarray(s); total=0.0
    for lo,hi in zip(np.linspace(0,1,bins,endpoint=False),np.linspace(0,1,bins+1)[1:]):
        m=(s>=lo)&((s<hi) if hi<1 else (s<=hi))
        if m.any(): total += m.mean()*abs(y[m].mean()-s[m].mean())
    return float(total)
def ci(vals):
    vals=np.asarray(vals,float); return [float(np.nanpercentile(vals,2.5)),float(np.nanpercentile(vals,97.5))]
def bootstrap(y,s,fn,B=2000,seed=42):
    rng=np.random.default_rng(seed); n=len(y); out=[]
    for _ in range(B):
        ix=rng.integers(0,n,n); out.append(fn(y[ix],s[ix]))
    return ci(out)
def main():
    with (EXP01/'test_predictions.csv').open(newline='',encoding='utf-8') as f: base=list(csv.DictReader(f))
    y=np.array([int(r['central_underestimate']) for r in base]); score=np.array([float(r['risk_score']) for r in base])
    risk={'n':len(y),'positive_rate':float(y.mean()),'auroc':auroc(y,score),'auroc_95ci':bootstrap(y,score,auroc),'brier':brier(y,score),'brier_95ci':bootstrap(y,score,lambda a,b:brier(a,b)),'ece_10bin':ece(y,score),'ece_95ci':bootstrap(y,score,lambda a,b:ece(a,b))}
    byfrac={}
    with (EXP02/'metrics.csv').open(newline='',encoding='utf-8') as f: metrics=list(csv.DictReader(f))
    # bootstrap accuracy, MAE, and underestimation rate from saved per-image predictions
    with (EXP02/'test_predictions_by_fraction.csv').open(newline='',encoding='utf-8') as f: pred=list(csv.DictReader(f))
    for frac in sorted({float(r['fraction']) for r in pred}):
        rr=[r for r in pred if float(r['fraction'])==frac]
        # The saved rows do not include severity, so use hard underestimation and accuracy only.
        yy=np.array([int(r['true_label']) for r in rr]); pp=np.array([int(r['pred']) for r in rr]); under=np.array([int(r['underestimate']) for r in rr])
        rng=np.random.default_rng(100+int(frac*100)); n=len(yy); acc=[]; rate=[]
        for _ in range(2000):
            ix=rng.integers(0,n,n); acc.append(np.mean(pp[ix]==yy[ix])); rate.append(np.mean(under[ix]))
        byfrac[str(frac)]={'n':n,'accuracy':float(np.mean(pp==yy)),'accuracy_95ci':ci(acc),'underestimate_rate':float(under.mean()),'underestimate_rate_95ci':ci(rate)}
    # paired bootstrap difference between smallest and largest view.
    a=[r for r in pred if float(r['fraction'])==0.35]; b=[r for r in pred if float(r['fraction'])==0.90]
    if [r['image'] for r in a] != [r['image'] for r in b]: raise RuntimeError('fraction rows not aligned')
    ya=np.array([int(r['true_label']) for r in a]); pa=np.array([int(r['pred']) for r in a]); ua=np.array([int(r['underestimate']) for r in a]); pb=np.array([int(r['pred']) for r in b]); ub=np.array([int(r['underestimate']) for r in b]); rng=np.random.default_rng(77); diffa=[]; diffr=[]
    for _ in range(2000):
        ix=rng.integers(0,len(ya),len(ya)); diffa.append(np.mean(pb[ix]==ya[ix])-np.mean(pa[ix]==ya[ix])); diffr.append(np.mean(ub[ix])-np.mean(ua[ix]))
    result={'risk_head':risk,'view_fraction_bootstrap':byfrac,'paired_difference_0.90_minus_0.35':{'accuracy_difference':float(np.mean(pb==ya)-np.mean(pa==ya)),'accuracy_difference_95ci':ci(diffa),'underestimate_rate_difference':float(ub.mean()-ua.mean()),'underestimate_rate_difference_95ci':ci(diffr)},'notes':['CIs are nonparametric bootstrap intervals on the existing patient-level test split.','The risk head score was trained on the training split and evaluated on held-out test predictions.','This quantifies uncertainty; it does not replace external clinical validation.']}
    json.dump(result,(HERE/'results.json').open('w'),ensure_ascii=False,indent=2)
    (HERE/'REPORT.md').write_text('# Exp05：不确定性与校准分析\n\n对 Exp01/Exp02 的已有测试结果进行 2000 次非参数 bootstrap。\n\n- 风险头：AUROC 95% CI、Brier score、10-bin ECE。\n- 视野实验：各比例准确率与低估率的 95% CI。\n- 配对差异：同一测试图像上比较 90% 与 35% 视野。\n\n结果见 `results.json`。\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
