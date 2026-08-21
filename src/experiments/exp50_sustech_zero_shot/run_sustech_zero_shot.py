#!/usr/bin/env python3
"""Exp50: zero-shot UWF-to-45deg DR transfer and exudate-attention audit."""
from __future__ import annotations
import csv, importlib.util, json, xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np, torch
from scipy.stats import spearmanr

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]; DATA=ROOT/'7hao/datasets/SUSTech_SYSU_Figshare/extracted'; CACHE=ROOT/'7hao/experiments/exp34_shared_uwf_region_cache'; HERE.mkdir(parents=True,exist_ok=True)
sp=importlib.util.spec_from_file_location('ab',ROOT/'7hao/experiments/exp35_region_mask_pool_ablation/run_ablation.py'); ab=importlib.util.module_from_spec(sp); assert sp.loader; sp.loader.exec_module(ab)
sp2=importlib.util.spec_from_file_location('m30',ROOT/'7hao/experiments/exp30_deep_region_attention/run_deep_region_attention.py'); m30=importlib.util.module_from_spec(sp2); assert sp2.loader; sp2.loader.exec_module(m30)
meta=json.loads((CACHE/'split_meta.json').read_text()); z=np.load(CACHE/'region_features_g3.npz'); raw={s:z[f'{s}_features'] for s in ('train','val')}; mu=raw['train'].reshape(-1,raw['train'].shape[-1]).mean(0); sd=raw['train'].reshape(-1,raw['train'].shape[-1]).std(0); sd[sd<1e-8]=1; Xtr=(raw['train']-mu)/sd; Xv=(raw['val']-mu)/sd; ytr=np.asarray(meta['train']['y'],int); yv=np.asarray(meta['val']['y'],int)
def read_target():
    rows=[]
    with (DATA/'originalImages/drLabels.csv').open(newline='',encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            p=DATA/'originalImages'/r['Fundus_images']; g=int(r['DR_grade(International_Clinical_DR_Severity_Scale)']);
            if p.exists(): rows.append((p,g,0 if g==0 else 1 if g<=3 else 2))
    return rows
def lesion_grid(path,arr):
    xmlp=DATA/'exudatesLabels'/f'{path.stem}.xml'; out=np.zeros(9,np.float64)
    if not xmlp.exists(): return out,False
    x0,y0,x1,y1,_=m30.baseline.retinal_bbox(arr); h=y1-y0; w=x1-x0
    try: root=ET.parse(xmlp).getroot()
    except ET.ParseError: return out,False
    for obj in root.findall('.//object'):
        b=obj.find('bndbox')
        if b is None: continue
        bx0=float(b.findtext('xmin','0')); by0=float(b.findtext('ymin','0')); bx1=float(b.findtext('xmax','0')); by1=float(b.findtext('ymax','0'))
        for r in range(3):
            for c in range(3):
                gx0=x0+c*w/3; gx1=x0+(c+1)*w/3; gy0=y0+r*h/3; gy1=y0+(r+1)*h/3
                iw=max(0.,min(bx1,gx1)-max(bx0,gx0)); ih=max(0.,min(by1,gy1)-max(by0,gy0)); out[r*3+c]+=iw*ih/max(1.,(gx1-gx0)*(gy1-gy0))
    return out,True
def main():
    target=read_target(); paths=[r[0] for r in target]; grade=np.asarray([r[1] for r in target],int); y=np.asarray([r[2] for r in target],int); arr=[m30.baseline.read_image(p) for p in paths]; model,dev=m30.load_model(); ext=(m30.extract(model,dev,arr)-mu)/sd
    lesion=np.vstack([lesion_grid(p,a)[0] for p,a in zip(paths,arr)]); annotated=np.asarray([lesion_grid(p,a)[1] for p,a in zip(paths,arr)])
    rows=[]; att=[]
    for seed in (0,1,2,3,4):
        head,hdev,vs,ep=ab.train(Xtr,ytr,Xv,yv,'attention',.30,seed)
        with torch.no_grad(): p=torch.softmax(head(torch.from_numpy(ext).float().to(hdev),torch.ones((len(y),9),device=hdev))[0],1).cpu().numpy(); a=head(torch.from_numpy(ext).float().to(hdev),torch.ones((len(y),9),device=hdev))[1].cpu().numpy()
        pred=p.argmax(1); rows.append({'seed':seed,'best_source_val_macro_f1':float(vs),'epochs':int(ep),'accuracy':float(np.mean(pred==y)),'macro_f1':float(ab.m30.baseline.macro_f1(y,pred)),'severity_mae':float(np.mean(abs(pred-y))),'underestimation_rate':float(np.mean(pred<y)),'per_original_grade':{str(g):{'n':int((grade==g).sum()),'accuracy':float(np.mean(pred[grade==g]==y[grade==g])),'underestimation_rate':float(np.mean(pred[grade==g]<y[grade==g]))} for g in range(6)}}); att.append(a)
    mean_att=np.mean(att,0); ix=np.flatnonzero(annotated)
    rho,pv=spearmanr(mean_att[ix].ravel(),lesion[ix].ravel()) if len(ix)>3 else (np.nan,np.nan)
    result={'dataset':{'name':'SUSTech-SYSU','n_images':int(len(y)),'mapped_labels':'ICDR 0->Normal; 1-3->NPDR; 4-5->PDR/laser-treated','grade_counts':{str(g):int((grade==g).sum()) for g in range(6)},'exudate_annotated_n':int(len(ix))},'protocol':'Five UWF-trained region-attention models are applied zero-shot to SUSTech images; no SUSTech label is used for training or model selection.','rows':rows,'aggregate':{k:{'mean':float(np.mean([r[k] for r in rows])),'std':float(np.std([r[k] for r in rows],ddof=1))} for k in ('accuracy','macro_f1','severity_mae','underestimation_rate')},'attention_exudate_audit':{'spearman_rho':float(rho),'p_value':float(pv),'region_pairs':int(len(ix)*9),'note':'Exploratory image-region correlation using exudate bounding-box area fractions; region pairs are not independent.'},'notes':['This is a cross-device, cross-field external zero-shot audit, not a paired UWF/45-degree study.','The target label mapping merges ICDR grades to match the source 3-class taxonomy.','Laser-treated grade is conservatively mapped to the severe/PDR class.']}
    (HERE/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8'); (HERE/'REPORT.md').write_text('# Exp50：SUSTech-SYSU外部零样本DR与病灶审计\n\n将UWF训练的区域模型直接迁移到公开45°DR分级数据，不使用外部标签训练；并以渗出物框做探索性注意力关联审计。\n\n```json\n'+json.dumps(result,ensure_ascii=False,indent=2)+'\n```\n',encoding='utf-8'); print(json.dumps({'aggregate':result['aggregate'],'attention_exudate_audit':result['attention_exudate_audit']},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
