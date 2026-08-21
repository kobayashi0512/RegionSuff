#!/usr/bin/env python3
"""Exp08: repeat the UWF 55% view baseline under multiple patient splits."""
from __future__ import annotations
import importlib.util,json
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent; WS=HERE.parents[2]; BASE=WS/"7hao/experiments/exp01_quality_fov_baseline/run_baseline.py"
sp=importlib.util.spec_from_file_location('b',BASE); b=importlib.util.module_from_spec(sp); assert sp.loader; sp.loader.exec_module(b)
def main():
 mp=b.find_uwf_image_map(); rec=[]
 for split in ('train','val','test'):
  p,y=b.read_split(split,mp); rec.extend(zip(p,y.tolist()))
 cache={}
 for p,y in rec:
  cache[str(p)]=b.feature_vector(b.central_view(b.read_image(p),.55))[0]
 rows=[]
 for seed in (1,7,42,77,123):
  splits=b.make_patient_level_splits(rec,seed=seed); X={s:np.vstack([cache[str(p)] for p in d['paths']]) for s,d in splits.items()}; tr,oth,_,_=b.standardize(X['train'],[X['val'],X['test']]); X['train'],X['val'],X['test']=tr,oth[0],oth[1]; W=b.fit_multiclass(X['train'],splits['train']['y']); y=splits['test']['y']; pred=b.predict_multi(W,X['test']).argmax(1); rows.append({'seed':seed,'n_test':len(y),'accuracy':float(np.mean(pred==y)),'macro_f1':b.macro_f1(y,pred),'severity_mae':float(np.mean(abs(pred-y))),'underestimate_rate':float(np.mean(pred<y)),'test_class_counts':np.bincount(y,minlength=3).tolist()}); print(rows[-1],flush=True)
 json.dump({'rows':rows,'notes':['All splits are patient-level grouped; features are cached once.','This is a robustness check, not external validation.']},(HERE/'results.json').open('w'),ensure_ascii=False,indent=2)
 (HERE/'REPORT.md').write_text('# Exp08：多随机 patient-level split 稳健性\n\n固定 55% 中心视野，重复 seed=1/7/42/77/123 的 patient-level 划分和训练，观察测试性能波动。\n',encoding='utf-8')
if __name__=='__main__': main()
