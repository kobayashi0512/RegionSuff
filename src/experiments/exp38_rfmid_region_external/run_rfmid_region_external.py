#!/usr/bin/env python3
"""Task 8: RFMiD2 external disease validation for regional representations."""
from __future__ import annotations
import csv, importlib.util, json
from pathlib import Path
import numpy as np, torch
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]; RF=ROOT/'7hao/datasets/RFMiD2_0/extracted'; HERE.mkdir(parents=True,exist_ok=True)
sp=importlib.util.spec_from_file_location('m30',ROOT/'7hao/experiments/exp30_deep_region_attention/run_deep_region_attention.py'); m30=importlib.util.module_from_spec(sp); assert sp.loader; sp.loader.exec_module(m30)
def read_split(name):
    folder=RF/name; csvp=next(folder.glob('*_labels.csv')); rows=[]
    with csvp.open(newline='',encoding='latin-1') as f:
        rd=csv.DictReader(f); labels=[x for x in (rd.fieldnames or []) if x and x!='ID']; mp={int(p.stem):p for p in folder.iterdir() if p.suffix.lower() in {'.jpg','.jpeg','.png'}}
        for row in rd:
            i=int(row['ID']);
            if i in mp: rows.append((mp[i],np.asarray([int(float(row.get(x,0) or 0)) for x in labels],np.int64)))
    return labels,rows
def global_extract(model,device,arrs):
    out=[]
    for st in range(0,len(arrs),32):
        with torch.no_grad():out.append(model.global_pool(model.forward_features(m30.tensor_batch(arrs[st:st+32]).to(device))).flatten(1).cpu().numpy().astype(np.float32))
    return np.vstack(out)
def main():
    labels={};data={}
    for s in ('Training','Validation','Test'):labels[s],data[s]=read_split(s)
    names=labels['Training']; train=data['Training']+data['Validation']; test=data['Test']; train_arr=[m30.baseline.read_image(p) for p,_ in train]; test_arr=[m30.baseline.read_image(p) for p,_ in test]; ytr=np.vstack([x[1] for x in train]); yt=np.vstack([x[1] for x in test]); model,device=m30.load_model(); print(f'device={device}; train={len(train_arr)} test={len(test_arr)}',flush=True)
    reps={'global':(global_extract(model,device,train_arr),global_extract(model,device,test_arr)),'region_mean':(m30.extract(model,device,train_arr).mean(1),m30.extract(model,device,test_arr).mean(1))}
    result={'dataset':{'name':'RFMiD2.0','train_n':len(train_arr),'test_n':len(test_arr),'device':str(device)},'models':{},'notes':['RFMiD2 is ordinary color fundus data and is not paired UWF/45-degree data.','Test labels are not used for training; only Training+Validation labels train probes.','The regional model averages frozen 3x3 RetinaRadar embeddings before fitting per-label probes.']}
    for rep,(a,b) in reps.items():
        mu=a.mean(0);sd=a.std(0);sd[sd<1e-8]=1;a=(a-mu)/sd;b=(b-mu)/sd; per=[]
        for j,n in enumerate(names):
            if ytr[:,j].sum()==0 or ytr[:,j].sum()==len(ytr) or len(np.unique(yt[:,j]))<2:continue
            clf=LogisticRegression(C=.1,max_iter=500,solver='liblinear',random_state=42);clf.fit(a,ytr[:,j]);p=clf.predict_proba(b)[:,1];per.append({'label':n,'test_positive':int(yt[:,j].sum()),'auroc':float(roc_auc_score(yt[:,j],p)),'average_precision':float(average_precision_score(yt[:,j],p))})
        result['models'][rep]={'n_labels':len(per),'mean_auroc':float(np.mean([r['auroc'] for r in per])),'mean_average_precision':float(np.mean([r['average_precision'] for r in per])),'per_label':per};print(rep,result['models'][rep]['mean_auroc'],flush=True)
    (HERE/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');(HERE/'REPORT.md').write_text('# Exp38：RFMiD2区域表征外部疾病验证\n\n比较全图冻结特征与3×3区域平均冻结特征在RFMiD2多标签疾病任务上的外部迁移性能。\n\n```json\n'+json.dumps(result,ensure_ascii=False,indent=2)+'\n```\n',encoding='utf-8');print(json.dumps({k:{x:y for x,y in v.items() if x!='per_label'} for k,v in result['models'].items()},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
