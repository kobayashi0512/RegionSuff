# Deduplicated-validation sensitivity

The original test set is unchanged. Duplicate validation filenames are retained once; conflicting labels use majority vote with severe-class tie-breaking.

```json
{
  "purpose": "Sensitivity to duplicate/conflicting UWF-DR list entries used for early stopping",
  "original_validation_records": 364,
  "unique_validation_filenames": 342,
  "duplicate_extra_rows_removed": 22,
  "conflicting_validation_filenames": [
    {
      "filename": "5_197_2022-07-10_1_R.png",
      "listed_labels": [
        1,
        2,
        2
      ],
      "resolved_label": 2
    },
    {
      "filename": "5_123_2022-04-30_1_L.png",
      "listed_labels": [
        1,
        2
      ],
      "resolved_label": 2
    }
  ],
  "test_set_unchanged": true,
  "all_empty_mask_fallback": "geometric centre token (index 4)",
  "rows": [
    {
      "seed": 0,
      "best_deduplicated_val_full_macro_f1": 0.7578942771689037,
      "epochs": 48,
      "full": {
        "accuracy": 0.8461538461538461,
        "macro_f1": 0.8472133017388792,
        "severity_mae": 0.1641025641025641,
        "underestimation_rate": 0.06153846153846154
      },
      "center": {
        "accuracy": 0.8025641025641026,
        "macro_f1": 0.8030890298332158,
        "severity_mae": 0.2153846153846154,
        "underestimation_rate": 0.09230769230769231
      },
      "cross": {
        "accuracy": 0.8461538461538461,
        "macro_f1": 0.8474364796585808,
        "severity_mae": 0.16153846153846155,
        "underestimation_rate": 0.06153846153846154
      }
    },
    {
      "seed": 1,
      "best_deduplicated_val_full_macro_f1": 0.7644620811287478,
      "epochs": 52,
      "full": {
        "accuracy": 0.8307692307692308,
        "macro_f1": 0.8320867043779284,
        "severity_mae": 0.17692307692307693,
        "underestimation_rate": 0.07692307692307693
      },
      "center": {
        "accuracy": 0.782051282051282,
        "macro_f1": 0.7830641787298135,
        "severity_mae": 0.2358974358974359,
        "underestimation_rate": 0.09487179487179487
      },
      "cross": {
        "accuracy": 0.8282051282051283,
        "macro_f1": 0.8289362881525518,
        "severity_mae": 0.1794871794871795,
        "underestimation_rate": 0.07948717948717948
      }
    },
    {
      "seed": 2,
      "best_deduplicated_val_full_macro_f1": 0.7438819236168297,
      "epochs": 47,
      "full": {
        "accuracy": 0.8384615384615385,
        "macro_f1": 0.8405372555867118,
        "severity_mae": 0.16923076923076924,
        "underestimation_rate": 0.0641025641025641
      },
      "center": {
        "accuracy": 0.7871794871794872,
        "macro_f1": 0.7881924709871416,
        "severity_mae": 0.2282051282051282,
        "underestimation_rate": 0.09743589743589744
      },
      "cross": {
        "accuracy": 0.8461538461538461,
        "macro_f1": 0.8477169207603991,
        "severity_mae": 0.16153846153846155,
        "underestimation_rate": 0.06923076923076923
      }
    },
    {
      "seed": 3,
      "best_deduplicated_val_full_macro_f1": 0.7713852136387348,
      "epochs": 52,
      "full": {
        "accuracy": 0.8384615384615385,
        "macro_f1": 0.8400853253027166,
        "severity_mae": 0.1717948717948718,
        "underestimation_rate": 0.07179487179487179
      },
      "center": {
        "accuracy": 0.7974358974358975,
        "macro_f1": 0.7991946778711485,
        "severity_mae": 0.2153846153846154,
        "underestimation_rate": 0.08717948717948718
      },
      "cross": {
        "accuracy": 0.8307692307692308,
        "macro_f1": 0.8324926207838654,
        "severity_mae": 0.18205128205128204,
        "underestimation_rate": 0.07179487179487179
      }
    },
    {
      "seed": 4,
      "best_deduplicated_val_full_macro_f1": 0.7776729468458793,
      "epochs": 82,
      "full": {
        "accuracy": 0.8025641025641026,
        "macro_f1": 0.8026585758602268,
        "severity_mae": 0.2076923076923077,
        "underestimation_rate": 0.07692307692307693
      },
      "center": {
        "accuracy": 0.7769230769230769,
        "macro_f1": 0.778287664447276,
        "severity_mae": 0.2358974358974359,
        "underestimation_rate": 0.1
      },
      "cross": {
        "accuracy": 0.8025641025641026,
        "macro_f1": 0.8028453473521638,
        "severity_mae": 0.20256410256410257,
        "underestimation_rate": 0.08205128205128205
      }
    }
  ],
  "aggregate": {
    "full": {
      "accuracy": {
        "mean": 0.8312820512820513,
        "std": 0.016950250134398357
      },
      "macro_f1": {
        "mean": 0.8325162325732925,
        "std": 0.017530658685944684
      },
      "severity_mae": {
        "mean": 0.17794871794871797,
        "std": 0.017257762738937275
      },
      "underestimation_rate": {
        "mean": 0.07025641025641026,
        "std": 0.007161148740394331
      }
    },
    "center": {
      "accuracy": {
        "mean": 0.7892307692307693,
        "std": 0.01063407248888603
      },
      "macro_f1": {
        "mean": 0.7903656043737192,
        "std": 0.010532664101053538
      },
      "severity_mae": {
        "mean": 0.22615384615384615,
        "std": 0.010320313742306712
      },
      "underestimation_rate": {
        "mean": 0.09435897435897436,
        "std": 0.0049321497594029115
      }
    },
    "cross": {
      "accuracy": {
        "mean": 0.8307692307692308,
        "std": 0.01785690804767193
      },
      "macro_f1": {
        "mean": 0.8318855313415122,
        "std": 0.01833619210473124
      },
      "severity_mae": {
        "mean": 0.17743589743589744,
        "std": 0.017046943731891955
      },
      "underestimation_rate": {
        "mean": 0.07282051282051281,
        "std": 0.008229131556862158
      }
    }
  }
}
```
