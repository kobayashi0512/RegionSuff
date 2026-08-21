#!/usr/bin/env python3
"""Exp43: five-seed robustness of the 4x4 regional model."""
from __future__ import annotations
import copy, importlib.util, json
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]; CACHE=ROOT/'7hao/experiments/exp34_shared_uwf_region_cache'; HERE.mkdir(parents=True,exist_ok=True)
sp=importlib.util.spec_from_file_location('ab',ROOT/'7hao/experiments/exp35_region_mask_pool_ablation/run_ablation.py'); ab=importlib.util.module_from_spec(sp); assert sp.loader; sp.loader.exec_module(ab)
meta=json.loads((CACHE/'split_meta.json').read_text()); y={s:np.asarray(meta[s]['y'],int) for s in ('train','val','test')}
z=np.load(CACHE/'region_features_g4.npz'); raw={s:z[f'{s}_features'] for s in y}; mu=raw['train'].reshape(-1,raw['train'].shape[-1]).mean(0); sd=raw['train'].reshape(-1,raw['train'].shape[-1]).std(0); sd[sd<1e-8]=1; X={s:(raw[s]-mu)/sd for s in y}

def main():
    rows=[]
    for seed in (0,1,2,3,4):
        mdl,dev,vs,ep=ab.train(X['train'],y['train'],X['val'],y['val'],'attention',.30,seed)
        for view in ('full','center','cross'):
            rows.append({'seed':seed,'view':view,'best_val_macro_f1':float(vs),'epochs':int(ep),**ab.evaluate(mdl,dev,X['test'],y['test'],ab.eval_mask(view,len(y['test']),4))})
    result={'grid':'4x4','n_seeds':5,'rows':rows,'aggregate':{}}
    for v in ('full','center','cross'):
        q=[r for r in rows if r['view']==v]; result['aggregate'][v]={k:{'mean':float(np.mean([r[k] for r in q])),'std':float(np.std([r[k] for r in q],ddof=1))} for k in ('accuracy','macro_f1','severity_mae','underestimation_rate')}
    (HERE/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    (HERE/'REPORT.md').write_text('# Exp43：4×4区域模型五随机种子稳定性\n\n在共享patient-level split和同一attention聚合器下，评估4×4区域粒度的五随机种子稳定性。\n\n```json\n'+json.dumps(result,ensure_ascii=False,indent=2)+'\n```\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
