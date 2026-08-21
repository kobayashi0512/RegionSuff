#!/usr/bin/env python3
"""Exp07: same crop size, different location."""
from __future__ import annotations
import importlib.util,json
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent; WS=HERE.parents[2]; BASE=WS/"7hao/experiments/exp01_quality_fov_baseline/run_baseline.py"
sp=importlib.util.spec_from_file_location('b',BASE); b=importlib.util.module_from_spec(sp); assert sp.loader; sp.loader.exec_module(b)
def crop(arr,frac,dx,dy):
 x0,y0,x1,y1,_=b.retinal_bbox(arr); roi=arr[y0:y1,x0:x1]; h,w=roi.shape[:2]; ch=int(h*frac); cw=int(w*frac); yy=int((h-ch)/2+dy*(h-ch)/2); xx=int((w-cw)/2+dx*(w-cw)/2); return roi[max(0,yy):max(0,yy)+ch,max(0,xx):max(0,xx)+cw]
def main():
 mp=b.find_uwf_image_map(); rec=[]
 for split in ('train','val','test'):
  p,y=b.read_split(split,mp); rec.extend(zip(p,y.tolist()))
 splits=b.make_patient_level_splits(rec,seed=42); positions={'center':(0,0),'left':(-1,0),'right':(1,0),'up':(0,-1),'down':(0,1)}; rows=[]
 for name,(dx,dy) in positions.items():
  X={}
  for split,d in splits.items(): X[split]=np.vstack([b.feature_vector(crop(b.read_image(p),.55,dx,dy))[0] for p in d['paths']])
  tr,oth,_,_=b.standardize(X['train'],[X['val'],X['test']]); X['train'],X['val'],X['test']=tr,oth[0],oth[1]; W=b.fit_multiclass(X['train'],splits['train']['y']); y=splits['test']['y']; pred=b.predict_multi(W,X['test']).argmax(1)
  rows.append({'position':name,'accuracy':float(np.mean(pred==y)),'macro_f1':b.macro_f1(y,pred),'severity_mae':float(np.mean(abs(pred-y))),'underestimate_rate':float(np.mean(pred<y))})
  print(rows[-1],flush=True)
 json.dump({'crop_fraction':.55,'rows':rows,'notes':['All views have the same crop size; only location changes.','Positions are geometric shifts inside the retinal bounding box.']},(HERE/'results.json').open('w'),ensure_ascii=False,indent=2)
 (HERE/'REPORT.md').write_text('# Exp07：同尺寸不同视野位置\n\n固定 55% 视野大小，比较 center/left/right/up/down 五个裁剪位置。用于区分“视野大小”与“视野内容”。\n',encoding='utf-8')
if __name__=='__main__': main()
