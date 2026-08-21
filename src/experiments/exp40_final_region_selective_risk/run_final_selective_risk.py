#!/usr/bin/env python3
"""Task 6: final selective risk head matched to the deep region model."""
from __future__ import annotations
import importlib.util,json
from pathlib import Path
import numpy as np, torch
from scipy.stats import beta
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score,brier_score_loss,roc_auc_score

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];CACHE=ROOT/'7hao/experiments/exp34_shared_uwf_region_cache';HERE.mkdir(parents=True,exist_ok=True)
sp=importlib.util.spec_from_file_location('ab',ROOT/'7hao/experiments/exp35_region_mask_pool_ablation/run_ablation.py');ab=importlib.util.module_from_spec(sp);assert sp.loader;sp.loader.exec_module(ab)
meta=json.loads((CACHE/'split_meta.json').read_text());y={s:np.asarray(meta[s]['y'],int) for s in ('train','val','test')};z=np.load(CACHE/'region_features_g3.npz');raw={s:z[f'{s}_features'] for s in y};mu=raw['train'].reshape(-1,raw['train'].shape[-1]).mean(0);sd=raw['train'].reshape(-1,raw['train'].shape[-1]).std(0);sd[sd<1e-8]=1;X={s:(raw[s]-mu)/sd for s in y}
def pair(mdl,dev,X,y):
    with torch.no_grad():
        x=torch.from_numpy(X).float().to(dev); masks={k:torch.from_numpy(ab.eval_mask(k,len(X),3)).float().to(dev) for k in ('full','cross')}; pf=torch.softmax(mdl(x,masks['full'])[0],1).cpu().numpy();pp=torch.softmax(mdl(x,masks['cross'])[0],1).cpu().numpy()
    ef=pf@np.asarray([0.,1.,2.]);ep=pp@np.asarray([0.,1.,2.]);ent=-np.sum(np.clip(pf,1e-8,1)*np.log(np.clip(pf,1e-8,1)),1);entp=-np.sum(np.clip(pp,1e-8,1)*np.log(np.clip(pp,1e-8,1)),1);kl=.5*np.sum(pf*np.log(np.clip(pf,1e-8,1)/np.clip(pp,1e-8,1))+pp*np.log(np.clip(pp,1e-8,1)/np.clip(pf,1e-8,1)),1);F=np.c_[pf,pp,pf-pp,np.abs(pf-pp),ef,ep,ef-ep,ent,entp,kl];risk=(pp.argmax(1)<y).astype(int);return F,risk,ef-ep,kl
def metric(y,p,probabilistic=False):
    out={'auroc':float(roc_auc_score(y,p)),'average_precision':float(average_precision_score(y,p)),'positive_rate':float(y.mean())}
    if probabilistic:out['brier']=float(brier_score_loss(y,np.clip(p,0,1)))
    return out
def upper(k,n):return 1. if n==0 else (1. if k==n else float(beta.ppf(.95,k+1,n-k)))
def calibrate(s,y,a):
    opts=[]
    for t in np.unique(s):
        m=s<=t;n=int(m.sum());k=int(y[m].sum())
        if n and upper(k,n)<=a:opts.append((n,float(t),k,upper(k,n)))
    if not opts:return {'threshold':float(s.min()),'validation_coverage':float(1/len(y)),'validation_cp_upper':upper(int(y[np.argmin(s)]),1),'feasible':False}
    n,t,k,u=max(opts,key=lambda q:q[0]);return {'threshold':t,'validation_coverage':float(n/len(y)),'validation_risk':float(k/n),'validation_cp_upper':u,'feasible':True}
def main():
    mdl,dev,vs,ep=ab.train(X['train'],y['train'],X['val'],y['val'],'attention',.30,42);Fv,yv,gapv,klv=pair(mdl,dev,X['val'],y['val']);Ft,yt,gapt,klt=pair(mdl,dev,X['test'],y['test']);mu2=Fv.mean(0);sd2=Fv.std(0);sd2[sd2<1e-8]=1;clf=LogisticRegression(C=.1,class_weight='balanced',max_iter=1000,solver='liblinear',random_state=42).fit((Fv-mu2)/sd2,yv);sv=clf.predict_proba((Fv-mu2)/sd2)[:,1];st=clf.predict_proba((Ft-mu2)/sd2)[:,1]
    result={'model':{'best_val_full_macro_f1':float(vs),'epochs':int(ep)},'risk_head':{'test':metric(yt,st,True),'validation':metric(yv,sv,True)},'direct_scores':{'severity_gap':{'test':metric(yt,gapt)},'student_teacher_kl':{'test':metric(yt,klt)}},'selective':{},'notes':['This risk head is trained only on Exp30-matched validation teacher/student features and evaluated on the held-out test split.','The selective threshold is calibrated with a one-sided Clopper-Pearson upper bound.','Partial view remains a geometric center+cross proxy, not a real paired acquisition.']}
    for a in (.05,.10,.20):
        c=calibrate(sv,yv,a);m=st<=c['threshold'];result['selective'][str(a)]={'calibration':c,'test':{'coverage':float(m.mean()),'accepted_n':int(m.sum()),'accepted_risk':float(yt[m].mean()) if m.any() else None,'accepted_accuracy':float(1-yt[m].mean()) if m.any() else None,'rejected_n':int((~m).sum())}}
    (HERE/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');(HERE/'REPORT.md').write_text('# Exp40：最终深度区域选择性风险头\n\n在Exp30匹配的区域注意力模型上重新训练风险头并校准风险—覆盖率工作点，替代Exp29使用的旧风险头。\n\n```json\n'+json.dumps(result,ensure_ascii=False,indent=2)+'\n```\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
