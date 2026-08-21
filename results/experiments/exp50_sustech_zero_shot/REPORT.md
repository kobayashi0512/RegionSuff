# Exp50：SUSTech-SYSU外部零样本DR与病灶审计

将UWF训练的区域模型直接迁移到公开45°DR分级数据，不使用外部标签训练；并以渗出物框做探索性注意力关联审计。

```json
{
  "dataset": {
    "name": "SUSTech-SYSU",
    "n_images": 1219,
    "mapped_labels": "ICDR 0->Normal; 1-3->NPDR; 4-5->PDR/laser-treated",
    "grade_counts": {
      "0": 631,
      "1": 24,
      "2": 365,
      "3": 73,
      "4": 58,
      "5": 68
    },
    "exudate_annotated_n": 564
  },
  "protocol": "Five UWF-trained region-attention models are applied zero-shot to SUSTech images; no SUSTech label is used for training or model selection.",
  "rows": [
    {
      "seed": 0,
      "best_source_val_macro_f1": 0.7578849652516272,
      "epochs": 47,
      "accuracy": 0.10336341263330599,
      "macro_f1": 0.062453531598513,
      "severity_mae": 1.4142739950779328,
      "underestimation_rate": 0.0,
      "per_original_grade": {
        "0": {
          "n": 631,
          "accuracy": 0.0,
          "underestimation_rate": 0.0
        },
        "1": {
          "n": 24,
          "accuracy": 0.0,
          "underestimation_rate": 0.0
        },
        "2": {
          "n": 365,
          "accuracy": 0.0,
          "underestimation_rate": 0.0
        },
        "3": {
          "n": 73,
          "accuracy": 0.0,
          "underestimation_rate": 0.0
        },
        "4": {
          "n": 58,
          "accuracy": 1.0,
          "underestimation_rate": 0.0
        },
        "5": {
          "n": 68,
          "accuracy": 1.0,
          "underestimation_rate": 0.0
        }
      }
    },
    {
      "seed": 1,
      "best_source_val_macro_f1": 0.7608917234678296,
      "epochs": 68,
      "accuracy": 0.11894995898277276,
      "macro_f1": 0.08308226141588694,
      "severity_mae": 1.379819524200164,
      "underestimation_rate": 0.002461033634126333,
      "per_original_grade": {
        "0": {
          "n": 631,
          "accuracy": 0.030110935023771792,
          "underestimation_rate": 0.0
        },
        "1": {
          "n": 24,
          "accuracy": 0.0,
          "underestimation_rate": 0.08333333333333333
        },
        "2": {
          "n": 365,
          "accuracy": 0.0,
          "underestimation_rate": 0.0027397260273972603
        },
        "3": {
          "n": 73,
          "accuracy": 0.0,
          "underestimation_rate": 0.0
        },
        "4": {
          "n": 58,
          "accuracy": 1.0,
          "underestimation_rate": 0.0
        },
        "5": {
          "n": 68,
          "accuracy": 1.0,
          "underestimation_rate": 0.0
        }
      }
    },
    {
      "seed": 2,
      "best_source_val_macro_f1": 0.7386532460424086,
      "epochs": 49,
      "accuracy": 0.10336341263330599,
      "macro_f1": 0.062453531598513,
      "severity_mae": 1.4142739950779328,
      "underestimation_rate": 0.0,
      "per_original_grade": {
        "0": {
          "n": 631,
          "accuracy": 0.0,
          "underestimation_rate": 0.0
        },
        "1": {
          "n": 24,
          "accuracy": 0.0,
          "underestimation_rate": 0.0
        },
        "2": {
          "n": 365,
          "accuracy": 0.0,
          "underestimation_rate": 0.0
        },
        "3": {
          "n": 73,
          "accuracy": 0.0,
          "underestimation_rate": 0.0
        },
        "4": {
          "n": 58,
          "accuracy": 1.0,
          "underestimation_rate": 0.0
        },
        "5": {
          "n": 68,
          "accuracy": 1.0,
          "underestimation_rate": 0.0
        }
      }
    },
    {
      "seed": 3,
      "best_source_val_macro_f1": 0.7592964047848154,
      "epochs": 52,
      "accuracy": 0.10418375717801477,
      "macro_f1": 0.0635548523206751,
      "severity_mae": 1.4126333059885152,
      "underestimation_rate": 0.0,
      "per_original_grade": {
        "0": {
          "n": 631,
          "accuracy": 0.001584786053882726,
          "underestimation_rate": 0.0
        },
        "1": {
          "n": 24,
          "accuracy": 0.0,
          "underestimation_rate": 0.0
        },
        "2": {
          "n": 365,
          "accuracy": 0.0,
          "underestimation_rate": 0.0
        },
        "3": {
          "n": 73,
          "accuracy": 0.0,
          "underestimation_rate": 0.0
        },
        "4": {
          "n": 58,
          "accuracy": 1.0,
          "underestimation_rate": 0.0
        },
        "5": {
          "n": 68,
          "accuracy": 1.0,
          "underestimation_rate": 0.0
        }
      }
    },
    {
      "seed": 4,
      "best_source_val_macro_f1": 0.76846533495698,
      "epochs": 81,
      "accuracy": 0.1542247744052502,
      "macro_f1": 0.129284709996903,
      "severity_mae": 1.3002461033634127,
      "underestimation_rate": 0.006562756357670222,
      "per_original_grade": {
        "0": {
          "n": 631,
          "accuracy": 0.09033280507131537,
          "underestimation_rate": 0.0
        },
        "1": {
          "n": 24,
          "accuracy": 0.0,
          "underestimation_rate": 0.0
        },
        "2": {
          "n": 365,
          "accuracy": 0.0136986301369863,
          "underestimation_rate": 0.019178082191780823
        },
        "3": {
          "n": 73,
          "accuracy": 0.0136986301369863,
          "underestimation_rate": 0.0
        },
        "4": {
          "n": 58,
          "accuracy": 0.9827586206896551,
          "underestimation_rate": 0.017241379310344827
        },
        "5": {
          "n": 68,
          "accuracy": 1.0,
          "underestimation_rate": 0.0
        }
      }
    }
  ],
  "aggregate": {
    "accuracy": {
      "mean": 0.11681706316652993,
      "std": 0.021940191146740905
    },
    "macro_f1": {
      "mean": 0.08016577738609822,
      "std": 0.02882943614229021
    },
    "severity_mae": {
      "mean": 1.3842493847415915,
      "std": 0.04920563073411367
    },
    "underestimation_rate": {
      "mean": 0.0018047579983593112,
      "std": 0.0028653403111686595
    }
  },
  "attention_exudate_audit": {
    "spearman_rho": 0.1383805468707254,
    "p_value": 3.986615303884276e-23,
    "region_pairs": 5076,
    "note": "Exploratory image-region correlation using exudate bounding-box area fractions; region pairs are not independent."
  },
  "notes": [
    "This is a cross-device, cross-field external zero-shot audit, not a paired UWF/45-degree study.",
    "The target label mapping merges ICDR grades to match the source 3-class taxonomy.",
    "Laser-treated grade is conservatively mapped to the severe/PDR class."
  ]
}
```
