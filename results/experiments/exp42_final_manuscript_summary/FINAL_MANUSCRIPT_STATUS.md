# RegionSufficiency投稿前十项任务最终审计

## 固定主要终点

- Primary endpoint：test macro-F1 under the center+cross limited-view mask
- Model selection：validation macro-F1；测试集只做一次最终评估。
- Final configuration：3×3 region bank + frozen RetinaRadar + attention pooling + 30% random region masking。

## 任务状态

- task1_multiseed: completed
- task2_grid_ablation: completed
- task3_mask_ratio: completed
- task4_pooling_ablation: completed
- task5_encoder: completed
- task6_selective: completed
- task7_occlusion: completed
- task8_rfmid: completed
- task9_bootstrap_paired: completed

## 证据边界

- Geometric limited-view masks are proxies, not real same-eye 45-degree acquisitions.
- MSHF source-holdout results are quality/domain audits, not disease external validation.
- No clinical deployment claim is made.
