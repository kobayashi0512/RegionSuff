#!/usr/bin/env python3
"""Exp04: external ordinary fundus check with RFMiD2 multi-label disease tags."""
from __future__ import annotations
import csv, json, importlib.util
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent; WORKSPACE=HERE.parents[2]; BASE=WORKSPACE/"7hao/experiments/exp01_quality_fov_baseline/run_baseline.py"
spec=importlib.util.spec_from_file_location("baseline",BASE); mod=importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(mod)
ROOT=WORKSPACE/"7hao/datasets/RFMiD2_0/extracted"

def read_labels(split):
    path=next((ROOT/split).glob("*_labels.csv")); out=[]
    with path.open(newline='',encoding='latin-1') as f:
        reader=csv.DictReader(f); names=[n for n in (reader.fieldnames or []) if n and n!='ID']
        for row in reader:
            out.append((int(row['ID']),np.asarray([int(float(row.get(n,0) or 0)) for n in names],dtype=np.int64)))
    return names,out
def image_map(split):
    return {int(p.stem):p for p in (ROOT/split).iterdir() if p.suffix.lower() in {'.jpg','.jpeg','.png'}}
def metric(y,s):
    if len(np.unique(y))<2: return None
    return mod.auc_pr(y,s)
def main():
    data={}; names=None
    for split in ('Training','Validation','Test'):
        names,rows=read_labels(split); mp=image_map(split); data[split]={'ids':[],'ys':[],'paths':[]}
        for ident,y in rows:
            if ident in mp: data[split]['ids'].append(ident); data[split]['ys'].append(y); data[split]['paths'].append(mp[ident])
        data[split]['ys']=np.vstack(data[split]['ys'])
    outputs={}
    for view in ('full','central_55'):
        X={}
        for split,d in data.items():
            fs=[]
            for i,p in enumerate(d['paths'],1):
                arr=mod.read_image(p) if view=='full' else mod.central_view(mod.read_image(p),.55)
                fs.append(mod.feature_vector(arr)[0]);
                if i%200==0: print(view,split,i,flush=True)
            X[split]=np.vstack(fs)
        tr=X['Training']; mu=tr.mean(0); sd=tr.std(0); sd[sd<1e-8]=1
        X={k:(v-mu)/sd for k,v in X.items()}; per=[]
        for j,name in enumerate(names):
            ytr=data['Training']['ys'][:,j]
            if ytr.sum()==0 or ytr.sum()==len(ytr): continue
            w=mod.fit_binary(X['Training'],ytr,epochs=500,lr=.08,l2=1e-3)
            yte=data['Test']['ys'][:,j]; score=mod.predict_binary(w,X['Test']); m=metric(yte,score)
            if m is None: continue
            per.append({'label':name,'test_positive':int(yte.sum()),'auroc':m[0],'average_precision':m[1]})
        outputs[view]={'n_test':len(data['Test']['paths']),'labels_evaluated':len(per),'mean_auroc':float(np.mean([r['auroc'] for r in per])),'mean_average_precision':float(np.mean([r['average_precision'] for r in per])),'per_label':per}
    result={'dataset':'RFMiD 2.0','counts':{k:len(v['paths']) for k,v in data.items()},'n_labels':len(names),'views':outputs,'notes':['This is an external ordinary color fundus check, not a paired full-UWF ground truth experiment.','The central view is a geometric crop and the labels are image-level multi-label disease tags.']}
    json.dump(result,(HERE/'results.json').open('w'),ensure_ascii=False,indent=2)
    (HERE/'REPORT.md').write_text('# Exp04：RFMiD2 外部普通眼底多标签视野消融\n\n目的：在独立的普通眼底图像数据上，检查中心视野裁剪是否会改变多种眼底疾病的可检测性。\n\n- RFMiD2：51 个疾病/异常标签，按官方 Training/Validation/Test 划分。\n- 模型：每个疾病标签一个 67 维手工特征二分类逻辑回归。\n- 对比：完整图像 vs 55% 中心视野裁剪。\n- 解释边界：不是 paired UWF/45° 数据；只能作为外部方向性验证。\n\n完整结果见 `results.json`。\n',encoding='utf-8')
    print(json.dumps({k:{q:v for q,v in val.items() if q!='per_label'} for k,val in outputs.items()},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
