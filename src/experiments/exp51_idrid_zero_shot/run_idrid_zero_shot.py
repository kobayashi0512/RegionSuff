#!/usr/bin/env python3
"""Exp51: zero-shot UWF-to-IDRiD DR severity transfer."""
from __future__ import annotations
import csv, importlib.util, json
from pathlib import Path
import numpy as np
import torch
from sklearn.metrics import average_precision_score, roc_auc_score

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = ROOT / '7hao/datasets/IDRiD_Zenodo/extracted/B. Disease Grading'
CACHE = ROOT / '7hao/experiments/exp34_shared_uwf_region_cache'
HERE.mkdir(parents=True, exist_ok=True)

sp = importlib.util.spec_from_file_location('ab', ROOT / '7hao/experiments/exp35_region_mask_pool_ablation/run_ablation.py')
ab = importlib.util.module_from_spec(sp); assert sp.loader; sp.loader.exec_module(ab)
sp2 = importlib.util.spec_from_file_location('m30', ROOT / '7hao/experiments/exp30_deep_region_attention/run_deep_region_attention.py')
m30 = importlib.util.module_from_spec(sp2); assert sp2.loader; sp2.loader.exec_module(m30)

def read_idrid(split: str):
    label = DATA / '2. Groundtruths' / f"{'a' if split == 'train' else 'b'}. IDRiD_Disease Grading_{'Training' if split == 'train' else 'Testing'} Labels.csv"
    image_dir = DATA / '1. Original Images' / f"{'a. Training Set' if split == 'train' else 'b. Testing Set'}"
    rows = []
    with label.open(newline='', encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            name = r['Image name'].strip()
            grade = int(r['Retinopathy grade'])
            p = image_dir / f'{name}.jpg'
            if p.exists():
                # Source taxonomy: 0 normal, 1 non-proliferative DR, 2 proliferative DR.
                mapped = 0 if grade == 0 else 1 if grade <= 3 else 2
                rows.append((p, grade, mapped))
    return rows

def metrics(y, pred):
    return {
        'accuracy': float(np.mean(pred == y)),
        'macro_f1': float(ab.m30.baseline.macro_f1(y, pred)),
        'severity_mae': float(np.mean(np.abs(pred-y))),
        'underestimation_rate': float(np.mean(pred < y)),
    }

def main():
    meta = json.loads((CACHE / 'split_meta.json').read_text())
    z = np.load(CACHE / 'region_features_g3.npz')
    raw = {s: z[f'{s}_features'] for s in ('train', 'val')}
    mu = raw['train'].reshape(-1, raw['train'].shape[-1]).mean(0)
    sd = raw['train'].reshape(-1, raw['train'].shape[-1]).std(0); sd[sd < 1e-8] = 1
    xtr = (raw['train'] - mu) / sd; xv = (raw['val'] - mu) / sd
    ytr = np.asarray(meta['train']['y'], int); yv = np.asarray(meta['val']['y'], int)
    target = read_idrid('test')
    paths = [r[0] for r in target]
    original = np.asarray([r[1] for r in target], int)
    y = np.asarray([r[2] for r in target], int)
    feature_cache = HERE / 'idrid_testing_region_features.npz'
    if feature_cache.exists():
        x = np.load(feature_cache)['features']
    else:
        arrays = [m30.baseline.read_image(p) for p in paths]
        encoder, dev = m30.load_model()
        x = (m30.extract(encoder, dev, arrays) - mu) / sd
        np.savez_compressed(feature_cache, features=x)
    rows = []
    for seed in (0, 1, 2, 3, 4):
        head, hdev, source_f1, epochs = ab.train(xtr, ytr, xv, yv, 'attention', .30, seed)
        with torch.no_grad():
            logits, attention = head(torch.from_numpy(x).float().to(hdev), torch.ones((len(y), 9), device=hdev))
            prob = torch.softmax(logits, 1).cpu().numpy(); pred = prob.argmax(1)
        row = {'seed': seed, 'best_source_val_macro_f1': float(source_f1), 'epochs': int(epochs), **metrics(y, pred)}
        row['per_idrid_grade'] = {str(g): {'n': int((original == g).sum()), **metrics(y[original == g], pred[original == g])} for g in range(5) if np.any(original == g)}
        # P(DR) is the clinically binary use of the source 3-class head.
        binary_y = (y > 0).astype(int); binary_score = prob[:, 1] + prob[:, 2]
        row['binary_DR_vs_normal'] = {'auroc': float(roc_auc_score(binary_y, binary_score)), 'ap': float(average_precision_score(binary_y, binary_score))}
        rows.append(row)
    keys = ('accuracy', 'macro_f1', 'severity_mae', 'underestimation_rate')
    result = {
        'dataset': {'name': 'IDRiD Disease Grading official testing set', 'n_images': int(len(y)), 'original_grade_counts': {str(g): int((original == g).sum()) for g in range(5)}, 'mapped_labels': 'IDRiD grade 0 -> Normal; grades 1-3 -> NPDR; grade 4 -> PDR'},
        'protocol': 'Five source-UWF-trained RetinaRadar regional-attention heads are applied to IDRiD without using any IDRiD labels during training, early stopping, threshold selection, or model selection.',
        'rows': rows,
        'aggregate': {k: {'mean': float(np.mean([r[k] for r in rows])), 'std': float(np.std([r[k] for r in rows], ddof=1))} for k in keys},
        'binary_DR_vs_normal': {k: {'mean': float(np.mean([r['binary_DR_vs_normal'][k] for r in rows])), 'std': float(np.std([r['binary_DR_vs_normal'][k] for r in rows], ddof=1))} for k in ('auroc', 'ap')},
        'notes': ['Primary target is the official IDRiD test split (103 images).', 'This assesses disease-grade transfer, not the main sufficiency endpoint; it is supporting external evidence for the regional representation.', 'Three-class mapping is specified before evaluation to match the source task taxonomy.'],
    }
    (HERE / 'results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    (HERE / 'REPORT.md').write_text('# Exp51：IDRiD 外部零样本DR分级验证\n\n```json\n' + json.dumps(result, ensure_ascii=False, indent=2) + '\n```\n', encoding='utf-8')
    print(json.dumps({'aggregate': result['aggregate'], 'binary_DR_vs_normal': result['binary_DR_vs_normal']}, ensure_ascii=False, indent=2))

if __name__ == '__main__': main()
