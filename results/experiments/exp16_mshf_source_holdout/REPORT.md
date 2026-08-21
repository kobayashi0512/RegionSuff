# Exp16：MSHF 来源留一审计

MSHF 公布包没有患者ID字段，无法进行严格患者级重划分；本实验采用来源留一（leave-one-source-out）验证作为更严格的域外审计。每次留出一个来源，其余来源训练冻结 RetinaRadar 特征线性探针。

UWF-mosaic 来源留出时总体质量 AUROC 为 0.605，说明来源域偏移明显。

完整结果见 `results.json`。
