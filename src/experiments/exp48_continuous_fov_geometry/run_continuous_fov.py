#!/usr/bin/env python3
"""Exp48: continuous FOV fractions, locations and aperture shapes with 4x4 regional masks."""
from __future__ import annotations
import importlib.util, json
from pathlib import Path
import numpy as np, torch

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]; CACHE=ROOT/'7hao/experiments/exp34_shared_uwf_region_cache'; HERE.mkdir(parents=True,exist_ok=True)
sp=importlib.util.spec_from_file_location('ab',ROOT/'7hao/experiments/exp35_region_mask_pool_ablation/run_ablation.py'); ab=importlib.util.module_from_spec(sp); assert sp.loader; sp.loader.exec_module(ab)
meta=json.loads((CACHE/'split_meta.json').read_text()); y={s:np.asarray(meta[s]['y'],int) for s in ('train','val','test')}; z=np.load(CACHE/'region_features_g4.npz'); raw={s:z[f'{s}_features'] for s in y}; mu=raw['train'].reshape(-1,raw['train'].shape[-1]).mean(0); sd=raw['train'].reshape(-1,raw['train'].shape[-1]).std(0); sd[sd<1e-8]=1; X={s:(raw[s]-mu)/sd for s in y}
G=4; centers=np.asarray([((c+.5)/G,(r+.5)/G) for r in range(G) for c in range(G)])
def mask(shape,fraction,dx=0.,dy=0.):
    # fraction is the side-length fraction; each aperture has matched area fraction fraction^2.
    cx=.5+dx*(1-fraction)/2; cy=.5+dy*(1-fraction)/2
    if shape=='rect': keep=(np.abs(centers[:,0]-cx)<=fraction/2)&(np.abs(centers[:,1]-cy)<=fraction/2)
    else:
        radius=fraction/np.sqrt(np.pi); keep=((centers[:,0]-cx)**2+(centers[:,1]-cy)**2)<=radius**2
    if not keep.any(): keep[np.argmin((centers[:,0]-cx)**2+(centers[:,1]-cy)**2)]=True
    return keep.astype(np.float32)
def evaluate(model,dev,m):
    mm=np.repeat(m[None,:],len(y['test']),0)
    return ab.evaluate(model,dev,X['test'],y['test'],mm)
def main():
    scenarios=[]
    for f in (.35,.45,.55,.65,.75,.90): scenarios.append((f'rect_center_{f:.2f}','rect',f,0.,0.))
    for pos,dx,dy in (('center',0,0),('left',-1,0),('right',1,0),('up',0,-1),('down',0,1)):
        scenarios.append((f'rect_{pos}_0.55','rect',.55,dx,dy))
    for f in (.35,.45,.55,.65,.75,.90): scenarios.append((f'circle_center_{f:.2f}','circle',f,0.,0.))
    rows=[]
    for seed in (0,1,2,3,4):
        model,dev,vs,ep=ab.train(X['train'],y['train'],X['val'],y['val'],'attention',.30,seed)
        for name,shape,f,dx,dy in scenarios:
            m=mask(shape,f,dx,dy); rows.append({'seed':seed,'scenario':name,'shape':shape,'linear_fraction':f,'dx':dx,'dy':dy,'visible_regions':np.flatnonzero(m).tolist(),'visible_region_fraction':float(m.mean()),'best_val_macro_f1':float(vs),'epochs':int(ep),**evaluate(model,dev,m)})
    aggregate={}
    for name,_,_,_,_ in scenarios:
        q=[r for r in rows if r['scenario']==name]; aggregate[name]={k:{'mean':float(np.mean([r[k] for r in q])),'std':float(np.std([r[k] for r in q],ddof=1))} for k in ('accuracy','macro_f1','severity_mae','underestimation_rate')}
    result={'grid':'4x4','n_seeds':5,'rows':rows,'aggregate':aggregate,'notes':['Visibility is determined by 4x4 regional-cell centers within a rectangle or area-matched circular aperture.','This is a geometric visibility proxy over frozen full-image regional embeddings, not a real camera acquisition.','All models are trained with 30% random region masking.']}
    (HERE/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8'); (HERE/'REPORT.md').write_text('# Exp48：连续视野比例、位置与形状鲁棒性\n\n在4×4区域模型上，比较连续中心视野比例、55%视野的位置变化和等面积圆形视野。\n\n```json\n'+json.dumps(result,ensure_ascii=False,indent=2)+'\n```\n',encoding='utf-8'); print(json.dumps(aggregate,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
