# Exp53：MMRDR独立UWF受限视野外部验证

```json
{
  "dataset": {
    "name": "MMRDR UWF official patient-level test split",
    "n_images": 2597,
    "original_grade_counts": {
      "0": 800,
      "1": 509,
      "2": 544,
      "3": 358,
      "4": 386
    },
    "mapped_labels": "MMRDR grade 0->Normal; 1-3->NPDR; 4->PDR"
  },
  "protocol": "Five UWF-source-trained frozen-RetinaRadar regional attention heads are applied without MMRDR label training, calibration, early stopping, or model selection. Views are applied as 3x3 geometric region masks.",
  "quality_proxy": "Descriptive unlabeled proxy from retinal coverage, within-retina contrast and first-difference sharpness; it is not a clinical image-quality label.",
  "records": [
    {
      "seed": 0,
      "best_source_val_macro_f1": 0.7578849652516272,
      "epochs": 47,
      "views": {
        "full": {
          "accuracy": 0.6199460916442049,
          "macro_f1": 0.6221558194540776,
          "severity_mae": 0.41278398151713513,
          "underestimation_rate": 0.2934154793993069,
          "quality_proxy_quartiles": {
            "lowest_n": 650,
            "lowest": {
              "accuracy": 0.6169230769230769,
              "macro_f1": 0.5703313180940836,
              "severity_mae": 0.39692307692307693,
              "underestimation_rate": 0.35846153846153844
            },
            "highest_n": 650,
            "highest": {
              "accuracy": 0.6153846153846154,
              "macro_f1": 0.6211916583675449,
              "severity_mae": 0.44153846153846155,
              "underestimation_rate": 0.21076923076923076
            }
          }
        },
        "center": {
          "accuracy": 0.6030034655371582,
          "macro_f1": 0.6021731951144175,
          "severity_mae": 0.43088178667693494,
          "underestimation_rate": 0.2922603003465537
        },
        "center_plus_cross": {
          "accuracy": 0.6422795533307663,
          "macro_f1": 0.6425576684910488,
          "severity_mae": 0.3850596842510589,
          "underestimation_rate": 0.2653061224489796
        }
      }
    },
    {
      "seed": 1,
      "best_source_val_macro_f1": 0.7608917234678296,
      "epochs": 68,
      "views": {
        "full": {
          "accuracy": 0.626877165960724,
          "macro_f1": 0.6208261616305626,
          "severity_mae": 0.3993068925683481,
          "underestimation_rate": 0.2645360030804775,
          "quality_proxy_quartiles": {
            "lowest_n": 650,
            "lowest": {
              "accuracy": 0.6323076923076923,
              "macro_f1": 0.5599623964888373,
              "severity_mae": 0.3769230769230769,
              "underestimation_rate": 0.31846153846153846
            },
            "highest_n": 650,
            "highest": {
              "accuracy": 0.5861538461538461,
              "macro_f1": 0.594645967414272,
              "severity_mae": 0.46615384615384614,
              "underestimation_rate": 0.22615384615384615
            }
          }
        },
        "center": {
          "accuracy": 0.6060839430111667,
          "macro_f1": 0.6015403417658364,
          "severity_mae": 0.42818636888717754,
          "underestimation_rate": 0.2633808240277243
        },
        "center_plus_cross": {
          "accuracy": 0.6438197920677705,
          "macro_f1": 0.6403140193092728,
          "severity_mae": 0.37658837119753563,
          "underestimation_rate": 0.2579899884482095
        }
      }
    },
    {
      "seed": 2,
      "best_source_val_macro_f1": 0.7386532460424086,
      "epochs": 49,
      "views": {
        "full": {
          "accuracy": 0.6349634193299961,
          "macro_f1": 0.6346575212663058,
          "severity_mae": 0.38968040046207164,
          "underestimation_rate": 0.2760877936080092,
          "quality_proxy_quartiles": {
            "lowest_n": 650,
            "lowest": {
              "accuracy": 0.64,
              "macro_f1": 0.588712862715817,
              "severity_mae": 0.3676923076923077,
              "underestimation_rate": 0.3292307692307692
            },
            "highest_n": 650,
            "highest": {
              "accuracy": 0.6107692307692307,
              "macro_f1": 0.6192533508575723,
              "severity_mae": 0.4338461538461538,
              "underestimation_rate": 0.21076923076923076
            }
          }
        },
        "center": {
          "accuracy": 0.594532152483635,
          "macro_f1": 0.5936447648784359,
          "severity_mae": 0.4408933384674625,
          "underestimation_rate": 0.30034655371582597
        },
        "center_plus_cross": {
          "accuracy": 0.6488255679630343,
          "macro_f1": 0.6496103102311396,
          "severity_mae": 0.37158259530227183,
          "underestimation_rate": 0.26646130150173275
        }
      }
    },
    {
      "seed": 3,
      "best_source_val_macro_f1": 0.7592964047848154,
      "epochs": 52,
      "views": {
        "full": {
          "accuracy": 0.6403542549095109,
          "macro_f1": 0.6354229368704183,
          "severity_mae": 0.38544474393531,
          "underestimation_rate": 0.2618405852907201,
          "quality_proxy_quartiles": {
            "lowest_n": 650,
            "lowest": {
              "accuracy": 0.676923076923077,
              "macro_f1": 0.6066528800219463,
              "severity_mae": 0.3323076923076923,
              "underestimation_rate": 0.28
            },
            "highest_n": 650,
            "highest": {
              "accuracy": 0.6107692307692307,
              "macro_f1": 0.619659785991416,
              "severity_mae": 0.44,
              "underestimation_rate": 0.2276923076923077
            }
          }
        },
        "center": {
          "accuracy": 0.6041586445899114,
          "macro_f1": 0.5994108234756609,
          "severity_mae": 0.431651906045437,
          "underestimation_rate": 0.2710820177127455
        },
        "center_plus_cross": {
          "accuracy": 0.6476703889102811,
          "macro_f1": 0.6429689261540514,
          "severity_mae": 0.37350789372352716,
          "underestimation_rate": 0.2560646900269542
        }
      }
    },
    {
      "seed": 4,
      "best_source_val_macro_f1": 0.76846533495698,
      "epochs": 81,
      "views": {
        "full": {
          "accuracy": 0.6153253754331921,
          "macro_f1": 0.6122817211844437,
          "severity_mae": 0.4143242202541394,
          "underestimation_rate": 0.2633808240277243,
          "quality_proxy_quartiles": {
            "lowest_n": 650,
            "lowest": {
              "accuracy": 0.6307692307692307,
              "macro_f1": 0.5779471525929213,
              "severity_mae": 0.38153846153846155,
              "underestimation_rate": 0.31384615384615383
            },
            "highest_n": 650,
            "highest": {
              "accuracy": 0.5723076923076923,
              "macro_f1": 0.5807819394835144,
              "severity_mae": 0.4815384615384615,
              "underestimation_rate": 0.2276923076923077
            }
          }
        },
        "center": {
          "accuracy": 0.6026184058529072,
          "macro_f1": 0.6026880894654933,
          "severity_mae": 0.4289564882556796,
          "underestimation_rate": 0.29264536003080477
        },
        "center_plus_cross": {
          "accuracy": 0.6380438968040046,
          "macro_f1": 0.6368111707479525,
          "severity_mae": 0.3835194455140547,
          "underestimation_rate": 0.2564497497112052
        }
      }
    }
  ],
  "summary": {
    "full": {
      "accuracy": {
        "mean": 0.6274932614555255,
        "std": 0.01032721171668679
      },
      "macro_f1": {
        "mean": 0.6250688320811616,
        "std": 0.009863398837103627
      },
      "severity_mae": {
        "mean": 0.40030804774740086,
        "std": 0.01310504687028889
      },
      "underestimation_rate": {
        "mean": 0.2718521370812476,
        "std": 0.013308255416854415
      }
    },
    "center": {
      "accuracy": {
        "mean": 0.6020793222949556,
        "std": 0.004429023376052539
      },
      "macro_f1": {
        "mean": 0.5998914429399688,
        "std": 0.003708047801275816
      },
      "severity_mae": {
        "mean": 0.4321139776665383,
        "std": 0.005104038376474246
      },
      "underestimation_rate": {
        "mean": 0.2839430111667308,
        "std": 0.01582871659181346
      }
    },
    "center_plus_cross": {
      "accuracy": {
        "mean": 0.6441278398151713,
        "std": 0.00433427395156108
      },
      "macro_f1": {
        "mean": 0.642452418986693,
        "std": 0.004688008613764187
      },
      "severity_mae": {
        "mean": 0.3780515979976896,
        "std": 0.005992597651893898
      },
      "underestimation_rate": {
        "mean": 0.26045437042741626,
        "std": 0.00502499199622944
      }
    }
  },
  "paired_limited_minus_full": {
    "center": {
      "accuracy": {
        "mean": -0.025413939160569887,
        "std": 0.01221009626161561
      },
      "macro_f1": {
        "mean": -0.02517738914119281,
        "std": 0.01296822820170378
      },
      "severity_mae": {
        "mean": 0.031805929919137464,
        "std": 0.0163969427808277
      },
      "underestimation_rate": {
        "mean": 0.01209087408548325,
        "std": 0.014160043071861092
      }
    },
    "center_plus_cross": {
      "accuracy": {
        "mean": 0.016634578359645748,
        "std": 0.006405199040819086
      },
      "macro_f1": {
        "mean": 0.017383586905531413,
        "std": 0.006466999313949465
      },
      "severity_mae": {
        "mean": -0.022256449749711204,
        "std": 0.0075328146504925605
      },
      "underestimation_rate": {
        "mean": -0.011397766653831343,
        "std": 0.009453979847161433
      }
    }
  },
  "notes": [
    "This is the required independent same-modality UWF replication, distinct from the Exp50/51 UWF-to-45-degree transfer audits.",
    "The official MMRDR UWF testing split is patient-level according to the data descriptor.",
    "Quality-proxy strata are exploratory and cannot be represented as clinically adjudicated quality-gate validation."
  ]
}
```
