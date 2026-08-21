#!/usr/bin/env python3
"""Task 10: freeze endpoints/model rule and generate the manuscript audit."""
from __future__ import annotations
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];HERE.mkdir(parents=True,exist_ok=True)
def load(dir_name):
    p=ROOT/'7hao/experiments'/dir_name/'results.json'; return json.load(p.open()) if p.exists() else None
def main():
    registry={'primary_endpoint':'test macro-F1 under the center+cross limited-view mask','secondary_endpoints':['test severity MAE','test underestimation rate','PDR recall','selective accepted underestimation risk at target coverage','MSHF leave-one-source-out overall AUROC','RFMiD2 mean AUROC/AP'],'selection_rule':'Choose the final model using validation macro-F1 under the center+cross mask; use test only once for final reporting. If validation scores tie within 0.005, choose the smaller model and lower validation underestimation rate.','frozen_configuration':{'region_grid':'3x3','encoder':'RetinaRadar EfficientNet-B0 frozen regional representation','aggregator':'attention','training_mask_ratio':0.30,'random_seeds':[0,1,2,3,4]},'claim_boundary':['Geometric limited-view masks are proxies, not real same-eye 45-degree acquisitions.','MSHF source-holdout results are quality/domain audits, not disease external validation.','No clinical deployment claim is made.'],'status':{}}
    tasks=[
        ('task1_multiseed','exp36_multiseed_deep_region'),
        ('task2_grid_ablation','exp35_region_mask_pool_ablation'),
        ('task3_mask_ratio','exp35_region_mask_pool_ablation'),
        ('task4_pooling_ablation','exp35_region_mask_pool_ablation'),
        ('task5_encoder','exp37_encoder_ablation'),
        ('task6_selective','exp40_final_region_selective_risk'),
        ('task7_occlusion','exp39_attention_occlusion_validation'),
        ('task8_rfmid','exp38_rfmid_region_external'),
        ('task9_bootstrap_paired','exp41_bootstrap_paired_stats'),
    ]
    for name,d in tasks:
        p=ROOT/'7hao/experiments'/d/'results.json'; registry['status'][name]='completed' if p.exists() else 'pending'
    (HERE/'endpoint_registry.json').write_text(json.dumps(registry,ensure_ascii=False,indent=2),encoding='utf-8')
    lines=['# RegionSufficiency投稿前十项任务最终审计','', '## 固定主要终点','',f'- Primary endpoint：{registry["primary_endpoint"]}','- Model selection：validation macro-F1；测试集只做一次最终评估。','- Final configuration：3×3 region bank + frozen RetinaRadar + attention pooling + 30% random region masking。','', '## 任务状态','']
    for k,v in registry['status'].items():lines.append(f'- {k}: {v}')
    registry['status']['task10_final_audit']='completed'
    (HERE/'results.json').write_text(json.dumps(registry,ensure_ascii=False,indent=2),encoding='utf-8')
    (HERE/'REPORT.md').write_text('# Exp42：投稿前十项任务终点与论文结果汇总\n\n本任务冻结主要终点、最终模型配置、模型选择规则和证据边界。未重新训练模型，仅对Exp34–Exp41结果进行审计登记。\n\n```json\n'+json.dumps(registry,ensure_ascii=False,indent=2)+'\n```\n',encoding='utf-8')
    lines += ['', '## 证据边界','']+[f'- {x}' for x in registry['claim_boundary']]
    (HERE/'FINAL_MANUSCRIPT_STATUS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8');print(json.dumps(registry,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
