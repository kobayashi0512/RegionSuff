#!/usr/bin/env python3
"""Exp52: source-free target moment normalization for UWF-to-CFP transfer.

The target labels are *never* used by the adaptation. They are read only once
after prediction to quantify whether unlabeled feature alignment changes the
external result.
"""
from __future__ import annotations
import csv, importlib.util, json
from pathlib import Path
import numpy as np
import torch
from sklearn.metrics import average_precision_score, roc_auc_score

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CACHE = ROOT / '7hao/experiments/exp34_shared_uwf_region_cache'
HERE.mkdir(parents=True, exist_ok=True)
sp = importlib.util.spec_from_file_location('ab', ROOT / '7hao/experiments/exp35_region_mask_pool_ablation/run_ablation.py')
ab = importlib.util.module_from_spec(sp); assert sp.loader; sp.loader.exec_module(ab)
sp2 = importlib.util.spec_from_file_location('m30', ROOT / '7hao/experiments/exp30_deep_region_attention/run_deep_region_attention.py')
m30 = importlib.util.module_from_spec(sp2); assert sp2.loader; sp2.loader.exec_module(m30)

def idrid_rows():
    base = ROOT / '7hao/datasets/IDRiD_Zenodo/extracted/B. Disease Grading'
    csvp = base / '2. Groundtruths/b. IDRiD_Disease Grading_Testing Labels.csv'
    idir = base / '1. Original Images/b. Testing Set'
    rows=[]
    with csvp.open(newline='',encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            p=idir/(r['Image name'].strip()+'.jpg'); g=int(r['Retinopathy grade'])
            if p.exists(): rows.append((p,g,0 if g==0 else 1 if g<=3 else 2))
    return rows

def sustech_rows():
    base=ROOT/'7hao/datasets/SUSTech_SYSU_Figshare/extracted/originalImages'; rows=[]
    with (base/'drLabels.csv').open(newline='',encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            p=base/r['Fundus_images']; g=int(r['DR_grade(International_Clinical_DR_Severity_Scale)'])
            if p.exists(): rows.append((p,g,0 if g==0 else 1 if g<=3 else 2))
    return rows

def external_features(name, rows, encoder, dev):
    cp=HERE/f'{name}_raw_region_features.npz'
    if cp.exists(): return np.load(cp)['features']
    arrays=[m30.baseline.read_image(p) for p,_,_ in rows]
    raw=m30.extract(encoder,dev,arrays,batch=64)
    np.savez_compressed(cp,features=raw)
    return raw

def met(y,pred,prob):
    b=(y>0).astype(int); s=prob[:,1]+prob[:,2]
    return {'accuracy':float(np.mean(pred==y)),'macro_f1':float(ab.m30.baseline.macro_f1(y,pred)),
            'severity_mae':float(np.mean(np.abs(pred-y))),'underestimation_rate':float(np.mean(pred<y)),
            'binary_dr_auroc':float(roc_auc_score(b,s)),'binary_dr_ap':float(average_precision_score(b,s))}

def main():
    z=np.load(CACHE/'region_features_g3.npz'); meta=json.loads((CACHE/'split_meta.json').read_text())
    source_raw=z['train_features']; src_mu=source_raw.reshape(-1,source_raw.shape[-1]).mean(0); src_sd=source_raw.reshape(-1,source_raw.shape[-1]).std(0); src_sd[src_sd<1e-8]=1
    xtr=(source_raw-src_mu)/src_sd; xv=(z['val_features']-src_mu)/src_sd
    ytr=np.asarray(meta['train']['y'],int); yv=np.asarray(meta['val']['y'],int)
    encoder,dev=m30.load_model()
    targets={'IDRiD_test':idrid_rows(),'SUSTech_SYSU':sustech_rows()}
    output={'protocol':'Source-free region-wise target-moment normalization. Target images but no target labels are used to estimate feature mean/std; all labels are held out until evaluation. Source heads and early stopping remain exactly as in Exp50/51.','adaptation':'For each embedding dimension, x_target=(raw-target_mean)/target_std, thereby mapping unlabeled target features into source-standardized coordinates.','targets':{}}
    for name, rows in targets.items():
        raw=external_features(name,rows,encoder,dev)
        y=np.asarray([r[2] for r in rows],int); original=np.asarray([r[1] for r in rows],int)
        base=(raw-src_mu)/src_sd
        tm=raw.reshape(-1,raw.shape[-1]).mean(0); ts=raw.reshape(-1,raw.shape[-1]).std(0); ts[ts<1e-8]=1
        aligned=(raw-tm)/ts
        records=[]
        for seed in range(5):
            head,hdev,source_f1,epochs=ab.train(xtr,ytr,xv,yv,'attention',.30,seed)
            item={'seed':seed,'best_source_val_macro_f1':float(source_f1),'epochs':int(epochs)}
            for variant,x in (('source_normalization',base),('unlabeled_target_moment_normalization',aligned)):
                with torch.no_grad(): logits,_=head(torch.from_numpy(x).float().to(hdev),torch.ones((len(y),9),device=hdev)); prob=torch.softmax(logits,1).cpu().numpy()
                item[variant]=met(y,prob.argmax(1),prob)
            item['delta_macro_f1']=item['unlabeled_target_moment_normalization']['macro_f1']-item['source_normalization']['macro_f1']
            item['delta_auroc']=item['unlabeled_target_moment_normalization']['binary_dr_auroc']-item['source_normalization']['binary_dr_auroc']
            records.append(item)
        keys=('accuracy','macro_f1','severity_mae','underestimation_rate','binary_dr_auroc','binary_dr_ap')
        summary={v:{k:{'mean':float(np.mean([r[v][k] for r in records])),'std':float(np.std([r[v][k] for r in records],ddof=1))} for k in keys} for v in ('source_normalization','unlabeled_target_moment_normalization')}
        output['targets'][name]={'n_images':int(len(y)),'original_grade_counts':{str(g):int((original==g).sum()) for g in sorted(set(original))},'records':records,'summary':summary,'paired_delta':{k:{'mean':float(np.mean([r[k] for r in records])),'std':float(np.std([r[k] for r in records],ddof=1))} for k in ('delta_macro_f1','delta_auroc')}}
    output['notes']=['This is a transductive, source-free adaptation audit, not a zero-shot result and not a deployable pre-specified calibration procedure.','A favorable result would motivate future target-domain calibration; an unfavorable result means simple first/second-moment alignment is insufficient.']
    (HERE/'results.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
    (HERE/'REPORT.md').write_text('# Exp52：无标签特征矩匹配跨域适配\n\n```json\n'+json.dumps(output,ensure_ascii=False,indent=2)+'\n```\n',encoding='utf-8')
    print(json.dumps({n:{'source_macro_f1':d['summary']['source_normalization']['macro_f1'],'adapted_macro_f1':d['summary']['unlabeled_target_moment_normalization']['macro_f1'],'delta':d['paired_delta']} for n,d in output['targets'].items()},ensure_ascii=False,indent=2))

if __name__=='__main__': main()
