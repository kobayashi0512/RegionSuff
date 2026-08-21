#!/usr/bin/env python3
"""External validation of RetinaRadar frozen features on ordinary fundus images."""
from __future__ import annotations
import csv, json
from pathlib import Path
import numpy as np
import torch, timm
from PIL import Image
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score

ROOT = Path(__file__).resolve().parents[3]
RF = ROOT / "7hao" / "datasets" / "RFMiD2_0" / "extracted"
MODEL_PATH = ROOT / "7hao" / "models" / "retinaradar" / "efficientnet_b0_retinaradar_model.ckpt"
OUT = ROOT / "7hao" / "experiments" / "exp12_retinaradar_rfmid_external"
OUT.mkdir(parents=True, exist_ok=True)
MEAN = np.asarray([.485, .456, .406], np.float32); STD = np.asarray([.229, .224, .225], np.float32)

def read_split(name):
    folder = RF / name
    p_csv = next(folder.glob("*_labels.csv"))
    rows=[]
    with p_csv.open(newline="", encoding="latin-1") as f:
        rd=csv.DictReader(f); labels=[x for x in (rd.fieldnames or []) if x and x != "ID"]
        mp={int(p.stem):p for p in folder.iterdir() if p.suffix.lower() in {".jpg",".jpeg",".png"}}
        for row in rd:
            i=int(row["ID"])
            if i in mp: rows.append((mp[i],np.asarray([int(float(row.get(x,0) or 0)) for x in labels],np.int64)))
    return labels, rows

def load_model():
    c=torch.load(MODEL_PATH,map_location="cpu"); m=timm.create_model("efficientnet_b0",pretrained=False,num_classes=17)
    m.load_state_dict({k.replace("model.","",1):v for k,v in c["state_dict"].items()},strict=True); m.eval()
    d=torch.device("mps" if torch.backends.mps.is_available() else "cpu"); return m.to(d),d

def prep(paths, view):
    xs=[]
    for p in paths:
        with Image.open(p) as im: im=im.convert("RGB").resize((256,256),Image.Resampling.BILINEAR)
        if view=="central": im=im.crop((32,32,224,224)).resize((256,256),Image.Resampling.BILINEAR)
        x=np.asarray(im,np.float32)/255.; x=(x-MEAN)/STD; xs.append(np.transpose(x,(2,0,1)))
    return torch.from_numpy(np.stack(xs)).float()

def extract(m,d,paths,view):
    fs=[]; qs=[]
    for st in range(0,len(paths),32):
        x=prep(paths[st:st+32],view).to(d)
        with torch.no_grad():
            z=m.global_pool(m.forward_features(x)).flatten(1); q=m(x)
        fs.append(z.cpu().numpy().astype(np.float32)); qs.append(q.cpu().numpy().astype(np.float32))
    return np.vstack(fs),np.vstack(qs)

def aucs(y,score):
    out=[]
    for j in range(y.shape[1]):
        if len(np.unique(y[:,j]))<2: continue
        out.append((roc_auc_score(y[:,j],score[:,j]),average_precision_score(y[:,j],score[:,j])))
    return out

def main():
    labels={}; data={}
    for s in ("Training","Validation","Test"):
        labels[s],data[s]=read_split(s)
    labels_list=labels["Training"]; m,d=load_model(); print(f"device={d}; counts="+str({s:len(data[s]) for s in data}),flush=True)
    results={"dataset":"RFMiD2.0","models":{},"quality_shift":{},"notes":[]}
    all_tr=data["Training"]+data["Validation"]; xtr_paths=[x[0] for x in all_tr]; ytr=np.vstack([x[1] for x in all_tr]); xt_paths=[x[0] for x in data["Test"]]; yt=np.vstack([x[1] for x in data["Test"]])
    for view in ("full","central"):
        ftr,qtr=extract(m,d,xtr_paths,view); fte,qte=extract(m,d,xt_paths,view)
        mu=ftr.mean(0); sd=ftr.std(0); sd[sd<1e-8]=1.; ftr=(ftr-mu)/sd; fte=(fte-mu)/sd
        scores=[]; per=[]
        for j,label in enumerate(labels_list):
            if ytr[:,j].sum()==0 or ytr[:,j].sum()==len(ytr): continue
            clf=LogisticRegression(max_iter=300,C=.1,solver="liblinear",random_state=42); clf.fit(ftr,ytr[:,j]); sc=clf.predict_proba(fte)[:,1]
            if len(np.unique(yt[:,j]))<2: continue
            per.append({"label":label,"test_positive":int(yt[:,j].sum()),"auroc":float(roc_auc_score(yt[:,j],sc)),"average_precision":float(average_precision_score(yt[:,j],sc))})
        results["models"][view]={"n_labels":len(per),"mean_auroc":float(np.mean([r["auroc"] for r in per])),"mean_average_precision":float(np.mean([r["average_precision"] for r in per])),"per_label":per}
        # sigmoid quality outputs are retained as a domain-shift diagnostic;
        # they are not treated as disease ground truth.
        qp=1/(1+np.exp(-qte)); results["quality_shift"][view]={"mean_quality_logits_sigmoid":qp.mean(0).tolist(),"mean_abs_quality_logit":np.abs(qte).mean(0).tolist()}
        print(view,results["models"][view]["mean_auroc"],results["models"][view]["mean_average_precision"],flush=True)
    results["notes"]=["RFMiD2.0 is an external ordinary color fundus dataset, not a paired UWF/45-degree dataset.","The frozen RetinaRadar representation is trained only through linear probes on the RFMiD training+validation images.","Quality outputs are reported for shift diagnosis, not as ophthalmologist quality labels."]
    (OUT/"results.json").write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding="utf-8")
    (OUT/"REPORT.md").write_text("# Exp12：RetinaRadar 冻结表征外部验证\n\n在 RFMiD2.0 普通彩色眼底图像上，用 RetinaRadar 冻结特征训练多标签线性探针；比较完整图像与中心裁剪，检验表征是否具有跨数据集可迁移性。\n\n完整结果见 `results.json`。注意：这不是 UWF/45° 同眼配对验证。\n",encoding="utf-8")
    print(json.dumps({k:{x:y for x,y in v.items() if x!='per_label'} for k,v in results["models"].items()},ensure_ascii=False,indent=2))
if __name__=="__main__": main()
