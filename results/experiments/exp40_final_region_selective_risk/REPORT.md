# Exp40：最终深度区域选择性风险头

在Exp30匹配的区域注意力模型上重新训练风险头并校准风险—覆盖率工作点，替代Exp29使用的旧风险头。

```json
{
  "model": {
    "best_val_full_macro_f1": 0.7558871666336615,
    "epochs": 54
  },
  "risk_head": {
    "test": {
      "auroc": 0.7400925925925926,
      "average_precision": 0.13903642663525778,
      "positive_rate": 0.07692307692307693,
      "brier": 0.18419314449261937
    },
    "validation": {
      "auroc": 0.7610088803442278,
      "average_precision": 0.23378275347786096,
      "positive_rate": 0.09065934065934066,
      "brier": 0.21796100530319792
    }
  },
  "direct_scores": {
    "severity_gap": {
      "test": {
        "auroc": 0.6772222222222223,
        "average_precision": 0.19694549231721592,
        "positive_rate": 0.07692307692307693
      }
    },
    "student_teacher_kl": {
      "test": {
        "auroc": 0.5387037037037038,
        "average_precision": 0.10728401327734255,
        "positive_rate": 0.07692307692307693
      }
    }
  },
  "selective": {
    "0.05": {
      "calibration": {
        "threshold": 0.49495495277449125,
        "validation_coverage": 0.5274725274725275,
        "validation_risk": 0.020833333333333332,
        "validation_cp_upper": 0.04703755834755209,
        "feasible": true
      },
      "test": {
        "coverage": 0.6282051282051282,
        "accepted_n": 245,
        "accepted_risk": 0.02857142857142857,
        "accepted_accuracy": 0.9714285714285714,
        "rejected_n": 145
      }
    },
    "0.1": {
      "calibration": {
        "threshold": 0.6887897829615481,
        "validation_coverage": 0.8516483516483516,
        "validation_risk": 0.06451612903225806,
        "validation_cp_upper": 0.0923706917778612,
        "feasible": true
      },
      "test": {
        "coverage": 0.9179487179487179,
        "accepted_n": 358,
        "accepted_risk": 0.07541899441340782,
        "accepted_accuracy": 0.9245810055865922,
        "rejected_n": 32
      }
    },
    "0.2": {
      "calibration": {
        "threshold": 0.8251003270896746,
        "validation_coverage": 1.0,
        "validation_risk": 0.09065934065934066,
        "validation_cp_upper": 0.119348439537593,
        "feasible": true
      },
      "test": {
        "coverage": 0.9974358974358974,
        "accepted_n": 389,
        "accepted_risk": 0.07712082262210797,
        "accepted_accuracy": 0.922879177377892,
        "rejected_n": 1
      }
    }
  },
  "notes": [
    "This risk head is trained only on Exp30-matched validation teacher/student features and evaluated on the held-out test split.",
    "The selective threshold is calibrated with a one-sided Clopper-Pearson upper bound.",
    "Partial view remains a geometric center+cross proxy, not a real paired acquisition."
  ]
}
```
