# 眼底图像可观测性与质量研究数据

本目录用于研究：当前拍摄的眼底图像是否清晰、属于哪类成像方式、覆盖是否充分，以及是否可能导致某一眼底疾病的危险性低估。

## 已下载并完成完整性检查

### 1. UWF-DR 主数据集

- 名称：Ultra-wide-field (SLO) fundus image dataset for intelligent diabetic retinopathy system
- 内容：1630 张 UWF 图像，Normal / NPDR / PDR，附 train/val/test 标签文件
- 来源：Figshare DOI `10.6084/m9.figshare.31259494`
- 原始压缩包：`UWF_DR_1630/Ultra-wide-field (SLO) fundus image dataset for intelligent diabetic retinopathy system.zip`
- 解压目录：`UWF_DR_1630/extracted/`
- SHA-256：`4d60410559620a14dee62bca67472c38cd27c4e1b88cd4e4191c21f3986ff26b`

### 2. RFMiD 2.0

- 内容：860 张多标签普通眼底图像，51 类眼底疾病标签
- 来源：Zenodo DOI `10.5281/zenodo.7505822`
- 原始压缩包：`RFMiD2_0.zip`
- 解压目录：`RFMiD2_0/extracted/`
- ZIP 完整性：已通过 `unzip -tq` 检查
- 用途：测试图像类型、疾病类型与跨疾病泛化，不作为 UWF 完整视野真值

## 已核查但暂未作为依赖

- FLUID：当前 Zenodo API 标记为 restricted，文件列表为空，需要访问授权，因此不使用。
- UWF4DR Challenge：需要注册并提交规则同意文件，因此不使用。
- DRCR Retina Network 周边病灶数据：下载页要求姓名、邮箱、单位和研究用途，因此不使用。
- MSHF 质量数据集：论文提供了 Figshare DOI `10.6084/m9.figshare.21507564.v1`，但当前下载接口触发站点 WAF，暂未把它作为主数据依赖。

## 当前任务定义

质量评价和图像类型识别是基础子任务；主体任务是“病种条件下的图像诊断充分性”：在当前图像上判断是否看到了足以支持 DR 筛查的区域，并估计因视野、模糊、照明或遮挡造成危险性低估的概率。
