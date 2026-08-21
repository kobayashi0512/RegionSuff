# Exp21：共享模型的公平视野比较

## 为什么重做
早期实验为每个视野单独训练分类器，视野差异和模型可学习性混在一起。Exp21固定同一个分类器，在同一批测试图像上比较完整视野、55%中心方形和近似45°圆形视野。

## 主要结果
```json
{
  "full_only_shared": {
    "train_views": [
      "full"
    ],
    "views": {
      "full": {
        "train": {
          "accuracy": 0.634703196347032,
          "macro_f1": 0.6264912576904983,
          "severity_mae": 0.4132420091324201,
          "underestimation_rate": 0.16210045662100456,
          "predicted_class_counts": [
            195,
            447,
            234
          ]
        },
        "val": {
          "accuracy": 0.49725274725274726,
          "macro_f1": 0.48479473845898974,
          "severity_mae": 0.5796703296703297,
          "underestimation_rate": 0.19230769230769232,
          "predicted_class_counts": [
            67,
            175,
            122
          ]
        },
        "test": {
          "accuracy": 0.5743589743589743,
          "macro_f1": 0.5606467229720841,
          "severity_mae": 0.5128205128205128,
          "underestimation_rate": 0.1641025641025641,
          "predicted_class_counts": [
            77,
            191,
            122
          ]
        }
      },
      "square55": {
        "train": {
          "accuracy": 0.5205479452054794,
          "macro_f1": 0.5030820171264776,
          "severity_mae": 0.5468036529680366,
          "underestimation_rate": 0.2808219178082192,
          "predicted_class_counts": [
            233,
            536,
            107
          ]
        },
        "val": {
          "accuracy": 0.3901098901098901,
          "macro_f1": 0.3902065509619519,
          "severity_mae": 0.7472527472527473,
          "underestimation_rate": 0.4258241758241758,
          "predicted_class_counts": [
            167,
            152,
            45
          ]
        },
        "test": {
          "accuracy": 0.5128205128205128,
          "macro_f1": 0.5246197605405548,
          "severity_mae": 0.5615384615384615,
          "underestimation_rate": 0.3,
          "predicted_class_counts": [
            134,
            194,
            62
          ],
          "paired_accuracy_delta_vs_full": -0.06153846153846154,
          "paired_win_rate": 0.1717948717948718,
          "paired_tie_rate": 0.5948717948717949,
          "paired_loss_rate": 0.23333333333333334,
          "paired_underestimation_delta_vs_full": 0.1358974358974359
        }
      },
      "circle45": {
        "train": {
          "accuracy": 0.5079908675799086,
          "macro_f1": 0.4112717190051412,
          "severity_mae": 0.5102739726027398,
          "underestimation_rate": 0.1678082191780822,
          "predicted_class_counts": [
            21,
            692,
            163
          ]
        },
        "val": {
          "accuracy": 0.44505494505494503,
          "macro_f1": 0.377134381672968,
          "severity_mae": 0.5961538461538461,
          "underestimation_rate": 0.2445054945054945,
          "predicted_class_counts": [
            30,
            267,
            67
          ]
        },
        "test": {
          "accuracy": 0.5102564102564102,
          "macro_f1": 0.44825949675103466,
          "severity_mae": 0.5461538461538461,
          "underestimation_rate": 0.14871794871794872,
          "predicted_class_counts": [
            22,
            268,
            100
          ],
          "paired_accuracy_delta_vs_full": -0.0641025641025641,
          "paired_win_rate": 0.12051282051282051,
          "paired_tie_rate": 0.6948717948717948,
          "paired_loss_rate": 0.18461538461538463,
          "paired_underestimation_delta_vs_full": -0.015384615384615385
        }
      }
    }
  },
  "view_augmented_shared": {
    "train_views": [
      "full",
      "square55",
      "circle45"
    ],
    "views": {
      "full": {
        "train": {
          "accuracy": 0.5993150684931506,
          "macro_f1": 0.5891812099547956,
          "severity_mae": 0.4531963470319635,
          "underestimation_rate": 0.1780821917808219,
          "predicted_class_counts": [
            183,
            450,
            243
          ]
        },
        "val": {
          "accuracy": 0.5082417582417582,
          "macro_f1": 0.5072920864087477,
          "severity_mae": 0.5741758241758241,
          "underestimation_rate": 0.21978021978021978,
          "predicted_class_counts": [
            90,
            157,
            117
          ]
        },
        "test": {
          "accuracy": 0.5153846153846153,
          "macro_f1": 0.5053113553113553,
          "severity_mae": 0.5743589743589743,
          "underestimation_rate": 0.19743589743589743,
          "predicted_class_counts": [
            81,
            175,
            134
          ]
        }
      },
      "square55": {
        "train": {
          "accuracy": 0.6541095890410958,
          "macro_f1": 0.6434097002987658,
          "severity_mae": 0.3755707762557078,
          "underestimation_rate": 0.13812785388127855,
          "predicted_class_counts": [
            162,
            484,
            230
          ]
        },
        "val": {
          "accuracy": 0.5054945054945055,
          "macro_f1": 0.5071904636956764,
          "severity_mae": 0.5769230769230769,
          "underestimation_rate": 0.23076923076923078,
          "predicted_class_counts": [
            102,
            138,
            124
          ]
        },
        "test": {
          "accuracy": 0.5769230769230769,
          "macro_f1": 0.5706991517290908,
          "severity_mae": 0.4948717948717949,
          "underestimation_rate": 0.1717948717948718,
          "predicted_class_counts": [
            83,
            190,
            117
          ],
          "paired_accuracy_delta_vs_full": 0.06153846153846154,
          "paired_win_rate": 0.16923076923076924,
          "paired_tie_rate": 0.7230769230769231,
          "paired_loss_rate": 0.1076923076923077,
          "paired_underestimation_delta_vs_full": -0.025641025641025633
        }
      },
      "circle45": {
        "train": {
          "accuracy": 0.613013698630137,
          "macro_f1": 0.5931427253853975,
          "severity_mae": 0.4292237442922374,
          "underestimation_rate": 0.1506849315068493,
          "predicted_class_counts": [
            145,
            507,
            224
          ]
        },
        "val": {
          "accuracy": 0.4807692307692308,
          "macro_f1": 0.4849251436211231,
          "severity_mae": 0.6043956043956044,
          "underestimation_rate": 0.29120879120879123,
          "predicted_class_counts": [
            122,
            144,
            98
          ]
        },
        "test": {
          "accuracy": 0.5435897435897435,
          "macro_f1": 0.5306012314169312,
          "severity_mae": 0.5307692307692308,
          "underestimation_rate": 0.1717948717948718,
          "predicted_class_counts": [
            70,
            200,
            120
          ],
          "paired_accuracy_delta_vs_full": 0.028205128205128206,
          "paired_win_rate": 0.17435897435897435,
          "paired_tie_rate": 0.6794871794871795,
          "paired_loss_rate": 0.14615384615384616,
          "paired_underestimation_delta_vs_full": -0.025641025641025633
        }
      }
    }
  }
}
```

## 解释
paired_accuracy_delta_vs_full是同一张图上局部视野相对完整视野的准确率变化；paired_win/loss/tie把每张测试图作为配对单位，避免仅比较总体准确率。

## 限制
几何裁剪仍然不能替代真实同眼配对的45°眼底照相；结果用于检验‘视野缩小是否导致低估’这一机制，而不是估计临床设备之间的绝对差异。