#!/usr/bin/env python3
"""Exp09: quality stress stratified by true DR severity."""
from __future__ import annotations
import importlib.util,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageFilter,ImageEnhance
HERE=Path(__file__).resolve().parent; WS=HERE.parents[2]; BASE=WS/"7hao/experiments/exp01_quality_fov_baseline/run_baseline.py"
sp=importlib.util.spec_from_file_location('b',BASE); b=importlib.util.module_from_spec(sp); assert sp.loader; sp.loader.exec_module(b)
def corrupt(a,kind):
 im=Image.fromarray(np.clip(a*255,0,255).astype('uint8'))
 if kind=='clean': return a
 if kind=='blur': im=im.filter(ImageFilter.GaussianBlur(3))
 if kind=='dark': im=ImageEnhance.Brightness(im).enhance(.6)
 if kind=='low_contrast': im=ImageEnhance.Contrast(im).enhance(.8)
 return np.asarray(im,dtype=np.float32)/255.
def main():
 mp=b.find_uwf_image_map(); rec=[]
 for s in ('train','val','test'):
  p,y=b.read_split(s,mp); rec.extend(zip(p,y.tolist()))
 splits=b.make_patient_level_splits(rec,seed=42); X=[]
 for p in splits['train']['paths']: X.append(b.feature_vector(b.read_image(p))[0])
 tr=np.vstack(X); mu=tr.mean(0); sd=tr.std(0); sd[sd<1e-8]=1; W=b.fit_multiclass((tr-mu)/sd,splits['train']['y']); paths=splits['test']['paths']; y=splits['test']['y']; arrays=[b.read_image(p) for p in paths]; rows=[]
 for kind in ('clean','blur','dark','low_contrast'):
  Z=np.vstack([b.feature_vector(corrupt(a,kind))[0] for a in arrays]); pred=b.predict_multi(W,(Z-mu)/sd).argmax(1)
  for cls,name in enumerate(('Normal','NPDR','PDR')):
   m=y==cls
   rows.append({'condition':kind,'true_class':name,'n':int(m.sum()),'accuracy':float(np.mean(pred[m]==y[m])),'underestimate_rate':float(np.mean(pred[m]<y[m])),'mean_predicted_class':float(pred[m].mean())})
 json.dump({'rows':rows,'notes':['All metrics are stratified on true class in the held-out test split.','Synthetic corruption is not clinical quality ground truth.']},(HERE/'results.json').open('w'),ensure_ascii=False,indent=2)
 (HERE/'REPORT.md').write_text('# Exp09：按疾病严重度分层的质量退化\n\n比较 clean、强模糊、降亮度、降对比度，并按 Normal/NPDR/PDR 分层。\n',encoding='utf-8')
 print(json.dumps(rows,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
