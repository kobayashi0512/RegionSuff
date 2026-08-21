#!/usr/bin/env python3
"""Exp47: group-nested validation of the selective-risk threshold."""
from __future__ import annotations
import importlib.util, json
from pathlib import Path
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold, GroupShuffleSplit

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]; CACHE=ROOT/'7hao/experiments/exp34_shared_uwf_region_cache'; HERE.mkdir(parents=True,exist_ok=True)
sp=importlib.util.spec_from_file_location('ab',ROOT/'7hao/experiments/exp35_region_mask_pool_ablation/run_ablation.py'); ab=importlib.util.module_from_spec(sp); assert sp.loader; sp.loader.exec_module(ab)
sp2=importlib.util.spec_from_file_location('risk',ROOT/'7hao/experiments/exp40_final_region_selective_risk/run_final_selective_risk.py'); risk=importlib.util.module_from_spec(sp2); assert sp2.loader; sp2.loader.exec_module(risk)
meta=json.loads((CACHE/'split_meta.json').read_text()); z=np.load(CACHE/'region_features_g3.npz')
parts=('train','val'); raw=np.concatenate([z[f'{s}_features'] for s in parts]); y=np.concatenate([np.asarray(meta[s]['y'],int) for s in parts]); paths=sum([meta[s]['paths'] for s in parts],[]); groups=np.asarray([ab.m30.baseline.patient_key(Path(p)) for p in paths])

def pair(model,dev,X,y): return risk.pair(model,dev,X,y)
def one_fold(fid,tr_outer,te_outer):
    # Only outer-train is used for representation fitting, early stopping, risk fitting and threshold calibration.
    gss=GroupShuffleSplit(n_splits=1,test_size=.25,random_state=700+fid)
    tr_inner,cal_idx=next(gss.split(tr_outer,y[tr_outer],groups[tr_outer])); fit_idx=tr_outer[tr_inner]; cal_idx=tr_outer[cal_idx]
    mu=raw[fit_idx].reshape(-1,raw.shape[-1]).mean(0); sd=raw[fit_idx].reshape(-1,raw.shape[-1]).std(0); sd[sd<1e-8]=1
    Xfit=(raw[fit_idx]-mu)/sd; Xcal=(raw[cal_idx]-mu)/sd; Xtest=(raw[te_outer]-mu)/sd
    model,dev,vs,ep=ab.train(Xfit,y[fit_idx],Xcal,y[cal_idx],'attention',.30,100+fid)
    Fc,yc,_,_=pair(model,dev,Xcal,y[cal_idx]); Ft,yt,_,_=pair(model,dev,Xtest,y[te_outer])
    fmu=Fc.mean(0); fsd=Fc.std(0); fsd[fsd<1e-8]=1
    clf=LogisticRegression(C=.1,class_weight='balanced',max_iter=1000,solver='liblinear',random_state=100+fid).fit((Fc-fmu)/fsd,yc)
    sc=clf.predict_proba((Fc-fmu)/fsd)[:,1]; st=clf.predict_proba((Ft-fmu)/fsd)[:,1]
    row={'fold':fid,'n_fit':int(len(fit_idx)),'n_calibration':int(len(cal_idx)),'n_outer_test':int(len(te_outer)),'best_val_macro_f1':float(vs),'epochs':int(ep),'risk_test':risk.metric(yt,st,True),'selective':{}}
    for target in (.05,.10,.20):
        key=f'{target:.2f}'; c=risk.calibrate(sc,yc,target); accept=st<=c['threshold']; row['selective'][key]={'calibration':c,'test_coverage':float(accept.mean()),'test_accepted_risk':float(yt[accept].mean()) if accept.any() else None,'test_accepted_n':int(accept.sum()),'test_rejected_n':int((~accept).sum())}
    return row
def agg(rows,key):
    vals=np.asarray([r[key] for r in rows],float); return {'mean':float(vals.mean()),'std':float(vals.std(ddof=1))}
def main():
    folds=[]; gkf=GroupKFold(n_splits=4)
    for fid,(tr,te) in enumerate(gkf.split(raw,y,groups)):
        folds.append(one_fold(fid,tr,te)); print(f'fold={fid} done',flush=True)
    result={'protocol':'4-fold outer GroupKFold on original train+validation patients; each outer-train fold is group-split into model-fit and independent calibration subsets. Original held-out test is untouched.','n_samples':int(len(y)),'n_patients':int(len(np.unique(groups))),'folds':folds,'aggregate':{'risk_auroc':agg([{'x':r['risk_test']['auroc']} for r in folds],'x')}}
    for target in ('0.05','0.10','0.20'):
        result['aggregate'][f'target_{target}']={k:agg([{'x':r['selective'][target][k]} for r in folds],'x') for k in ('test_coverage','test_accepted_risk')}
    result['notes']=['Thresholds are calibrated without outer-fold labels, then assessed once on the held-out outer fold.','This validates threshold transport across patient groups; it does not replace real prospective external calibration.','The limited view remains the center+cross geometric proxy.']
    (HERE/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8'); (HERE/'REPORT.md').write_text('# Exp47：患者级嵌套风险校准\n\n采用4折外层患者分组交叉验证；每个外层训练折再划分模型拟合和独立阈值校准子集，外层留出折只用于评估风险—覆盖率。\n\n```json\n'+json.dumps(result,ensure_ascii=False,indent=2)+'\n```\n',encoding='utf-8'); print(json.dumps(result['aggregate'],ensure_ascii=False,indent=2))
if __name__=='__main__': main()
