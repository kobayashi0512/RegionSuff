# Exp23：序数严重度与PDR优化

## 设计
原始严重度预测对最高级PDR的召回和区分能力偏弱。这里比较三类表征（冻结特征、质量输出+冻结特征+手工统计融合）以及两种学习方式：类别均衡多分类和两个累计阈值的序数回归。序数模型显式利用Normal < NPDR < PDR的等级关系。

## 结果
```json
{
  "full_frozen_balanced": {
    "selected_C": 0.01,
    "tuning": [
      {
        "C": 0.01,
        "val_macro_f1": 0.7445676631511237
      },
      {
        "C": 0.03,
        "val_macro_f1": 0.7292977545719893
      },
      {
        "C": 0.1,
        "val_macro_f1": 0.7187419408491359
      },
      {
        "C": 0.3,
        "val_macro_f1": 0.7135707229474088
      },
      {
        "C": 1.0,
        "val_macro_f1": 0.705700446125978
      }
    ],
    "train": {
      "accuracy": 0.9897260273972602,
      "macro_f1": 0.9900056880874953,
      "severity_mae": 0.010273972602739725,
      "underestimation_rate": 0.00684931506849315,
      "pdr_n": 265,
      "pdr_recall": 0.9924528301886792,
      "pdr_precision": 0.9924528301886792,
      "pdr_predicted_rate": 0.3025114155251142,
      "predicted_class_counts": [
        263,
        348,
        265
      ],
      "pdr_auroc": 0.9999197109594541,
      "pdr_average_precision": 0.9998140547201774,
      "normal_n": 260,
      "normal_accuracy": 0.9961538461538462,
      "normal_underestimation_rate": 0.0,
      "npdr_n": 351,
      "npdr_accuracy": 0.9829059829059829,
      "npdr_underestimation_rate": 0.011396011396011397,
      "pdr_accuracy": 0.9924528301886792,
      "pdr_underestimation_rate": 0.007547169811320755
    },
    "val": {
      "accuracy": 0.7417582417582418,
      "macro_f1": 0.7445676631511237,
      "severity_mae": 0.27197802197802196,
      "underestimation_rate": 0.13736263736263737,
      "pdr_n": 111,
      "pdr_recall": 0.8108108108108109,
      "pdr_precision": 0.7142857142857143,
      "pdr_predicted_rate": 0.34615384615384615,
      "predicted_class_counts": [
        127,
        111,
        126
      ],
      "pdr_auroc": 0.9127764127764127,
      "pdr_average_precision": 0.8225131642860367,
      "normal_n": 107,
      "normal_accuracy": 0.897196261682243,
      "normal_underestimation_rate": 0.0,
      "npdr_n": 146,
      "npdr_accuracy": 0.5753424657534246,
      "npdr_underestimation_rate": 0.19863013698630136,
      "pdr_accuracy": 0.8108108108108109,
      "pdr_underestimation_rate": 0.1891891891891892
    },
    "test": {
      "accuracy": 0.7897435897435897,
      "macro_f1": 0.7897581569993578,
      "severity_mae": 0.22564102564102564,
      "underestimation_rate": 0.08974358974358974,
      "pdr_n": 124,
      "pdr_recall": 0.8790322580645161,
      "pdr_precision": 0.7841726618705036,
      "pdr_predicted_rate": 0.3564102564102564,
      "predicted_class_counts": [
        128,
        123,
        139
      ],
      "pdr_auroc": 0.9475200097016735,
      "pdr_average_precision": 0.9177631174319537,
      "normal_n": 129,
      "normal_accuracy": 0.8294573643410853,
      "normal_underestimation_rate": 0.0,
      "npdr_n": 137,
      "npdr_accuracy": 0.6715328467153284,
      "npdr_underestimation_rate": 0.145985401459854,
      "pdr_accuracy": 0.8790322580645161,
      "pdr_underestimation_rate": 0.12096774193548387
    }
  },
  "full_frozen_ordinal": {
    "selected_C": 0.03,
    "tuning": [
      {
        "C": 0.03,
        "val_macro_f1": 0.7574660974089364
      },
      {
        "C": 0.1,
        "val_macro_f1": 0.7427835777362058
      },
      {
        "C": 0.01,
        "val_macro_f1": 0.7326480832983143
      },
      {
        "C": 0.3,
        "val_macro_f1": 0.7218981021736731
      },
      {
        "C": 1.0,
        "val_macro_f1": 0.7195728669686078
      }
    ],
    "train": {
      "accuracy": 0.9874429223744292,
      "macro_f1": 0.987768117005405,
      "severity_mae": 0.012557077625570776,
      "underestimation_rate": 0.010273972602739725,
      "pdr_n": 265,
      "pdr_recall": 1.0,
      "pdr_precision": 0.9962406015037594,
      "pdr_predicted_rate": 0.3036529680365297,
      "predicted_class_counts": [
        268,
        342,
        266
      ],
      "pdr_auroc": 1.0,
      "pdr_average_precision": 1.0,
      "normal_n": 260,
      "normal_accuracy": 0.9961538461538462,
      "normal_underestimation_rate": 0.0,
      "npdr_n": 351,
      "npdr_accuracy": 0.9715099715099715,
      "npdr_underestimation_rate": 0.02564102564102564,
      "pdr_accuracy": 1.0,
      "pdr_underestimation_rate": 0.0
    },
    "val": {
      "accuracy": 0.7527472527472527,
      "macro_f1": 0.7574660974089364,
      "severity_mae": 0.25274725274725274,
      "underestimation_rate": 0.12087912087912088,
      "pdr_n": 111,
      "pdr_recall": 0.8288288288288288,
      "pdr_precision": 0.7419354838709677,
      "pdr_predicted_rate": 0.34065934065934067,
      "predicted_class_counts": [
        118,
        122,
        124
      ],
      "pdr_auroc": 0.907755581668625,
      "pdr_average_precision": 0.8008417687612299,
      "normal_n": 107,
      "normal_accuracy": 0.8598130841121495,
      "normal_underestimation_rate": 0.0,
      "npdr_n": 146,
      "npdr_accuracy": 0.6164383561643836,
      "npdr_underestimation_rate": 0.17123287671232876,
      "pdr_accuracy": 0.8288288288288288,
      "pdr_underestimation_rate": 0.17117117117117117
    },
    "test": {
      "accuracy": 0.7743589743589744,
      "macro_f1": 0.7748993285026189,
      "severity_mae": 0.23846153846153847,
      "underestimation_rate": 0.10512820512820513,
      "pdr_n": 124,
      "pdr_recall": 0.8548387096774194,
      "pdr_precision": 0.7969924812030075,
      "pdr_predicted_rate": 0.34102564102564104,
      "predicted_class_counts": [
        131,
        126,
        133
      ],
      "pdr_auroc": 0.9407591559544021,
      "pdr_average_precision": 0.8996474404790529,
      "normal_n": 129,
      "normal_accuracy": 0.8217054263565892,
      "normal_underestimation_rate": 0.0,
      "npdr_n": 137,
      "npdr_accuracy": 0.656934306569343,
      "npdr_underestimation_rate": 0.1678832116788321,
      "pdr_accuracy": 0.8548387096774194,
      "pdr_underestimation_rate": 0.14516129032258066
    }
  },
  "full_fusion_balanced": {
    "selected_C": 0.01,
    "tuning": [
      {
        "C": 0.01,
        "val_macro_f1": 0.7299576412570764
      },
      {
        "C": 0.1,
        "val_macro_f1": 0.7228867623604466
      },
      {
        "C": 0.03,
        "val_macro_f1": 0.7193396654123406
      },
      {
        "C": 1.0,
        "val_macro_f1": 0.715006216489016
      },
      {
        "C": 0.3,
        "val_macro_f1": 0.7147008160651485
      }
    ],
    "train": {
      "accuracy": 0.9897260273972602,
      "macro_f1": 0.9900056880874953,
      "severity_mae": 0.010273972602739725,
      "underestimation_rate": 0.00684931506849315,
      "pdr_n": 265,
      "pdr_recall": 0.9924528301886792,
      "pdr_precision": 0.9924528301886792,
      "pdr_predicted_rate": 0.3025114155251142,
      "predicted_class_counts": [
        263,
        348,
        265
      ],
      "pdr_auroc": 0.9999320631195381,
      "pdr_average_precision": 0.9998431383341666,
      "normal_n": 260,
      "normal_accuracy": 0.9961538461538462,
      "normal_underestimation_rate": 0.0,
      "npdr_n": 351,
      "npdr_accuracy": 0.9829059829059829,
      "npdr_underestimation_rate": 0.011396011396011397,
      "pdr_accuracy": 0.9924528301886792,
      "pdr_underestimation_rate": 0.007547169811320755
    },
    "val": {
      "accuracy": 0.7252747252747253,
      "macro_f1": 0.7299576412570764,
      "severity_mae": 0.29120879120879123,
      "underestimation_rate": 0.12912087912087913,
      "pdr_n": 111,
      "pdr_recall": 0.8018018018018018,
      "pdr_precision": 0.712,
      "pdr_predicted_rate": 0.3434065934065934,
      "predicted_class_counts": [
        115,
        124,
        125
      ],
      "pdr_auroc": 0.9080404515187125,
      "pdr_average_precision": 0.8213142140869454,
      "normal_n": 107,
      "normal_accuracy": 0.8130841121495327,
      "normal_underestimation_rate": 0.0,
      "npdr_n": 146,
      "npdr_accuracy": 0.6027397260273972,
      "npdr_underestimation_rate": 0.17123287671232876,
      "pdr_accuracy": 0.8018018018018018,
      "pdr_underestimation_rate": 0.1981981981981982
    },
    "test": {
      "accuracy": 0.7948717948717948,
      "macro_f1": 0.7950642325895876,
      "severity_mae": 0.21794871794871795,
      "underestimation_rate": 0.08461538461538462,
      "pdr_n": 124,
      "pdr_recall": 0.8870967741935484,
      "pdr_precision": 0.7857142857142857,
      "pdr_predicted_rate": 0.358974358974359,
      "predicted_class_counts": [
        126,
        124,
        140
      ],
      "pdr_auroc": 0.9507943245209799,
      "pdr_average_precision": 0.9235628127003386,
      "normal_n": 129,
      "normal_accuracy": 0.8294573643410853,
      "normal_underestimation_rate": 0.0,
      "npdr_n": 137,
      "npdr_accuracy": 0.6788321167883211,
      "npdr_underestimation_rate": 0.1386861313868613,
      "pdr_accuracy": 0.8870967741935484,
      "pdr_underestimation_rate": 0.11290322580645161
    }
  },
  "central_frozen_balanced": {
    "selected_C": 0.01,
    "tuning": [
      {
        "C": 0.01,
        "val_macro_f1": 0.759699766434613
      },
      {
        "C": 0.03,
        "val_macro_f1": 0.7402262109360479
      },
      {
        "C": 0.1,
        "val_macro_f1": 0.7158119658119659
      },
      {
        "C": 0.3,
        "val_macro_f1": 0.7131766524218716
      },
      {
        "C": 1.0,
        "val_macro_f1": 0.7021773748662731
      }
    ],
    "train": {
      "accuracy": 0.9908675799086758,
      "macro_f1": 0.9909620833737991,
      "severity_mae": 0.010273972602739725,
      "underestimation_rate": 0.0091324200913242,
      "pdr_n": 265,
      "pdr_recall": 0.9886792452830189,
      "pdr_precision": 1.0,
      "pdr_predicted_rate": 0.2990867579908676,
      "predicted_class_counts": [
        266,
        348,
        262
      ],
      "pdr_auroc": 0.999925887039496,
      "pdr_average_precision": 0.9998325945523606,
      "normal_n": 260,
      "normal_accuracy": 1.0,
      "normal_underestimation_rate": 0.0,
      "npdr_n": 351,
      "npdr_accuracy": 0.9857549857549858,
      "npdr_underestimation_rate": 0.014245014245014245,
      "pdr_accuracy": 0.9886792452830189,
      "pdr_underestimation_rate": 0.011320754716981131
    },
    "val": {
      "accuracy": 0.7554945054945055,
      "macro_f1": 0.759699766434613,
      "severity_mae": 0.25824175824175827,
      "underestimation_rate": 0.13736263736263737,
      "pdr_n": 111,
      "pdr_recall": 0.6756756756756757,
      "pdr_precision": 0.7653061224489796,
      "pdr_predicted_rate": 0.2692307692307692,
      "predicted_class_counts": [
        104,
        162,
        98
      ],
      "pdr_auroc": 0.8853932984367767,
      "pdr_average_precision": 0.8358459846529483,
      "normal_n": 107,
      "normal_accuracy": 0.822429906542056,
      "normal_underestimation_rate": 0.0,
      "npdr_n": 146,
      "npdr_accuracy": 0.7671232876712328,
      "npdr_underestimation_rate": 0.0958904109589041,
      "pdr_accuracy": 0.6756756756756757,
      "pdr_underestimation_rate": 0.32432432432432434
    },
    "test": {
      "accuracy": 0.8589743589743589,
      "macro_f1": 0.8592172953269421,
      "severity_mae": 0.14871794871794872,
      "underestimation_rate": 0.09230769230769231,
      "pdr_n": 124,
      "pdr_recall": 0.8709677419354839,
      "pdr_precision": 0.8925619834710744,
      "pdr_predicted_rate": 0.31025641025641026,
      "predicted_class_counts": [
        142,
        127,
        121
      ],
      "pdr_auroc": 0.9654377880184333,
      "pdr_average_precision": 0.9540385508417142,
      "normal_n": 129,
      "normal_accuracy": 0.937984496124031,
      "normal_underestimation_rate": 0.0,
      "npdr_n": 137,
      "npdr_accuracy": 0.7737226277372263,
      "npdr_underestimation_rate": 0.145985401459854,
      "pdr_accuracy": 0.8709677419354839,
      "pdr_underestimation_rate": 0.12903225806451613
    }
  },
  "central_frozen_ordinal": {
    "selected_C": 0.01,
    "tuning": [
      {
        "C": 0.01,
        "val_macro_f1": 0.767228017259436
      },
      {
        "C": 0.03,
        "val_macro_f1": 0.7514997573542318
      },
      {
        "C": 0.1,
        "val_macro_f1": 0.7458784305942592
      },
      {
        "C": 0.3,
        "val_macro_f1": 0.7350153170680659
      },
      {
        "C": 1.0,
        "val_macro_f1": 0.721284722175366
      }
    ],
    "train": {
      "accuracy": 0.9691780821917808,
      "macro_f1": 0.9698778689862843,
      "severity_mae": 0.0319634703196347,
      "underestimation_rate": 0.023972602739726026,
      "pdr_n": 265,
      "pdr_recall": 0.9924528301886792,
      "pdr_precision": 0.9776951672862454,
      "pdr_predicted_rate": 0.3070776255707763,
      "predicted_class_counts": [
        280,
        327,
        269
      ],
      "pdr_auroc": 0.9996047308773122,
      "pdr_average_precision": 0.9991149805623901,
      "normal_n": 260,
      "normal_accuracy": 1.0,
      "normal_underestimation_rate": 0.0,
      "npdr_n": 351,
      "npdr_accuracy": 0.9287749287749287,
      "npdr_underestimation_rate": 0.05413105413105413,
      "pdr_accuracy": 0.9924528301886792,
      "pdr_underestimation_rate": 0.007547169811320755
    },
    "val": {
      "accuracy": 0.7637362637362637,
      "macro_f1": 0.767228017259436,
      "severity_mae": 0.25824175824175827,
      "underestimation_rate": 0.13186813186813187,
      "pdr_n": 111,
      "pdr_recall": 0.7117117117117117,
      "pdr_precision": 0.7383177570093458,
      "pdr_predicted_rate": 0.29395604395604397,
      "predicted_class_counts": [
        111,
        146,
        107
      ],
      "pdr_auroc": 0.8917672613324787,
      "pdr_average_precision": 0.840369925221545,
      "normal_n": 107,
      "normal_accuracy": 0.8598130841121495,
      "normal_underestimation_rate": 0.0,
      "npdr_n": 146,
      "npdr_accuracy": 0.7328767123287672,
      "npdr_underestimation_rate": 0.1095890410958904,
      "pdr_accuracy": 0.7117117117117117,
      "pdr_underestimation_rate": 0.2882882882882883
    },
    "test": {
      "accuracy": 0.8461538461538461,
      "macro_f1": 0.8457083857339032,
      "severity_mae": 0.1641025641025641,
      "underestimation_rate": 0.09743589743589744,
      "pdr_n": 124,
      "pdr_recall": 0.8709677419354839,
      "pdr_precision": 0.8709677419354839,
      "pdr_predicted_rate": 0.31794871794871793,
      "predicted_class_counts": [
        145,
        121,
        124
      ],
      "pdr_auroc": 0.9713497453310695,
      "pdr_average_precision": 0.9545914009006075,
      "normal_n": 129,
      "normal_accuracy": 0.937984496124031,
      "normal_underestimation_rate": 0.0,
      "npdr_n": 137,
      "npdr_accuracy": 0.7372262773722628,
      "npdr_underestimation_rate": 0.16058394160583941,
      "pdr_accuracy": 0.8709677419354839,
      "pdr_underestimation_rate": 0.12903225806451613
    }
  },
  "central_fusion_balanced": {
    "selected_C": 0.01,
    "tuning": [
      {
        "C": 0.01,
        "val_macro_f1": 0.7595400398220309
      },
      {
        "C": 0.03,
        "val_macro_f1": 0.7575634959673326
      },
      {
        "C": 1.0,
        "val_macro_f1": 0.7510448261474921
      },
      {
        "C": 0.3,
        "val_macro_f1": 0.7358511185847947
      },
      {
        "C": 0.1,
        "val_macro_f1": 0.7304806919179482
      }
    ],
    "train": {
      "accuracy": 0.9920091324200914,
      "macro_f1": 0.9920707207614229,
      "severity_mae": 0.0091324200913242,
      "underestimation_rate": 0.007990867579908675,
      "pdr_n": 265,
      "pdr_recall": 0.9886792452830189,
      "pdr_precision": 1.0,
      "pdr_predicted_rate": 0.2990867579908676,
      "predicted_class_counts": [
        265,
        349,
        262
      ],
      "pdr_auroc": 0.999919710959454,
      "pdr_average_precision": 0.9998190282402268,
      "normal_n": 260,
      "normal_accuracy": 1.0,
      "normal_underestimation_rate": 0.0,
      "npdr_n": 351,
      "npdr_accuracy": 0.9886039886039886,
      "npdr_underestimation_rate": 0.011396011396011397,
      "pdr_accuracy": 0.9886792452830189,
      "pdr_underestimation_rate": 0.011320754716981131
    },
    "val": {
      "accuracy": 0.7554945054945055,
      "macro_f1": 0.7595400398220309,
      "severity_mae": 0.25824175824175827,
      "underestimation_rate": 0.14285714285714285,
      "pdr_n": 111,
      "pdr_recall": 0.6846846846846847,
      "pdr_precision": 0.7755102040816326,
      "pdr_predicted_rate": 0.2692307692307692,
      "predicted_class_counts": [
        110,
        156,
        98
      ],
      "pdr_auroc": 0.8908770430509559,
      "pdr_average_precision": 0.844625821939082,
      "normal_n": 107,
      "normal_accuracy": 0.8411214953271028,
      "normal_underestimation_rate": 0.0,
      "npdr_n": 146,
      "npdr_accuracy": 0.7465753424657534,
      "npdr_underestimation_rate": 0.11643835616438356,
      "pdr_accuracy": 0.6846846846846847,
      "pdr_underestimation_rate": 0.3153153153153153
    },
    "test": {
      "accuracy": 0.8435897435897436,
      "macro_f1": 0.8441714104205765,
      "severity_mae": 0.16666666666666666,
      "underestimation_rate": 0.10256410256410256,
      "pdr_n": 124,
      "pdr_recall": 0.8467741935483871,
      "pdr_precision": 0.8898305084745762,
      "pdr_predicted_rate": 0.30256410256410254,
      "predicted_class_counts": [
        142,
        130,
        118
      ],
      "pdr_auroc": 0.9660744603444094,
      "pdr_average_precision": 0.9528216746460975,
      "normal_n": 129,
      "normal_accuracy": 0.9224806201550387,
      "normal_underestimation_rate": 0.0,
      "npdr_n": 137,
      "npdr_accuracy": 0.7664233576642335,
      "npdr_underestimation_rate": 0.15328467153284672,
      "pdr_accuracy": 0.8467741935483871,
      "pdr_underestimation_rate": 0.1532258064516129
    }
  }
}
```

## 重点读法
PDR AUROC/AP反映把PDR与非PDR区分开的能力；PDR recall反映真正PDR中被识别出来的比例；underestimation_rate反映模型把严重度报低的风险。不能只看总体accuracy。