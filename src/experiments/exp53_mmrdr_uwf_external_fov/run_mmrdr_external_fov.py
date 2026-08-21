#!/usr/bin/env python3
"""Exp53: independent cross-center UWF limited-field external validation."""
from __future__ import annotations
import csv, importlib.util, json, gc, subprocess, sys
from pathlib import Path
import numpy as np
import torch

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]; HERE.mkdir(parents=True,exist_ok=True)
DATA=ROOT/'7hao/datasets/MMRDR_figshare/extracted/MMRDR-UWF'; CACHE=ROOT/'7hao/experiments/exp34_shared_uwf_region_cache'
sp=importlib.util.spec_from_file_location('ab',ROOT/'7hao/experiments/exp35_region_mask_pool_ablation/run_ablation.py'); ab=importlib.util.module_from_spec(sp); assert sp.loader; sp.loader.exec_module(ab)
sp2=importlib.util.spec_from_file_location('m30',ROOT/'7hao/experiments/exp30_deep_region_attention/run_deep_region_attention.py'); m30=importlib.util.module_from_spec(sp2); assert sp2.loader; sp2.loader.exec_module(m30)

def rows():
    out=[]
    with (DATA/'UWF.csv').open(newline='',encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            if not r['image'].startswith('img/ts'): continue
            p=DATA/r['image']; g=int(r['grade'])
            if p.exists(): out.append((p,g,0 if g==0 else 1 if g<=3 else 2))
    return out

def quality_proxy(arr):
    x0,y0,x1,y1,_=m30.baseline.retinal_bbox(arr); roi=arr[y0:y1,x0:x1]; gray=roi.mean(2)
    coverage=(x1-x0)*(y1-y0)/(arr.shape[0]*arr.shape[1])
    contrast=float(gray.std()); sharp=float(np.mean(np.abs(np.diff(gray,axis=0)))+np.mean(np.abs(np.diff(gray,axis=1))))
    return coverage,contrast,sharp

def extract_block(paths, start, end):
    block_dir=HERE/'feature_blocks'; block_dir.mkdir(exist_ok=True)
    out=block_dir/f'block_{start:05d}_{end:05d}.npz'
    if out.exists(): return
    encoder,dev=m30.load_model(); features=[]; quality=[]
    for offset in range(start,end,16):
        arrays=[m30.baseline.read_image(p) for p in paths[offset:min(offset+16,end)]]
        features.append(m30.extract(encoder,dev,arrays,batch=32))
        quality.append(np.asarray([quality_proxy(a) for a in arrays],np.float32))
        del arrays; gc.collect()
        if torch.backends.mps.is_available(): torch.mps.empty_cache()
    np.savez_compressed(out,features=np.concatenate(features),quality_proxy=np.concatenate(quality))
    print(f'block complete: {start}:{end}',flush=True)

def metrics(y,p): return {'accuracy':float(np.mean(p==y)),'macro_f1':float(ab.m30.baseline.macro_f1(y,p)),'severity_mae':float(np.mean(np.abs(p-y))),'underestimation_rate':float(np.mean(p<y))}

def main():
    meta=json.loads((CACHE/'split_meta.json').read_text()); z=np.load(CACHE/'region_features_g3.npz'); raw=z['train_features']; mu=raw.reshape(-1,raw.shape[-1]).mean(0); sd=raw.reshape(-1,raw.shape[-1]).std(0); sd[sd<1e-8]=1
    xtr=(raw-mu)/sd; xv=(z['val_features']-mu)/sd; ytr=np.asarray(meta['train']['y'],int); yv=np.asarray(meta['val']['y'],int)
    target=rows(); paths=[r[0] for r in target]
    if len(sys.argv)==3 and sys.argv[1]=='--block':
        extract_block(paths,int(sys.argv[2]),min(int(sys.argv[2])+128,len(paths))); return
    original=np.asarray([r[1] for r in target],int); y=np.asarray([r[2] for r in target],int)
    fc=HERE/'mmrdr_test_raw_region_features.npz'; qc=HERE/'mmrdr_test_quality_proxy.npz'
    if fc.exists() and qc.exists():
        ext=np.load(fc)['features']; qp=np.load(qc)['quality_proxy']
    else:
        # One child process per 128 images: MPS memory is released between
        # blocks instead of accumulating across the full high-resolution set.
        for start in range(0,len(paths),128):
            subprocess.run([sys.executable,str(Path(__file__).resolve()),'--block',str(start)],check=True)
        feature_blocks=[]; quality_blocks=[]
        for start in range(0,len(paths),128):
            end=min(start+128,len(paths)); b=np.load(HERE/'feature_blocks'/f'block_{start:05d}_{end:05d}.npz')
            feature_blocks.append(b['features']); quality_blocks.append(b['quality_proxy'])
        ext=np.concatenate(feature_blocks,axis=0); qp=np.concatenate(quality_blocks,axis=0)
        np.savez_compressed(fc,features=ext); np.savez_compressed(qc,quality_proxy=qp)
    x=(ext-mu)/sd
    # No labels are used to define this quality proxy; quartiles are descriptive only.
    zq=(qp-qp.mean(0))/np.maximum(qp.std(0),1e-8); q=zq.mean(1); lo=q<=np.quantile(q,.25); hi=q>=np.quantile(q,.75)
    records=[]
    for seed in range(5):
        head,hdev,source_f1,epochs=ab.train(xtr,ytr,xv,yv,'attention',.30,seed); rec={'seed':seed,'best_source_val_macro_f1':float(source_f1),'epochs':int(epochs),'views':{}}
        with torch.no_grad():
            for view in ('full','center','center_plus_cross'):
                mask=torch.from_numpy(m30.mask_named(view,len(y))).float().to(hdev); logits,_=head(torch.from_numpy(x).float().to(hdev),mask); pred=logits.argmax(1).cpu().numpy(); m=metrics(y,pred)
                if view=='full': m['quality_proxy_quartiles']={'lowest_n':int(lo.sum()),'lowest':metrics(y[lo],pred[lo]),'highest_n':int(hi.sum()),'highest':metrics(y[hi],pred[hi])}
                rec['views'][view]=m
        records.append(rec)
    views=('full','center','center_plus_cross'); keys=('accuracy','macro_f1','severity_mae','underestimation_rate')
    summary={v:{k:{'mean':float(np.mean([r['views'][v][k] for r in records])),'std':float(np.std([r['views'][v][k] for r in records],ddof=1))} for k in keys} for v in views}
    output={'dataset':{'name':'MMRDR UWF official patient-level test split','n_images':int(len(y)),'original_grade_counts':{str(g):int((original==g).sum()) for g in range(5)},'mapped_labels':'MMRDR grade 0->Normal; 1-3->NPDR; 4->PDR'},'protocol':'Five UWF-source-trained frozen-RetinaRadar regional attention heads are applied without MMRDR label training, calibration, early stopping, or model selection. Views are applied as 3x3 geometric region masks.','quality_proxy':'Descriptive unlabeled proxy from retinal coverage, within-retina contrast and first-difference sharpness; it is not a clinical image-quality label.','records':records,'summary':summary,'paired_limited_minus_full':{v:{k:{'mean':float(np.mean([r['views'][v][k]-r['views']['full'][k] for r in records])),'std':float(np.std([r['views'][v][k]-r['views']['full'][k] for r in records],ddof=1))} for k in keys} for v in ('center','center_plus_cross')},'notes':['This is the required independent same-modality UWF replication, distinct from the Exp50/51 UWF-to-45-degree transfer audits.','The official MMRDR UWF testing split is patient-level according to the data descriptor.','Quality-proxy strata are exploratory and cannot be represented as clinically adjudicated quality-gate validation.']}
    (HERE/'results.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8'); (HERE/'REPORT.md').write_text('# Exp53：MMRDR独立UWF受限视野外部验证\n\n```json\n'+json.dumps(output,ensure_ascii=False,indent=2)+'\n```\n',encoding='utf-8'); print(json.dumps({'summary':summary,'paired_limited_minus_full':output['paired_limited_minus_full']},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
