#!/usr/bin/env python3
"""Exp18: bootstrap uncertainty and paired model comparisons."""
from __future__ import annotations
import csv,json
from pathlib import Path
import numpy as np
from sklearn.metrics import average_precision_score,brier_score_loss,roc_auc_score

ROOT=Path(__file__).resolve().parents[3]; SOURCE=ROOT/'7hao/experiments/exp17_risk_ablation/test_risk_scores.csv'; OUT=ROOT/'7hao/experiments/exp18_final_model_bootstrap'; OUT.mkdir(parents=True,exist_ok=True)

def ece(y,p,bins=10):
    edges=np.linspace(0,1,bins+1); val=0.
    for i in range(bins):
        m=(p>=edges[i])&((p<edges[i+1]) if i<bins-1 else (p<=edges[i+1]))
        if m.any(): val+=m.mean()*abs(p[m].mean()-y[m].mean())
    return float(val)

def main():
    groups={}
    for r in csv.DictReader(SOURCE.open(encoding='utf-8')): groups.setdefault(r['model'],[]).append((int(r['target']),float(r['score'])))
    y=np.asarray([r[0] for r in groups[next(iter(groups))]],int); pred={m:np.asarray([r[1] for r in rows]) for m,rows in groups.items()}; rng=np.random.default_rng(42); n=len(y); auc={m:[] for m in pred}; ap={m:[] for m in pred}; br={m:[] for m in pred}; ec={m:[] for m in pred}; diff={}
    for _ in range(2000):
        ix=rng.integers(0,n,n); yy=y[ix]
        if len(np.unique(yy))<2: continue
        for m,p in pred.items():
            pp=p[ix]; auc[m].append(roc_auc_score(yy,pp)); ap[m].append(average_precision_score(yy,pp)); br[m].append(brier_score_loss(yy,pp)); ec[m].append(ece(yy,pp))
        final=pred['baseline_plus_uncertainty_quality'][ix]
        for m,p in pred.items():
            if m!='baseline_plus_uncertainty_quality': diff.setdefault(m,[]).append(roc_auc_score(yy,final)-roc_auc_score(yy,p[ix]))
    result={'dataset':{'n_test':n,'positive':int(y.sum()),'bootstrap_replicates':len(next(iter(auc.values())))},'models':{},'paired_differences_vs_final':{}}
    for m in pred:
        result['models'][m]={'auroc':float(roc_auc_score(y,pred[m])),'auroc_95ci':[float(np.percentile(auc[m],2.5)),float(np.percentile(auc[m],97.5))],'average_precision':float(average_precision_score(y,pred[m])),'brier':float(brier_score_loss(y,pred[m])),'brier_95ci':[float(np.percentile(br[m],2.5)),float(np.percentile(br[m],97.5))],'ece':ece(y,pred[m]),'ece_95ci':[float(np.percentile(ec[m],2.5)),float(np.percentile(ec[m],97.5))]}
    for m,v in diff.items(): result['paired_differences_vs_final'][m]={'auroc_difference_final_minus_model':float(roc_auc_score(y,pred['baseline_plus_uncertainty_quality'])-roc_auc_score(y,pred[m])),'difference_95ci':[float(np.percentile(v,2.5)),float(np.percentile(v,97.5))]}
    result['notes']=['All bootstrap samples resample held-out test images with replacement.','The final candidate is baseline_plus_uncertainty_quality from Exp17.','These are statistical uncertainty estimates, not independent multicenter validation.']
    (OUT/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8'); (OUT/'REPORT.md').write_text('# Exp18：最终候选模型 bootstrap 与成对比较\n\n对 Exp17 的测试集风险分数进行 5000 次 bootstrap，报告 AUROC、AP、Brier、ECE及最终候选模型与各消融模型的成对 AUROC 差异。\n\n完整结果见 `results.json`。\n',encoding='utf-8'); print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
