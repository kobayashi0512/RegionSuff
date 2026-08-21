#!/usr/bin/env python3
"""Exp54: paired bootstrap CIs for independent MMRDR UWF view comparisons."""
from __future__ import annotations
import csv, importlib.util, json
from pathlib import Path
import numpy as np
import torch

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]; HERE.mkdir(parents=True,exist_ok=True)
DATA=ROOT/'7hao/datasets/MMRDR_figshare/extracted/MMRDR-UWF'; CACHE=ROOT/'7hao/experiments/exp34_shared_uwf_region_cache'; E53=ROOT/'7hao/experiments/exp53_mmrdr_uwf_external_fov'
sp=importlib.util.spec_from_file_location('ab',ROOT/'7hao/experiments/exp35_region_mask_pool_ablation/run_ablation.py'); ab=importlib.util.module_from_spec(sp); assert sp.loader; sp.loader.exec_module(ab)
sp2=importlib.util.spec_from_file_location('m30',ROOT/'7hao/experiments/exp30_deep_region_attention/run_deep_region_attention.py'); m30=importlib.util.module_from_spec(sp2); assert sp2.loader; sp2.loader.exec_module(m30)

def target_labels():
    ys=[]
    with (DATA/'UWF.csv').open(newline='',encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            if r['image'].startswith('img/ts'):
                g=int(r['grade']); ys.append(0 if g==0 else 1 if g<=3 else 2)
    return np.asarray(ys,int)

def mf1(y,p): return float(ab.m30.baseline.macro_f1(y,p))
def point_metrics(y,p): return {'accuracy':float(np.mean(p==y)),'macro_f1':mf1(y,p),'severity_mae':float(np.mean(np.abs(p-y))),'underestimation_rate':float(np.mean(p<y))}

def bootstrap(y, preds, n=2000, seed=20260812):
    rng=np.random.default_rng(seed); N=len(y); views=list(preds); out={}
    for v in views: out[v]={k:[] for k in ('accuracy','macro_f1','severity_mae','underestimation_rate')}
    diffs={v:{k:[] for k in out[views[0]]} for v in views if v!='full'}
    for _ in range(n):
        ix=rng.integers(0,N,N); yy=y[ix]; ms={v:point_metrics(yy,preds[v][ix]) for v in views}
        for v in views:
            for k,val in ms[v].items(): out[v][k].append(val)
        for v in diffs:
            for k in diffs[v]: diffs[v][k].append(ms[v][k]-ms['full'][k])
    def ci(a): return [float(np.quantile(a,.025)),float(np.quantile(a,.975))]
    return {'metric_ci':{v:{k:{'estimate':float(np.mean(a)),'ci95':ci(a)} for k,a in out[v].items()} for v in views},'paired_delta_vs_full':{v:{k:{'estimate':float(np.mean(a)),'ci95':ci(a)} for k,a in diffs[v].items()} for v in diffs},'n_bootstrap':n,'seed':seed}

def main():
    z=np.load(CACHE/'region_features_g3.npz'); meta=json.loads((CACHE/'split_meta.json').read_text()); raw=z['train_features']; mu=raw.reshape(-1,raw.shape[-1]).mean(0); sd=raw.reshape(-1,raw.shape[-1]).std(0); sd[sd<1e-8]=1
    xtr=(raw-mu)/sd; xv=(z['val_features']-mu)/sd; ytr=np.asarray(meta['train']['y'],int); yv=np.asarray(meta['val']['y'],int)
    fc=E53/'mmrdr_test_raw_region_features.npz'
    if not fc.exists(): raise FileNotFoundError('Exp53 feature cache not ready: '+str(fc))
    x=(np.load(fc)['features']-mu)/sd; y=target_labels(); assert len(x)==len(y)
    preds_by_seed=[]
    for seed in range(5):
        head,hdev,source_f1,epochs=ab.train(xtr,ytr,xv,yv,'attention',.30,seed); pred={}
        for view in ('full','center','center_plus_cross'):
            mask=torch.from_numpy(m30.mask_named(view,len(y))).float().to(hdev)
            with torch.no_grad(): pred[view]=head(torch.from_numpy(x).float().to(hdev),mask)[0].argmax(1).cpu().numpy()
        preds_by_seed.append({'seed':seed,'best_source_val_macro_f1':float(source_f1),'epochs':int(epochs),'point_metrics':{v:point_metrics(y,pred[v]) for v in pred},'bootstrap':bootstrap(y,pred,n=2000,seed=20260812+seed)})
    keys=('accuracy','macro_f1','severity_mae','underestimation_rate'); aggregate={}
    for v in ('full','center','center_plus_cross'):
        aggregate[v]={k:{'mean':float(np.mean([r['point_metrics'][v][k] for r in preds_by_seed])),'std':float(np.std([r['point_metrics'][v][k] for r in preds_by_seed],ddof=1))} for k in keys}
    output={'dataset':'MMRDR-UWF official testing split','protocol':'Five source-UWF-trained heads; paired 2000-resample bootstrap uses the same target images for each view. No MMRDR labels enter training or model selection.','aggregate_point_metrics':aggregate,'per_seed':preds_by_seed,'notes':['The CI is a paired image-level uncertainty interval for view differences, not an independent-dataset confidence interval.','The MMRDR official test split is patient-level according to its data descriptor.']}
    (HERE/'results.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8'); (HERE/'REPORT.md').write_text('# Exp54：MMRDR完整/受限视野配对Bootstrap\n\n```json\n'+json.dumps(output,ensure_ascii=False,indent=2)+'\n```\n',encoding='utf-8'); print(json.dumps({'aggregate_point_metrics':aggregate,'paired_deltas_seed0':preds_by_seed[0]['bootstrap']['paired_delta_vs_full']},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
