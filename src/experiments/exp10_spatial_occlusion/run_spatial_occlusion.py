#!/usr/bin/env python3
"""Exp10: hide one spatial quadrant at a time to probe spatial sufficiency."""
from __future__ import annotations
import importlib.util,json
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent; WS=HERE.parents[2]; BASE=WS/"7hao/experiments/exp01_quality_fov_baseline/run_baseline.py"
sp=importlib.util.spec_from_file_location('b',BASE); b=importlib.util.module_from_spec(sp); assert sp.loader; sp.loader.exec_module(b)
def hide(arr,which):
 x0,y0,x1,y1,_=b.retinal_bbox(arr); out=arr.copy(); xm=(x0+x1)//2; ym=(y0+y1)//2; boxes={'top_left':(x0,y0,xm,ym),'top_right':(xm,y0,x1,ym),'bottom_left':(x0,ym,xm,y1),'bottom_right':(xm,ym,x1,y1)}
 if which!='none':
  xa,ya,xb,yb=boxes[which]; out[ya:yb,xa:xb]=0
 return out
def main():
 mp=b.find_uwf_image_map(); rec=[]
 for s in ('train','val','test'):
  p,y=b.read_split(s,mp); rec.extend(zip(p,y.tolist()))
 splits=b.make_patient_level_splits(rec,seed=42); X={s:np.vstack([b.feature_vector(b.read_image(p))[0] for p in d['paths']]) for s,d in splits.items()}; tr,oth,mu,sd=b.standardize(X['train'],[X['val'],X['test']]); X['train'],X['val'],X['test']=tr,oth[0],oth[1]; W=b.fit_multiclass(X['train'],splits['train']['y']); y=splits['test']['y']; arrays=[b.read_image(p) for p in splits['test']['paths']]; rows=[]
 for q in ('none','top_left','top_right','bottom_left','bottom_right'):
  Z=np.vstack([b.feature_vector(hide(a,q))[0] for a in arrays]); pred=b.predict_multi(W,(Z-mu)/sd).argmax(1); rows.append({'occluded_region':q,'accuracy':float(np.mean(pred==y)),'macro_f1':b.macro_f1(y,pred),'severity_mae':float(np.mean(abs(pred-y))),'underestimate_rate':float(np.mean(pred<y))})
 json.dump({'rows':rows,'notes':['Occlusion is synthetic and probes spatial sensitivity, not lesion segmentation.','The classifier is trained on clean full-view features.']},(HERE/'results.json').open('w'),ensure_ascii=False,indent=2)
 (HERE/'REPORT.md').write_text('# Exp10：空间区域遮挡实验\n\n分别遮住视网膜 bounding box 的四个象限，观察同一个 clean-trained 模型的性能变化。\n',encoding='utf-8')
 print(json.dumps(rows,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
