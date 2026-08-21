# RegionSufficiency：一区导向的论文叙事与图表架构

## 1. 从 VOCT_2.0 继承的叙事方法

VOCT_2.0 的核心写法不是按“数据—模型—实验”机械罗列，而是遵循以下逻辑：

1. 指出一个被现有工作默认忽略的隐藏前提；
2. 说明这个隐藏前提为什么构成实际推理缺口；
3. 提出一个能够在仅有图像输入时闭合该缺口的方法；
4. 将实验拆成相互独立、问题明确的验证协议；
5. Results 使用问句式小标题，每一组图表只回答一个问题；
6. 每组结论后立即说明它能够证明什么、不能证明什么。

RegionSufficiency 对应的隐藏前提是：现有眼底 AI 默认输入图像已经包含足够的疾病证据。本文要证明，图像清晰、视野面积较大或模型置信度较高，都不自动等价于诊断证据充分。

## 2. 全文唯一主线

> Diagnostic sufficiency is determined by the spatial composition of visible retinal evidence, not by image quality or field-of-view area alone.

全文不得分叉成“质量模型、DR 分类器、域适配、多病种识别”四篇论文。MSHF、RFMiD2、IDRiD 与 SUSTech 仅作为边界审计或补充材料。主文只围绕 UWF-DR、受控视野和 MMRDR-UWF 展开。

## 3. 题目与核心贡献

### 推荐题目

**When Is a Fundus Image Diagnostically Sufficient? Visibility-Conditioned Regional Evidence Aggregation under Limited Fields of View**

### 三项贡献

1. 提出模型层面的眼底图像诊断充分性任务，并与传统图像质量评估明确区分；
2. 提出可见性条件化区域证据聚合框架，在随机区域缺失训练下学习不完整视野中的疾病证据；
3. 建立从连续像素视野、区域组合拓扑、患者级内部验证到独立 MMRDR-UWF 外部审计和选择性风险控制的完整评估协议。

## 4. Abstract：五段式信息顺序

1. **Background**：眼底 AI 默认图像已包含足够证据，但清晰图像也可能遗漏关键区域；
2. **Operational gap**：传统质量分数和全图分类概率不能回答当前可见区域是否足以支撑严重度判断；
3. **Method**：3×3 区域、冻结眼底编码器、随机区域屏蔽、可见性条件化注意力、严重度预测与低估风险审计；
4. **Results**：内部有限视野、连续面积/位置/形状、独立 MMRDR-UWF 和选择性预测的主结果；
5. **Conclusion and boundary**：诊断充分性是可见证据空间构成属性；当前几何视野是代理实验，不声称完成真实临床部署。

## 5. Introduction：七段环环相扣

### 第1段：应用价值

DR 自动分级能够提高大规模眼底筛查效率，但实际采集存在视野不完整、黑边、睫毛、眩光和设备差异。

### 第2段：隐藏前提

多数研究在模型接收图像之前，已经默认该图像包含足够证据。这个前提在训练集上很少被显式检查。

### 第3段：概念区分

Image quality 回答清晰度、曝光和伪影；diagnostic sufficiency 回答当前可见区域是否包含目标判断所需证据。二者相关但不等价。

### 第4段：为什么现有方法不完整

全图 CNN 强制输出疾病类别；质量网络不以疾病判断为条件；普通不确定性不能表达缺少哪个区域；全局池化无法显式区分不可见区域和低权重区域。

### 第5段：方法概览（插入 Figure 1）

提出 RegionSufficiency，将视网膜表示为区域证据集合，并用可见掩码控制证据聚合。训练时随机隐藏区域，推理时根据真实或模拟可见区域生成严重度预测和充分性风险。

### 第6段：四个实验问题

1. 诊断充分性是否只是可见面积的函数？
2. 可见性条件化区域聚合为什么有效？
3. 该规律能否在独立 MMRDR-UWF 数据中复现？
4. 模型能否识别高低估风险并选择性拒绝？

### 第7段：贡献与边界

只列三项贡献，同时声明人工遮罩不等价于真实同眼有限视野采集，当前风险头首先是配对视野风险审计。

## 6. Materials and Methods

### 2.1 Study design and datasets（Table 1）

- UWF-DR 1,630 张：模型开发、内部视野压力测试；
- MMRDR-UWF 2,597 张：不参与训练、早停、阈值和模型选择的独立外部测试；
- 其他数据集：补充边界审计，不与主任务混写。

### 2.2 Patient grouping and leakage control

说明患者级划分、五随机种子、训练集标准化、验证集模型选择、测试集最终报告，以及外部标签完全不进入训练。

### 2.3 Operational definition of diagnostic sufficiency

设视野掩码为 `m`，有限视野预测为 `y_hat(m)`。主要效能终点为中心十字视野 macro-F1；安全终点为 severity MAE、underestimation rate 和 PDR recall。选择性风险目标为有限视野预测低于真实等级。

### 2.4 RegionSufficiency architecture（插入 Figure 2）

按图中顺序写区域构造、冻结编码器、区域投影、随机掩码、masked attention、严重度头和风险估计；公式必须紧跟对应模块，不设孤立公式小节。

### 2.5 Controlled visibility protocols

分别定义区域掩码、连续像素面积、相同面积不同位置、相同面积不同形状，以及未来的 511 个非空区域子集拓扑图谱。明确这些实验改变可见证据，不改变患者和真实标签。

### 2.6 Baselines and ablations

统一数据划分与模型选择条件，比较全图模型、手工特征、ImageNet、RetinaRadar、mean/max/attention、mask ratio 和网格粒度。

### 2.7 Paired-view underestimation risk and calibration

准确描述当前风险特征来自完整视野和有限视野概率、概率差、期望严重度差、熵与对称 KL。风险逻辑回归在验证集拟合，Clopper-Pearson 上界用于阈值校准。若补做单视野风险头，则在同一节单独列为可部署扩展。

### 2.8 Statistical analysis

多随机种子报告 mean±SD；同一测试图像不同视野使用 paired bootstrap；MMRDR 使用 2,000 次配对图像级 bootstrap，并明确它不是跨数据集置信区间；多病种探索分析控制多重比较。

## 7. Results and Discussion：问句式标题

### 4.1 Is diagnostic sufficiency determined by visible area alone?（Figure 3）

先报告连续面积，再比较相同面积不同位置和形状；若完成 511 区域组合搜索，则用 topology atlas 作为本节主图。结论：面积重要，但无法单独决定低估风险和疾病证据保留。

### 4.2 Why does visibility-conditioned regional aggregation matter?（Figure 4；Tables 2–3）

先报告五种子最终结果，再按 encoder、pooling、mask ratio、grid size 解释各模块。必须同时报告全图基线高于区域模型的情况，不能宣称 RegionSufficiency 是最强通用分类器。

### 4.3 Does regional attention correspond to counterfactual evidence?（Figure 5）

使用逐图逐区域删除造成的真实概率或性能下降验证注意力；展示正确接受、正确拒绝、过度自信和跨域改善病例。若相关性仍不显著，则将注意力定位降为探索性结果。

### 4.4 Does the evidence topology replicate in independent UWF data?（Figure 6；Table 4）

报告 MMRDR 的 Full、Center、Center+Cross 和配对 bootstrap。进一步检查 foreground crop、黑边、质量代理分层和随机五区域组合，排除“中心十字优于全图”仅由设备边缘伪影造成。不得把该结果写成临床裁剪建议。

### 4.5 Can the system identify when evidence is insufficient?（Figure 7；Table 5）

比较 paired evidence gap、entropy、maximum probability、margin 和单视野风险头。依次报告 risk AUROC、risk-coverage、accepted underestimation、嵌套校准和严重度亚组。固定划分效果与嵌套校准波动必须同时出现。

### 4.6 Discussion and implications

依次讨论：主要发现；可见证据拓扑；MMRDR 中中心十字的非单调现象；选择性预测；45°跨设备失败揭示的边界；临床采集工作流意义。

### 4.7 Limitations and future work

主动声明：无医生直接充分性标签；人工遮罩不等于真实配对采集；当前主要疾病为 DR；风险阈值尚未临床验证；一个独立 UWF 外部队列；注意力不是病灶定位金标准。

## 8. 图表插入顺序

1. Figure 1：Introduction 第5段之后，负责解释全文故事；
2. Table 1：Methods 2.1，负责数据、分组和用途；
3. Figure 2：Methods 2.4，负责算法可复现性；
4. Figure 3：Results 4.1，证明面积、位置、形状与拓扑；
5. Tables 2–3 + Figure 4：Results 4.2，证明模型和模块贡献；
6. Figure 5：Results 4.3，证明区域证据解释是否可信；
7. Table 4 + Figure 6：Results 4.4，独立外部验证；
8. Table 5 + Figure 7：Results 4.5，选择性风险与拒绝。

## 9. 全局视觉系统：2019 年版人民币 20 元配色

- 页面背景：`#FFFDFC`；
- 浅桃纸色：`#F7ECE6`；
- 浅杏色：`#F5CFAA`；
- 主橙色：`#E49F5D`；
- 赭棕色：`#965E4A`；
- 深棕线条/文字：`#704C2B`；
- 桂林山水橄榄绿：`#8B9A7C`；
- 浅橄榄填充：`#E5E8D9`；
- 少量防伪玫红强调：`#C74282`，仅用于风险或异常点。

所有后续实验图遵循同一语义：橙色表示主方法，橄榄绿表示证据保留或接受，赭色表示基线，玫红表示低估/拒绝，灰米色表示不可见区域。

## 10. 制图硬约束

- 总体图和模块图仅使用水平或垂直的单段直线箭头；
- 禁止曲线、斜线、跨模块连线和文字压线；
- 模块至少保留 2.5 mm 内边距，箭头端点与边框保持可见间距；
- 公式紧邻对应模块，不能漂浮在空白处；
- 最终英文标签，Arial 字体，双栏成图后最小文字不低于 7.5 pt；
- 概念图导出 SVG/PDF，数据图由程序读取 results.json 精确绘制；
- 同一指标跨图保持颜色、方向和坐标范围一致。

