# Exp43：4×4区域模型五随机种子稳定性

在共享patient-level split和同一attention聚合器下，评估4×4区域粒度的五随机种子稳定性。

```json
{
  "grid": "4x4",
  "n_seeds": 5,
  "rows": [
    {
      "seed": 0,
      "view": "full",
      "best_val_macro_f1": 0.7262012732944111,
      "epochs": 62,
      "accuracy": 0.8205128205128205,
      "macro_f1": 0.822100250869583,
      "severity_mae": 0.19743589743589743,
      "underestimation_rate": 0.08205128205128205
    },
    {
      "seed": 0,
      "view": "center",
      "best_val_macro_f1": 0.7262012732944111,
      "epochs": 62,
      "accuracy": 0.8179487179487179,
      "macro_f1": 0.8193825337930752,
      "severity_mae": 0.19487179487179487,
      "underestimation_rate": 0.08974358974358974
    },
    {
      "seed": 0,
      "view": "cross",
      "best_val_macro_f1": 0.7262012732944111,
      "epochs": 62,
      "accuracy": 0.8205128205128205,
      "macro_f1": 0.8218662542524234,
      "severity_mae": 0.19743589743589743,
      "underestimation_rate": 0.08461538461538462
    },
    {
      "seed": 1,
      "view": "full",
      "best_val_macro_f1": 0.7407550297022,
      "epochs": 70,
      "accuracy": 0.8333333333333334,
      "macro_f1": 0.8352082325956233,
      "severity_mae": 0.18205128205128204,
      "underestimation_rate": 0.08205128205128205
    },
    {
      "seed": 1,
      "view": "center",
      "best_val_macro_f1": 0.7407550297022,
      "epochs": 70,
      "accuracy": 0.8333333333333334,
      "macro_f1": 0.8351912621092903,
      "severity_mae": 0.18205128205128204,
      "underestimation_rate": 0.08205128205128205
    },
    {
      "seed": 1,
      "view": "cross",
      "best_val_macro_f1": 0.7407550297022,
      "epochs": 70,
      "accuracy": 0.8333333333333334,
      "macro_f1": 0.8352594569512058,
      "severity_mae": 0.1794871794871795,
      "underestimation_rate": 0.08461538461538462
    },
    {
      "seed": 2,
      "view": "full",
      "best_val_macro_f1": 0.7330430567236706,
      "epochs": 46,
      "accuracy": 0.8615384615384616,
      "macro_f1": 0.8624121853071269,
      "severity_mae": 0.15128205128205127,
      "underestimation_rate": 0.07179487179487179
    },
    {
      "seed": 2,
      "view": "center",
      "best_val_macro_f1": 0.7330430567236706,
      "epochs": 46,
      "accuracy": 0.8512820512820513,
      "macro_f1": 0.8530861945707469,
      "severity_mae": 0.1564102564102564,
      "underestimation_rate": 0.07948717948717948
    },
    {
      "seed": 2,
      "view": "cross",
      "best_val_macro_f1": 0.7330430567236706,
      "epochs": 46,
      "accuracy": 0.8641025641025641,
      "macro_f1": 0.8650022492127757,
      "severity_mae": 0.14615384615384616,
      "underestimation_rate": 0.07692307692307693
    },
    {
      "seed": 3,
      "view": "full",
      "best_val_macro_f1": 0.7260609873680748,
      "epochs": 51,
      "accuracy": 0.8487179487179487,
      "macro_f1": 0.8497622895443332,
      "severity_mae": 0.16153846153846155,
      "underestimation_rate": 0.07435897435897436
    },
    {
      "seed": 3,
      "view": "center",
      "best_val_macro_f1": 0.7260609873680748,
      "epochs": 51,
      "accuracy": 0.8435897435897436,
      "macro_f1": 0.845651714849323,
      "severity_mae": 0.1641025641025641,
      "underestimation_rate": 0.08461538461538462
    },
    {
      "seed": 3,
      "view": "cross",
      "best_val_macro_f1": 0.7260609873680748,
      "epochs": 51,
      "accuracy": 0.8487179487179487,
      "macro_f1": 0.8497649323755351,
      "severity_mae": 0.16153846153846155,
      "underestimation_rate": 0.07692307692307693
    },
    {
      "seed": 4,
      "view": "full",
      "best_val_macro_f1": 0.7121396478876013,
      "epochs": 65,
      "accuracy": 0.8333333333333334,
      "macro_f1": 0.8354733858327735,
      "severity_mae": 0.17692307692307693,
      "underestimation_rate": 0.07435897435897436
    },
    {
      "seed": 4,
      "view": "center",
      "best_val_macro_f1": 0.7121396478876013,
      "epochs": 65,
      "accuracy": 0.8282051282051283,
      "macro_f1": 0.8307177918583403,
      "severity_mae": 0.1794871794871795,
      "underestimation_rate": 0.08461538461538462
    },
    {
      "seed": 4,
      "view": "cross",
      "best_val_macro_f1": 0.7121396478876013,
      "epochs": 65,
      "accuracy": 0.8384615384615385,
      "macro_f1": 0.8402961564640538,
      "severity_mae": 0.1717948717948718,
      "underestimation_rate": 0.07692307692307693
    }
  ],
  "aggregate": {
    "full": {
      "accuracy": {
        "mean": 0.8394871794871795,
        "std": 0.015868459945400835
      },
      "macro_f1": {
        "mean": 0.840991268829888,
        "std": 0.015464051599850063
      },
      "severity_mae": {
        "mean": 0.17384615384615384,
        "std": 0.017985310683846338
      },
      "underestimation_rate": {
        "mean": 0.07692307692307693,
        "std": 0.004796996649710183
      }
    },
    "center": {
      "accuracy": {
        "mean": 0.834871794871795,
        "std": 0.013024025742769523
      },
      "macro_f1": {
        "mean": 0.8368058994361551,
        "std": 0.013100975516178729
      },
      "severity_mae": {
        "mean": 0.1753846153846154,
        "std": 0.01523430848975687
      },
      "underestimation_rate": {
        "mean": 0.08410256410256411,
        "std": 0.003803178711331111
      }
    },
    "cross": {
      "accuracy": {
        "mean": 0.841025641025641,
        "std": 0.01641826727546886
      },
      "macro_f1": {
        "mean": 0.8424378098511986,
        "std": 0.016141135163998916
      },
      "severity_mae": {
        "mean": 0.1712820512820513,
        "std": 0.019222220322042363
      },
      "underestimation_rate": {
        "mean": 0.08,
        "std": 0.004213250442347432
      }
    }
  }
}
```
