# Exp38：RFMiD2区域表征外部疾病验证

比较全图冻结特征与3×3区域平均冻结特征在RFMiD2多标签疾病任务上的外部迁移性能。

```json
{
  "dataset": {
    "name": "RFMiD2.0",
    "train_n": 684,
    "test_n": 170,
    "device": "mps"
  },
  "models": {
    "global": {
      "n_labels": 45,
      "mean_auroc": 0.7314050004914072,
      "mean_average_precision": 0.37505512403301444,
      "per_label": [
        {
          "label": "WNL",
          "test_positive": 52,
          "auroc": 0.9967405475880052,
          "average_precision": 0.9936962019555833
        },
        {
          "label": "AH",
          "test_positive": 1,
          "auroc": 1.0,
          "average_precision": 1.0
        },
        {
          "label": "AION",
          "test_positive": 1,
          "auroc": 0.6390532544378698,
          "average_precision": 0.016129032258064516
        },
        {
          "label": "ARMD",
          "test_positive": 2,
          "auroc": 0.9732142857142857,
          "average_precision": 0.5909090909090909
        },
        {
          "label": "BRVO",
          "test_positive": 5,
          "auroc": 0.8812121212121213,
          "average_precision": 0.5874183006535947
        },
        {
          "label": "CB",
          "test_positive": 1,
          "auroc": 1.0,
          "average_precision": 1.0
        },
        {
          "label": "CF",
          "test_positive": 1,
          "auroc": 0.20118343195266275,
          "average_precision": 0.007352941176470588
        },
        {
          "label": "CME",
          "test_positive": 7,
          "auroc": 0.7861524978089395,
          "average_precision": 0.36804576376004944
        },
        {
          "label": "CNV",
          "test_positive": 1,
          "auroc": 1.0,
          "average_precision": 1.0
        },
        {
          "label": "CRS",
          "test_positive": 9,
          "auroc": 0.6052449965493445,
          "average_precision": 0.20581028777408927
        },
        {
          "label": "CRVO",
          "test_positive": 2,
          "auroc": 0.6279761904761905,
          "average_precision": 0.5078740157480315
        },
        {
          "label": "CSR",
          "test_positive": 3,
          "auroc": 0.6626746506986028,
          "average_precision": 0.5058823529411764
        },
        {
          "label": "CWS",
          "test_positive": 6,
          "auroc": 0.6981707317073171,
          "average_precision": 0.13350086201771594
        },
        {
          "label": "DN",
          "test_positive": 1,
          "auroc": 1.0,
          "average_precision": 1.0
        },
        {
          "label": "DR",
          "test_positive": 14,
          "auroc": 0.9981684981684982,
          "average_precision": 0.9804748822605964
        },
        {
          "label": "EDN",
          "test_positive": 17,
          "auroc": 0.8869665513264129,
          "average_precision": 0.5003098852570504
        },
        {
          "label": "ERM",
          "test_positive": 1,
          "auroc": 0.9289940828402367,
          "average_precision": 0.07692307692307693
        },
        {
          "label": "HPED",
          "test_positive": 1,
          "auroc": 0.18343195266272194,
          "average_precision": 0.007194244604316547
        },
        {
          "label": "HR",
          "test_positive": 16,
          "auroc": 0.7061688311688311,
          "average_precision": 0.30069104184182893
        },
        {
          "label": "LS",
          "test_positive": 2,
          "auroc": 0.9970238095238095,
          "average_precision": 0.8333333333333333
        },
        {
          "label": "MCA",
          "test_positive": 2,
          "auroc": 0.8779761904761905,
          "average_precision": 0.07291666666666666
        },
        {
          "label": "ME",
          "test_positive": 2,
          "auroc": 0.8392857142857143,
          "average_precision": 0.051587301587301584
        },
        {
          "label": "MH",
          "test_positive": 7,
          "auroc": 0.7300613496932515,
          "average_precision": 0.26092581950699556
        },
        {
          "label": "MHL",
          "test_positive": 1,
          "auroc": 0.6331360946745562,
          "average_precision": 0.015873015873015872
        },
        {
          "label": "MS",
          "test_positive": 7,
          "auroc": 0.7458369851007887,
          "average_precision": 0.12037183055040199
        },
        {
          "label": "MYA",
          "test_positive": 5,
          "auroc": 0.8933333333333333,
          "average_precision": 0.652987012987013
        },
        {
          "label": "ODC",
          "test_positive": 7,
          "auroc": 0.7309377738825591,
          "average_precision": 0.08764581729802114
        },
        {
          "label": "ODE",
          "test_positive": 4,
          "auroc": 0.8222891566265061,
          "average_precision": 0.136489898989899
        },
        {
          "label": "ODP",
          "test_positive": 4,
          "auroc": 0.45331325301204817,
          "average_precision": 0.10264698509731622
        },
        {
          "label": "ON ",
          "test_positive": 1,
          "auroc": 0.6272189349112426,
          "average_precision": 0.015625
        },
        {
          "label": "PRH",
          "test_positive": 4,
          "auroc": 0.7123493975903614,
          "average_precision": 0.07523488562091503
        },
        {
          "label": "RD",
          "test_positive": 2,
          "auroc": 0.7857142857142857,
          "average_precision": 0.5135135135135135
        },
        {
          "label": "RTR",
          "test_positive": 1,
          "auroc": 0.047337278106508895,
          "average_precision": 0.006172839506172839
        },
        {
          "label": "RP",
          "test_positive": 1,
          "auroc": 0.7869822485207101,
          "average_precision": 0.02702702702702703
        },
        {
          "label": "RPEC",
          "test_positive": 1,
          "auroc": 1.0,
          "average_precision": 1.0
        },
        {
          "label": "RS",
          "test_positive": 1,
          "auroc": 0.7810650887573964,
          "average_precision": 0.02631578947368421
        },
        {
          "label": "RT",
          "test_positive": 8,
          "auroc": 0.7283950617283951,
          "average_precision": 0.32296374993067495
        },
        {
          "label": "SOFE",
          "test_positive": 1,
          "auroc": 0.035502958579881616,
          "average_precision": 0.006097560975609756
        },
        {
          "label": "ST",
          "test_positive": 1,
          "auroc": 0.11834319526627224,
          "average_precision": 0.006666666666666667
        },
        {
          "label": "TD",
          "test_positive": 4,
          "auroc": 0.6566265060240963,
          "average_precision": 0.07718404080219834
        },
        {
          "label": "TSLN",
          "test_positive": 8,
          "auroc": 0.9567901234567902,
          "average_precision": 0.5575358422939068
        },
        {
          "label": "TV",
          "test_positive": 6,
          "auroc": 0.8658536585365855,
          "average_precision": 0.27972135530275066
        },
        {
          "label": "VS",
          "test_positive": 2,
          "auroc": 0.31547619047619047,
          "average_precision": 0.01309931506849315
        },
        {
          "label": "HTN",
          "test_positive": 2,
          "auroc": 0.9970238095238095,
          "average_precision": 0.8333333333333333
        },
        {
          "label": "IIH",
          "test_positive": 1,
          "auroc": 1.0,
          "average_precision": 1.0
        }
      ]
    },
    "region_mean": {
      "n_labels": 45,
      "mean_auroc": 0.7666607612250276,
      "mean_average_precision": 0.3772107569148991,
      "per_label": [
        {
          "label": "WNL",
          "test_positive": 52,
          "auroc": 0.9991851368970013,
          "average_precision": 0.9983130904183537
        },
        {
          "label": "AH",
          "test_positive": 1,
          "auroc": 1.0,
          "average_precision": 1.0
        },
        {
          "label": "AION",
          "test_positive": 1,
          "auroc": 0.6272189349112426,
          "average_precision": 0.015625
        },
        {
          "label": "ARMD",
          "test_positive": 2,
          "auroc": 0.9226190476190477,
          "average_precision": 0.5357142857142857
        },
        {
          "label": "BRVO",
          "test_positive": 5,
          "auroc": 0.953939393939394,
          "average_precision": 0.4525974025974026
        },
        {
          "label": "CB",
          "test_positive": 1,
          "auroc": 0.9881656804733728,
          "average_precision": 0.3333333333333333
        },
        {
          "label": "CF",
          "test_positive": 1,
          "auroc": 0.053254437869822535,
          "average_precision": 0.006211180124223602
        },
        {
          "label": "CME",
          "test_positive": 7,
          "auroc": 0.9474145486415425,
          "average_precision": 0.5053595527279737
        },
        {
          "label": "CNV",
          "test_positive": 1,
          "auroc": 1.0,
          "average_precision": 1.0
        },
        {
          "label": "CRS",
          "test_positive": 9,
          "auroc": 0.5452035886818496,
          "average_precision": 0.09948570224571929
        },
        {
          "label": "CRVO",
          "test_positive": 2,
          "auroc": 0.8720238095238095,
          "average_precision": 0.5222222222222223
        },
        {
          "label": "CSR",
          "test_positive": 3,
          "auroc": 0.998003992015968,
          "average_precision": 0.9166666666666665
        },
        {
          "label": "CWS",
          "test_positive": 6,
          "auroc": 0.7489837398373984,
          "average_precision": 0.4323964672978472
        },
        {
          "label": "DN",
          "test_positive": 1,
          "auroc": 1.0,
          "average_precision": 1.0
        },
        {
          "label": "DR",
          "test_positive": 14,
          "auroc": 0.9986263736263736,
          "average_precision": 0.9846415489272632
        },
        {
          "label": "EDN",
          "test_positive": 17,
          "auroc": 0.9058054594386774,
          "average_precision": 0.5434669718620362
        },
        {
          "label": "ERM",
          "test_positive": 1,
          "auroc": 0.5207100591715976,
          "average_precision": 0.012195121951219513
        },
        {
          "label": "HPED",
          "test_positive": 1,
          "auroc": 0.6568047337278107,
          "average_precision": 0.01694915254237288
        },
        {
          "label": "HR",
          "test_positive": 16,
          "auroc": 0.7228084415584416,
          "average_precision": 0.30702274030263527
        },
        {
          "label": "LS",
          "test_positive": 2,
          "auroc": 1.0,
          "average_precision": 1.0
        },
        {
          "label": "MCA",
          "test_positive": 2,
          "auroc": 0.6994047619047619,
          "average_precision": 0.05620723362658847
        },
        {
          "label": "ME",
          "test_positive": 2,
          "auroc": 0.8839285714285714,
          "average_precision": 0.1923076923076923
        },
        {
          "label": "MH",
          "test_positive": 7,
          "auroc": 0.677475898334794,
          "average_precision": 0.11777469879572375
        },
        {
          "label": "MHL",
          "test_positive": 1,
          "auroc": 0.1597633136094675,
          "average_precision": 0.006993006993006993
        },
        {
          "label": "MS",
          "test_positive": 7,
          "auroc": 0.7326906222611744,
          "average_precision": 0.20970723451009532
        },
        {
          "label": "MYA",
          "test_positive": 5,
          "auroc": 0.9030303030303031,
          "average_precision": 0.8117647058823529
        },
        {
          "label": "ODC",
          "test_positive": 7,
          "auroc": 0.838737949167397,
          "average_precision": 0.1341895243497074
        },
        {
          "label": "ODE",
          "test_positive": 4,
          "auroc": 0.8418674698795181,
          "average_precision": 0.09564393939393939
        },
        {
          "label": "ODP",
          "test_positive": 4,
          "auroc": 0.7409638554216867,
          "average_precision": 0.09276710684273709
        },
        {
          "label": "ON ",
          "test_positive": 1,
          "auroc": 1.0,
          "average_precision": 1.0
        },
        {
          "label": "PRH",
          "test_positive": 4,
          "auroc": 0.3930722891566265,
          "average_precision": 0.02558057794180412
        },
        {
          "label": "RD",
          "test_positive": 2,
          "auroc": 0.9970238095238095,
          "average_precision": 0.8333333333333333
        },
        {
          "label": "RTR",
          "test_positive": 1,
          "auroc": 0.9171597633136095,
          "average_precision": 0.06666666666666667
        },
        {
          "label": "RP",
          "test_positive": 1,
          "auroc": 0.11834319526627224,
          "average_precision": 0.006666666666666667
        },
        {
          "label": "RPEC",
          "test_positive": 1,
          "auroc": 0.9763313609467456,
          "average_precision": 0.2
        },
        {
          "label": "RS",
          "test_positive": 1,
          "auroc": 0.5739644970414202,
          "average_precision": 0.0136986301369863
        },
        {
          "label": "RT",
          "test_positive": 8,
          "auroc": 0.8024691358024691,
          "average_precision": 0.1634280496467773
        },
        {
          "label": "SOFE",
          "test_positive": 1,
          "auroc": 0.9230769230769231,
          "average_precision": 0.07142857142857142
        },
        {
          "label": "ST",
          "test_positive": 1,
          "auroc": 0.46153846153846156,
          "average_precision": 0.010869565217391304
        },
        {
          "label": "TD",
          "test_positive": 4,
          "auroc": 0.45783132530120485,
          "average_precision": 0.029505494505494508
        },
        {
          "label": "TSLN",
          "test_positive": 8,
          "auroc": 0.8302469135802469,
          "average_precision": 0.5345250814000814
        },
        {
          "label": "TV",
          "test_positive": 6,
          "auroc": 0.8302845528455285,
          "average_precision": 0.32885699734439233
        },
        {
          "label": "VS",
          "test_positive": 2,
          "auroc": 0.30654761904761907,
          "average_precision": 0.01259106746911625
        },
        {
          "label": "HTN",
          "test_positive": 2,
          "auroc": 0.9732142857142857,
          "average_precision": 0.2777777777777778
        },
        {
          "label": "IIH",
          "test_positive": 1,
          "auroc": 1.0,
          "average_precision": 1.0
        }
      ]
    }
  },
  "notes": [
    "RFMiD2 is ordinary color fundus data and is not paired UWF/45-degree data.",
    "Test labels are not used for training; only Training+Validation labels train probes.",
    "The regional model averages frozen 3x3 RetinaRadar embeddings before fitting per-label probes."
  ]
}
```
