# Exp47：患者级嵌套风险校准

采用4折外层患者分组交叉验证；每个外层训练折再划分模型拟合和独立阈值校准子集，外层留出折只用于评估风险—覆盖率。

```json
{
  "protocol": "4-fold outer GroupKFold on original train+validation patients; each outer-train fold is group-split into model-fit and independent calibration subsets. Original held-out test is untouched.",
  "n_samples": 1240,
  "n_patients": 656,
  "folds": [
    {
      "fold": 0,
      "n_fit": 669,
      "n_calibration": 261,
      "n_outer_test": 310,
      "best_val_macro_f1": 0.8541926058734663,
      "epochs": 43,
      "risk_test": {
        "auroc": 0.6583468981732682,
        "average_precision": 0.10446335130015917,
        "positive_rate": 0.06129032258064516,
        "brier": 0.21301860392601077
      },
      "selective": {
        "0.05": {
          "calibration": {
            "threshold": 0.7441240367994193,
            "validation_coverage": 0.9578544061302682,
            "validation_risk": 0.024,
            "validation_cp_upper": 0.04681743080651248,
            "feasible": true
          },
          "test_coverage": 0.9580645161290322,
          "test_accepted_risk": 0.06060606060606061,
          "test_accepted_n": 297,
          "test_rejected_n": 13
        },
        "0.10": {
          "calibration": {
            "threshold": 0.807352024121252,
            "validation_coverage": 1.0,
            "validation_risk": 0.038314176245210725,
            "validation_cp_upper": 0.06412267420953204,
            "feasible": true
          },
          "test_coverage": 0.9774193548387097,
          "test_accepted_risk": 0.0627062706270627,
          "test_accepted_n": 303,
          "test_rejected_n": 7
        },
        "0.20": {
          "calibration": {
            "threshold": 0.807352024121252,
            "validation_coverage": 1.0,
            "validation_risk": 0.038314176245210725,
            "validation_cp_upper": 0.06412267420953204,
            "feasible": true
          },
          "test_coverage": 0.9774193548387097,
          "test_accepted_risk": 0.0627062706270627,
          "test_accepted_n": 303,
          "test_rejected_n": 7
        }
      }
    },
    {
      "fold": 1,
      "n_fit": 724,
      "n_calibration": 206,
      "n_outer_test": 310,
      "best_val_macro_f1": 0.891575242053711,
      "epochs": 45,
      "risk_test": {
        "auroc": 0.6957932598326686,
        "average_precision": 0.27776614126442656,
        "positive_rate": 0.15806451612903225,
        "brier": 0.22502733385400212
      },
      "selective": {
        "0.05": {
          "calibration": {
            "threshold": 0.47592714409641046,
            "validation_coverage": 0.5533980582524272,
            "validation_risk": 0.008771929824561403,
            "validation_cp_upper": 0.04093575055116398,
            "feasible": true
          },
          "test_coverage": 0.5548387096774193,
          "test_accepted_risk": 0.0872093023255814,
          "test_accepted_n": 172,
          "test_rejected_n": 138
        },
        "0.10": {
          "calibration": {
            "threshold": 0.7826640422362194,
            "validation_coverage": 0.9660194174757282,
            "validation_risk": 0.06030150753768844,
            "validation_cp_upper": 0.09587165799540366,
            "feasible": true
          },
          "test_coverage": 0.9225806451612903,
          "test_accepted_risk": 0.13986013986013987,
          "test_accepted_n": 286,
          "test_rejected_n": 24
        },
        "0.20": {
          "calibration": {
            "threshold": 0.9454133297368776,
            "validation_coverage": 1.0,
            "validation_risk": 0.07281553398058252,
            "validation_cp_upper": 0.10990975505778265,
            "feasible": true
          },
          "test_coverage": 0.967741935483871,
          "test_accepted_risk": 0.15333333333333332,
          "test_accepted_n": 300,
          "test_rejected_n": 10
        }
      }
    },
    {
      "fold": 2,
      "n_fit": 686,
      "n_calibration": 244,
      "n_outer_test": 310,
      "best_val_macro_f1": 0.7833218594282717,
      "epochs": 48,
      "risk_test": {
        "auroc": 0.645053779730344,
        "average_precision": 0.14132798921194498,
        "positive_rate": 0.07419354838709677,
        "brier": 0.21642256650289832
      },
      "selective": {
        "0.05": {
          "calibration": {
            "threshold": 0.37129820929119733,
            "validation_coverage": 0.4180327868852459,
            "validation_risk": 0.00980392156862745,
            "validation_cp_upper": 0.045663596327639985,
            "feasible": true
          },
          "test_coverage": 0.3903225806451613,
          "test_accepted_risk": 0.008264462809917356,
          "test_accepted_n": 121,
          "test_rejected_n": 189
        },
        "0.10": {
          "calibration": {
            "threshold": 0.5929320890268976,
            "validation_coverage": 0.7459016393442623,
            "validation_risk": 0.06043956043956044,
            "validation_cp_upper": 0.0980589558090448,
            "feasible": true
          },
          "test_coverage": 0.7193548387096774,
          "test_accepted_risk": 0.07174887892376682,
          "test_accepted_n": 223,
          "test_rejected_n": 87
        },
        "0.20": {
          "calibration": {
            "threshold": 0.9996442999031642,
            "validation_coverage": 1.0,
            "validation_risk": 0.12295081967213115,
            "validation_cp_upper": 0.16305473622009392,
            "feasible": true
          },
          "test_coverage": 1.0,
          "test_accepted_risk": 0.07419354838709677,
          "test_accepted_n": 310,
          "test_rejected_n": 0
        }
      }
    },
    {
      "fold": 3,
      "n_fit": 708,
      "n_calibration": 222,
      "n_outer_test": 310,
      "best_val_macro_f1": 0.8208427703381197,
      "epochs": 39,
      "risk_test": {
        "auroc": 0.6140476190476191,
        "average_precision": 0.12290052501779572,
        "positive_rate": 0.0967741935483871,
        "brier": 0.27704437648337626
      },
      "selective": {
        "0.05": {
          "calibration": {
            "threshold": 0.4392202668770094,
            "validation_coverage": 0.44144144144144143,
            "validation_risk": 0.01020408163265306,
            "validation_cp_upper": 0.047491903920603436,
            "feasible": true
          },
          "test_coverage": 0.36451612903225805,
          "test_accepted_risk": 0.04424778761061947,
          "test_accepted_n": 113,
          "test_rejected_n": 197
        },
        "0.10": {
          "calibration": {
            "threshold": 0.6584275018381488,
            "validation_coverage": 0.7207207207207207,
            "validation_risk": 0.05625,
            "validation_cp_upper": 0.096103154644457,
            "feasible": true
          },
          "test_coverage": 0.6290322580645161,
          "test_accepted_risk": 0.09230769230769231,
          "test_accepted_n": 195,
          "test_rejected_n": 115
        },
        "0.20": {
          "calibration": {
            "threshold": 0.7789844690379045,
            "validation_coverage": 1.0,
            "validation_risk": 0.10810810810810811,
            "validation_cp_upper": 0.1486602641541892,
            "feasible": true
          },
          "test_coverage": 0.9741935483870968,
          "test_accepted_risk": 0.09933774834437085,
          "test_accepted_n": 302,
          "test_rejected_n": 8
        }
      }
    }
  ],
  "aggregate": {
    "risk_auroc": {
      "mean": 0.653310389195975,
      "std": 0.03386196213946152
    },
    "target_0.05": {
      "test_coverage": {
        "mean": 0.5669354838709677,
        "std": 0.2740401215273579
      },
      "test_accepted_risk": {
        "mean": 0.0500819033380447,
        "std": 0.03302492432707016
      }
    },
    "target_0.10": {
      "test_coverage": {
        "mean": 0.8120967741935483,
        "std": 0.16497669035153997
      },
      "test_accepted_risk": {
        "mean": 0.09165574542966543,
        "std": 0.03444049991202568
      }
    },
    "target_0.20": {
      "test_coverage": {
        "mean": 0.9798387096774194,
        "std": 0.014030095000752554
      },
      "test_accepted_risk": {
        "mean": 0.09739272517296592,
        "std": 0.04030916640581927
      }
    }
  },
  "notes": [
    "Thresholds are calibrated without outer-fold labels, then assessed once on the held-out outer fold.",
    "This validates threshold transport across patient groups; it does not replace real prospective external calibration.",
    "The limited view remains the center+cross geometric proxy."
  ]
}
```
