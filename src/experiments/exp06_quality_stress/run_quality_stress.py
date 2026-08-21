#!/usr/bin/env python3
"""Exp06: sensitivity to blur, brightness and contrast degradation."""
from __future__ import annotations
import importlib.util,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageFilter,ImageEnhance
HERE=Path(__file__).resolve().parent; WS=HERE.parents[2]; BASE=WS/"7hao/experiments/exp01_quality_fov_baseline/run_baseline.py"
sp=importlib.util.spec_from_file_location('b',BASE); b=importlib.util.module_from_spec(sp); assert sp.loader; sp.loader.exec_module(b)
def corrupt(arr,kind,level):
 im=Image.fromarray(np.clip(arr*255,0,255).astype('uint8'))
 if kind=='blur': im=im.filter(ImageFilter.GaussianBlur([1,2,3][level-1]))
 if kind=='brightness': im=ImageEnhance.Brightness(im).enhance([.8,.6,.4][level-1])
 if kind=='contrast': im=ImageEnhance.Contrast(im).enhance([.8,.6,.4][level-1])
 return np.asarray(im,dtype=np.float32)/255.0
def main():
 mp=b.find_uwf_image_map(); rec=[]
 for split in ('train','val','test'):
  p,y=b.read_split(split,mp); rec.extend(zip(p,y.tolist()))
 splits=b.make_patient_level_splits(rec,seed=42); X={}
 for split,d in splits.items(): X[split]=np.vstack([b.feature_vector(b.read_image(p))[0] for p in d['paths']])
 tr,others,mu,sd=b.standardize(X['train'],[X['val'],X['test']]); X['train'],X['val'],X['test']=tr,others[0],others[1]; W=b.fit_multiclass(X['train'],splits['train']['y']); rows=[]
 def score(name,arrs,y):
  Z=np.vstack([b.feature_vector(a)[0] for a in arrs]); Z=(Z-mu)/sd; pred=b.predict_multi(W,Z).argmax(1); return {'condition':name,'accuracy':float(np.mean(pred==y)),'macro_f1':b.macro_f1(y,pred),'severity_mae':float(np.mean(abs(pred-y))),'underestimate_rate':float(np.mean(pred<y))}
 y=splits['test']['y']; clean=[b.read_image(p) for p in splits['test']['paths']]; rows.append(score('clean',clean,y))
 for kind in ('blur','brightness','contrast'):
  for level in (1,2,3): rows.append(score(f'{kind}_L{level}',[corrupt(a,kind,level) for a in clean],y))
 json.dump({'rows':rows,'notes':['Classifier trained on clean full UWF features; only test images are corrupted.','Synthetic corruption is not a substitute for real quality labels.']},(HERE/'results.json').open('w'),ensure_ascii=False,indent=2)
 (HERE/'REPORT.md').write_text('# Exp06：图像质量退化压力测试\n\n在同一 clean-trained 分类器上施加 Gaussian blur、亮度降低和对比度降低，观察疾病严重度预测是否退化。\n\n结果见 `results.json`。\n',encoding='utf-8')
 print(json.dumps(rows,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
