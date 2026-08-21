# Exp30：冻结深度区域表征注意力

用RetinaRadar冻结深度特征替换Exp28的67维手工区域特征，再训练区域注意力聚合器，比较完整和受限区域覆盖。

```json
{
  "dataset": {
    "n": 1630,
    "regions": 9,
    "encoder": "RetinaRadar EfficientNet-B0 frozen global features",
    "device": "mps",
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
    "deep_attention_full_only": {
      "best_val_full_macro_f1": 0.733376531427003,
      "epochs": 60,
      "full": {
        "accuracy": 0.8307692307692308,
        "macro_f1": 0.8313833309904698,
        "severity_mae": 0.18205128205128204,
        "underestimation_rate": 0.07692307692307693
      },
      "center": {
        "accuracy": 0.7923076923076923,
        "macro_f1": 0.7929404175797071,
        "severity_mae": 0.2230769230769231,
        "underestimation_rate": 0.10256410256410256
      },
      "center_plus_cross": {
        "accuracy": 0.8307692307692308,
        "macro_f1": 0.8314408874845195,
        "severity_mae": 0.18205128205128204,
        "underestimation_rate": 0.07435897435897436
      },
      "left_half": {
        "accuracy": 0.8307692307692308,
        "macro_f1": 0.8306588513485065,
        "severity_mae": 0.18205128205128204,
        "underestimation_rate": 0.07692307692307693
      },
      "right_half": {
        "accuracy": 0.8076923076923077,
        "macro_f1": 0.8083932632614174,
        "severity_mae": 0.20512820512820512,
        "underestimation_rate": 0.07948717948717948
      },
      "top_half": {
        "accuracy": 0.8307692307692308,
        "macro_f1": 0.8313330590191047,
        "severity_mae": 0.18205128205128204,
        "underestimation_rate": 0.07948717948717948
      },
      "bottom_half": {
        "accuracy": 0.823076923076923,
        "macro_f1": 0.824400871459695,
        "severity_mae": 0.18461538461538463,
        "underestimation_rate": 0.07948717948717948
      }
    },
    "deep_attention_mask_augmented": {
      "best_val_full_macro_f1": 0.7592123708682451,
      "epochs": 62,
      "full": {
        "accuracy": 0.8461538461538461,
        "macro_f1": 0.8471993270979588,
        "severity_mae": 0.16153846153846155,
        "underestimation_rate": 0.07179487179487179
      },
      "center": {
        "accuracy": 0.7923076923076923,
        "macro_f1": 0.7930540720065625,
        "severity_mae": 0.2282051282051282,
        "underestimation_rate": 0.1
      },
      "center_plus_cross": {
        "accuracy": 0.8564102564102564,
        "macro_f1": 0.8576568169173441,
        "severity_mae": 0.15128205128205127,
        "underestimation_rate": 0.06153846153846154
      },
      "left_half": {
        "accuracy": 0.8384615384615385,
        "macro_f1": 0.8386557077924915,
        "severity_mae": 0.1717948717948718,
        "underestimation_rate": 0.07435897435897436
      },
      "right_half": {
        "accuracy": 0.8256410256410256,
        "macro_f1": 0.8271037581699346,
        "severity_mae": 0.1794871794871795,
        "underestimation_rate": 0.08205128205128205
      },
      "top_half": {
        "accuracy": 0.8512820512820513,
        "macro_f1": 0.8523970988880268,
        "severity_mae": 0.16153846153846155,
        "underestimation_rate": 0.0641025641025641
      },
      "bottom_half": {
        "accuracy": 0.8384615384615385,
        "macro_f1": 0.8393155450335317,
        "severity_mae": 0.1717948717948718,
        "underestimation_rate": 0.07179487179487179
      }
    }
  },
  "attention_summary": {
    "overall_mean_attention": [
      0.04285291259181507,
      0.13540269864890248,
      0.04305921926503428,
      0.11574297808856966,
      0.36457689004735305,
      0.14854626702831294,
      0.04238667169239563,
      0.08535250004004831,
      0.02207986323419624
    ],
    "by_severity": {
      "0": [
        0.044225099572348735,
        0.12148403228881459,
        0.046440264243495386,
        0.11065518870487694,
        0.3941086113828328,
        0.11811328689881795,
        0.05447711226216322,
        0.0870261889198333,
        0.02347021602687982
      ],
      "1": [
        0.03569812995248243,
        0.16315580633584492,
        0.03810792393306012,
        0.0976951969795976,
        0.3899681898391377,
        0.14411659217541561,
        0.03051017941210256,
        0.08580730564171707,
        0.014940678584304415
      ],
      "2": [
        0.049330276310361264,
        0.11921989386938812,
        0.04501222457357442,
        0.14097580746296914,
        0.305801082597745,
        0.18510045970211766,
        0.04293032176417088,
        0.0831088368713315,
        0.028521095385639777
      ]
    }
  },
  "notes": [
    "Region embeddings come from the released RetinaRadar quality model and are frozen; only the attention aggregator is trained.",
    "The 3x3 region bank and masks are geometric proxies; no lesion-level annotation is available.",
    "Validation macro-F1 is used for early stopping."
  ]
}
```
