# Exp28：区域证据注意力与视野覆盖

把UWF视网膜包围盒划分为3×3区域，使用注意力池化判断不同区域对严重度预测的贡献，并在中心/半视野遮罩下评估证据缺失。

```json
{
  "dataset": {
    "n": 1630,
    "regions": 9,
    "region_layout": "3x3 retinal bounding-box tiles",
    "split_counts": {
      "train": [
        260,
        351,
        265
      ],
      "val": [
        107,
        146,
        111
      ],
      "test": [
        129,
        137,
        124
      ]
    }
  },
  "models": {
    "attention_full_only": {
      "full": {
        "accuracy": 0.5743589743589743,
        "macro_f1": 0.5729512637505004,
        "severity_mae": 0.5102564102564102,
        "underestimation_rate": 0.19230769230769232
      },
      "center": {
        "accuracy": 0.617948717948718,
        "macro_f1": 0.6257515826320246,
        "severity_mae": 0.44358974358974357,
        "underestimation_rate": 0.23333333333333334
      },
      "center_plus_cross": {
        "accuracy": 0.5794871794871795,
        "macro_f1": 0.5824912289901398,
        "severity_mae": 0.4948717948717949,
        "underestimation_rate": 0.21794871794871795
      },
      "left_half": {
        "accuracy": 0.5897435897435898,
        "macro_f1": 0.5915775795697995,
        "severity_mae": 0.4794871794871795,
        "underestimation_rate": 0.2
      },
      "right_half": {
        "accuracy": 0.5717948717948718,
        "macro_f1": 0.576890827020776,
        "severity_mae": 0.5230769230769231,
        "underestimation_rate": 0.24102564102564103
      },
      "top_half": {
        "accuracy": 0.5743589743589743,
        "macro_f1": 0.5748393412248052,
        "severity_mae": 0.5025641025641026,
        "underestimation_rate": 0.20512820512820512
      },
      "bottom_half": {
        "accuracy": 0.5897435897435898,
        "macro_f1": 0.5892701797249523,
        "severity_mae": 0.48717948717948717,
        "underestimation_rate": 0.18717948717948718
      },
      "val_full": {
        "accuracy": 0.4065934065934066,
        "macro_f1": 0.4047342474908082,
        "severity_mae": 0.7362637362637363,
        "underestimation_rate": 0.260989010989011
      }
    },
    "attention_mask_augmented": {
      "full": {
        "accuracy": 0.5769230769230769,
        "macro_f1": 0.5798284247555113,
        "severity_mae": 0.5,
        "underestimation_rate": 0.2076923076923077
      },
      "center": {
        "accuracy": 0.6076923076923076,
        "macro_f1": 0.6117109268341779,
        "severity_mae": 0.4564102564102564,
        "underestimation_rate": 0.19487179487179487
      },
      "center_plus_cross": {
        "accuracy": 0.5948717948717949,
        "macro_f1": 0.6000297348944462,
        "severity_mae": 0.45897435897435895,
        "underestimation_rate": 0.19743589743589743
      },
      "left_half": {
        "accuracy": 0.5820512820512821,
        "macro_f1": 0.5862623895712132,
        "severity_mae": 0.49743589743589745,
        "underestimation_rate": 0.2128205128205128
      },
      "right_half": {
        "accuracy": 0.5794871794871795,
        "macro_f1": 0.5825495131908854,
        "severity_mae": 0.4948717948717949,
        "underestimation_rate": 0.2076923076923077
      },
      "top_half": {
        "accuracy": 0.5794871794871795,
        "macro_f1": 0.5827903435025458,
        "severity_mae": 0.4948717948717949,
        "underestimation_rate": 0.2128205128205128
      },
      "bottom_half": {
        "accuracy": 0.5897435897435898,
        "macro_f1": 0.5923470789624071,
        "severity_mae": 0.46923076923076923,
        "underestimation_rate": 0.18717948717948718
      },
      "val_full": {
        "accuracy": 0.4642857142857143,
        "macro_f1": 0.4548997877045991,
        "severity_mae": 0.6291208791208791,
        "underestimation_rate": 0.2087912087912088
      }
    },
    "mean_pool_baseline": {
      "full": {
        "accuracy": 0.4307692307692308,
        "macro_f1": 0.41310385072294925,
        "severity_mae": 0.6794871794871795,
        "underestimation_rate": 0.19230769230769232
      },
      "center": {
        "accuracy": 0.40512820512820513,
        "macro_f1": 0.28347840928486095,
        "severity_mae": 0.6205128205128205,
        "underestimation_rate": 0.27692307692307694
      },
      "center_plus_cross": {
        "accuracy": 0.41025641025641024,
        "macro_f1": 0.3285556406466903,
        "severity_mae": 0.6358974358974359,
        "underestimation_rate": 0.2923076923076923
      },
      "left_half": {
        "accuracy": 0.44871794871794873,
        "macro_f1": 0.45218884004615073,
        "severity_mae": 0.6948717948717948,
        "underestimation_rate": 0.32051282051282054
      },
      "right_half": {
        "accuracy": 0.4641025641025641,
        "macro_f1": 0.42624365792530106,
        "severity_mae": 0.6205128205128205,
        "underestimation_rate": 0.14871794871794872
      },
      "top_half": {
        "accuracy": 0.4641025641025641,
        "macro_f1": 0.40962912834394577,
        "severity_mae": 0.5871794871794872,
        "underestimation_rate": 0.16153846153846155
      },
      "bottom_half": {
        "accuracy": 0.4230769230769231,
        "macro_f1": 0.38820599535231737,
        "severity_mae": 0.676923076923077,
        "underestimation_rate": 0.3128205128205128
      },
      "val_full": {
        "accuracy": 0.38461538461538464,
        "macro_f1": 0.33712769981348517,
        "severity_mae": 0.8351648351648352,
        "underestimation_rate": 0.11813186813186813
      }
    }
  },
  "attention_summary": {
    "overall_mean_attention": [
      0.02271417256251732,
      0.048977606413466844,
      0.0439983696706336,
      0.05670156060319757,
      0.5976240691704625,
      0.09261712903592333,
      0.034658558533410024,
      0.07567386234809724,
      0.02703466967050951
    ],
    "by_severity": {
      "0": [
        0.022361248397557827,
        0.05887745268131869,
        0.05645937298043584,
        0.08163556924673879,
        0.5834730161713119,
        0.0623667848843373,
        0.0480927059756451,
        0.04957470192224253,
        0.03715914527272909
      ],
      "1": [
        0.01820221600670656,
        0.04044021491098807,
        0.03478020943460616,
        0.045934949930839214,
        0.6553464566435399,
        0.07722967768638064,
        0.022716963088828,
        0.0928617894117072,
        0.012487517425929186
      ],
      "2": [
        0.028066311799822545,
        0.048111013407714454,
        0.0412194868107245,
        0.042657516628167566,
        0.5485718010501306,
        0.14108789702335836,
        0.03387624850001819,
        0.08383552111600606,
        0.032574205999712565
      ]
    }
  },
  "notes": [
    "The region bank is a geometric 3x3 partition of the retinal bounding box; it is an evidence-localization proxy, not lesion-level annotation.",
    "Attention-mask-augmented training randomly hides 30% of regions during training and keeps the center tile if all regions would be hidden.",
    "Features are 67-dimensional image statistics; this is a low-cost proof-of-concept before replacing the region encoder with a deep frozen encoder."
  ]
}
```
