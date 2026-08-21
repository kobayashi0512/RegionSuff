#!/usr/bin/env python3
"""Task 9: bootstrap CI and paired comparison for the final cached model."""
from __future__ import annotations
import csv, importlib.util, json
from pathlib import Path
import numpy as np, torch

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];CACHE=ROOT/'7hao/experiments/exp34_shared_uwf_region_cache';HERE.mkdir(parents=True,exist_ok=True)
sp=importlib.util.spec_from_file_location('ab',ROOT/'7hao/experiments/exp35_region_mask_pool_ablation/run_ablation.py');ab=importlib.util.module_from_spec(sp);assert sp.loader;sp.loader.exec_module(ab)
meta=json.loads((CACHE/'split_meta.json').read_text());y={s:np.asarray(meta[s]['y'],int) for s in ('train','val','test')};z=np.load(CACHE/'region_features_g3.npz');raw={s:z[f'{s}_features'] for s in y};mu=raw['train'].reshape(-1,raw['train'].shape[-1]).mean(0);sd=raw['train'].reshape(-1,raw['train'].shape[-1]).std(0);sd[sd<1e-8]=1;X={s:(raw[s]-mu)/sd for s in y}
def metrics(y,p):
    pr=p.argmax(1);return {'accuracy':float(np.mean(pr==y)),'macro_f1':ab.m30.baseline.macro_f1(y,pr),'severity_mae':float(np.mean(abs(pr-y))),'underestimation_rate':float(np.mean(pr<y))}
def main():
    mdl,dev,vs,ep=ab.train(X['train'],y['train'],X['val'],y['val'],'attention',.30,42);xt=torch.from_numpy(X['test']).float().to(dev);mt=torch.from_numpy(ab.eval_mask('cross',len(y['test']),3)).float().to(dev)
    with torch.no_grad():p=torch.softmax(mdl(xt,mt)[0],1).cpu().numpy()
    old_rows={r['image']:r for r in csv.DictReader((ROOT/'7hao/experiments/exp23_ordinal_pdr/test_predictions.csv').open(encoding='utf-8')) if r['model']=='central_frozen_balanced'}; old=np.asarray([int(old_rows[p]['pred_label']) for p in meta['test']['paths']]); yt=y['test'];rng=np.random.default_rng(20260810);keys=('accuracy','macro_f1','severity_mae','underestimation_rate');vals={k:[] for k in keys};dacc=[];dunder=[]
    for _ in range(2000):
        ix=rng.integers(0,len(yt),len(yt));mm=metrics(yt[ix],p[ix]);
        for k in keys:vals[k].append(mm[k])
        pp=p[ix].argmax(1);dacc.append(float(np.mean(pp==yt[ix])-np.mean(old[ix]==yt[ix])));dunder.append(float(np.mean(pp<yt[ix])-np.mean(old[ix]<yt[ix])))
    base=metrics(yt,p); result={'model':{'best_val_macro_f1':float(vs),'epochs':int(ep),'test':base,'bootstrap_2000':{k:{'estimate':base[k],'ci95':[float(np.quantile(v,.025)),float(np.quantile(v,.975))]} for k,v in vals.items()}},'paired_vs_exp23_central_balanced':{'accuracy_delta':{'estimate':float(np.mean(p.argmax(1)==yt)-np.mean(old==yt)),'ci95':[float(np.quantile(dacc,.025)),float(np.quantile(dacc,.975))]},'underestimation_delta':{'estimate':float(np.mean(p.argmax(1)<yt)-np.mean(old<yt)),'ci95':[float(np.quantile(dunder,.025)),float(np.quantile(dunder,.975))]}}}
    (HERE/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');(HERE/'REPORT.md').write_text('# Exp41：Bootstrap与配对统计\n\n对最终区域模型进行2000次bootstrap，并与Exp23中心冻结类别均衡模型进行同图配对比较。\n\n```json\n'+json.dumps(result,ensure_ascii=False,indent=2)+'\n```\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
