#!/usr/bin/env python3
"""Exp48b: pixel-space continuous apertures with fixed retinal coordinates."""
from __future__ import annotations
import importlib.util, json
from pathlib import Path
import numpy as np, torch

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]; CACHE=ROOT/'7hao/experiments/exp34_shared_uwf_region_cache'; HERE.mkdir(parents=True,exist_ok=True)
sp=importlib.util.spec_from_file_location('ab',ROOT/'7hao/experiments/exp35_region_mask_pool_ablation/run_ablation.py'); ab=importlib.util.module_from_spec(sp); assert sp.loader; sp.loader.exec_module(ab)
sp2=importlib.util.spec_from_file_location('m30',ROOT/'7hao/experiments/exp30_deep_region_attention/run_deep_region_attention.py'); m30=importlib.util.module_from_spec(sp2); assert sp2.loader; sp2.loader.exec_module(m30)
meta=json.loads((CACHE/'split_meta.json').read_text()); y={s:np.asarray(meta[s]['y'],int) for s in ('train','val','test')}; z=np.load(CACHE/'region_features_g3.npz'); raw={s:z[f'{s}_features'] for s in y}; mu=raw['train'].reshape(-1,raw['train'].shape[-1]).mean(0); sd=raw['train'].reshape(-1,raw['train'].shape[-1]).std(0); sd[sd<1e-8]=1; X={s:(raw[s]-mu)/sd for s in y}
image_map=m30.baseline.find_uwf_image_map(); test_arr=[m30.baseline.read_image(image_map[Path(p).name]) for p in meta['test']['paths']]; bboxes=[m30.baseline.retinal_bbox(a)[:4] for a in test_arr]
def aperture(arr,bbox,shape,f,dx=0.,dy=0.):
    x0,y0,x1,y1=bbox; h=y1-y0; w=x1-x0; cx=x0+w*(.5+dx*(1-f)/2); cy=y0+h*(.5+dy*(1-f)/2); yy,xx=np.ogrid[:arr.shape[0],:arr.shape[1]]
    if shape=='rect': keep=(np.abs(xx-cx)<=w*f/2)&(np.abs(yy-cy)<=h*f/2)
    else: keep=((xx-cx)/(w+1e-8))**2+((yy-cy)/(h+1e-8))**2 <= (f/np.sqrt(np.pi))**2
    out=np.zeros_like(arr); out[keep]=arr[keep]; return out
def fixed_grid_crops(arr,bbox):
    x0,y0,x1,y1=bbox; roi=arr[y0:y1,x0:x1]; h,w=roi.shape[:2]; return [roi[int(r*h/3):int((r+1)*h/3),int(c*w/3):int((c+1)*w/3)] for r in range(3) for c in range(3)]
def extract_fixed(model,dev,arrs,bboxes,batch=32):
    crops=[]
    for a,b in zip(arrs,bboxes): crops.extend(fixed_grid_crops(a,b))
    out=[]
    for st in range(0,len(crops),batch):
        with torch.no_grad(): out.append(model.global_pool(model.forward_features(m30.tensor_batch(crops[st:st+batch]).to(dev))).flatten(1).cpu().numpy().astype(np.float32))
        if st%2048==0: print(f'features={min(st+batch,len(crops))}/{len(crops)}',flush=True)
    return np.vstack(out).reshape(len(arrs),9,-1)
def main():
    scenarios=[]
    for f in (.35,.45,.55,.65,.75,.90): scenarios.append((f'rect_center_{f:.2f}','rect',f,0.,0.))
    for pos,dx,dy in (('center',0,0),('left',-1,0),('right',1,0),('up',0,-1),('down',0,1)): scenarios.append((f'rect_{pos}_0.55','rect',.55,dx,dy))
    for f in (.35,.45,.55,.65,.75,.90): scenarios.append((f'circle_center_{f:.2f}','circle',f,0.,0.))
    model,dev=m30.load_model(); models=[]
    for seed in (0,1,2,3,4): models.append((seed,*ab.train(X['train'],y['train'],X['val'],y['val'],'attention',.30,seed)))
    rows=[]
    for name,shape,f,dx,dy in scenarios:
        masked=[aperture(a,b,shape,f,dx,dy) for a,b in zip(test_arr,bboxes)]; feat=extract_fixed(model,dev,masked,bboxes); feat=(feat-mu)/sd
        for seed,head,hdev,vs,ep in models:
            rows.append({'seed':seed,'scenario':name,'shape':shape,'linear_fraction':f,'dx':dx,'dy':dy,'best_val_macro_f1':float(vs),'epochs':int(ep),**ab.evaluate(head,hdev,feat,y['test'],np.ones((len(y['test']),9),np.float32))})
        print(f'{name} done',flush=True)
    aggregate={}
    for name,_,_,_,_ in scenarios:
        q=[r for r in rows if r['scenario']==name]; aggregate[name]={k:{'mean':float(np.mean([r[k] for r in q])),'std':float(np.std([r[k] for r in q],ddof=1))} for k in ('accuracy','macro_f1','severity_mae','underestimation_rate')}
    result={'grid':'3x3 frozen-region features on pixel-masked inputs','n_seeds':5,'rows':rows,'aggregate':aggregate,'notes':['Apertures are drawn in the original retinal bounding box, while feature-grid coordinates stay fixed to that full bbox.','Unlike Exp48, this experiment re-extracts CNN embeddings after pixel-space masking, so continuous apertures change the observed image content.','Apertures are geometric proxies, not real paired camera acquisitions.']}
    (HERE/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8'); (HERE/'REPORT.md').write_text('# Exp48b：像素空间连续视野与位置/形状实验\n\n在原始UWF像素空间绘制连续矩形和等面积圆形孔径，并保持原视网膜坐标系固定后重新提取3×3冻结区域表征。\n\n```json\n'+json.dumps(result,ensure_ascii=False,indent=2)+'\n```\n',encoding='utf-8'); print(json.dumps(aggregate,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
