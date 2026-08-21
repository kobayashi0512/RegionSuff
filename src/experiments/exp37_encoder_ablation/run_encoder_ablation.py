#!/usr/bin/env python3
"""Task 5: encoder ablation for regional aggregation."""
from __future__ import annotations
import copy, importlib.util, json
from pathlib import Path
import numpy as np, torch
from torch import nn

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]; CACHE=ROOT/'7hao/experiments/exp34_shared_uwf_region_cache'; HERE.mkdir(parents=True,exist_ok=True)
sp=importlib.util.spec_from_file_location('ab',ROOT/'7hao/experiments/exp35_region_mask_pool_ablation/run_ablation.py'); ab=importlib.util.module_from_spec(sp); assert sp.loader; sp.loader.exec_module(ab)
sp2=importlib.util.spec_from_file_location('m30',ROOT/'7hao/experiments/exp30_deep_region_attention/run_deep_region_attention.py'); m30=importlib.util.module_from_spec(sp2); assert sp2.loader; sp2.loader.exec_module(m30)

def handcrafted(arrs):
    return np.stack([np.vstack([m30.baseline.feature_vector(c)[0] for c in m30.grid_crops(a)]) for a in arrs]).astype(np.float32)
def load_arrs(meta):
    b=m30.baseline; mp=b.find_uwf_image_map(); out={}
    for s in ('train','val','test'):
        out[s]=[b.read_image(mp[n]) for n in meta[s]['paths']]
    return out
def resnet_features(arrs,weights):
    from torchvision.models import resnet50,ResNet50_Weights
    model=resnet50(weights=weights); model.fc=nn.Identity(); model.eval(); dev=torch.device('mps' if torch.backends.mps.is_available() else 'cpu'); model=model.to(dev); crops=[]
    for a in arrs:crops.extend(m30.grid_crops(a))
    out=[]
    for st in range(0,len(crops),32):
        with torch.no_grad():out.append(model(m30.tensor_batch(crops[st:st+32]).to(dev)).cpu().numpy().astype(np.float32))
        if st%512==0:print(f'resnet: {min(st+32,len(crops))}/{len(crops)}',flush=True)
    return np.vstack(out).reshape(len(arrs),9,-1)
def fit_eval(raw,y):
    mu=raw['train'].reshape(-1,raw['train'].shape[-1]).mean(0); sd=raw['train'].reshape(-1,raw['train'].shape[-1]).std(0); sd[sd<1e-8]=1; X={s:(raw[s]-mu)/sd for s in raw}; mdl,dev,vs,ep=ab.train(X['train'],y['train'],X['val'],y['val'],'attention',.30,42); return {'best_val_macro_f1':float(vs),'epochs':int(ep),'full':ab.evaluate(mdl,dev,X['test'],y['test'],ab.eval_mask('full',len(y['test']),3)),'cross':ab.evaluate(mdl,dev,X['test'],y['test'],ab.eval_mask('cross',len(y['test']),3))}
def main():
    meta=json.loads((CACHE/'split_meta.json').read_text()); y={s:np.asarray(meta[s]['y'],int) for s in ('train','val','test')}; arr=load_arrs(meta); result={'representations':{},'notes':['RetinaRadar is the primary frozen retinal-quality encoder; ImageNet uses cached torchvision ResNet50 weights; random is an untrained ResNet50 control; handcrafted is the 67-dimensional regional-statistics control.','All representations use the same 3x3 region masks and attention aggregator.']}
    z=np.load(CACHE/'region_features_g3.npz'); result['representations']['retinaradar_region']=fit_eval({s:z[f'{s}_features'] for s in y},y); result['representations']['handcrafted_region']=fit_eval({s:handcrafted(arr[s]) for s in y},y)
    try:
        from torchvision.models import ResNet50_Weights
        result['representations']['imagenet_resnet50_region']=fit_eval({s:resnet_features(arr[s],ResNet50_Weights.DEFAULT) for s in y},y)
        result['representations']['random_resnet50_region']=fit_eval({s:resnet_features(arr[s],None) for s in y},y)
    except Exception as e:
        result['encoder_error']=repr(e)
    (HERE/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8'); (HERE/'REPORT.md').write_text('# Exp37：区域编码器消融\n\n比较RetinaRadar、ImageNet ResNet50、随机ResNet50和手工区域特征在同一注意力聚合器下的表现。\n\n```json\n'+json.dumps(result,ensure_ascii=False,indent=2)+'\n```\n',encoding='utf-8'); print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
