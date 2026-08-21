#!/usr/bin/env python3
"""Bootstrap uncertainty for the Exp11 held-out risk score."""
from __future__ import annotations
import csv, json
from pathlib import Path
import numpy as np
from sklearn.metrics import brier_score_loss, roc_auc_score

HERE=Path(__file__).resolve().parent

def ece(y,p,bins=10):
    edges=np.linspace(0,1,bins+1); total=0.
    for i in range(bins):
        m=(p>=edges[i])&(p<(edges[i+1]) if i<bins-1 else p<=edges[i+1])
        if m.any(): total += m.mean()*abs(p[m].mean()-y[m].mean())
    return float(total)

def main():
    rows=list(csv.DictReader((HERE/'test_predictions.csv').open(encoding='utf-8')))
    y=np.asarray([int(r['underestimate']) for r in rows]); p=np.asarray([float(r['risk_score']) for r in rows]); rng=np.random.default_rng(42); auc=[]; br=[]; ec=[]
    for _ in range(5000):
        idx=rng.integers(0,len(y),len(y)); yy,pp=y[idx],p[idx]
        if len(np.unique(yy))<2: continue
        auc.append(roc_auc_score(yy,pp)); br.append(brier_score_loss(yy,pp)); ec.append(ece(yy,pp))
    result={'n_test':int(len(y)),'positive':int(y.sum()),'auroc':float(roc_auc_score(y,p)),'auroc_95ci':[float(np.percentile(auc,2.5)),float(np.percentile(auc,97.5))],'brier':float(brier_score_loss(y,p)),'brier_95ci':[float(np.percentile(br,2.5)),float(np.percentile(br,97.5))],'ece':ece(y,p),'ece_95ci':[float(np.percentile(ec,2.5)),float(np.percentile(ec,97.5))],'bootstrap_replicates':len(auc)}
    (HERE/'bootstrap.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8'); print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
