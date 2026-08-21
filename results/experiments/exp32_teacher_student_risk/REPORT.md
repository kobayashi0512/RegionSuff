# Exp32：Teacher–Student证据差异风险头

训练完整区域模型作为teacher，再用中心+十字视野作为student；用两者预测概率差、期望严重度差、KL和注意力缺失量训练独立低估风险头。风险头只在验证集拟合，测试集仅用于最终评估。

```json
{
  "dataset": {
    "n": 1630,
    "regions": 9,
    "teacher": "full-region attention",
    "student": "center+cross masked attention",
    "device": "mps",
    "best_val_full_macro_f1": 0.7569651682978765,
    "epochs": 62
  },
  "direct_scores": {
    "expected_severity_gap": {
      "val": {
        "auroc": 0.5583037475345167,
        "average_precision": 0.1436729360418059,
        "positive_rate": 0.10714285714285714
      },
      "test": {
        "auroc": 0.7084726334893494,
        "average_precision": 0.2081246525095174,
        "positive_rate": 0.07435897435897436
      }
    },
    "student_teacher_kl": {
      "val": {
        "auroc": 0.6457199211045365,
        "average_precision": 0.13996895312599716,
        "positive_rate": 0.10714285714285714
      },
      "test": {
        "auroc": 0.5687267169739231,
        "average_precision": 0.10424180402120459,
        "positive_rate": 0.07435897435897436
      }
    },
    "missing_attention": {
      "val": {
        "auroc": 0.5100197238658777,
        "average_precision": 0.10512722605201129,
        "positive_rate": 0.10714285714285714
      },
      "test": {
        "auroc": 0.4580189129811825,
        "average_precision": 0.06980044054811646,
        "positive_rate": 0.07435897435897436
      }
    }
  },
  "risk_head": {
    "n_features": 19,
    "calibration_n": 364,
    "test": {
      "auroc": 0.7367465851561753,
      "average_precision": 0.13838212524695429,
      "positive_rate": 0.07435897435897436,
      "brier": 0.17975009335118441
    }
  },
  "notes": [
    "The attention model is trained only on the training split; the independent risk head is fitted on validation teacher-student features and evaluated on the held-out test split.",
    "Risk target is whether the masked student predicts a grade below the UWF label.",
    "This is still a geometric partial-view proxy, not a real paired 45-degree acquisition."
  ]
}
```
