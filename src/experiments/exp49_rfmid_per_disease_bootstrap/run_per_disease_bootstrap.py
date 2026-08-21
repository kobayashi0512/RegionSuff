#!/usr/bin/env python3
"""Exp49: disease-wise paired stratified bootstrap for RFMiD2 global vs region features."""
from __future__ import annotations
import importlib.util, json
from pathlib import Path
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]; HERE.mkdir(parents=True,exist_ok=True)
sp=importlib.util.spec_from_file_location('e38',ROOT/'7hao/experiments/exp38_rfmid_region_external/run_rfmid_region_external.py'); e38=importlib.util.module_from_spec(sp); assert sp.loader; sp.loader.exec_module(e38)
def norm(train,test):
    mu=train.mean(0); sd=train.std(0); sd[sd<1e-8]=1; return (train-mu)/sd,(test-mu)/sd
def ci(x): return [float(np.quantile(x,.025)),float(np.quantile(x,.975))]
def p_two(delta):
    n=len(delta); lo=(np.sum(delta<=0)+1)/(n+1); hi=(np.sum(delta>=0)+1)/(n+1); return float(min(1.,2*min(lo,hi)))
def bh(pvals):
    n=len(pvals); order=np.argsort(pvals); out=np.empty(n); prev=1.
    for rank,i in reversed(list(enumerate(order,1))): prev=min(prev,pvals[i]*n/rank); out[i]=prev
    return out
def bootstrap(y,pg,pr,seed,nboot=2000):
    rng=np.random.default_rng(seed); pos=np.flatnonzero(y==1); neg=np.flatnonzero(y==0); au_g=[]; au_r=[]; ap_g=[]; ap_r=[]
    for _ in range(nboot):
        ix=np.r_[rng.choice(pos,len(pos),replace=True),rng.choice(neg,len(neg),replace=True)]
        au_g.append(roc_auc_score(y[ix],pg[ix])); au_r.append(roc_auc_score(y[ix],pr[ix])); ap_g.append(average_precision_score(y[ix],pg[ix])); ap_r.append(average_precision_score(y[ix],pr[ix]))
    au_g=np.asarray(au_g); au_r=np.asarray(au_r); ap_g=np.asarray(ap_g); ap_r=np.asarray(ap_r)
    return {'global_auroc_ci':ci(au_g),'region_auroc_ci':ci(au_r),'delta_auroc_ci':ci(au_r-au_g),'delta_auroc_p_two_sided':p_two(au_r-au_g),'global_ap_ci':ci(ap_g),'region_ap_ci':ci(ap_r),'delta_ap_ci':ci(ap_r-ap_g),'delta_ap_p_two_sided':p_two(ap_r-ap_g)}
def main():
    labels={};data={}
    for s in ('Training','Validation','Test'): labels[s],data[s]=e38.read_split(s)
    names=labels['Training']; train=data['Training']+data['Validation']; test=data['Test']; train_arr=[e38.m30.baseline.read_image(p) for p,_ in train]; test_arr=[e38.m30.baseline.read_image(p) for p,_ in test]; ytr=np.vstack([x[1] for x in train]); yt=np.vstack([x[1] for x in test]); model,device=e38.m30.load_model(); print(f'device={device}; train={len(train)} test={len(test)}',flush=True)
    reps={'global':e38.global_extract(model,device,train_arr),'region':e38.m30.extract(model,device,train_arr).mean(1)}; test_reps={'global':e38.global_extract(model,device,test_arr),'region':e38.m30.extract(model,device,test_arr).mean(1)}
    reps={k:norm(v,test_reps[k]) for k,v in reps.items()}; rows=[]; excluded=[]
    for j,name in enumerate(names):
        pos=int(yt[:,j].sum()); neg=int((yt[:,j]==0).sum())
        if ytr[:,j].min()==ytr[:,j].max() or pos<5 or neg<5: excluded.append({'label':name,'test_positive':pos,'test_negative':neg,'reason':'requires >=5 positives and >=5 negatives for bootstrap inference'}); continue
        probs={}
        for rep in ('global','region'):
            a,b=reps[rep]; clf=LogisticRegression(C=.1,max_iter=500,solver='liblinear',random_state=42).fit(a,ytr[:,j]); probs[rep]=clf.predict_proba(b)[:,1]
        q=bootstrap(yt[:,j],probs['global'],probs['region'],1000+j,2000); rows.append({'label':name,'test_positive':pos,'test_negative':neg,'global_auroc':float(roc_auc_score(yt[:,j],probs['global'])),'region_auroc':float(roc_auc_score(yt[:,j],probs['region'])),'global_average_precision':float(average_precision_score(yt[:,j],probs['global'])),'region_average_precision':float(average_precision_score(yt[:,j],probs['region']),),**q}); print(f'{j}:{name} done',flush=True)
    if rows:
        qa=bh(np.asarray([r['delta_auroc_p_two_sided'] for r in rows])); qp=bh(np.asarray([r['delta_ap_p_two_sided'] for r in rows]));
        for r,a,p in zip(rows,qa,qp): r['delta_auroc_q_bh']=float(a); r['delta_ap_q_bh']=float(p)
    result={'dataset':{'name':'RFMiD2.0','train_n':len(train),'test_n':len(test),'eligible_labels':len(rows),'excluded_labels':len(excluded),'bootstrap_replicates':2000},'per_disease':rows,'excluded':excluded,'notes':['Per-disease probes train only on RFMiD2 Training+Validation labels.','Bootstrap is paired and stratified within test positives/negatives to preserve disease prevalence.','Benjamini-Hochberg q-values control FDR across eligible diseases.','This is external ordinary-color-fundus validation, not true same-eye UWF/45-degree validation.']}
    (HERE/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8'); (HERE/'REPORT.md').write_text('# Exp49：RFMiD2逐病种配对Bootstrap外部验证\n\n对阳性和阴性测试样本均不少于5例的病种，比较全图与3×3区域平均冻结表征；每病种实施2000次分层配对Bootstrap，并做BH-FDR校正。\n\n```json\n'+json.dumps(result,ensure_ascii=False,indent=2)+'\n```\n',encoding='utf-8'); print(json.dumps({'eligible_labels':len(rows),'excluded_labels':len(excluded)},ensure_ascii=False))
if __name__=='__main__': main()
