#!/usr/bin/env python3
"""Exp15: circular 45-degree FOV proxy on UWF-DR."""
from __future__ import annotations
import csv, json, importlib.util
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[3]; OUT=ROOT/'7hao/experiments/exp15_circular_45deg_mask'; OUT.mkdir(parents=True,exist_ok=True)
BASE=ROOT/'7hao/experiments/exp01_quality_fov_baseline/run_baseline.py'
spec=importlib.util.spec_from_file_location('baseline',BASE); mod=importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(mod)

def circle45(arr, ratio=45/200):
    x0,y0,x1,y1,_=mod.retinal_bbox(arr); roi=arr[y0:y1,x0:x1]; h,w=roi.shape[:2]
    r=max(8,int(min(h,w)*ratio)); cx,cy=w//2,h//2; xa,xb=max(0,cx-r),min(w,cx+r); ya,yb=max(0,cy-r),min(h,cy+r); z=roi[ya:yb,xa:xb].copy()
    yy,xx=np.ogrid[:z.shape[0],:z.shape[1]]; ccx=z.shape[1]/2.; ccy=z.shape[0]/2.; mask=(xx-ccx)**2+(yy-ccy)**2 <= r*r
    z[~mask]=0.; return z

def extract(paths,view):
    xs=[]
    for i,p in enumerate(paths,1):
        arr=mod.read_image(p)
        if view=='square55': arr=mod.central_view(arr,.55)
        elif view=='circle45': arr=circle45(arr)
        xs.append(mod.feature_vector(arr)[0])
        if i%250==0: print(view,i,flush=True)
    return np.vstack(xs)

def metrics(y,p):
    pred=p.argmax(1); return {'accuracy':float(np.mean(pred==y)),'macro_f1':mod.macro_f1(y,pred),'severity_mae':float(np.mean(abs(pred-y))),'underestimation_rate':float(np.mean(pred<y))}

def main():
    mp=mod.find_uwf_image_map(); rec=[]
    for s in ('train','val','test'):
        p,y=mod.read_split(s,mp); rec.extend(zip(p,y.tolist()))
    splits=mod.make_patient_level_splits(rec,seed=42); result={'dataset':{'n':len(rec),'ratio_45_over_200':45/200,'split_counts':{s:np.bincount(splits[s]['y'],minlength=3).tolist() for s in splits}},'views':{},'notes':[]}
    for view in ('full','square55','circle45'):
        X={s:extract(splits[s]['paths'],view) for s in splits}; tr=X['train']; mu=tr.mean(0); sd=tr.std(0); sd[sd<1e-8]=1.; X={s:(v-mu)/sd for s,v in X.items()}; W=mod.fit_multiclass(X['train'],splits['train']['y']); result['views'][view]={s:metrics(splits[s]['y'],mod.predict_multi(W,X[s])) for s in splits}
    result['notes']=['circle45 retains a central circular region with radius ratio 45/200 inside the retinal bounding box; it is a geometric proxy, not a real 45-degree camera pair.','Patient-level grouped split is reused for comparability.','The experiment tests whether the qualitative underestimation signal survives a more camera-like circular mask.']
    (OUT/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8'); (OUT/'REPORT.md').write_text('# Exp15：45°圆形视野替代实验\n\n将 UWF 图像的中心区域按 45/200 视野比例做圆形遮罩，比较完整 UWF、55% 方形中心裁剪与近似 45° 圆形视野。该实验不能替代真实同眼配对，但比方形裁剪更接近相机视野形状。\n\n完整结果见 `results.json`。\n',encoding='utf-8'); print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
