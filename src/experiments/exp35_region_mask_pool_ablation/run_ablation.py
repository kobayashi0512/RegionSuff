#!/usr/bin/env python3
"""Tasks 2-4: grid granularity, mask ratio and pooling ablations."""
from __future__ import annotations
import copy, json
from pathlib import Path
import numpy as np, torch
from torch import nn
import importlib.util
from sklearn.metrics import accuracy_score

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]; CACHE=ROOT/'7hao/experiments/exp34_shared_uwf_region_cache'; HERE.mkdir(parents=True,exist_ok=True)
M30=ROOT/'7hao/experiments/exp30_deep_region_attention/run_deep_region_attention.py'; sp=importlib.util.spec_from_file_location('m30',M30); m30=importlib.util.module_from_spec(sp); assert sp.loader; sp.loader.exec_module(m30)
meta=json.loads((CACHE/'split_meta.json').read_text())

class PoolNet(nn.Module):
    def __init__(self,f,pool):
        super().__init__(); self.pool=pool; self.e=nn.Sequential(nn.Linear(f,128),nn.LayerNorm(128),nn.ReLU()); self.a=nn.Sequential(nn.Linear(128,48),nn.Tanh(),nn.Linear(48,1)); self.c=nn.Linear(128,3)
    def forward(self,x,mask):
        h=self.e(x)
        if self.pool=='attention':
            s=self.a(h).squeeze(-1).masked_fill(mask<=0,-1e4); w=torch.softmax(s,1); z=(w.unsqueeze(-1)*h).sum(1)
        elif self.pool=='max': z=(h.masked_fill(mask.unsqueeze(-1)<=0,-1e4)).max(1).values; w=mask/mask.sum(1,keepdim=True).clamp_min(1)
        else: w=mask/mask.sum(1,keepdim=True).clamp_min(1); z=(w.unsqueeze(-1)*h).sum(1)
        return self.c(z),w

def mask_random(n,R,p,rng):
    m=(rng.random((n,R))>p).astype(np.float32); empty=m.sum(1)==0; m[empty,0]=1; return m
def eval_mask(name,n,g):
    m=np.ones((n,g*g),np.float32)
    if name=='full':return m
    m[:]=0; center=(g-1)/2
    for r in range(g):
        for c in range(g):
            if name=='center' and abs(r-center)<=.51 and abs(c-center)<=.51:m[:,r*g+c]=1
            if name=='cross' and (abs(r-center)<=.51 or abs(c-center)<=.51):m[:,r*g+c]=1
    if not m.any():m[:,0]=1
    return m
def train(X,y,Xv,yv,pool,p,seed=42):
    torch.manual_seed(seed); rng=np.random.default_rng(seed); dev=torch.device('mps' if torch.backends.mps.is_available() else 'cpu'); model=PoolNet(X.shape[-1],pool).to(dev); xt=torch.from_numpy(X).float().to(dev); yt=torch.from_numpy(y).long().to(dev); xvt=torch.from_numpy(Xv).float().to(dev); opt=torch.optim.AdamW(model.parameters(),lr=1.5e-3,weight_decay=3e-4); best=None; bests=-1; patience=0
    for ep in range(180):
        mt=torch.from_numpy(mask_random(len(X),X.shape[1],p,rng)).float().to(dev); out,_=model(xt,mt); loss=nn.functional.cross_entropy(out,yt); opt.zero_grad(); loss.backward(); opt.step()
        with torch.no_grad(): vp,_=model(xvt,torch.ones((len(Xv),X.shape[1]),device=dev)); pred=vp.argmax(1).cpu().numpy(); s=m30.baseline.macro_f1(yv,pred)
        if s>bests:bests=s; best=copy.deepcopy({k:v.detach().cpu() for k,v in model.state_dict().items()});patience=0
        else:patience+=1
        if patience>=25:break
    model.load_state_dict(best); return model,dev,bests,ep+1
def evaluate(model,dev,X,y,mask):
    with torch.no_grad(): p=torch.softmax(model(torch.from_numpy(X).float().to(dev),torch.from_numpy(mask).float().to(dev))[0],1).cpu().numpy(); pred=p.argmax(1)
    return {'accuracy':float(np.mean(pred==y)),'macro_f1':m30.baseline.macro_f1(y,pred),'severity_mae':float(np.mean(abs(pred-y))),'underestimation_rate':float(np.mean(pred<y))}
def main():
    y={s:np.asarray(meta[s]['y'],int) for s in ('train','val','test')}; result={'dataset':{'split_counts':{s:np.bincount(y[s],minlength=3).tolist() for s in y}},'grid_granularity':{},'pooling':{},'mask_ratio':{},'notes':['Tasks 2-4 share the same patient-level UWF split and frozen regional feature cache.','The center/cross masks are geometric proxies.','Validation macro-F1 is used for early stopping; test is evaluated once.']}
    for g in (1,2,3,4):
        z=np.load(CACHE/f'region_features_g{g}.npz'); raw={s:z[f'{s}_features'] for s in y}; mu=raw['train'].reshape(-1,raw['train'].shape[-1]).mean(0); sd=raw['train'].reshape(-1,raw['train'].shape[-1]).std(0); sd[sd<1e-8]=1; X={s:(raw[s]-mu)/sd for s in y}; result['grid_granularity'][str(g)]={}
        for pool in ('mean','max','attention'):
            mdl,dev,vs,ep=train(X['train'],y['train'],X['val'],y['val'],pool,.30,42); result['grid_granularity'][str(g)][pool]={'best_val_macro_f1':float(vs),'epochs':ep,'full':evaluate(mdl,dev,X['test'],y['test'],eval_mask('full',len(y['test']),g)),'center':evaluate(mdl,dev,X['test'],y['test'],eval_mask('center',len(y['test']),g)),'cross':evaluate(mdl,dev,X['test'],y['test'],eval_mask('cross',len(y['test']),g))}
    z=np.load(CACHE/'region_features_g3.npz'); raw={s:z[f'{s}_features'] for s in y}; mu=raw['train'].reshape(-1,raw['train'].shape[-1]).mean(0); sd=raw['train'].reshape(-1,raw['train'].shape[-1]).std(0); sd[sd<1e-8]=1; X={s:(raw[s]-mu)/sd for s in y}
    for p in (0,.15,.30,.45,.60):
        mdl,dev,vs,ep=train(X['train'],y['train'],X['val'],y['val'],'attention',p,42); result['mask_ratio'][str(p)]={'best_val_macro_f1':float(vs),'epochs':ep,'full':evaluate(mdl,dev,X['test'],y['test'],eval_mask('full',len(y['test']),3)),'center':evaluate(mdl,dev,X['test'],y['test'],eval_mask('center',len(y['test']),3)),'cross':evaluate(mdl,dev,X['test'],y['test'],eval_mask('cross',len(y['test']),3))}
    result['pooling']=result['grid_granularity']['3']; (HERE/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8'); (HERE/'REPORT.md').write_text('# Exp35：区域粒度、mask比例和聚合方式消融\n\n统一评估3×3区域方法的关键设计选择。\n\n```json\n'+json.dumps(result,ensure_ascii=False,indent=2)+'\n```\n',encoding='utf-8'); print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
