#!/usr/bin/env python3
"""Exp20: zero-shot FOV transport on RFMiD2.

Train disease probes only on RFMiD training+validation data. On the held-out
test set, quantify how much disease evidence changes after a central crop;
the test labels are used only for final evaluation, never for fitting.
"""
from __future__ import annotations
import csv,json,importlib.util
from pathlib import Path
import numpy as np
from sklearn.metrics import roc_auc_score

ROOT=Path(__file__).resolve().parents[3]; OUT=ROOT/'7hao/experiments/exp20_rfmid_zero_shot_fov_transport'; OUT.mkdir(parents=True,exist_ok=True); BASE=ROOT/'7hao/experiments/exp01_quality_fov_baseline/run_baseline.py'; spec=importlib.util.spec_from_file_location('b',BASE); b=importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(b); RF=ROOT/'7hao/datasets/RFMiD2_0/extracted'

def read(split):
    f=next((RF/split).glob('*_labels.csv')); rows=[]
    with f.open(newline='',encoding='latin-1') as h:
        rd=csv.DictReader(h); names=[x for x in rd.fieldnames if x and x!='ID']; mp={int(p.stem):p for p in (RF/split).iterdir() if p.suffix.lower() in {'.jpg','.jpeg','.png'}}
        for r in rd:
            i=int(r['ID'])
            if i in mp: rows.append((mp[i],np.asarray([int(float(r.get(x,0) or 0)) for x in names],int)))
    return names,rows

def extract(paths,view):
    out=[]
    for p in paths:
        arr=b.read_image(p); arr=arr if view=='full' else b.central_view(arr,.55); out.append(b.feature_vector(arr)[0])
    return np.vstack(out)

def main():
    names,tr=read('Training'); _,va=read('Validation'); _,te=read('Test'); train=tr+va; ytr=np.vstack([r[1] for r in train]); yte=np.vstack([r[1] for r in te]); result={'dataset':{'train':len(train),'test':len(te),'labels':len(names)},'aggregate':{},'per_label':{},'notes':[]}; scores={}
    for view in ('full','central'):
        Xtr=extract([r[0] for r in train],view); Xte=extract([r[0] for r in te],view); mu=Xtr.mean(0); sd=Xtr.std(0); sd[sd<1e-8]=1.; Xtr=(Xtr-mu)/sd; Xte=(Xte-mu)/sd; all_scores=[]
        for j in range(len(names)):
            if ytr[:,j].sum()==0 or ytr[:,j].sum()==len(ytr): all_scores.append(np.full(len(te),.5)); continue
            w=b.fit_binary(Xtr,ytr[:,j]); all_scores.append(b.predict_binary(w,Xte))
        scores[view]=np.vstack(all_scores).T
    delta=scores['full']-scores['central']; pos=yte.astype(bool); valid=np.ones_like(pos,dtype=bool)
    pos_vals=delta[pos]; neg_vals=delta[~pos]
    result['aggregate']={'mean_delta_positive_labels':float(pos_vals.mean()),'mean_delta_negative_labels':float(neg_vals.mean()),'positive_delta_fraction_positive_labels':float((pos_vals>0).mean()),'positive_delta_fraction_negative_labels':float((neg_vals>0).mean()),'positive_minus_negative_delta':float(pos_vals.mean()-neg_vals.mean())}
    for j,n in enumerate(names):
        y=yte[:,j]; d=delta[:,j]; item={'test_positive':int(y.sum()),'mean_delta_positive':float(d[y==1].mean()) if y.sum() else None,'mean_delta_negative':float(d[y==0].mean()) if (y==0).sum() else None,'positive_minus_negative_delta':float(d[y==1].mean()-d[y==0].mean()) if y.sum() and (y==0).sum() else None,'full_vs_central_positive_score':float(scores['full'][y==1,j].mean()-scores['central'][y==1,j].mean()) if y.sum() else None}
        if len(np.unique(y))==2: item['delta_pair_auroc']=float(roc_auc_score(y,d))
        result['per_label'][n]=item
    result['notes']=['No RFMiD test labels are used for fitting; probes are trained on RFMiD Training+Validation only.','This is a zero-shot transport diagnostic for FOV evidence loss, not a paired UWF/45-degree clinical validation.','A positive delta means the full image probe score exceeds the central-view score.']
    (OUT/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8'); (OUT/'REPORT.md').write_text('# Exp20：RFMiD2 零样本视野证据迁移\n\n仅使用 RFMiD2 Training+Validation 训练病种探针，在 Test 上比较完整图像与55%中心裁剪的疾病证据差异，不用测试标签调参。\n\n完整结果见 `results.json`。\n',encoding='utf-8'); print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
