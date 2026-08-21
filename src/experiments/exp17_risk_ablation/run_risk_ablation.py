#!/usr/bin/env python3
"""Exp17: ablation of content, quality and FOV signals for underestimation risk."""
from __future__ import annotations
import json, importlib.util
from pathlib import Path
import numpy as np
from sklearn.model_selection import GroupKFold

ROOT=Path(__file__).resolve().parents[3]; OUT=ROOT/'7hao/experiments/exp17_risk_ablation'; OUT.mkdir(parents=True,exist_ok=True); BASE=ROOT/'7hao/experiments/exp01_quality_fov_baseline/run_baseline.py'
spec=importlib.util.spec_from_file_location('b',BASE); b=importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(b)

def small_content(arr):
    z=b.resize_array(arr,16); gray=z.mean(2); red=z[:,:,0]
    return np.r_[gray.ravel(),red.ravel(),gray.mean(),gray.std()]

def per_image(path):
    full=b.read_image(path); central=b.central_view(full,.55); f,meta=b.feature_vector(central)
    content=small_content(central)
    quality=np.asarray([meta['sharpness'],meta['contrast'],meta['brightness'],float(np.mean(central.mean(2)<.035)),float(np.mean(central.mean(2)>.90)),float(np.mean(central.mean(2)>0)),float(np.std(central.mean(2)))],float)
    fov=np.asarray([meta['nonblack_coverage'],meta['bbox_width_ratio'],meta['bbox_height_ratio'],meta['bbox_aspect'],.55],float)
    return {'baseline':f,'content':content,'quality':quality,'fov':fov,'content_quality':np.r_[content,quality],'content_fov':np.r_[content,fov],'quality_fov':np.r_[quality,fov],'all':np.r_[content,quality,fov]}

def standardize(tr,others):
    mu=tr.mean(0); sd=tr.std(0); sd[sd<1e-8]=1.; return (tr-mu)/sd,[(x-mu)/sd for x in others]

def main():
    mp=b.find_uwf_image_map(); rec=[]
    for s in ('train','val','test'):
        p,y=b.read_split(s,mp); rec.extend(zip(p,y.tolist()))
    splits=b.make_patient_level_splits(rec,seed=42); fs={}
    for s in splits:
        print('features',s,flush=True); fs[s]={k:[] for k in ('baseline','content','quality','fov','content_quality','content_fov','quality_fov','all')}
        for p in splits[s]['paths']:
            d=per_image(p)
            for k,v in d.items(): fs[s][k].append(v)
        for k in fs[s]: fs[s][k]=np.vstack(fs[s][k])
    # Produce out-of-fold central predictions so risk labels are not an
    # in-sample artifact.
    xtr=fs['train']['baseline']; ytr=splits['train']['y']; groups=np.asarray([b.patient_key(p) for p in splits['train']['paths']]); oof=np.zeros(len(ytr),int); oof_p=np.zeros((len(ytr),3),float)
    for a,c in GroupKFold(5).split(xtr,ytr,groups):
        mu=xtr[a].mean(0); sd=xtr[a].std(0); sd[sd<1e-8]=1.; W=b.fit_multiclass((xtr[a]-mu)/sd,ytr[a]); oof_p[c]=b.predict_multi(W,(xtr[c]-mu)/sd); oof[c]=oof_p[c].argmax(1)
    mu=xtr.mean(0); sd=xtr.std(0); sd[sd<1e-8]=1.; W=b.fit_multiclass((xtr-mu)/sd,ytr); probs={'train':oof_p,'val':b.predict_multi(W,(fs['val']['baseline']-mu)/sd),'test':b.predict_multi(W,(fs['test']['baseline']-mu)/sd)}; c_pred={s:probs[s].argmax(1) for s in splits}; risk_y={s:(c_pred[s]<splits[s]['y']).astype(int) for s in splits}
    result={'dataset':{'n':sum(len(x['paths']) for x in splits.values()),'risk_definition':'baseline 67-feature central-view severity probe prediction < UWF clinical grade','train_positive_oof':int(risk_y['train'].sum())},'ablations':{},'notes':[]}
    score_rows=[]
    for name in ('baseline','content','quality','fov','content_quality','content_fov','quality_fov','all'):
        X={s:fs[s][name] for s in splits}; X['train'],[X['val'],X['test']]=standardize(X['train'],[X['val'],X['test']]); w=b.fit_binary(X['train'],risk_y['train']); scores={s:b.predict_binary(w,X[s]) for s in ('val','test')}; va=b.auc_pr(risk_y['val'],scores['val']); te=b.auc_pr(risk_y['test'],scores['test']); result['ablations'][name]={'dimension':int(X['train'].shape[1]),'val_auroc':va[0],'val_average_precision':va[1],'test_auroc':te[0],'test_average_precision':te[1]}; score_rows.extend((name,int(risk_y['test'][i]),float(scores['test'][i])) for i in range(len(risk_y['test'])))
    def enriched(s):
        p=probs[s]; ent=(-np.sum(p*np.log(np.clip(p,1e-8,1.0)),axis=1))[:,None]; sp=np.sort(p,axis=1); margin=(sp[:,-1]-sp[:,-2])[:,None]; q=fs[s]['quality'][:,[0,1,2]]; return np.c_[fs[s]['baseline'],p,ent,margin,q]
    X={s:enriched(s) for s in splits}; X['train'],[X['val'],X['test']]=standardize(X['train'],[X['val'],X['test']]); w=b.fit_binary(X['train'],risk_y['train']); scores={s:b.predict_binary(w,X[s]) for s in ('val','test')}; va=b.auc_pr(risk_y['val'],scores['val']); te=b.auc_pr(risk_y['test'],scores['test']); result['ablations']['baseline_plus_uncertainty_quality']={'dimension':int(X['train'].shape[1]),'val_auroc':va[0],'val_average_precision':va[1],'test_auroc':te[0],'test_average_precision':te[1]}; score_rows.extend(('baseline_plus_uncertainty_quality',int(risk_y['test'][i]),float(scores['test'][i])) for i in range(len(risk_y['test'])))
    result['notes']=['Content uses a 16x16 central grayscale/red spatial descriptor; quality uses brightness/contrast/sharpness/dark-light statistics; FOV uses nonblack coverage and retinal bounding-box geometry.','Risk labels use patient-grouped out-of-fold central severity predictions for the training split.','This ablation identifies predictive signal sources; it does not establish causal importance.']
    import csv
    with (OUT/'test_risk_scores.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f); w.writerow(['model','index','target','score'])
        for m in sorted({r[0] for r in score_rows}):
            rows=[(r[1],r[2]) for r in score_rows if r[0]==m]
            w.writerows((m,i,y,s) for i,(y,s) in enumerate(rows))
    (OUT/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8'); (OUT/'REPORT.md').write_text('# Exp17：低估风险组件消融\n\n比较内容、图像质量、视野几何及其组合对中心视野低估风险的贡献。训练风险标签采用患者分组 out-of-fold 预测，避免中心分类器训练集过拟合造成正例塌缩。\n\n完整结果见 `results.json`。\n',encoding='utf-8'); print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
