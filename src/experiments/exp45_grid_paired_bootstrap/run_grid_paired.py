#!/usr/bin/env python3
"""Exp45: paired 3x3 vs 4x4 comparison with per-seed bootstrap CIs."""
from __future__ import annotations
import copy, importlib.util, json
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]; CACHE=ROOT/'7hao/experiments/exp34_shared_uwf_region_cache'; HERE.mkdir(parents=True,exist_ok=True)
sp=importlib.util.spec_from_file_location('ab',ROOT/'7hao/experiments/exp35_region_mask_pool_ablation/run_ablation.py'); ab=importlib.util.module_from_spec(sp); assert sp.loader; sp.loader.exec_module(ab)
meta=json.loads((CACHE/'split_meta.json').read_text()); y={s:np.asarray(meta[s]['y'],int) for s in ('train','val','test')}
def load(g):
    z=np.load(CACHE/f'region_features_g{g}.npz'); raw={s:z[f'{s}_features'] for s in y}; mu=raw['train'].reshape(-1,raw['train'].shape[-1]).mean(0); sd=raw['train'].reshape(-1,raw['train'].shape[-1]).std(0); sd[sd<1e-8]=1; return {s:(raw[s]-mu)/sd for s in y}
def pred(g,X,seed,view):
    mdl,dev,vs,ep=ab.train(X['train'],y['train'],X['val'],y['val'],'attention',.30,seed)
    import torch
    with torch.no_grad():
        p=torch.softmax(mdl(torch.from_numpy(X['test']).float().to(dev),torch.from_numpy(ab.eval_mask(view,len(y['test']),g)).float().to(dev))[0],1).cpu().numpy()
    return p.argmax(1), {'best_val_macro_f1':float(vs),'epochs':int(ep)}
def metrics(y,p): return {'accuracy':float(np.mean(p==y)),'macro_f1':float(ab.m30.baseline.macro_f1(y,p)),'mae':float(np.mean(np.abs(p-y))),'underestimation':float(np.mean(p<y))}
def boot_delta(y,p3,p4,n=2000,seed=123):
    rng=np.random.default_rng(seed); vals=[]
    for _ in range(n):
        ix=rng.integers(0,len(y),len(y)); vals.append([metrics(y[ix],p4[ix])[k]-metrics(y[ix],p3[ix])[k] for k in ('accuracy','macro_f1','mae','underestimation')])
    a=np.asarray(vals); return {k:{'mean':float(a[:,i].mean()),'ci95':[float(np.quantile(a[:,i],.025)),float(np.quantile(a[:,i],.975))]} for i,k in enumerate(('accuracy','macro_f1','mae','underestimation'))}
def main():
    X3=load(3); X4=load(4); rows=[]
    for seed in (0,1,2,3,4):
        for view in ('full','cross'):
            p3,m3=pred(3,X3,seed,view); p4,m4=pred(4,X4,seed,view)
            rows.append({'seed':seed,'view':view,'metrics_3x3':metrics(y['test'],p3),'metrics_4x4':metrics(y['test'],p4),'delta_4x4_minus_3x3':boot_delta(y['test'],p3,p4,2000,seed+100)})
    result={'comparison':'4x4 minus 3x3','n_seeds':5,'rows':rows,'notes':['Paired bootstrap resamples the same held-out test images within each seed.','Each grid is normalized using its own training split statistics.','CIs are per-seed exploratory intervals, not a replacement for independent external validation.']}
    (HERE/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8'); (HERE/'REPORT.md').write_text('# Exp45：3×3与4×4同图配对比较\n\n在相同测试图像、相同随机种子和相同attention聚合器下比较4×4与3×3，并对每个种子做2000次paired bootstrap。\n\n```json\n'+json.dumps(result,ensure_ascii=False,indent=2)+'\n```\n',encoding='utf-8'); print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
