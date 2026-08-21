# 优化实验决策清单：RegionSufficiency 新论文

本清单对应 Exp55–Exp62。规则是：不根据单个随机种子或单个测试指标做推广；至少检查五种子结果、同图/同测试集配对比较或明确的外部安全终点。所有原始 Exp01–Exp54 结果均未覆盖。

## 逐项结论

| 实验 | 测试内容 | 结论 | 是否写入新论文 | 判定依据 |
|---|---|---:|---:|---|
| Exp55-A | 3×3 区域 token 加可学习二维坐标 | 剔除 | 否 | center-plus-cross 点估计有小幅 F1 增益，但五个种子方向不一致；不能证明稳定改善。 |
| Exp55-B | 坐标编码 + 连通区域遮罩 | 剔除 | 否 | center-plus-cross macro-F1 约 0.815，低于同批基线约 0.839；MAE 与低估率也未改善。 |
| Exp55-C | 连通遮罩 + 低估惩罚 | 剔除 | 否 | center-plus-cross macro-F1 约 0.825，仍低于同批基线；低估率升高。 |
| Exp56/57 | 五种子集成、单视图风险头 | 剔除 | 否 | 初始 AUROC=0.767；严格同测试集 Exp62 比较时，单视图−配对视图 AUROC=−0.005，95% bootstrap CI=[−0.062, 0.047]。 |
| Exp58 | 区域级 source/target moment normalization | 剔除 | 否 | IDRiD/SUSTech 的分类点估计虽上升，但 MMRDR 分类性能下降，且低估率显著增加；不具备可迁移安全性。 |
| Exp59 | 分层选择性风险阈值 | 剔除 | 否 | 整体 coverage 明显坍缩，NPDR 分层几乎无法接受样本且出现 1.0 的接受风险；不写成改进。 |
| Exp60 | 连续像素 aperture 训练增强 | 保留为鲁棒性模块 | 是 | 35% 中心矩形：macro-F1 0.519→0.794，MAE 0.446→0.221，低估率 0.272→0.097；55%、75% 矩形和 55% 圆形的 F1/MAE 也一致改善，但较大视野低估率小幅上升，论文中明确报告 trade-off。 |
| Exp61 | 区域序数注意力/低估惩罚 | 剔除 | 否 | 五种子 cross-view 点估计混合，配对差异不一致；未形成稳定的宏 F1、MAE 和低估率共同改善。 |
| Exp62 | 单视图风险头与配对风险头的严格配对比较 | 作为否定性筛选证据 | 否 | 单视图模型没有显著优于可获得完整视图的配对模型，且真实单次采集风险标签仍缺失。 |

## 新论文实际保留的改动

只将 Exp60 作为“Continuous-aperture robustness extension”写入方法、结果、讨论和局限性。主模型仍是预先锁定的 3×3 RetinaRadar 冻结区域表征 + masked attention + 30% 随机区域遮罩；连续 aperture 变体不改变主要内部终点、MMRDR 外部评估或选择性风险主结论。

新增论文材料：

- 新增方法小节：`2.13 Continuous-aperture robustness extension`。
- 新增结果小节：`3.7 Continuous-aperture training improves severe evidence-loss robustness`。
- 新增表 6：四种 held-out pixel-space aperture 的 baseline/augmentation 对比。
- 新增图 8：macro-F1、severity MAE、underestimation rate 三个面板。
- 摘要、讨论、结论和局限性均明确说明：F1/MAE 改善并不等于所有安全指标无代价改善。

## 证据位置

- Exp55：`experiments/exp55_optimization_batch/results.json` 与 `REPORT.md`
- Exp56/57：`experiments/exp56_ensemble_singleview/results.json` 与 `REPORT.md`
- Exp58：`experiments/exp58_regionwise_external_adaptation/results.json` 与 `REPORT.md`
- Exp59：`experiments/exp59_stratified_risk_calibration/results.json` 与 `REPORT.md`
- Exp60：`experiments/exp60_pixel_aperture_training/results.json` 与 `REPORT.md`
- Exp61：`experiments/exp61_regional_ordinal/results.json` 与 `REPORT.md`
- Exp62：`experiments/exp62_singleview_risk_paired_bootstrap/results.json` 与 `REPORT.md`

