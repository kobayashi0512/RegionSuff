#!/usr/bin/env python3
"""Exp30: RetinaRadar frozen region embeddings with attention pooling."""
from __future__ import annotations

import copy
import csv
import importlib.util
import json
from pathlib import Path

import numpy as np
import timm
import torch
from PIL import Image
from torch import nn

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HERE.mkdir(parents=True, exist_ok=True)
BASE = ROOT / "7hao/experiments/exp01_quality_fov_baseline/run_baseline.py"
MODEL_PATH = ROOT / "7hao/models/retinaradar/efficientnet_b0_retinaradar_model.ckpt"
spec = importlib.util.spec_from_file_location("baseline", BASE)
baseline = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(baseline)
MEAN = np.asarray([.485, .456, .406], np.float32)
STD = np.asarray([.229, .224, .225], np.float32)


def load_model():
    ckpt = torch.load(MODEL_PATH, map_location="cpu")
    m = timm.create_model("efficientnet_b0", pretrained=False, num_classes=17)
    m.load_state_dict({k.replace("model.", "", 1): v for k, v in ckpt["state_dict"].items()}, strict=True)
    m.eval(); device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    return m.to(device), device


def grid_crops(arr):
    x0, y0, x1, y1, _ = baseline.retinal_bbox(arr); roi = arr[y0:y1, x0:x1]; h, w = roi.shape[:2]
    out=[]
    for r in range(3):
        for c in range(3): out.append(roi[int(r*h/3):int((r+1)*h/3),int(c*w/3):int((c+1)*w/3)])
    return out


def tensor_batch(crops):
    xs=[]
    for a in crops:
        im=Image.fromarray(np.clip(a*255,0,255).astype("uint8")).resize((256,256),Image.Resampling.BILINEAR).crop((16,16,240,240))
        x=np.asarray(im,np.float32)/255.; x=(x-MEAN)/STD; xs.append(np.transpose(x,(2,0,1)))
    return torch.from_numpy(np.stack(xs)).float()


def extract(model, device, arrs, batch=32):
    crops=[]
    for a in arrs: crops.extend(grid_crops(a))
    out=[]
    for st in range(0,len(crops),batch):
        with torch.no_grad(): z=model.global_pool(model.forward_features(tensor_batch(crops[st:st+batch]).to(device))).flatten(1)
        out.append(z.cpu().numpy().astype(np.float32))
        if st % 512 == 0: print(f"regions: {min(st+batch,len(crops))}/{len(crops)}",flush=True)
    return np.vstack(out).reshape(len(arrs),9,-1)


class AttentionMIL(nn.Module):
    def __init__(self, fdim, hidden=128):
        super().__init__(); self.embed=nn.Sequential(nn.Linear(fdim,hidden),nn.LayerNorm(hidden),nn.ReLU()); self.att=nn.Sequential(nn.Linear(hidden,48),nn.Tanh(),nn.Linear(48,1)); self.cls=nn.Linear(hidden,3)
    def forward(self,x,mask):
        h=self.embed(x); s=self.att(h).squeeze(-1).masked_fill(mask<=0,-1e4); a=torch.softmax(s,1); return self.cls((a.unsqueeze(-1)*h).sum(1)),a


def mask_named(name,n):
    m=np.ones((n,9),np.float32)
    if name=="center": m[:]=0; m[:,4]=1
    elif name=="center_plus_cross": m[:]=0; m[:,[1,3,4,5,7]]=1
    elif name=="left_half": m[:]=0; m[:,[0,1,3,4,6,7]]=1
    elif name=="right_half": m[:]=0; m[:,[1,2,4,5,7,8]]=1
    elif name=="top_half": m[:]=0; m[:,[0,1,2,3,4,5]]=1
    elif name=="bottom_half": m[:]=0; m[:,[3,4,5,6,7,8]]=1
    return m


def train(model,X,y,Xv,yv,augmented,seed=42):
    torch.manual_seed(seed); rng=np.random.default_rng(seed); dev=torch.device("mps" if torch.backends.mps.is_available() else "cpu"); model=model.to(dev); xt=torch.from_numpy(X).float().to(dev); yt=torch.from_numpy(y).long().to(dev); xvt=torch.from_numpy(Xv).float().to(dev); yvt=torch.from_numpy(yv).long().to(dev); opt=torch.optim.AdamW(model.parameters(),lr=1.5e-3,weight_decay=3e-4); best=None; best_score=-1; patience=0
    for epoch in range(240):
        if augmented:
            mask=(rng.random((len(X),9))>.30).astype(np.float32); empty=mask.sum(1)==0; mask[empty,4]=1
        else: mask=np.ones((len(X),9),np.float32)
        logits,_=model(xt,torch.from_numpy(mask).float().to(dev)); loss=nn.functional.cross_entropy(logits,yt); opt.zero_grad(); loss.backward(); opt.step()
        with torch.no_grad(): vp,_=model(xvt,torch.ones((len(Xv),9),device=dev)); vm=torch.softmax(vp,1).argmax(1).cpu().numpy(); score=baseline.macro_f1(yv,vm)
        if score>best_score:
            best_score=score; best=copy.deepcopy({k:v.detach().cpu() for k,v in model.state_dict().items()}); patience=0
        else: patience+=1
        if patience>=35: break
    model.load_state_dict(best); return model,best_score,epoch+1,dev


def evaluate(model,X,y,name,device):
    mask=torch.from_numpy(mask_named(name,len(X))).float().to(device)
    with torch.no_grad(): p=torch.softmax(model(torch.from_numpy(X).float().to(device),mask)[0],1).cpu().numpy(); a=model(torch.from_numpy(X).float().to(device),mask)[1].cpu().numpy()
    pred=p.argmax(1); return {"accuracy":float(np.mean(pred==y)),"macro_f1":baseline.macro_f1(y,pred),"severity_mae":float(np.mean(abs(pred-y))),"underestimation_rate":float(np.mean(pred<y))},p,a


def main():
    mp=baseline.find_uwf_image_map(); records=[]
    for s in ("train","val","test"):
        p,y=baseline.read_split(s,mp); records.extend(zip(p,y.tolist()))
    splits=baseline.make_patient_level_splits(records,seed=42); arr={s:[baseline.read_image(p) for p in splits[s]["paths"]] for s in splits}; y={s:splits[s]["y"] for s in splits}
    model,device=load_model(); print(f"device={device}",flush=True); raw={s:extract(model,device,arr[s]) for s in splits}; mu=raw["train"].reshape(-1,raw["train"].shape[-1]).mean(0); sd=raw["train"].reshape(-1,raw["train"].shape[-1]).std(0); sd[sd<1e-8]=1; X={s:(raw[s]-mu)/sd for s in splits}; fdim=X["train"].shape[-1]
    result={"dataset":{"n":len(records),"regions":9,"encoder":"RetinaRadar EfficientNet-B0 frozen global features","device":str(device),"split_counts":{s:np.bincount(y[s],minlength=3).tolist() for s in splits}},"models":{},"attention_summary":{},"notes":["Region embeddings come from the released RetinaRadar quality model and are frozen; only the attention aggregator is trained.","The 3x3 region bank and masks are geometric proxies; no lesion-level annotation is available.","Validation macro-F1 is used for early stopping."]}; rows=[]
    for name,aug in (("deep_attention_full_only",False),("deep_attention_mask_augmented",True)):
        mdl,vs,epochs,dev=train(AttentionMIL(fdim),X["train"],y["train"],X["val"],y["val"],augmented=aug); result["models"][name]={"best_val_full_macro_f1":float(vs),"epochs":int(epochs)}
        for view in ("full","center","center_plus_cross","left_half","right_half","top_half","bottom_half"):
            met,p,a=evaluate(mdl,X["test"],y["test"],view,dev); result["models"][name][view]=met
            if view=="full":
                for i in range(len(y["test"])): rows.append([name,splits["test"]["paths"][i].name,int(y["test"][i]),int(p[i].argmax()),*a[i].tolist()])
    with (HERE/"attention_test.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(["model","image","true_label","pred_label"]+[f"attention_region_{i}" for i in range(9)]); w.writerows(rows)
    z=[r for r in rows if r[0]=="deep_attention_mask_augmented"]; aa=np.asarray([r[4:13] for r in z]); yy=np.asarray([r[2] for r in z]); result["attention_summary"]={"overall_mean_attention":aa.mean(0).tolist(),"by_severity":{str(c):aa[yy==c].mean(0).tolist() for c in (0,1,2)}}
    (HERE/"results.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8"); (HERE/"REPORT.md").write_text("# Exp30：冻结深度区域表征注意力\n\n用RetinaRadar冻结深度特征替换Exp28的67维手工区域特征，再训练区域注意力聚合器，比较完整和受限区域覆盖。\n\n```json\n"+json.dumps(result,ensure_ascii=False,indent=2)+"\n```\n",encoding="utf-8"); print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
