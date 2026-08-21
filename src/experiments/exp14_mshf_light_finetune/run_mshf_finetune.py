#!/usr/bin/env python3
"""Exp14: lightweight fine-tuning of a retinal quality model on MSHF."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn
import timm
import openpyxl
from PIL import Image
from sklearn.metrics import average_precision_score, f1_score, roc_auc_score

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'7hao/datasets/MSHF_IQA/extracted/MSHF dataset 2.0'
MODEL=ROOT/'7hao/models/retinaradar/efficientnet_b0_retinaradar_model.ckpt'
OUT=ROOT/'7hao/experiments/exp14_mshf_light_finetune'; OUT.mkdir(parents=True,exist_ok=True)
MEAN=np.asarray([.485,.456,.406],np.float32); STD=np.asarray([.229,.224,.225],np.float32)

def labels():
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

def tensor(paths):
    xs=[]
    for p in paths:
        with Image.open(p) as im: im=im.convert('RGB').resize((256,256),Image.Resampling.BILINEAR).crop((16,16,240,240))
        x=np.asarray(im,np.float32)/255.; x=(x-MEAN)/STD; xs.append(np.transpose(x,(2,0,1)))
    return torch.from_numpy(np.stack(xs)).float()

def model():
    c=torch.load(MODEL,map_location='cpu'); m=timm.create_model('efficientnet_b0',pretrained=False,num_classes=17)
    m.load_state_dict({k.replace('model.','',1):v for k,v in c['state_dict'].items()},strict=True)
    d=torch.device('mps' if torch.backends.mps.is_available() else 'cpu'); return m.to(d),d

class QualityHead(nn.Module):
    def __init__(self, backbone, train_last=False):
        super().__init__(); self.backbone=backbone; self.head=nn.Linear(1280,4)
        for p in self.backbone.parameters(): p.requires_grad=False
        if train_last:
            for module in (self.backbone.blocks[-1],self.backbone.conv_head,self.backbone.bn2):
                for p in module.parameters(): p.requires_grad=True
    def forward(self,x):
        z=self.backbone.forward_features(x); z=self.backbone.global_pool(z).flatten(1); return self.head(z)

def run_train(model,d,paths,y,epochs,lr,weight):
    model.train(); model.backbone.eval(); model.head.train()
    # Keep BatchNorm in the last block trainable only when requested.
    for module in (model.backbone.blocks[-1],model.backbone.conv_head,model.backbone.bn2):
        if any(p.requires_grad for p in module.parameters()): module.train()
    pos=np.clip(y.sum(0),1,None); neg=np.clip(len(y)-y.sum(0),1,None); pw=torch.tensor(neg/pos,dtype=torch.float32,device=d)
    loss_fn=nn.BCEWithLogitsLoss(pos_weight=pw); opt=torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],lr=lr,weight_decay=1e-4)
    rng=np.random.default_rng(42); bs=32
    for ep in range(epochs):
        order=rng.permutation(len(paths)); losses=[]
        for st in range(0,len(paths),bs):
            ix=order[st:st+bs]; x=tensor([paths[i] for i in ix]).to(d); yy=torch.tensor(y[ix],dtype=torch.float32,device=d)
            opt.zero_grad(set_to_none=True); loss=loss_fn(model(x),yy); loss.backward(); opt.step(); losses.append(float(loss.detach().cpu()))
        print(f'epoch={ep+1}/{epochs} loss={np.mean(losses):.4f}',flush=True)

def predict(model,d,paths):
    model.eval(); out=[]
    for st in range(0,len(paths),32):
        with torch.no_grad(): out.append(torch.sigmoid(model(tensor(paths[st:st+32]).to(d))).cpu().numpy())
    return np.vstack(out)

def best_t(y,p):
    ts=np.linspace(.02,.98,193); f=[f1_score(y,(p>=t).astype(int),zero_division=0) for t in ts]; return float(ts[int(np.argmax(f))])

def metrics(y,p,t):
    return {'auroc':float(roc_auc_score(y,p)) if len(np.unique(y))==2 else None,'average_precision':float(average_precision_score(y,p)) if y.sum() else None,'f1':float(f1_score(y,(p>=t).astype(int),zero_division=0)),'threshold':float(t)}

def main():
    lab=labels(); tr=sorted([p for p in (BASE/'AI-use/train').glob('*.[jJ][pP][gG]') if p.name in lab]); te=sorted([p for p in (BASE/'AI-use/test').glob('*.[jJ][pP][gG]') if p.name in lab]); ytr=np.asarray([lab[p.name] for p in tr],np.int64); yte=np.asarray([lab[p.name] for p in te],np.int64); m,d=model()
    result={'dataset':{'train':len(tr),'test':len(te),'device':str(d),'labels':['clarity','illumination','contrast','overall']},'models':{},'notes':[]}
    for name,last,epochs,lr in [('frozen_backbone_head',False,12,2e-3),('last_block_head',True,8,1e-4)]:
        q=QualityHead(m,last).to(d); run_train(q,d,tr,ytr,epochs,lr,1.0); ptr=predict(q,d,tr); pte=predict(q,d,te); result['models'][name]={}
        for j,label in enumerate(result['dataset']['labels']): result['models'][name][label]=metrics(yte[:,j],pte[:,j],best_t(ytr[:,j],ptr[:,j]))
        torch.save(q.state_dict(),OUT/f'{name}.pt')
    result['notes']=['This is lightweight supervised adaptation on MSHF doctor quality labels, not full foundation-model fine-tuning.','The frozen model head and last-block model are trained only on MSHF train images and evaluated on the held-out MSHF test images.','Thresholds are selected on training data to avoid fixed 0.5 threshold bias under class imbalance.']
    (OUT/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'REPORT.md').write_text('# Exp14：MSHF 质量任务轻量微调\n\n比较冻结 RetinaRadar 骨干只训练新质量头，以及只解冻 EfficientNet-B0 最后 block、conv_head、bn2 的轻量微调。阈值只在训练集选择，测试集只作最终评估。\n\n完整结果见 `results.json`。\n',encoding='utf-8'); print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
