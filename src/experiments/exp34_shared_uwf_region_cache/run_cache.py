#!/usr/bin/env python3
"""Shared UWF region-feature cache for the ten follow-up experiments."""
from __future__ import annotations
import csv, importlib.util, json
from pathlib import Path
import numpy as np, torch

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]; HERE.mkdir(parents=True,exist_ok=True)
M30=ROOT/'7hao/experiments/exp30_deep_region_attention/run_deep_region_attention.py'
spec=importlib.util.spec_from_file_location('m30',M30); m30=importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(m30)

def grid_crops(arr,g):
    x0,y0,x1,y1,_=m30.baseline.retinal_bbox(arr); roi=arr[y0:y1,x0:x1]; h,w=roi.shape[:2]; out=[]
    for r in range(g):
        for c in range(g): out.append(roi[int(r*h/g):int((r+1)*h/g),int(c*w/g):int((c+1)*w/g)])
    return out

def extract(model,device,arrs,g):
    crops=[]
    for a in arrs:crops.extend(grid_crops(a,g))
    out=[]
    for st in range(0,len(crops),32):
        with torch.no_grad(): out.append(model.global_pool(model.forward_features(m30.tensor_batch(crops[st:st+32]).to(device))).flatten(1).cpu().numpy().astype(np.float32))
        if st%512==0: print(f'g={g}: {min(st+32,len(crops))}/{len(crops)}',flush=True)
    return np.vstack(out).reshape(len(arrs),g*g,-1)

def main():
    b=m30.baseline; mp=b.find_uwf_image_map(); records=[]
    for s in ('train','val','test'):
        p,y=b.read_split(s,mp); records.extend(zip(p,y.tolist()))
    splits=b.make_patient_level_splits(records,seed=42); arr={s:[b.read_image(p) for p in splits[s]['paths']] for s in splits}; model,device=m30.load_model(); meta={s:{'y':splits[s]['y'].tolist(),'paths':[p.name for p in splits[s]['paths']]} for s in splits}; (HERE/'split_meta.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
    result={'device':str(device),'n_images':len(records),'grids':{},'split_counts':{s:np.bincount(splits[s]['y'],minlength=3).tolist() for s in splits}}
    for g in (1,2,3,4):
        out={s:extract(model,device,arr[s],g) for s in splits}
        np.savez_compressed(HERE/f'region_features_g{g}.npz',**{f'{s}_features':out[s] for s in splits})
        result['grids'][str(g)]={s:list(out[s].shape) for s in splits}; print('saved grid',g,flush=True)
    (HERE/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8'); (HERE/'REPORT.md').write_text('# Exp34：共享区域深度特征缓存\n\n为后续10项投稿前实验一次性缓存UWF-DR的1×1、2×2、3×3和4×4 RetinaRadar区域特征。该目录是共享基础资源，不替换Exp30结果。\n\n```json\n'+json.dumps(result,ensure_ascii=False,indent=2)+'\n```\n',encoding='utf-8'); print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
