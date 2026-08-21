# Exp51：IDRiD 外部零样本DR分级验证

```json
{
  "dataset": {
    "name": "IDRiD Disease Grading official testing set",
    "n_images": 103,
    "original_grade_counts": {
      "0": 34,
      "1": 5,
      "2": 32,
      "3": 19,
      "4": 13
    },
    "mapped_labels": "IDRiD grade 0 -> Normal; grades 1-3 -> NPDR; grade 4 -> PDR"
  },
  "protocol": "Five source-UWF-trained RetinaRadar regional-attention heads are applied to IDRiD without using any IDRiD labels during training, early stopping, threshold selection, or model selection.",
  "rows": [
    {
      "seed": 0,
      "best_source_val_macro_f1": 0.7578849652516272,
      "epochs": 47,
      "accuracy": 0.1262135922330097,
      "macro_f1": 0.10056390977443609,
      "severity_mae": 1.203883495145631,
      "underestimation_rate": 0.019417475728155338,
      "per_idrid_grade": {
        "0": {
          "n": 34,
          "accuracy": 0.058823529411764705,
          "macro_f1": 0.037037037037037035,
          "severity_mae": 1.8823529411764706,
          "underestimation_rate": 0.0
        },
        "1": {
          "n": 5,
          "accuracy": 0.0,
          "macro_f1": 0.0,
          "severity_mae": 1.0,
          "underestimation_rate": 0.0
        },
        "2": {
          "n": 32,
          "accuracy": 0.0,
          "macro_f1": 0.0,
          "severity_mae": 1.0,
          "underestimation_rate": 0.0
        },
        "3": {
          "n": 19,
          "accuracy": 0.0,
          "macro_f1": 0.0,
          "severity_mae": 1.0,
          "underestimation_rate": 0.0
        },
        "4": {
          "n": 13,
          "accuracy": 0.8461538461538461,
          "macro_f1": 0.3055555555555555,
          "severity_mae": 0.3076923076923077,
          "underestimation_rate": 0.15384615384615385
        }
      },
      "binary_DR_vs_normal": {
        "auroc": 0.676470588235294,
        "ap": 0.843770623616618
      }
    },
    {
      "seed": 1,
      "best_source_val_macro_f1": 0.7608917234678296,
      "epochs": 68,
      "accuracy": 0.14563106796116504,
      "macro_f1": 0.11246867167919801,
      "severity_mae": 1.1650485436893203,
      "underestimation_rate": 0.019417475728155338,
      "per_idrid_grade": {
        "0": {
          "n": 34,
          "accuracy": 0.058823529411764705,
          "macro_f1": 0.037037037037037035,
          "severity_mae": 1.8823529411764706,
          "underestimation_rate": 0.0
        },
        "1": {
          "n": 5,
          "accuracy": 0.0,
          "macro_f1": 0.0,
          "severity_mae": 1.0,
          "underestimation_rate": 0.2
        },
        "2": {
          "n": 32,
          "accuracy": 0.0,
          "macro_f1": 0.0,
          "severity_mae": 1.0,
          "underestimation_rate": 0.0
        },
        "3": {
          "n": 19,
          "accuracy": 0.0,
          "macro_f1": 0.0,
          "severity_mae": 1.0,
          "underestimation_rate": 0.05263157894736842
        },
        "4": {
          "n": 13,
          "accuracy": 1.0,
          "macro_f1": 0.3333333333333333,
          "severity_mae": 0.0,
          "underestimation_rate": 0.0
        }
      },
      "binary_DR_vs_normal": {
        "auroc": 0.6909633418584825,
        "ap": 0.8300248718788122
      }
    },
    {
      "seed": 2,
      "best_source_val_macro_f1": 0.7386532460424086,
      "epochs": 49,
      "accuracy": 0.1262135922330097,
      "macro_f1": 0.10056390977443609,
      "severity_mae": 1.203883495145631,
      "underestimation_rate": 0.019417475728155338,
      "per_idrid_grade": {
        "0": {
          "n": 34,
          "accuracy": 0.058823529411764705,
          "macro_f1": 0.037037037037037035,
          "severity_mae": 1.8823529411764706,
          "underestimation_rate": 0.0
        },
        "1": {
          "n": 5,
          "accuracy": 0.0,
          "macro_f1": 0.0,
          "severity_mae": 1.0,
          "underestimation_rate": 0.0
        },
        "2": {
          "n": 32,
          "accuracy": 0.0,
          "macro_f1": 0.0,
          "severity_mae": 1.0,
          "underestimation_rate": 0.0
        },
        "3": {
          "n": 19,
          "accuracy": 0.0,
          "macro_f1": 0.0,
          "severity_mae": 1.0,
          "underestimation_rate": 0.0
        },
        "4": {
          "n": 13,
          "accuracy": 0.8461538461538461,
          "macro_f1": 0.3055555555555555,
          "severity_mae": 0.3076923076923077,
          "underestimation_rate": 0.15384615384615385
        }
      },
      "binary_DR_vs_normal": {
        "auroc": 0.6781756180733163,
        "ap": 0.846081996308782
      }
    },
    {
      "seed": 3,
      "best_source_val_macro_f1": 0.7592964047848154,
      "epochs": 52,
      "accuracy": 0.1262135922330097,
      "macro_f1": 0.10025410025410025,
      "severity_mae": 1.203883495145631,
      "underestimation_rate": 0.02912621359223301,
      "per_idrid_grade": {
        "0": {
          "n": 34,
          "accuracy": 0.058823529411764705,
          "macro_f1": 0.037037037037037035,
          "severity_mae": 1.8823529411764706,
          "underestimation_rate": 0.0
        },
        "1": {
          "n": 5,
          "accuracy": 0.0,
          "macro_f1": 0.0,
          "severity_mae": 1.0,
          "underestimation_rate": 0.0
        },
        "2": {
          "n": 32,
          "accuracy": 0.0,
          "macro_f1": 0.0,
          "severity_mae": 1.0,
          "underestimation_rate": 0.03125
        },
        "3": {
          "n": 19,
          "accuracy": 0.0,
          "macro_f1": 0.0,
          "severity_mae": 1.0,
          "underestimation_rate": 0.0
        },
        "4": {
          "n": 13,
          "accuracy": 0.8461538461538461,
          "macro_f1": 0.3055555555555555,
          "severity_mae": 0.3076923076923077,
          "underestimation_rate": 0.15384615384615385
        }
      },
      "binary_DR_vs_normal": {
        "auroc": 0.727621483375959,
        "ap": 0.8697015629364908
      }
    },
    {
      "seed": 4,
      "best_source_val_macro_f1": 0.76846533495698,
      "epochs": 81,
      "accuracy": 0.20388349514563106,
      "macro_f1": 0.20473394630922048,
      "severity_mae": 1.058252427184466,
      "underestimation_rate": 0.038834951456310676,
      "per_idrid_grade": {
        "0": {
          "n": 34,
          "accuracy": 0.20588235294117646,
          "macro_f1": 0.11382113821138212,
          "severity_mae": 1.5588235294117647,
          "underestimation_rate": 0.0
        },
        "1": {
          "n": 5,
          "accuracy": 0.0,
          "macro_f1": 0.0,
          "severity_mae": 1.0,
          "underestimation_rate": 0.2
        },
        "2": {
          "n": 32,
          "accuracy": 0.03125,
          "macro_f1": 0.020202020202020204,
          "severity_mae": 0.96875,
          "underestimation_rate": 0.03125
        },
        "3": {
          "n": 19,
          "accuracy": 0.05263157894736842,
          "macro_f1": 0.03333333333333333,
          "severity_mae": 0.9473684210526315,
          "underestimation_rate": 0.05263157894736842
        },
        "4": {
          "n": 13,
          "accuracy": 0.9230769230769231,
          "macro_f1": 0.32,
          "severity_mae": 0.15384615384615385,
          "underestimation_rate": 0.07692307692307693
        }
      },
      "binary_DR_vs_normal": {
        "auroc": 0.7271952259164536,
        "ap": 0.8650502088733549
      }
    }
  ],
  "aggregate": {
    "accuracy": {
      "mean": 0.14563106796116504,
      "std": 0.033632054515900525
    },
    "macro_f1": {
      "mean": 0.1237169075582782,
      "std": 0.045587578674769764
    },
    "severity_mae": {
      "mean": 1.166990291262136,
      "std": 0.06306944376276391
    },
    "underestimation_rate": {
      "mean": 0.02524271844660194,
      "std": 0.008683759135921513
    }
  },
  "binary_DR_vs_normal": {
    "auroc": {
      "mean": 0.700085251491901,
      "std": 0.02556407817765227
    },
    "ap": {
      "mean": 0.8509258527228116,
      "std": 0.016305949676870497
    }
  },
  "notes": [
    "Primary target is the official IDRiD test split (103 images).",
    "This assesses disease-grade transfer, not the main sufficiency endpoint; it is supporting external evidence for the regional representation.",
    "Three-class mapping is specified before evaluation to match the source task taxonomy."
  ]
}
```
