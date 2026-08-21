#!/usr/bin/env python3
"""Exp03: a small raw-image MLP to test whether hand features leave signal unused."""
from __future__ import annotations
import importlib.util, json, csv
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent; WORKSPACE=HERE.parents[2]; BASE=WORKSPACE/"7hao/experiments/exp01_quality_fov_baseline/run_baseline.py"
spec=importlib.util.spec_from_file_location("baseline",BASE); mod=importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(mod)

def softmax(z):
    z=z-z.max(axis=1,keepdims=True); e=np.exp(np.clip(z,-30,30)); return e/e.sum(axis=1,keepdims=True)
def fit_mlp(X,y,hidden=32,epochs=180,lr=0.08,l2=1e-4,seed=7):
    rng=np.random.default_rng(seed); d=X.shape[1]; k=3
    W1=rng.normal(0,np.sqrt(2/d),(d,hidden)); b1=np.zeros(hidden); W2=rng.normal(0,np.sqrt(2/hidden),(hidden,k)); b2=np.zeros(k); Y=np.eye(k)[y]
    for ep in range(epochs):
        H=np.maximum(0,X@W1+b1); P=softmax(H@W2+b2); d2=(P-Y)/len(X); gW2=H.T@d2+l2*W2; gb2=d2.sum(0); d1=(d2@W2.T)*(H>0); gW1=X.T@d1+l2*W1; gb1=d1.sum(0)
        step=lr/(1+0.01*ep); W1-=step*gW1; b1-=step*gb1; W2-=step*gW2; b2-=step*gb2
    return W1,b1,W2,b2
def predict(par,X):
    W1,b1,W2,b2=par; return softmax(np.maximum(0,X@W1+b1)@W2+b2)
def load_view(splits,frac):
    out={}
    for split,d in splits.items():
        xs=[]
        for i,p in enumerate(d['paths'],1):
            a=mod.read_image(p) if frac>=0.99 else mod.central_view(mod.read_image(p),frac)
            a=mod.resize_array(a,16); xs.append(a.reshape(-1))
            if i%300==0: print(frac,split,i,flush=True)
        out[split]=np.vstack(xs).astype(np.float64)
    tr=out['train']; mu=tr.mean(0); sd=tr.std(0); sd[sd<1e-6]=1; return {k:(v-mu)/sd for k,v in out.items()}
def main():
    imap=mod.find_uwf_image_map(); records=[]
    for split in ('train','val','test'):
        p,y=mod.read_split(split,imap); records.extend(zip(p,y.tolist()))
    splits=mod.make_patient_level_splits(records,seed=42); rows=[]
    for frac in (0.99,0.55):
        X=load_view(splits,frac); par=fit_mlp(X['train'],splits['train']['y'])
        for split in ('train','val','test'):
            y=splits[split]['y']; p=predict(par,X[split]); pred=p.argmax(1)
            rows.append({'view':'full' if frac>=0.99 else 'central_55','split':split,'accuracy':float(np.mean(pred==y)),'macro_f1':mod.macro_f1(y,pred),'severity_mae':float(np.mean(abs(pred-y))),'underestimate_rate':float(np.mean(pred<y)),'mean_entropy':float(np.mean(-np.sum(p*np.log(np.clip(p,1e-8,1)),1)))})
    json.dump({'rows':rows,'model':'16x16 RGB flatten -> ReLU(32) -> softmax MLP','notes':['This is a shallow raw-image comparison, not a foundation model.','Central view is a geometric crop from UWF.']},(HERE/'results.json').open('w'),ensure_ascii=False,indent=2)
    with (HERE/'metrics.csv').open('w',newline='') as f: w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    (HERE/'REPORT.md').write_text('# Exp03：浅层原始图像模型对照\n\n目的：检验 67 维手工特征之外，低分辨率原始像素是否还包含可用信息。\n\n- 输入：16×16 RGB，展平为 768 维。\n- 模型：ReLU(32) 的浅层 MLP。\n- 对照：完整 UWF 与 55% 中心视野。\n- 结论解释：只用于判断“手工特征基线是否过弱”，不代表最终深度模型。\n\n结果见 `metrics.csv` 与 `results.json`。\n',encoding='utf-8')
    print(json.dumps(rows,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
