#!/usr/bin/env python3
"""Exp33: external MSHF source-held-out audit of global vs region features."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import openpyxl
import torch
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]; HERE.mkdir(parents=True,exist_ok=True)
M30=ROOT/"7hao/experiments/exp30_deep_region_attention/run_deep_region_attention.py"
spec=importlib.util.spec_from_file_location("m30",M30); m30=importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(m30)
BASE=ROOT/"7hao/datasets/MSHF_IQA/extracted/MSHF dataset 2.0"; NAMES=("clarity","illumination","contrast","overall")


def labels_map():
    wb=openpyxl.load_workbook(BASE/"Individual_scores.xlsx.xlsx",read_only=True,data_only=True); out={}
    for row in wb.active.iter_rows(min_row=3,values_only=True):
        if not row or not row[0]: continue
        groups=((1,2,3,4),(6,7,8,9),(11,12,13,14)); vals=[]
        for cols in zip(*groups):
            v=[row[i] for i in cols]; vals.append(None if any(x is None for x in v) else int(sum(int(x) for x in v)>=2))
        if all(x is not None for x in vals): out[str(row[0])]=[vals[1],vals[0],vals[2],vals[3]]
    return out


def global_extract(model,device,arrs):
    out=[]
    for st in range(0,len(arrs),32):
        with torch.no_grad(): out.append(model.global_pool(model.forward_features(m30.tensor_batch(arrs[st:st+32]).to(device))).flatten(1).cpu().numpy().astype(np.float32))
        if st%256==0: print(f"global: {min(st+32,len(arrs))}/{len(arrs)}",flush=True)
    return np.vstack(out)


def weights(src,y,mode):
    if mode=="unweighted": return np.ones(len(y))
    w=np.zeros(len(y))
    for s in sorted(set(src)):
        for c in (0,1):
            m=(src==s)&(y==c)
            if m.any(): w[m]=1/m.sum()
    return w*len(y)/max(1e-12,w.sum())


def metric(y,p):
    if len(np.unique(y))<2:return None
    return {"auroc":float(roc_auc_score(y,p)),"average_precision":float(average_precision_score(y,p)),"positive_rate":float(y.mean()),"n":int(len(y))}


def main():
    lab=labels_map(); paths=sorted([p for s in ("train","test") for p in (BASE/"AI-use"/s).glob("*.jpg") if p.name in lab]); y=np.asarray([lab[p.name] for p in paths],int); src=np.asarray([p.name.rsplit("-",1)[0] for p in paths]); arr=[m30.baseline.read_image(p) for p in paths]; model,device=m30.load_model(); print(f"device={device}; n={len(arr)}",flush=True); global_x=global_extract(model,device,arr); region_x=m30.extract(model,device,arr).mean(1)
    result={"dataset":{"n":len(paths),"sources":{s:int((src==s).sum()) for s in sorted(set(src))},"labels":list(NAMES),"device":str(device)},"leave_one_source_out":{},"aggregate":{},"notes":["MSHF has no public patient identifier; source holdout is used as the conservative available split.","All features are frozen RetinaRadar representations; region_mean averages the 3x3 regional embeddings.","This is an external quality/domain audit, not disease diagnosis validation."]}; cells={k:[] for k in ("global_unweighted","global_source_label_balanced","region_mean_unweighted","region_mean_source_label_balanced")}
    for hold in sorted(set(src)):
        tr,te=src!=hold,src==hold; result["leave_one_source_out"][hold]={"n_test":int(te.sum()),"metrics":{}}
        for rep,X in (("global",global_x),("region_mean",region_x)):
            mu,sd=X[tr].mean(0),X[tr].std(0); sd[sd<1e-8]=1; xt,xe=(X[tr]-mu)/sd,(X[te]-mu)/sd
            for mode in ("unweighted","source_label_balanced"):
                key=f"{rep}_{mode}"; result["leave_one_source_out"][hold]["metrics"][key]={}
                for j,name in enumerate(NAMES):
                    if len(np.unique(y[tr,j]))<2 or len(np.unique(y[te,j]))<2: continue
                    clf=LogisticRegression(C=.1,max_iter=800,solver="liblinear",random_state=42); clf.fit(xt,y[tr,j],sample_weight=weights(src[tr],y[tr,j],mode)); p=clf.predict_proba(xe)[:,1]; m=metric(y[te,j],p); result["leave_one_source_out"][hold]["metrics"][key][name]=m
                    if m: cells[key].append((hold,name,m["auroc"],m["average_precision"]))
    for key,rows in cells.items(): result["aggregate"][key]={"mean_auroc":float(np.mean([r[2] for r in rows])) if rows else None,"mean_average_precision":float(np.mean([r[3] for r in rows])) if rows else None,"n_cells":len(rows),"cells":[{"source":r[0],"label":r[1],"auroc":r[2],"average_precision":r[3]} for r in rows]}
    (HERE/"results.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8"); (HERE/"REPORT.md").write_text("# Exp33：外部来源区域泛化审计\n\n在MSHF来源留一设置中比较全图RetinaRadar特征和3×3区域平均RetinaRadar特征，并比较普通训练与来源×标签均衡。重点观察UWF-mosaic来源。\n\n```json\n"+json.dumps(result,ensure_ascii=False,indent=2)+"\n```\n",encoding="utf-8"); print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
