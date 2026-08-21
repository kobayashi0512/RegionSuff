# Exp56–57：五种子集成与单视图风险头

{
  "experiment": "Exp56 ensemble and Exp57 single-view risk",
  "protocol": "same patient-grouped split; five existing seed heads; no original result overwritten",
  "per_seed": [
    {
      "seed": 0,
      "full": {
        "accuracy": 0.841025641025641,
        "macro_f1": 0.8426622215256901,
        "severity_mae": 0.16666666666666666,
        "underestimation_rate": 0.05897435897435897
      },
      "cross": {
        "accuracy": 0.8435897435897436,
        "macro_f1": 0.8449773871818037,
        "severity_mae": 0.16666666666666666,
        "underestimation_rate": 0.05897435897435897
      }
    },
    {
      "seed": 1,
      "full": {
        "accuracy": 0.8153846153846154,
        "macro_f1": 0.8174835660935357,
        "severity_mae": 0.19230769230769232,
        "underestimation_rate": 0.07692307692307693
      },
      "cross": {
        "accuracy": 0.8153846153846154,
        "macro_f1": 0.816941605839416,
        "severity_mae": 0.19487179487179487,
        "underestimation_rate": 0.08974358974358974
      }
    },
    {
      "seed": 2,
      "full": {
        "accuracy": 0.841025641025641,
        "macro_f1": 0.8426367191584583,
        "severity_mae": 0.16666666666666666,
        "underestimation_rate": 0.07179487179487179
      },
      "cross": {
        "accuracy": 0.841025641025641,
        "macro_f1": 0.8423711364887835,
        "severity_mae": 0.16666666666666666,
        "underestimation_rate": 0.07435897435897436
      }
    },
    {
      "seed": 3,
      "full": {
        "accuracy": 0.841025641025641,
        "macro_f1": 0.8425762473121517,
        "severity_mae": 0.16923076923076924,
        "underestimation_rate": 0.06923076923076923
      },
      "cross": {
        "accuracy": 0.8333333333333334,
        "macro_f1": 0.8348938134557997,
        "severity_mae": 0.1794871794871795,
        "underestimation_rate": 0.07179487179487179
      }
    },
    {
      "seed": 4,
      "full": {
        "accuracy": 0.8051282051282052,
        "macro_f1": 0.8057991888399743,
        "severity_mae": 0.20512820512820512,
        "underestimation_rate": 0.07179487179487179
      },
      "cross": {
        "accuracy": 0.8051282051282052,
        "macro_f1": 0.8055343890777941,
        "severity_mae": 0.2,
        "underestimation_rate": 0.08205128205128205
      }
    }
  ],
  "ensemble": {
    "full": {
      "validation": {
        "accuracy": 0.760989010989011,
        "macro_f1": 0.7685783576055605,
        "severity_mae": 0.25274725274725274,
        "underestimation_rate": 0.08791208791208792
      },
      "test": {
        "accuracy": 0.8307692307692308,
        "macro_f1": 0.8321529549522557,
        "severity_mae": 0.1794871794871795,
        "underestimation_rate": 0.07179487179487179
      }
    },
    "cross": {
      "validation": {
        "accuracy": 0.75,
        "macro_f1": 0.7587816451264123,
        "severity_mae": 0.260989010989011,
        "underestimation_rate": 0.0989010989010989
      },
      "test": {
        "accuracy": 0.841025641025641,
        "macro_f1": 0.8424464196460089,
        "severity_mae": 0.16666666666666666,
        "underestimation_rate": 0.07179487179487179
      }
    }
  },
  "risk": {
    "single_seed": {
      "risk_head": {
        "test": {
          "auroc": 0.7405288082083662,
          "average_precision": 0.12357684679656036,
          "brier": 0.1762227515157819,
          "positive_rate": 0.07179487179487179
        }
      },
      "selective": {
        "0.05": {
          "calibration": {
            "threshold": 0.5168709196316315,
            "validation_coverage": 0.532967032967033,
            "validation_risk": 0.015463917525773196,
            "validation_cp_upper": 0.03947999390917666,
            "feasible": true
          },
          "test_coverage": 0.6230769230769231,
          "test_accepted_risk": 0.024691358024691357
        },
        "0.1": {
          "calibration": {
            "threshold": 0.6388336253018277,
            "validation_coverage": 0.7554945054945055,
            "validation_risk": 0.06909090909090909,
            "validation_cp_upper": 0.09973332176198718,
            "feasible": true
          },
          "test_coverage": 0.8205128205128205,
          "test_accepted_risk": 0.0625
        },
        "0.2": {
          "calibration": {
            "threshold": 0.8001289360822914,
            "validation_coverage": 1.0,
            "validation_risk": 0.0989010989010989,
            "validation_cp_upper": 0.1285079215928169,
            "feasible": true
          },
          "test_coverage": 1.0,
          "test_accepted_risk": 0.07179487179487179
        }
      }
    },
    "ensemble": {
      "risk_head": {
        "test": {
          "auroc": 0.7670678768745067,
          "average_precision": 0.14160342939975976,
          "brier": 0.16799451025143325,
          "positive_rate": 0.07179487179487179
        }
      },
      "selective": {
        "0.05": {
          "calibration": {
            "threshold": 0.6184488199453508,
            "validation_coverage": 0.6428571428571429,
            "validation_risk": 0.02564102564102564,
            "validation_cp_upper": 0.04997839123291399,
            "feasible": true
          },
          "test_coverage": 0.764102564102564,
          "test_accepted_risk": 0.050335570469798654
        },
        "0.1": {
          "calibration": {
            "threshold": 0.6789750167248093,
            "validation_coverage": 0.8186813186813187,
            "validation_risk": 0.07046979865771812,
            "validation_cp_upper": 0.09989467079518917,
            "feasible": true
          },
          "test_coverage": 0.9,
          "test_accepted_risk": 0.07122507122507123
        },
        "0.2": {
          "calibration": {
            "threshold": 0.7433567126734942,
            "validation_coverage": 1.0,
            "validation_risk": 0.0989010989010989,
            "validation_cp_upper": 0.1285079215928169,
            "feasible": true
          },
          "test_coverage": 1.0,
          "test_accepted_risk": 0.07179487179487179
        }
      }
    }
  },
  "notes": [
    "Ensemble averages probability vectors across the five trained heads.",
    "Single-view risk receives only center-plus-cross probabilities, entropy, margin, expected severity and visible fraction.",
    "The single-view risk experiment is a research audit; synthetic center-plus-cross is still not a real paired acquisition."
  ],
  "elapsed_seconds": 1.859982967376709
}