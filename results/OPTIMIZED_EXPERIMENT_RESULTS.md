# 优化实验最终结果

本轮新增 Exp21–Exp26，均使用独立目录保存，没有覆盖 Exp01–Exp20。UWF-DR 仍采用患者级分组；MSHF 因公开包没有患者ID，采用来源留一审计。

## 结论总览

| 优化方向 | 最终结果 | 判断 |
|---|---:|---|
| 共享模型公平视野比较 | full-only 下中心/圆形相对完整视野配对准确率 −0.062/−0.064 | 视野损失在公平协议下成立 |
| 质量鲁棒性 | clean 0.577；亮度L3 0.408；对比度L3 0.554 | 适度增强有效；强退化需拒识 |
| PDR/序数严重度 | PDR AUROC 0.965–0.971；准确率 0.846–0.859 | 明显优于原中心冻结探针 |
| 来源泛化 | UWF-mosaic overall AUROC 0.605→0.635（来源×标签均衡） | 只部分缓解域偏移 |
| 优化模型bootstrap | 中心类别均衡准确率 0.859，95% CI [0.823, 0.892] | 提升具有一定统计稳定性 |

## 推荐采用的模型

- 追求总体准确率：`central_frozen_balanced`，测试准确率 0.859、macro-F1 0.859、MAE 0.149、低估率 0.092。
- 追求PDR安全性：`central_frozen_ordinal`，PDR AUROC 0.971、AP 0.955，准确率 0.846。
- 图像质量模块：采用 Exp26 的“clean样本加倍 + 中等增强 + 质量门控”；强亮度退化时自动拒识并转人工复核。

## 需要如实说明的限制

1. 45°/UWF 仍是几何视野代理，不是真实同眼相机配对。
2. 质量压力测试中的亮度、对比度和模糊是合成退化。
3. MSHF 外部数据没有公开患者ID，来源留一不能等同于严格患者级外部验证。
4. RetinaRadar 是质量模型；本轮使用其冻结表征训练线性探针，不能称为已训练出临床“大眼底病模型”。

## 下一轮核心实验结果

- Exp27 多视野分歧风险：测试 AUROC 0.742–0.766，未超过原风险模型的 AP，因此不单独作为最终风险头。
- Exp28 手工区域注意力：完整视野准确率约0.575，证明区域注意力思路可运行，但手工特征瓶颈明显。
- Exp29 选择性预测：中心不确定性模型在目标低估风险5%时，测试自动通过率26.2%、实际低估风险0%；目标风险20%时，通过率74.6%、实际低估风险8.2%。
- Exp30 深度区域注意力：冻结 RetinaRadar 区域表征后，随机遮挡增强模型完整视野准确率0.846；中心+十字区域准确率0.856，优于Exp28，是当前最值得继续发展的区域证据模型。
- Exp31 注意力缺失量不能直接做风险分数：测试 AUROC 仅0.458–0.535，说明解释权重必须经过独立校准。
- Exp32 Teacher–Student差异风险头：测试 AUROC 0.737，方向有效但仍未超过原风险模型。
- Exp33 外部区域泛化：MSHF所有来源平均 AUROC 0.905；UWF-mosaic overall AUROC 0.923，明显高于全图特征的0.605，支持区域化表征作为域泛化模块。

## Exp34–Exp42 十项收尾实验结果

| 任务 | 核心结果 | 结论 |
|---|---:|---|
| 多随机种子 | full macro-F1 0.830±0.018；center+cross 0.829±0.017 | 结果方向稳定但存在约1.7个百分点波动 |
| 遮挡/网格/池化消融 | attention 单次完整 macro-F1 0.840；center+cross 0.837 | attention保留区域解释能力，模型选择仍以验证集为准 |
| 编码器消融 | RetinaRadar 0.840/0.837；ImageNet ResNet50 0.780/0.772；手工 0.605/0.604 | 眼底专用冻结表征有效 |
| RFMiD2区域外部验证 | AUROC 0.731→0.767；AP 0.375→0.377 | 外部疾病方向性支持，受标签稀疏限制 |
| 注意力遮挡 | Spearman ρ=0.600，p=0.0876 | 探索性支持，不能宣称显著病灶定位 |
| 最终选择性风险 | 目标5%：coverage 62.8%、错误率2.86%；目标10%：coverage 91.8%、错误率7.54% | 可作为自动通过/人工复核门控 |
| Bootstrap/配对比较 | macro-F1 CI [0.802,0.875]；相对Exp23准确率差值CI [−0.062,0.015] | 区域模型不是总体准确率明确冠军 |
| 终点冻结 | primary=中心+十字限制视野macro-F1 | 只按验证集选模，测试集一次性报告 |

### 本轮最终论文定位

最稳妥的主张是：**冻结眼底专用表征的区域证据聚合，能够在模拟有限视野下保持较稳定的严重度判别，并支持经过校准的选择性自动通过/人工复核机制。**

不应主张：真实45°临床配对验证、具体病灶定位已被证明、或区域模型在所有指标上超过中心冻结类别均衡模型。

## 新增后续实验

- [Exp43 4×4五随机种子](./exp43_g4_multiseed/REPORT.md)：center+cross macro-F1 `0.842±0.016`，没有显示相对3×3的明确优势。
- [Exp44 选择性风险五随机种子](./exp44_selective_risk_multiseed/REPORT.md)：风险头 AUROC `0.765±0.018`；目标风险5%时覆盖率 `0.661±0.057`、错误率 `0.034±0.015`。
- [Exp45 3×3/4×4配对Bootstrap](./exp45_grid_paired_bootstrap/REPORT.md)：4×4−3×3在各随机种子的center+cross macro-F1差值CI均跨0。
- [Exp46 选择性风险严重度分层](./exp46_selective_subgroup_audit/REPORT.md)：目标风险5%时PDR接受错误率约3.1%，目标风险10%时升至约11.4%；总体风险门控必须配合严重度分层。

### 新增实验后的模型判断

4×4区域粒度可以作为补充消融，但不建议替换3×3主模型：它的五种子结果与3×3相近，未证明更细粒度带来稳定收益。选择性风险头则值得保留为论文核心功能，但必须如实报告不同随机种子导致的覆盖率波动。

Exp45–Exp46进一步说明：区域粒度选择应遵循“性能相当时选更简单模型”，而风险门控应报告Normal/NPDR/PDR分层的覆盖率和接受错误率，尤其不能用总体风险掩盖PDR工作点的风险上升。

## 投稿前补充实验：关键结论

- [Exp47 患者级嵌套风险校准](./exp47_nested_risk_calibration/REPORT.md)：外层风险AUROC `0.653±0.034`；5%目标下覆盖率 `0.567±0.274`。选择性门控可保留，但必须报告跨折不稳定性。
- [Exp48b 像素空间连续视野](./exp48b_pixel_fov_geometry/REPORT.md)：中心矩形35%→90%的macro-F1 `0.643±0.150`→`0.814±0.022`；偏心55%视野的低估率明显高于中心。
- [Exp49 RFMiD2逐病种Bootstrap](./exp49_rfmid_per_disease_bootstrap/REPORT.md)：15个可推断病种中，区域表征平均ΔAUROC `+0.015`，但经BH-FDR校正没有病种达到显著。

### 投稿措辞更新

可以主张：受限可见内容、位置和孔径形状会改变模型严重度判断；区域表征在外部多病种任务上呈正向平均趋势；经过校准的风险门控可减少一部分高风险自动判读。

不能主张：风险阈值具有跨队列确定性保证；区域表征在任何特定RFMiD2疾病上已显著更优；或几何孔径等价于真实45°相机图像。

### 新增外部零样本边界实验

- [Exp50 SUSTech-SYSU](./exp50_sustech_zero_shot/REPORT.md)：1219张公开45°图像的三分类宏F1仅 `0.080±0.029`；渗出物区域注意力关联仅作探索性分析。
- [Exp51 IDRiD](./exp51_idrid_zero_shot/REPORT.md)：官方103张测试图像的三分类宏F1 `0.124±0.046`，但DR-vs-normal的AUROC `0.700±0.026`、AP `0.851±0.016`。

这两项是失败也必须报告的外部验证：它们证明当前冻结UWF区域模型不能被描述为跨45°设备、跨中心可直接部署的疾病分级器；同时也支持将下一步工作聚焦于域适配或同眼跨设备配对采集。

### Exp52：无标签目标矩匹配适配

- [Exp52无标签特征矩匹配](./exp52_unlabeled_moment_adaptation/REPORT.md)：在不使用目标标签的前提下，IDRiD macro-F1 `0.124→0.341`，SUSTech-SYSU macro-F1 `0.080→0.432`。
- 这证明特征尺度/成像域错配是可校正的一部分，但它也提高了IDRiD低估率，故域适配不能替代选择性风险门控。

### Exp53–Exp54：MMRDR独立UWF复现与配对Bootstrap

- [Exp53 MMRDR独立UWF受限视野](./exp53_mmrdr_uwf_external_fov/REPORT.md)：2,597张官方患者级测试图，五种子完整视野 macro-F1 `0.625±0.010`，中心 macro-F1 `0.600±0.004`，中心+十字 macro-F1 `0.642±0.005`。
- [Exp54 MMRDR配对Bootstrap](./exp54_mmrdr_paired_bootstrap/REPORT.md)：中心+十字相对完整视野的平均差为 accuracy `+0.0166`、macro-F1 `+0.0174`、MAE `−0.0223`；五个种子上accuracy和MAE的配对95% CI均支持改善方向。

该外部结果可以作为论文的独立同模态复现，但主张应限定为“外部UWF队列中的几何受限视野实验支持”，不能写成真实45°采集或临床部署验证。

## 详细结果目录

- [Exp21 共享视野模型](./exp21_shared_fov_model/REPORT.md)
- [Exp22 第一版质量增强与拒识](./exp22_quality_augmentation_gate/REPORT.md)
- [Exp23 序数/PDR优化](./exp23_ordinal_pdr/REPORT.md)
- [Exp24 来源均衡域泛化](./exp24_source_balanced_generalization/REPORT.md)
- [Exp25 Bootstrap与分层审计](./exp25_optimized_bootstrap_audit/REPORT.md)
- [Exp26 调优后的质量鲁棒性](./exp26_tuned_quality_invariance/REPORT.md)
- [Exp27 多视野分歧风险](./exp27_multiview_disagreement_risk/REPORT.md)
- [Exp28 手工区域注意力](./exp28_region_attention/REPORT.md)
- [Exp29 选择性风险控制](./exp29_selective_conformal/REPORT.md)
- [Exp30 深度区域注意力](./exp30_deep_region_attention/REPORT.md)
- [Exp31 区域证据缺失风险](./exp31_attention_gap_risk/REPORT.md)
- [Exp32 Teacher–Student证据差异风险](./exp32_teacher_student_risk/REPORT.md)
- [Exp33 外部来源区域泛化](./exp33_external_region_generalization/REPORT.md)
