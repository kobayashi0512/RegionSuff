# Exp59：按预测严重度分层的单视图风险校准

{
  "experiment": "Exp59 stratified single-view risk calibration",
  "protocol": "ensemble limited-view risk score; severity stratum is predicted limited-view severity; target labels are used only for validation calibration",
  "risk_head": {
    "test": {
      "auroc": 0.7670678768745067,
      "average_precision": 0.14160342939975976,
      "brier": 0.16799451025143325,
      "positive_rate": 0.07179487179487179
    }
  },
  "targets": {
    "0.05": {
      "global": {
        "calibration": {
          "threshold": 0.6184488199453508,
          "coverage": 0.6428571428571429,
          "accepted_risk": 0.02564102564102564,
          "cp_upper": 0.04997839123291399,
          "feasible": true
        },
        "test_coverage": 0.764102564102564,
        "test_accepted_risk": 0.050335570469798654
      },
      "stratified": {
        "calibration": {
          "0": {
            "threshold": 0.07295483543903616,
            "coverage": 0.010869565217391304,
            "accepted_risk": 0.0,
            "cp_upper": 0.95,
            "feasible": false
          },
          "1": {
            "threshold": 0.5764830925461831,
            "coverage": 0.006535947712418301,
            "accepted_risk": 0.0,
            "cp_upper": 0.95,
            "feasible": false
          },
          "2": {
            "threshold": 0.6806324793019495,
            "coverage": 1.0,
            "accepted_risk": 0.0,
            "cp_upper": 0.024859992430424385,
            "feasible": true
          }
        },
        "test": {
          "coverage": 0.3384615384615385,
          "accepted_n": 132,
          "accepted_risk": 0.007575757575757576,
          "by_predicted_severity": {
            "0": {
              "n": 2,
              "coverage_within_group": 0.016,
              "accepted_risk": 0.0
            },
            "1": {
              "n": 1,
              "coverage_within_group": 0.007352941176470588,
              "accepted_risk": 1.0
            },
            "2": {
              "n": 129,
              "coverage_within_group": 1.0,
              "accepted_risk": 0.0
            }
          }
        }
      }
    },
    "0.1": {
      "global": {
        "calibration": {
          "threshold": 0.6789750167248093,
          "coverage": 0.8186813186813187,
          "accepted_risk": 0.07046979865771812,
          "cp_upper": 0.09989467079518917,
          "feasible": true
        },
        "test_coverage": 0.9,
        "test_accepted_risk": 0.07122507122507123
      },
      "stratified": {
        "calibration": {
          "0": {
            "threshold": 0.5975554610428865,
            "coverage": 0.8913043478260869,
            "accepted_risk": 0.036585365853658534,
            "cp_upper": 0.09184700554975765,
            "feasible": true
          },
          "1": {
            "threshold": 0.5764830925461831,
            "coverage": 0.006535947712418301,
            "accepted_risk": 0.0,
            "cp_upper": 0.95,
            "feasible": false
          },
          "2": {
            "threshold": 0.6806324793019495,
            "coverage": 1.0,
            "accepted_risk": 0.0,
            "cp_upper": 0.024859992430424385,
            "feasible": true
          }
        },
        "test": {
          "coverage": 0.6435897435897436,
          "accepted_n": 251,
          "accepted_risk": 0.035856573705179286,
          "by_predicted_severity": {
            "0": {
              "n": 121,
              "coverage_within_group": 0.968,
              "accepted_risk": 0.06611570247933884
            },
            "1": {
              "n": 1,
              "coverage_within_group": 0.007352941176470588,
              "accepted_risk": 1.0
            },
            "2": {
              "n": 129,
              "coverage_within_group": 1.0,
              "accepted_risk": 0.0
            }
          }
        }
      }
    },
    "0.2": {
      "global": {
        "calibration": {
          "threshold": 0.7433567126734942,
          "coverage": 1.0,
          "accepted_risk": 0.0989010989010989,
          "cp_upper": 0.1285079215928169,
          "feasible": true
        },
        "test_coverage": 1.0,
        "test_accepted_risk": 0.07179487179487179
      },
      "stratified": {
        "calibration": {
          "0": {
            "threshold": 0.7031873623608814,
            "coverage": 1.0,
            "accepted_risk": 0.07608695652173914,
            "cp_upper": 0.1381628575092729,
            "feasible": true
          },
          "1": {
            "threshold": 0.6635139783306513,
            "coverage": 0.45751633986928103,
            "accepted_risk": 0.1,
            "cp_upper": 0.17963465865664738,
            "feasible": true
          },
          "2": {
            "threshold": 0.6806324793019495,
            "coverage": 1.0,
            "accepted_risk": 0.0,
            "cp_upper": 0.024859992430424385,
            "feasible": true
          }
        },
        "test": {
          "coverage": 0.8666666666666667,
          "accepted_n": 338,
          "accepted_risk": 0.05917159763313609,
          "by_predicted_severity": {
            "0": {
              "n": 123,
              "coverage_within_group": 0.984,
              "accepted_risk": 0.06504065040650407
            },
            "1": {
              "n": 86,
              "coverage_within_group": 0.6323529411764706,
              "accepted_risk": 0.13953488372093023
            },
            "2": {
              "n": 129,
              "coverage_within_group": 1.0,
              "accepted_risk": 0.0
            }
          }
        }
      }
    }
  },
  "notes": [
    "The full-view output is not used by the risk head.",
    "Stratification improves safety only if it lowers accepted risk without an unacceptable coverage collapse.",
    "The limited-view mask is a geometric proxy, not a real paired camera acquisition."
  ],
  "elapsed_seconds": 1.7046887874603271
}