# MSHF：多来源眼底图像质量数据

来源：Jin et al., MSHF dataset, Figshare `21507564`。

- 已下载：`MSHF_dataset_2.0.zip`，并解压到 `extracted/`；
- 约 1302 张图像，包含 CFP、便携式相机和 UWF-mosaic；
- Excel 中提供照明、清晰度、对比度和总体质量评分；
- `Individual_scores.xlsx.xlsx` 保存三位医生逐项评分，本项目以三位医生多数投票作为外部验证标签；
- `AI-use/train` 与 `AI-use/test` 用于本次外部验证，实际可匹配 1040/260 张；
- 实验脚本与结果：`7hao/experiments/exp13_mshf_quality_external/`。

注意：这是医生质量标注数据，不是同眼 UWF/45° 配对数据。
