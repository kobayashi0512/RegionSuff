# Exp11：RetinaRadar 冻结特征与质量输出实验

## 目的
验证一个公开的眼底图像质量模型的冻结表征和 17 维质量输出，是否能帮助判断中心视野是否低估 UWF 的糖网分级。

## 关键结果
```json
{
  "full": {
    "train": {
      "accuracy": 0.9988584474885844,
      "macro_f1": 0.9988835808732371,
      "severity_mae": 0.001141552511415525,
      "underestimation_rate": 0.0
    },
    "val": {
      "accuracy": 0.7005494505494505,
      "macro_f1": 0.7060131280313945,
      "severity_mae": 0.31868131868131866,
      "underestimation_rate": 0.14285714285714285
    },
    "test": {
      "accuracy": 0.7743589743589744,
      "macro_f1": 0.775690344291372,
      "severity_mae": 0.24358974358974358,
      "underestimation_rate": 0.10512820512820513
    }
  },
  "central": {
    "train": {
      "accuracy": 0.9988584474885844,
      "macro_f1": 0.9988846935599723,
      "severity_mae": 0.001141552511415525,
      "underestimation_rate": 0.001141552511415525
    },
    "val": {
      "accuracy": 0.7142857142857143,
      "macro_f1": 0.718262302619966,
      "severity_mae": 0.30494505494505497,
      "underestimation_rate": 0.14835164835164835
    },
    "test": {
      "accuracy": 0.8384615384615385,
      "macro_f1": 0.8397762530916942,
      "severity_mae": 0.1717948717948718,
      "underestimation_rate": 0.10256410256410256
    }
  },
  "quality_logits_only": {
    "full": {
      "train": {
        "accuracy": 0.6518264840182648,
        "macro_f1": 0.6574601676621595,
        "severity_mae": 0.3744292237442922,
        "underestimation_rate": 0.19292237442922375
      },
      "val": {
        "accuracy": 0.6346153846153846,
        "macro_f1": 0.6370292998235206,
        "severity_mae": 0.4340659340659341,
        "underestimation_rate": 0.12087912087912088
      },
      "test": {
        "accuracy": 0.6102564102564103,
        "macro_f1": 0.6139421706161904,
        "severity_mae": 0.43333333333333335,
        "underestimation_rate": 0.16153846153846155
      }
    },
    "central": {
      "train": {
        "accuracy": 0.6883561643835616,
        "macro_f1": 0.6899375505520756,
        "severity_mae": 0.3447488584474886,
        "underestimation_rate": 0.14383561643835616
      },
      "val": {
        "accuracy": 0.5714285714285714,
        "macro_f1": 0.5698989898989898,
        "severity_mae": 0.5054945054945055,
        "underestimation_rate": 0.21153846153846154
      },
      "test": {
        "accuracy": 0.6897435897435897,
        "macro_f1": 0.6906370730319248,
        "severity_mae": 0.36666666666666664,
        "underestimation_rate": 0.11025641025641025
      }
    }
  },
  "risk_head": {
    "train_positive": 78,
    "val_positive": 54,
    "test_positive": 40,
    "val": {
      "auroc": 0.5000597371565114,
      "average_precision": 0.1679802761872281
    },
    "test": {
      "auroc": 0.6160714285714286,
      "average_precision": 0.14163790797373516
    }
  }
}
```

## 风险头不确定性

在 390 张测试图像上进行 5000 次 bootstrap：AUROC=0.616，95% CI [0.527, 0.701]；Brier=0.118；ECE=0.098。这个区间仍接近随机水平，当前结果只能作为可行性信号，不能宣称临床可用。

## 解释
- `frozen_feature`：不更新 RetinaRadar 参数，只训练线性分类器，避免把诊断任务误称为大模型微调。
- `quality_logits_only`：只使用清晰度、照明、对比度、视野、可用性等质量输出。
- `risk_head`：预测中心视野分类结果是否低于 UWF 临床标签。

## 限制
本实验的中心视野仍是 UWF 的几何裁剪，不能替代真实同眼 45°/UWF 配对；当前数据没有医生逐图质量金标准。
