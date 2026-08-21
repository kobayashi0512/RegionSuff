#!/usr/bin/env python3
"""Exp46: severity-stratified audit of the selective risk head."""
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
    mdl,dev,vs,ep=ab.train(X['train'],y['train'],X['val'],y['val'],'attention',.30,seed); Fv,yv,_,_=risk.pair(mdl,dev,X['val'],y['val']); Ft,yt,_,_=risk.pair(mdl,dev,X['test'],y['test'])
    mu2=Fv.mean(0); sd2=Fv.std(0); sd2[sd2<1e-8]=1; clf=LogisticRegression(C=.1,class_weight='balanced',max_iter=1000,solver='liblinear',random_state=seed).fit((Fv-mu2)/sd2,yv); sv=clf.predict_proba((Fv-mu2)/sd2)[:,1]; st=clf.predict_proba((Ft-mu2)/sd2)[:,1]
    out={'seed':seed,'risk_auroc':risk.metric(yt,st,True),'strata':{}}
    for a in (.05,.10):
        c=risk.calibrate(sv,yv,a); accept=st<=c['threshold']; q={'target':a,'overall':{'coverage':float(accept.mean()),'risk':float(yt[accept].mean()) if accept.any() else None,'n':int(accept.sum())},'severity':{}}
        for sev in (0,1,2):
            g=(y['test']==sev); ag=accept&g; q['severity'][str(sev)]={'available_n':int(g.sum()),'accepted_n':int(ag.sum()),'coverage':float(ag.sum()/g.sum()),'accepted_risk':float(yt[ag].mean()) if ag.any() else None}
        out['strata'][f'{a:.2f}']=q
    return out
def main():
    rows=[one(s) for s in (0,1,2,3,4)]; result={'n_seeds':5,'rows':rows,'aggregate':{}}
    for a in ('0.05','0.10'):
        result['aggregate'][a]={'coverage_by_severity':{},'accepted_risk_by_severity':{}}
        for sev in ('0','1','2'):
            vals=[r['strata'][a]['severity'][sev] for r in rows]; result['aggregate'][a]['coverage_by_severity'][sev]={'mean':float(np.mean([v['coverage'] for v in vals])),'std':float(np.std([v['coverage'] for v in vals],ddof=1))}; result['aggregate'][a]['accepted_risk_by_severity'][sev]={'mean':float(np.mean([v['accepted_risk'] for v in vals if v['accepted_risk'] is not None])),'std':float(np.std([v['accepted_risk'] for v in vals if v['accepted_risk'] is not None],ddof=1))}
    (HERE/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8'); (HERE/'REPORT.md').write_text('# Exp46：选择性风险头严重度分层审计\n\n在五个随机种子下，分别统计目标风险5%和10%时Normal/NPDR/PDR的自动通过覆盖率与接受样本错误率。\n\n```json\n'+json.dumps(result,ensure_ascii=False,indent=2)+'\n```\n',encoding='utf-8'); print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
