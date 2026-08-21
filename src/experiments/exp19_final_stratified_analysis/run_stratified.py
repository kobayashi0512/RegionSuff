#!/usr/bin/env python3
"""Exp19: severity and image-quality stratification of final risk scores."""
from __future__ import annotations
import csv,json
from pathlib import Path
import numpy as np
from sklearn.metrics import roc_auc_score,average_precision_score

ROOT=Path(__file__).resolve().parents[3]; EXP=ROOT/'7hao/experiments/exp17_risk_ablation'; META=ROOT/'7hao/experiments/exp01_quality_fov_baseline/feature_meta_summary.csv'; OUT=ROOT/'7hao/experiments/exp19_final_stratified_analysis'; OUT.mkdir(parents=True,exist_ok=True)

def summarize(y,p):
    d={'n':int(len(y)),'positive':int(y.sum()),'positive_rate':float(y.mean()),'mean_score':float(p.mean()),'score_std':float(p.std())}
    if len(np.unique(y))==2: d.update({'auroc':float(roc_auc_score(y,p)),'average_precision':float(average_precision_score(y,p))})
    return d

def main():
    rows=list(csv.DictReader((EXP/'test_risk_scores.csv').open(encoding='utf-8'))); final=[r for r in rows if r['model']=='baseline_plus_uncertainty_quality']; final.sort(key=lambda r:int(r['index'])); y=np.asarray([int(r['target']) for r in final]); p=np.asarray([float(r['score']) for r in final])
    pred_rows=list(csv.DictReader((ROOT/'7hao/experiments/exp01_quality_fov_baseline/test_predictions.csv').open(encoding='utf-8'))); true_by={r['image']:int(r['true_label']) for r in pred_rows}
    meta=[]
    for r in csv.DictReader(META.open(encoding='utf-8')):
        if r['split']=='test' and r['view']=='central': meta.append(r)
    meta.sort(key=lambda r:r['image']); true=np.asarray([true_by[r['image']] for r in meta]); q=np.asarray([float(r['quality_proxy']) for r in meta])
    if len(true)!=len(y): raise RuntimeError(f'order mismatch {len(true)} {len(y)}')
    result={'dataset':{'n_test':len(y),'risk_positive':int(y.sum())},'by_severity':{},'by_quality_tertile':{},'notes':[]}
    for grade in sorted(set(true)): result['by_severity'][str(int(grade))]=summarize(y[true==grade],p[true==grade])
    edges=np.quantile(q,[0,1/3,2/3,1]); edges[0]-=1e-9; edges[-1]+=1e-9
    for i,name in enumerate(('low','middle','high')):
        m=(q>=edges[i])&(q<edges[i+1]); result['by_quality_tertile'][name]=dict(summarize(y[m],p[m]),quality_proxy_range=[float(edges[i]),float(edges[i+1])])
    result['notes']=['Severity strata use the UWF clinical grade; quality strata use the descriptive central-view quality proxy from the existing baseline.','The final score is the baseline_plus_uncertainty_quality model selected in Exp17.','Stratum-level AUROC is omitted when a stratum contains only one risk class.']
    (OUT/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8'); (OUT/'REPORT.md').write_text('# Exp19：最终风险模型严重度/质量分层\n\n按 UWF 临床严重度和中心视野质量代理的三分位数，分析最终低估风险分数是否只在某一类图像上有效。\n\n完整结果见 `results.json`。\n',encoding='utf-8'); print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
