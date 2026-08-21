#!/usr/bin/env python3
"""Exp13: doctor-annotated MSHF quality external validation."""
from __future__ import annotations
import csv, json
from pathlib import Path
import numpy as np
import torch, timm, openpyxl
from PIL import Image
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, average_precision_score, f1_score, roc_auc_score

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'7hao/datasets/MSHF_IQA/extracted/MSHF dataset 2.0'
MODEL=ROOT/'7hao/models/retinaradar/efficientnet_b0_retinaradar_model.ckpt'
OUT=ROOT/'7hao/experiments/exp13_mshf_quality_external'; OUT.mkdir(parents=True,exist_ok=True)
MEAN=np.asarray([.485,.456,.406],np.float32); STD=np.asarray([.229,.224,.225],np.float32)

def load_labels():
    # Use the three raw annotator sheets and majority vote. The aggregate
    # workbook contains a formula-based combined sheet whose cached values are
    # incomplete for several sources.
    wb=openpyxl.load_workbook(BASE/'Individual_scores.xlsx.xlsx',read_only=True,data_only=True); out={}
    for row in wb.active.iter_rows(min_row=3,values_only=True):
        if not row or not row[0]: continue
        groups=((1,2,3,4),(6,7,8,9),(11,12,13,14)); vals=[]
        for cols in zip(*groups):
            v=[row[i] for i in cols]
            if any(x is None for x in v): vals.append(None)
            else: vals.append(int(sum(int(x) for x in v)>=2))
        if all(x is not None for x in vals): out[str(row[0])]=[vals[1],vals[0],vals[2],vals[3]]
    return out

def load_model():
    c=torch.load(MODEL,map_location='cpu'); m=timm.create_model('efficientnet_b0',pretrained=False,num_classes=17)
    m.load_state_dict({k.replace('model.','',1):v for k,v in c['state_dict'].items()},strict=True); m.eval()
    d=torch.device('mps' if torch.backends.mps.is_available() else 'cpu'); return m.to(d),d

def prep(paths):
    xs=[]
    for p in paths:
        with Image.open(p) as im: im=im.convert('RGB').resize((256,256),Image.Resampling.BILINEAR).crop((16,16,240,240))
        x=np.asarray(im,np.float32)/255.; x=(x-MEAN)/STD; xs.append(np.transpose(x,(2,0,1)))
    return torch.from_numpy(np.stack(xs)).float()

def extract(m,d,paths):
    out=[]
    for st in range(0,len(paths),32):
        with torch.no_grad(): out.append(m(prep(paths[st:st+32]).to(d)).cpu().numpy())
    return np.vstack(out)

def score_metrics(y,s,threshold=0.5):
    pr=(s>=threshold).astype(int)
    return {'auroc':float(roc_auc_score(y,s)) if len(np.unique(y))==2 else None,'average_precision':float(average_precision_score(y,s)) if y.sum() else None,'accuracy':float(accuracy_score(y,pr)),'f1':float(f1_score(y,pr,zero_division=0))}

def best_threshold(y,s):
    ts=np.linspace(0.01,0.99,197); vals=[f1_score(y,(s>=t).astype(int),zero_division=0) for t in ts]
    return float(ts[int(np.argmax(vals))])

def main():
    label_map=load_labels(); train=sorted((BASE/'AI-use/train').glob('*.[jJ][pP][gG]')); test=sorted((BASE/'AI-use/test').glob('*.[jJ][pP][gG]'))
    train=[p for p in train if p.name in label_map]; test=[p for p in test if p.name in label_map]
    m,d=load_model(); print(f'device={d}; train={len(train)}; test={len(test)}',flush=True)
    ztr=extract(m,d,train); zte=extract(m,d,test)
    # Retinaradar logits: clarity true, illumination true, contrast true,
    # usable true. The first three are direct matches to MSHF; usable is an
    # interpretable proxy for MSHF's overall quality label.
    idx=[8,10,12,16]; names=['clarity','illumination','contrast','overall']
    qtr=1/(1+np.exp(-ztr[:,idx])); qte=1/(1+np.exp(-zte[:,idx]))
    ytr=np.asarray([label_map[p.name] for p in train],int)[:,[1,0,2,3]]; yte=np.asarray([label_map[p.name] for p in test],int)[:,[1,0,2,3]]
    result={'dataset':{'name':'MSHF','train':len(train),'test':len(test),'labels':names},'zero_shot':{},'calibrated':{},'by_source':{},'notes':[]}
    for j,n in enumerate(names): result['zero_shot'][n]=score_metrics(yte[:,j],qte[:,j])
    # One scalar per quality dimension, calibrated on the MSHF training split.
    for j,n in enumerate(names):
        xtr=qtr[:,j:j+1]; xte=qte[:,j:j+1]; clf=LogisticRegression(max_iter=300,C=1.0,solver='lbfgs'); clf.fit(xtr,ytr[:,j]); ptr=clf.predict_proba(xtr)[:,1]; pte=clf.predict_proba(xte)[:,1]; threshold=best_threshold(ytr[:,j],ptr); result['calibrated'][n]=dict(score_metrics(yte[:,j],pte,threshold),threshold=threshold)
    for source in sorted({p.name.split('-')[0] for p in test}):
        ix=np.asarray([p.name.split('-')[0]==source for p in test])
        if ix.sum()<5: continue
        result['by_source'][source]={'n':int(ix.sum()),'overall_positive_rate':float(yte[ix,3].mean()),'retinaradar_usable_mean':float(qte[ix,3].mean()),'retinaradar_usable_std':float(qte[ix,3].std())}
    result['notes']=['Quality labels are derived from the MSHF spreadsheet aggregated from multiple annotators; they are not UWF/45-degree paired labels.','RetinaRadar is evaluated zero-shot and with a one-dimensional logistic calibration trained only on the MSHF training split.','The RetinaRadar usable-positive logit is used as a proxy for MSHF overall quality because the label semantics are not identical.']
    (OUT/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'REPORT.md').write_text('# Exp13：MSHF 医生质量标签外部验证\n\n在 MSHF 的 1042/260 训练测试划分上，评估 RetinaRadar 的清晰度、照明、对比度和可用性输出。结果同时报告零样本性能与训练集校准后的性能。\n\n注意：MSHF 的总体质量与 RetinaRadar 的 usable 语义相近但不完全相同，因此这里只作外部可行性验证。完整结果见 `results.json`。\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
