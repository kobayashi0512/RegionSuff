#!/usr/bin/env python3
"""Task 7: validate attention weights with leave-one-region-out perturbations."""
from __future__ import annotations
import importlib.util,json
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];CACHE=ROOT/'7hao/experiments/exp34_shared_uwf_region_cache';HERE.mkdir(parents=True,exist_ok=True)
sp=importlib.util.spec_from_file_location('ab',ROOT/'7hao/experiments/exp35_region_mask_pool_ablation/run_ablation.py');ab=importlib.util.module_from_spec(sp);assert sp.loader;sp.loader.exec_module(ab)
meta=json.loads((CACHE/'split_meta.json').read_text());y={s:np.asarray(meta[s]['y'],int) for s in ('train','val','test')};z=np.load(CACHE/'region_features_g3.npz');raw={s:z[f'{s}_features'] for s in y};mu=raw['train'].reshape(-1,raw['train'].shape[-1]).mean(0);sd=raw['train'].reshape(-1,raw['train'].shape[-1]).std(0);sd[sd<1e-8]=1;X={s:(raw[s]-mu)/sd for s in y}
def one_removed(n,j):m=np.ones((n,9),np.float32);m[:,j]=0;return m
def main():
    mdl,dev,vs,ep=ab.train(X['train'],y['train'],X['val'],y['val'],'attention',.30,42);full=ab.eval_mask('full',len(y['test']),3);fullm=ab.evaluate(mdl,dev,X['test'],y['test'],full); import torch
    with torch.no_grad():_,att=mdl(torch.from_numpy(X['test']).float().to(dev),torch.ones((len(y['test']),9),device=dev));att=att.cpu().numpy()
    rows=[]
    for j in range(9):
        met=ab.evaluate(mdl,dev,X['test'],y['test'],one_removed(len(y['test']),j));rows.append({'region':j,'mean_attention':float(att[:,j].mean()),'performance_drop_macro_f1':float(fullm['macro_f1']-met['macro_f1']),'performance_drop_accuracy':float(fullm['accuracy']-met['accuracy']),'occluded_metrics':met})
    a=np.asarray([r['mean_attention'] for r in rows]);d=np.asarray([r['performance_drop_macro_f1'] for r in rows]);corr=spearmanr(a,d)
    result={'full_metrics':fullm,'rows':rows,'attention_occlusion_spearman':{'rho':float(corr.statistic),'p_value':float(corr.pvalue)},'notes':['Each test image is evaluated with one region masked at a time; the model and test labels are unchanged.','Attention is considered mechanistically supported only if its regional ranking aligns with performance loss, not merely because a heatmap looks plausible.']}
    (HERE/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');(HERE/'REPORT.md').write_text('# Exp39：注意力与逐区域遮挡验证\n\n用leave-one-region-out性能下降检验Exp30注意力权重是否具有机制一致性。\n\n```json\n'+json.dumps(result,ensure_ascii=False,indent=2)+'\n```\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
