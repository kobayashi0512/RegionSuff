#!/usr/bin/env python3
"""Exp44: five-seed stability of the Exp30-matched selective risk head."""
from __future__ import annotations
import importlib.util, json
from pathlib import Path
import numpy as np
from sklearn.linear_model import LogisticRegression

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]; CACHE=ROOT/'7hao/experiments/exp34_shared_uwf_region_cache'; HERE.mkdir(parents=True,exist_ok=True)
sp=importlib.util.spec_from_file_location('ab',ROOT/'7hao/experiments/exp35_region_mask_pool_ablation/run_ablation.py'); ab=importlib.util.module_from_spec(sp); assert sp.loader; sp.loader.exec_module(ab)
sp2=importlib.util.spec_from_file_location('risk',ROOT/'7hao/experiments/exp40_final_region_selective_risk/run_final_selective_risk.py'); risk=importlib.util.module_from_spec(sp2); assert sp2.loader; sp2.loader.exec_module(risk)
meta=json.loads((CACHE/'split_meta.json').read_text()); y={s:np.asarray(meta[s]['y'],int) for s in ('train','val','test')}
z=np.load(CACHE/'region_features_g3.npz'); raw={s:z[f'{s}_features'] for s in y}; mu=raw['train'].reshape(-1,raw['train'].shape[-1]).mean(0); sd=raw['train'].reshape(-1,raw['train'].shape[-1]).std(0); sd[sd<1e-8]=1; X={s:(raw[s]-mu)/sd for s in y}

def one(seed):
    mdl,dev,vs,ep=ab.train(X['train'],y['train'],X['val'],y['val'],'attention',.30,seed)
    Fv,yv,_,_=risk.pair(mdl,dev,X['val'],y['val']); Ft,yt,_,_=risk.pair(mdl,dev,X['test'],y['test'])
    mu2=Fv.mean(0); sd2=Fv.std(0); sd2[sd2<1e-8]=1
    clf=LogisticRegression(C=.1,class_weight='balanced',max_iter=1000,solver='liblinear',random_state=seed).fit((Fv-mu2)/sd2,yv)
    sv=clf.predict_proba((Fv-mu2)/sd2)[:,1]; st=clf.predict_proba((Ft-mu2)/sd2)[:,1]
    row={'seed':seed,'best_val_full_macro_f1':float(vs),'epochs':int(ep),'risk_head_test':risk.metric(yt,st,True),'selective':{}}
    for a in (.05,.10,.20):
        key=f'{a:.2f}'; c=risk.calibrate(sv,yv,a); m=st<=c['threshold']; row['selective'][key]={'coverage':float(m.mean()),'accepted_risk':float(yt[m].mean()) if m.any() else None,'accepted_n':int(m.sum()),'rejected_n':int((~m).sum()),'calibration':c}
    return row
def main():
    rows=[one(s) for s in (0,1,2,3,4)]; result={'n_seeds':5,'rows':rows,'aggregate':{}}
    result['aggregate']['risk_head_auroc']={'mean':float(np.mean([r['risk_head_test']['auroc'] for r in rows])),'std':float(np.std([r['risk_head_test']['auroc'] for r in rows],ddof=1))}
    for a in ('0.05','0.10','0.20'):
        result['aggregate'][f'selective_{a}']={k:{'mean':float(np.mean([r['selective'][a][k] for r in rows])),'std':float(np.std([r['selective'][a][k] for r in rows],ddof=1))} for k in ('coverage','accepted_risk')}
    (HERE/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    (HERE/'REPORT.md').write_text('# Exp44：选择性风险头五随机种子稳定性\n\n对Exp30匹配的区域模型和独立风险头同时改变随机种子，报告风险区分和风险—覆盖率工作点的均值与标准差。\n\n```json\n'+json.dumps(result,ensure_ascii=False,indent=2)+'\n```\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
