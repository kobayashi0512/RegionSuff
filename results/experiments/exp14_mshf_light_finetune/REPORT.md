# Exp14：MSHF 质量任务轻量微调

比较冻结 RetinaRadar 骨干只训练新质量头，以及只解冻 EfficientNet-B0 最后 block、conv_head、bn2 的轻量微调。标签使用三位医生逐项评分多数投票；阈值只在训练集选择，测试集只作最终评估。

冻结骨干四维 AUROC：0.924/0.927/0.936/0.966；解冻最后 block：0.827/0.741/0.829/0.847。

完整结果见 `results.json`。
