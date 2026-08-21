# Exp35：区域粒度、mask比例和聚合方式消融

统一评估3×3区域方法的关键设计选择。

```json
{
  "dataset": {
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
  "grid_granularity": {
    "1": {
      "mean": {
        "best_val_macro_f1": 0.7939703344468773,
        "epochs": 56,
        "full": {
          "accuracy": 0.782051282051282,
          "macro_f1": 0.7806490599647521,
          "severity_mae": 0.2358974358974359,
          "underestimation_rate": 0.11538461538461539
        },
        "center": {
          "accuracy": 0.782051282051282,
          "macro_f1": 0.7806490599647521,
          "severity_mae": 0.2358974358974359,
          "underestimation_rate": 0.11538461538461539
        },
        "cross": {
          "accuracy": 0.782051282051282,
          "macro_f1": 0.7806490599647521,
          "severity_mae": 0.2358974358974359,
          "underestimation_rate": 0.11538461538461539
        }
      },
      "max": {
        "best_val_macro_f1": 0.7939703344468773,
        "epochs": 56,
        "full": {
          "accuracy": 0.782051282051282,
          "macro_f1": 0.7806490599647521,
          "severity_mae": 0.2358974358974359,
          "underestimation_rate": 0.11538461538461539
        },
        "center": {
          "accuracy": 0.782051282051282,
          "macro_f1": 0.7806490599647521,
          "severity_mae": 0.2358974358974359,
          "underestimation_rate": 0.11538461538461539
        },
        "cross": {
          "accuracy": 0.782051282051282,
          "macro_f1": 0.7806490599647521,
          "severity_mae": 0.2358974358974359,
          "underestimation_rate": 0.11538461538461539
        }
      },
      "attention": {
        "best_val_macro_f1": 0.7939703344468773,
        "epochs": 56,
        "full": {
          "accuracy": 0.782051282051282,
          "macro_f1": 0.7806490599647521,
          "severity_mae": 0.2358974358974359,
          "underestimation_rate": 0.11538461538461539
        },
        "center": {
          "accuracy": 0.782051282051282,
          "macro_f1": 0.7806490599647521,
          "severity_mae": 0.2358974358974359,
          "underestimation_rate": 0.11538461538461539
        },
        "cross": {
          "accuracy": 0.782051282051282,
          "macro_f1": 0.7806490599647521,
          "severity_mae": 0.2358974358974359,
          "underestimation_rate": 0.11538461538461539
        }
      }
    },
    "2": {
      "mean": {
        "best_val_macro_f1": 0.7632185386454013,
        "epochs": 53,
        "full": {
          "accuracy": 0.8538461538461538,
          "macro_f1": 0.8534246263007651,
          "severity_mae": 0.14871794871794872,
          "underestimation_rate": 0.08974358974358974
        },
        "center": {
          "accuracy": 0.8538461538461538,
          "macro_f1": 0.8534246263007651,
          "severity_mae": 0.14871794871794872,
          "underestimation_rate": 0.08974358974358974
        },
        "cross": {
          "accuracy": 0.8538461538461538,
          "macro_f1": 0.8534246263007651,
          "severity_mae": 0.14871794871794872,
          "underestimation_rate": 0.08974358974358974
        }
      },
      "max": {
        "best_val_macro_f1": 0.7785805032924111,
        "epochs": 78,
        "full": {
          "accuracy": 0.8435897435897436,
          "macro_f1": 0.8444719253204344,
          "severity_mae": 0.15897435897435896,
          "underestimation_rate": 0.08461538461538462
        },
        "center": {
          "accuracy": 0.8435897435897436,
          "macro_f1": 0.8444719253204344,
          "severity_mae": 0.15897435897435896,
          "underestimation_rate": 0.08461538461538462
        },
        "cross": {
          "accuracy": 0.8435897435897436,
          "macro_f1": 0.8444719253204344,
          "severity_mae": 0.15897435897435896,
          "underestimation_rate": 0.08461538461538462
        }
      },
      "attention": {
        "best_val_macro_f1": 0.7617655249234195,
        "epochs": 54,
        "full": {
          "accuracy": 0.823076923076923,
          "macro_f1": 0.8241359716196932,
          "severity_mae": 0.19230769230769232,
          "underestimation_rate": 0.07948717948717948
        },
        "center": {
          "accuracy": 0.823076923076923,
          "macro_f1": 0.8241359716196932,
          "severity_mae": 0.19230769230769232,
          "underestimation_rate": 0.07948717948717948
        },
        "cross": {
          "accuracy": 0.823076923076923,
          "macro_f1": 0.8241359716196932,
          "severity_mae": 0.19230769230769232,
          "underestimation_rate": 0.07948717948717948
        }
      }
    },
    "3": {
      "mean": {
        "best_val_macro_f1": 0.7265830643686666,
        "epochs": 67,
        "full": {
          "accuracy": 0.7974358974358975,
          "macro_f1": 0.7989350965192278,
          "severity_mae": 0.21025641025641026,
          "underestimation_rate": 0.09743589743589744
        },
        "center": {
          "accuracy": 0.7589743589743589,
          "macro_f1": 0.7586921850987428,
          "severity_mae": 0.2641025641025641,
          "underestimation_rate": 0.10256410256410256
        },
        "cross": {
          "accuracy": 0.8179487179487179,
          "macro_f1": 0.819521034987552,
          "severity_mae": 0.18717948717948718,
          "underestimation_rate": 0.08974358974358974
        }
      },
      "max": {
        "best_val_macro_f1": 0.7122697406225433,
        "epochs": 62,
        "full": {
          "accuracy": 0.8076923076923077,
          "macro_f1": 0.8098462889767237,
          "severity_mae": 0.19743589743589743,
          "underestimation_rate": 0.08717948717948718
        },
        "center": {
          "accuracy": 0.7769230769230769,
          "macro_f1": 0.777908195418481,
          "severity_mae": 0.24358974358974358,
          "underestimation_rate": 0.09487179487179487
        },
        "cross": {
          "accuracy": 0.823076923076923,
          "macro_f1": 0.8239957871332027,
          "severity_mae": 0.1794871794871795,
          "underestimation_rate": 0.07692307692307693
        }
      },
      "attention": {
        "best_val_macro_f1": 0.7558871666336615,
        "epochs": 54,
        "full": {
          "accuracy": 0.8384615384615385,
          "macro_f1": 0.839725633843281,
          "severity_mae": 0.1717948717948718,
          "underestimation_rate": 0.07435897435897436
        },
        "center": {
          "accuracy": 0.7923076923076923,
          "macro_f1": 0.7934996879450722,
          "severity_mae": 0.22564102564102564,
          "underestimation_rate": 0.1
        },
        "cross": {
          "accuracy": 0.8358974358974359,
          "macro_f1": 0.8372226470293626,
          "severity_mae": 0.17435897435897435,
          "underestimation_rate": 0.07692307692307693
        }
      }
    },
    "4": {
      "mean": {
        "best_val_macro_f1": 0.7455224528343442,
        "epochs": 60,
        "full": {
          "accuracy": 0.823076923076923,
          "macro_f1": 0.8251667332729985,
          "severity_mae": 0.19230769230769232,
          "underestimation_rate": 0.08205128205128205
        },
        "center": {
          "accuracy": 0.841025641025641,
          "macro_f1": 0.8425763954344352,
          "severity_mae": 0.1641025641025641,
          "underestimation_rate": 0.07435897435897436
        },
        "cross": {
          "accuracy": 0.8307692307692308,
          "macro_f1": 0.8319054365435687,
          "severity_mae": 0.18205128205128204,
          "underestimation_rate": 0.08461538461538462
        }
      },
      "max": {
        "best_val_macro_f1": 0.7291560109368689,
        "epochs": 105,
        "full": {
          "accuracy": 0.8307692307692308,
          "macro_f1": 0.8326008980817861,
          "severity_mae": 0.18205128205128204,
          "underestimation_rate": 0.06153846153846154
        },
        "center": {
          "accuracy": 0.841025641025641,
          "macro_f1": 0.8432372949179672,
          "severity_mae": 0.16923076923076924,
          "underestimation_rate": 0.05897435897435897
        },
        "cross": {
          "accuracy": 0.8358974358974359,
          "macro_f1": 0.8381879956255333,
          "severity_mae": 0.17435897435897435,
          "underestimation_rate": 0.05897435897435897
        }
      },
      "attention": {
        "best_val_macro_f1": 0.7188377920915386,
        "epochs": 53,
        "full": {
          "accuracy": 0.841025641025641,
          "macro_f1": 0.8421663874319668,
          "severity_mae": 0.1717948717948718,
          "underestimation_rate": 0.06666666666666667
        },
        "center": {
          "accuracy": 0.8358974358974359,
          "macro_f1": 0.8370413579687263,
          "severity_mae": 0.1794871794871795,
          "underestimation_rate": 0.08205128205128205
        },
        "cross": {
          "accuracy": 0.841025641025641,
          "macro_f1": 0.8419293042495809,
          "severity_mae": 0.1717948717948718,
          "underestimation_rate": 0.07435897435897436
        }
      }
    }
  },
  "pooling": {
    "mean": {
      "best_val_macro_f1": 0.7265830643686666,
      "epochs": 67,
      "full": {
        "accuracy": 0.7974358974358975,
        "macro_f1": 0.7989350965192278,
        "severity_mae": 0.21025641025641026,
        "underestimation_rate": 0.09743589743589744
      },
      "center": {
        "accuracy": 0.7589743589743589,
        "macro_f1": 0.7586921850987428,
        "severity_mae": 0.2641025641025641,
        "underestimation_rate": 0.10256410256410256
      },
      "cross": {
        "accuracy": 0.8179487179487179,
        "macro_f1": 0.819521034987552,
        "severity_mae": 0.18717948717948718,
        "underestimation_rate": 0.08974358974358974
      }
    },
    "max": {
      "best_val_macro_f1": 0.7122697406225433,
      "epochs": 62,
      "full": {
        "accuracy": 0.8076923076923077,
        "macro_f1": 0.8098462889767237,
        "severity_mae": 0.19743589743589743,
        "underestimation_rate": 0.08717948717948718
      },
      "center": {
        "accuracy": 0.7769230769230769,
        "macro_f1": 0.777908195418481,
        "severity_mae": 0.24358974358974358,
        "underestimation_rate": 0.09487179487179487
      },
      "cross": {
        "accuracy": 0.823076923076923,
        "macro_f1": 0.8239957871332027,
        "severity_mae": 0.1794871794871795,
        "underestimation_rate": 0.07692307692307693
      }
    },
    "attention": {
      "best_val_macro_f1": 0.7558871666336615,
      "epochs": 54,
      "full": {
        "accuracy": 0.8384615384615385,
        "macro_f1": 0.839725633843281,
        "severity_mae": 0.1717948717948718,
        "underestimation_rate": 0.07435897435897436
      },
      "center": {
        "accuracy": 0.7923076923076923,
        "macro_f1": 0.7934996879450722,
        "severity_mae": 0.22564102564102564,
        "underestimation_rate": 0.1
      },
      "cross": {
        "accuracy": 0.8358974358974359,
        "macro_f1": 0.8372226470293626,
        "severity_mae": 0.17435897435897435,
        "underestimation_rate": 0.07692307692307693
      }
    }
  },
  "mask_ratio": {
    "0": {
      "best_val_macro_f1": 0.7441285949852078,
      "epochs": 50,
      "full": {
        "accuracy": 0.8358974358974359,
        "macro_f1": 0.8371022019919078,
        "severity_mae": 0.17435897435897435,
        "underestimation_rate": 0.07692307692307693
      },
      "center": {
        "accuracy": 0.8,
        "macro_f1": 0.8012389082571575,
        "severity_mae": 0.21794871794871795,
        "underestimation_rate": 0.09743589743589744
      },
      "cross": {
        "accuracy": 0.8461538461538461,
        "macro_f1": 0.847489765136824,
        "severity_mae": 0.16153846153846155,
        "underestimation_rate": 0.07179487179487179
      }
    },
    "0.15": {
      "best_val_macro_f1": 0.7607255946011025,
      "epochs": 70,
      "full": {
        "accuracy": 0.8153846153846154,
        "macro_f1": 0.8170772768333743,
        "severity_mae": 0.2,
        "underestimation_rate": 0.06153846153846154
      },
      "center": {
        "accuracy": 0.7948717948717948,
        "macro_f1": 0.7952493124480039,
        "severity_mae": 0.2230769230769231,
        "underestimation_rate": 0.09743589743589744
      },
      "cross": {
        "accuracy": 0.8179487179487179,
        "macro_f1": 0.8196840208186545,
        "severity_mae": 0.2,
        "underestimation_rate": 0.06153846153846154
      }
    },
    "0.3": {
      "best_val_macro_f1": 0.7558871666336615,
      "epochs": 54,
      "full": {
        "accuracy": 0.8384615384615385,
        "macro_f1": 0.839725633843281,
        "severity_mae": 0.1717948717948718,
        "underestimation_rate": 0.07435897435897436
      },
      "center": {
        "accuracy": 0.7923076923076923,
        "macro_f1": 0.7934996879450722,
        "severity_mae": 0.22564102564102564,
        "underestimation_rate": 0.1
      },
      "cross": {
        "accuracy": 0.8358974358974359,
        "macro_f1": 0.8372226470293626,
        "severity_mae": 0.17435897435897435,
        "underestimation_rate": 0.07692307692307693
      }
    },
    "0.45": {
      "best_val_macro_f1": 0.7439745146423302,
      "epochs": 52,
      "full": {
        "accuracy": 0.8333333333333334,
        "macro_f1": 0.8341103181888831,
        "severity_mae": 0.1794871794871795,
        "underestimation_rate": 0.07179487179487179
      },
      "center": {
        "accuracy": 0.7948717948717948,
        "macro_f1": 0.7946329159522193,
        "severity_mae": 0.23333333333333334,
        "underestimation_rate": 0.10256410256410256
      },
      "cross": {
        "accuracy": 0.8435897435897436,
        "macro_f1": 0.843327690160088,
        "severity_mae": 0.1641025641025641,
        "underestimation_rate": 0.06923076923076923
      }
    },
    "0.6": {
      "best_val_macro_f1": 0.7547867337341022,
      "epochs": 48,
      "full": {
        "accuracy": 0.8512820512820513,
        "macro_f1": 0.8531563885701333,
        "severity_mae": 0.15128205128205127,
        "underestimation_rate": 0.06923076923076923
      },
      "center": {
        "accuracy": 0.7974358974358975,
        "macro_f1": 0.7984372147852009,
        "severity_mae": 0.21794871794871795,
        "underestimation_rate": 0.1076923076923077
      },
      "cross": {
        "accuracy": 0.8538461538461538,
        "macro_f1": 0.8555952291760699,
        "severity_mae": 0.14871794871794872,
        "underestimation_rate": 0.06923076923076923
      }
    }
  },
  "notes": [
    "Tasks 2-4 share the same patient-level UWF split and frozen regional feature cache.",
    "The center/cross masks are geometric proxies.",
    "Validation macro-F1 is used for early stopping; test is evaluated once."
  ]
}
```
