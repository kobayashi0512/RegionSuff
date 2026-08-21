#!/usr/bin/env python3
"""Exp16: conservative source-held-out audit for MSHF quality labels."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import torch, timm, openpyxl
from PIL import Image
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score

ROOT=Path(__file__).resolve().parents[3]; BASE=ROOT/'7hao/datasets/MSHF_IQA/extracted/MSHF dataset 2.0'; MODEL=ROOT/'7hao/models/retinaradar/efficientnet_b0_retinaradar_model.ckpt'; OUT=ROOT/'7hao/experiments/exp16_mshf_source_holdout'; OUT.mkdir(parents=True,exist_ok=True)
MEAN=np.asarray([.485,.456,.406],np.float32); STD=np.asarray([.229,.224,.225],np.float32)

def load_label_map():
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
    c=torch.load(MODEL,map_location='cpu'); m=timm.create_model('efficientnet_b0',pretrained=False,num_classes=17); m.load_state_dict({k.replace('model.','',1):v for k,v in c['state_dict'].items()},strict=True); m.eval(); d=torch.device('mps' if torch.backends.mps.is_available() else 'cpu'); return m.to(d),d

def prep(paths):
    xs=[]
    for p in paths:
        with Image.open(p) as im: im=im.convert('RGB').resize((256,256),Image.Resampling.BILINEAR).crop((16,16,240,240))
        x=np.asarray(im,np.float32)/255.; x=(x-MEAN)/STD; xs.append(np.transpose(x,(2,0,1)))
    return torch.from_numpy(np.stack(xs)).float()

def extract(m,d,paths):
    out=[]
    for st in range(0,len(paths),32):
        with torch.no_grad(): out.append(m.global_pool(m.forward_features(prep(paths[st:st+32]).to(d))).flatten(1).cpu().numpy())
    return np.vstack(out)

def main():
    lab=load_label_map(); paths=sorted([p for split in ('train','test') for p in (BASE/'AI-use'/split).glob('*.jpg') if p.name in lab]); y=np.asarray([lab[p.name] for p in paths],int); src=np.asarray([p.name.rsplit('-',1)[0] for p in paths]); names=['clarity','illumination','contrast','overall']; m,d=load_model(); print(f'device={d}; n={len(paths)}; sources={sorted(set(src))}',flush=True); X=extract(m,d,paths); result={'dataset':{'n':len(paths),'sources':{s:int((src==s).sum()) for s in sorted(set(src))},'labels':names,'patient_id_available':False},'leave_one_source_out':{},'notes':[]}
    for hold in sorted(set(src)):
        tr=src!=hold; te=src==hold; result['leave_one_source_out'][hold]={'n_test':int(te.sum()),'metrics':{}}
        mu=X[tr].mean(0); sd=X[tr].std(0); sd[sd<1e-8]=1.; xtr=(X[tr]-mu)/sd; xte=(X[te]-mu)/sd
        for j,n in enumerate(names):
            if len(np.unique(y[tr,j]))<2 or len(np.unique(y[te,j]))<2: continue
            clf=LogisticRegression(max_iter=300,C=.1,solver='liblinear',random_state=42); clf.fit(xtr,y[tr,j]); p=clf.predict_proba(xte)[:,1]; result['leave_one_source_out'][hold]['metrics'][n]={'auroc':float(roc_auc_score(y[te,j],p)),'average_precision':float(average_precision_score(y[te,j],p)),'positive_rate':float(y[te,j].mean())}
    result['notes']=['The released MSHF package contains quality spreadsheets but no patient identifier field; patient-level grouping cannot be verified from the release.','Therefore this audit uses leave-one-source-out evaluation as a conservative domain-shift check.','These are frozen RetinaRadar features with source-held-out linear probes, not a clinical validation study.']
    (OUT/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8'); (OUT/'REPORT.md').write_text('# Exp16：MSHF 来源留一审计\n\nMSHF 公布包没有患者ID字段，无法进行严格患者级重划分；本实验采用来源留一（leave-one-source-out）验证作为更严格的域外审计。每次留出一个来源，其余来源训练冻结 RetinaRadar 特征线性探针。\n\n完整结果见 `results.json`。\n',encoding='utf-8'); print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
