# Exp48：连续视野比例、位置与形状鲁棒性

在4×4区域模型上，比较连续中心视野比例、55%视野的位置变化和等面积圆形视野。

```json
{
  "grid": "4x4",
  "n_seeds": 5,
  "rows": [
    {
      "seed": 0,
      "scenario": "rect_center_0.35",
      "shape": "rect",
      "linear_fraction": 0.35,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7262012732944111,
      "epochs": 62,
      "accuracy": 0.8179487179487179,
      "macro_f1": 0.8193825337930752,
      "severity_mae": 0.19487179487179487,
      "underestimation_rate": 0.08974358974358974
    },
    {
      "seed": 0,
      "scenario": "rect_center_0.45",
      "shape": "rect",
      "linear_fraction": 0.45,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7262012732944111,
      "epochs": 62,
      "accuracy": 0.8179487179487179,
      "macro_f1": 0.8193825337930752,
      "severity_mae": 0.19487179487179487,
      "underestimation_rate": 0.08974358974358974
    },
    {
      "seed": 0,
      "scenario": "rect_center_0.55",
      "shape": "rect",
      "linear_fraction": 0.55,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7262012732944111,
      "epochs": 62,
      "accuracy": 0.8179487179487179,
      "macro_f1": 0.8193825337930752,
      "severity_mae": 0.19487179487179487,
      "underestimation_rate": 0.08974358974358974
    },
    {
      "seed": 0,
      "scenario": "rect_center_0.65",
      "shape": "rect",
      "linear_fraction": 0.65,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7262012732944111,
      "epochs": 62,
      "accuracy": 0.8179487179487179,
      "macro_f1": 0.8193825337930752,
      "severity_mae": 0.19487179487179487,
      "underestimation_rate": 0.08974358974358974
    },
    {
      "seed": 0,
      "scenario": "rect_center_0.75",
      "shape": "rect",
      "linear_fraction": 0.75,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15
      ],
      "visible_region_fraction": 1.0,
      "best_val_macro_f1": 0.7262012732944111,
      "epochs": 62,
      "accuracy": 0.8205128205128205,
      "macro_f1": 0.822100250869583,
      "severity_mae": 0.19743589743589743,
      "underestimation_rate": 0.08205128205128205
    },
    {
      "seed": 0,
      "scenario": "rect_center_0.90",
      "shape": "rect",
      "linear_fraction": 0.9,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15
      ],
      "visible_region_fraction": 1.0,
      "best_val_macro_f1": 0.7262012732944111,
      "epochs": 62,
      "accuracy": 0.8205128205128205,
      "macro_f1": 0.822100250869583,
      "severity_mae": 0.19743589743589743,
      "underestimation_rate": 0.08205128205128205
    },
    {
      "seed": 0,
      "scenario": "rect_center_0.55",
      "shape": "rect",
      "linear_fraction": 0.55,
      "dx": 0,
      "dy": 0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7262012732944111,
      "epochs": 62,
      "accuracy": 0.8179487179487179,
      "macro_f1": 0.8193825337930752,
      "severity_mae": 0.19487179487179487,
      "underestimation_rate": 0.08974358974358974
    },
    {
      "seed": 0,
      "scenario": "rect_left_0.55",
      "shape": "rect",
      "linear_fraction": 0.55,
      "dx": -1,
      "dy": 0,
      "visible_regions": [
        4,
        5,
        8,
        9
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7262012732944111,
      "epochs": 62,
      "accuracy": 0.8205128205128205,
      "macro_f1": 0.8216409607809596,
      "severity_mae": 0.20256410256410257,
      "underestimation_rate": 0.07692307692307693
    },
    {
      "seed": 0,
      "scenario": "rect_right_0.55",
      "shape": "rect",
      "linear_fraction": 0.55,
      "dx": 1,
      "dy": 0,
      "visible_regions": [
        6,
        7,
        10,
        11
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7262012732944111,
      "epochs": 62,
      "accuracy": 0.7743589743589744,
      "macro_f1": 0.7757065563868134,
      "severity_mae": 0.2358974358974359,
      "underestimation_rate": 0.12307692307692308
    },
    {
      "seed": 0,
      "scenario": "rect_up_0.55",
      "shape": "rect",
      "linear_fraction": 0.55,
      "dx": 0,
      "dy": -1,
      "visible_regions": [
        1,
        2,
        5,
        6
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7262012732944111,
      "epochs": 62,
      "accuracy": 0.782051282051282,
      "macro_f1": 0.7835390140973653,
      "severity_mae": 0.2282051282051282,
      "underestimation_rate": 0.12051282051282051
    },
    {
      "seed": 0,
      "scenario": "rect_down_0.55",
      "shape": "rect",
      "linear_fraction": 0.55,
      "dx": 0,
      "dy": 1,
      "visible_regions": [
        9,
        10,
        13,
        14
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7262012732944111,
      "epochs": 62,
      "accuracy": 0.8025641025641026,
      "macro_f1": 0.8042671544631075,
      "severity_mae": 0.2153846153846154,
      "underestimation_rate": 0.08974358974358974
    },
    {
      "seed": 0,
      "scenario": "circle_center_0.35",
      "shape": "circle",
      "linear_fraction": 0.35,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7262012732944111,
      "epochs": 62,
      "accuracy": 0.8179487179487179,
      "macro_f1": 0.8193825337930752,
      "severity_mae": 0.19487179487179487,
      "underestimation_rate": 0.08974358974358974
    },
    {
      "seed": 0,
      "scenario": "circle_center_0.45",
      "shape": "circle",
      "linear_fraction": 0.45,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7262012732944111,
      "epochs": 62,
      "accuracy": 0.8179487179487179,
      "macro_f1": 0.8193825337930752,
      "severity_mae": 0.19487179487179487,
      "underestimation_rate": 0.08974358974358974
    },
    {
      "seed": 0,
      "scenario": "circle_center_0.55",
      "shape": "circle",
      "linear_fraction": 0.55,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7262012732944111,
      "epochs": 62,
      "accuracy": 0.8179487179487179,
      "macro_f1": 0.8193825337930752,
      "severity_mae": 0.19487179487179487,
      "underestimation_rate": 0.08974358974358974
    },
    {
      "seed": 0,
      "scenario": "circle_center_0.65",
      "shape": "circle",
      "linear_fraction": 0.65,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7262012732944111,
      "epochs": 62,
      "accuracy": 0.8179487179487179,
      "macro_f1": 0.8193825337930752,
      "severity_mae": 0.19487179487179487,
      "underestimation_rate": 0.08974358974358974
    },
    {
      "seed": 0,
      "scenario": "circle_center_0.75",
      "shape": "circle",
      "linear_fraction": 0.75,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        1,
        2,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        13,
        14
      ],
      "visible_region_fraction": 0.75,
      "best_val_macro_f1": 0.7262012732944111,
      "epochs": 62,
      "accuracy": 0.8205128205128205,
      "macro_f1": 0.8218662542524234,
      "severity_mae": 0.19743589743589743,
      "underestimation_rate": 0.08461538461538462
    },
    {
      "seed": 0,
      "scenario": "circle_center_0.90",
      "shape": "circle",
      "linear_fraction": 0.9,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        1,
        2,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        13,
        14
      ],
      "visible_region_fraction": 0.75,
      "best_val_macro_f1": 0.7262012732944111,
      "epochs": 62,
      "accuracy": 0.8205128205128205,
      "macro_f1": 0.8218662542524234,
      "severity_mae": 0.19743589743589743,
      "underestimation_rate": 0.08461538461538462
    },
    {
      "seed": 1,
      "scenario": "rect_center_0.35",
      "shape": "rect",
      "linear_fraction": 0.35,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7407550297022,
      "epochs": 70,
      "accuracy": 0.8333333333333334,
      "macro_f1": 0.8351912621092903,
      "severity_mae": 0.18205128205128204,
      "underestimation_rate": 0.08205128205128205
    },
    {
      "seed": 1,
      "scenario": "rect_center_0.45",
      "shape": "rect",
      "linear_fraction": 0.45,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7407550297022,
      "epochs": 70,
      "accuracy": 0.8333333333333334,
      "macro_f1": 0.8351912621092903,
      "severity_mae": 0.18205128205128204,
      "underestimation_rate": 0.08205128205128205
    },
    {
      "seed": 1,
      "scenario": "rect_center_0.55",
      "shape": "rect",
      "linear_fraction": 0.55,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7407550297022,
      "epochs": 70,
      "accuracy": 0.8333333333333334,
      "macro_f1": 0.8351912621092903,
      "severity_mae": 0.18205128205128204,
      "underestimation_rate": 0.08205128205128205
    },
    {
      "seed": 1,
      "scenario": "rect_center_0.65",
      "shape": "rect",
      "linear_fraction": 0.65,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7407550297022,
      "epochs": 70,
      "accuracy": 0.8333333333333334,
      "macro_f1": 0.8351912621092903,
      "severity_mae": 0.18205128205128204,
      "underestimation_rate": 0.08205128205128205
    },
    {
      "seed": 1,
      "scenario": "rect_center_0.75",
      "shape": "rect",
      "linear_fraction": 0.75,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15
      ],
      "visible_region_fraction": 1.0,
      "best_val_macro_f1": 0.7407550297022,
      "epochs": 70,
      "accuracy": 0.8333333333333334,
      "macro_f1": 0.8352082325956233,
      "severity_mae": 0.18205128205128204,
      "underestimation_rate": 0.08205128205128205
    },
    {
      "seed": 1,
      "scenario": "rect_center_0.90",
      "shape": "rect",
      "linear_fraction": 0.9,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15
      ],
      "visible_region_fraction": 1.0,
      "best_val_macro_f1": 0.7407550297022,
      "epochs": 70,
      "accuracy": 0.8333333333333334,
      "macro_f1": 0.8352082325956233,
      "severity_mae": 0.18205128205128204,
      "underestimation_rate": 0.08205128205128205
    },
    {
      "seed": 1,
      "scenario": "rect_center_0.55",
      "shape": "rect",
      "linear_fraction": 0.55,
      "dx": 0,
      "dy": 0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7407550297022,
      "epochs": 70,
      "accuracy": 0.8333333333333334,
      "macro_f1": 0.8351912621092903,
      "severity_mae": 0.18205128205128204,
      "underestimation_rate": 0.08205128205128205
    },
    {
      "seed": 1,
      "scenario": "rect_left_0.55",
      "shape": "rect",
      "linear_fraction": 0.55,
      "dx": -1,
      "dy": 0,
      "visible_regions": [
        4,
        5,
        8,
        9
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7407550297022,
      "epochs": 70,
      "accuracy": 0.8076923076923077,
      "macro_f1": 0.8085108475443049,
      "severity_mae": 0.2128205128205128,
      "underestimation_rate": 0.09743589743589744
    },
    {
      "seed": 1,
      "scenario": "rect_right_0.55",
      "shape": "rect",
      "linear_fraction": 0.55,
      "dx": 1,
      "dy": 0,
      "visible_regions": [
        6,
        7,
        10,
        11
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7407550297022,
      "epochs": 70,
      "accuracy": 0.7717948717948718,
      "macro_f1": 0.7742338078331055,
      "severity_mae": 0.23846153846153847,
      "underestimation_rate": 0.1282051282051282
    },
    {
      "seed": 1,
      "scenario": "rect_up_0.55",
      "shape": "rect",
      "linear_fraction": 0.55,
      "dx": 0,
      "dy": -1,
      "visible_regions": [
        1,
        2,
        5,
        6
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7407550297022,
      "epochs": 70,
      "accuracy": 0.8076923076923077,
      "macro_f1": 0.8098086359646937,
      "severity_mae": 0.2076923076923077,
      "underestimation_rate": 0.09230769230769231
    },
    {
      "seed": 1,
      "scenario": "rect_down_0.55",
      "shape": "rect",
      "linear_fraction": 0.55,
      "dx": 0,
      "dy": 1,
      "visible_regions": [
        9,
        10,
        13,
        14
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7407550297022,
      "epochs": 70,
      "accuracy": 0.8,
      "macro_f1": 0.801857318925736,
      "severity_mae": 0.2205128205128205,
      "underestimation_rate": 0.09487179487179487
    },
    {
      "seed": 1,
      "scenario": "circle_center_0.35",
      "shape": "circle",
      "linear_fraction": 0.35,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7407550297022,
      "epochs": 70,
      "accuracy": 0.8333333333333334,
      "macro_f1": 0.8351912621092903,
      "severity_mae": 0.18205128205128204,
      "underestimation_rate": 0.08205128205128205
    },
    {
      "seed": 1,
      "scenario": "circle_center_0.45",
      "shape": "circle",
      "linear_fraction": 0.45,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7407550297022,
      "epochs": 70,
      "accuracy": 0.8333333333333334,
      "macro_f1": 0.8351912621092903,
      "severity_mae": 0.18205128205128204,
      "underestimation_rate": 0.08205128205128205
    },
    {
      "seed": 1,
      "scenario": "circle_center_0.55",
      "shape": "circle",
      "linear_fraction": 0.55,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7407550297022,
      "epochs": 70,
      "accuracy": 0.8333333333333334,
      "macro_f1": 0.8351912621092903,
      "severity_mae": 0.18205128205128204,
      "underestimation_rate": 0.08205128205128205
    },
    {
      "seed": 1,
      "scenario": "circle_center_0.65",
      "shape": "circle",
      "linear_fraction": 0.65,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7407550297022,
      "epochs": 70,
      "accuracy": 0.8333333333333334,
      "macro_f1": 0.8351912621092903,
      "severity_mae": 0.18205128205128204,
      "underestimation_rate": 0.08205128205128205
    },
    {
      "seed": 1,
      "scenario": "circle_center_0.75",
      "shape": "circle",
      "linear_fraction": 0.75,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        1,
        2,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        13,
        14
      ],
      "visible_region_fraction": 0.75,
      "best_val_macro_f1": 0.7407550297022,
      "epochs": 70,
      "accuracy": 0.8333333333333334,
      "macro_f1": 0.8352594569512058,
      "severity_mae": 0.1794871794871795,
      "underestimation_rate": 0.08461538461538462
    },
    {
      "seed": 1,
      "scenario": "circle_center_0.90",
      "shape": "circle",
      "linear_fraction": 0.9,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        1,
        2,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        13,
        14
      ],
      "visible_region_fraction": 0.75,
      "best_val_macro_f1": 0.7407550297022,
      "epochs": 70,
      "accuracy": 0.8333333333333334,
      "macro_f1": 0.8352594569512058,
      "severity_mae": 0.1794871794871795,
      "underestimation_rate": 0.08461538461538462
    },
    {
      "seed": 2,
      "scenario": "rect_center_0.35",
      "shape": "rect",
      "linear_fraction": 0.35,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7330430567236706,
      "epochs": 46,
      "accuracy": 0.8512820512820513,
      "macro_f1": 0.8530861945707469,
      "severity_mae": 0.1564102564102564,
      "underestimation_rate": 0.07948717948717948
    },
    {
      "seed": 2,
      "scenario": "rect_center_0.45",
      "shape": "rect",
      "linear_fraction": 0.45,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7330430567236706,
      "epochs": 46,
      "accuracy": 0.8512820512820513,
      "macro_f1": 0.8530861945707469,
      "severity_mae": 0.1564102564102564,
      "underestimation_rate": 0.07948717948717948
    },
    {
      "seed": 2,
      "scenario": "rect_center_0.55",
      "shape": "rect",
      "linear_fraction": 0.55,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7330430567236706,
      "epochs": 46,
      "accuracy": 0.8512820512820513,
      "macro_f1": 0.8530861945707469,
      "severity_mae": 0.1564102564102564,
      "underestimation_rate": 0.07948717948717948
    },
    {
      "seed": 2,
      "scenario": "rect_center_0.65",
      "shape": "rect",
      "linear_fraction": 0.65,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7330430567236706,
      "epochs": 46,
      "accuracy": 0.8512820512820513,
      "macro_f1": 0.8530861945707469,
      "severity_mae": 0.1564102564102564,
      "underestimation_rate": 0.07948717948717948
    },
    {
      "seed": 2,
      "scenario": "rect_center_0.75",
      "shape": "rect",
      "linear_fraction": 0.75,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15
      ],
      "visible_region_fraction": 1.0,
      "best_val_macro_f1": 0.7330430567236706,
      "epochs": 46,
      "accuracy": 0.8615384615384616,
      "macro_f1": 0.8624121853071269,
      "severity_mae": 0.15128205128205127,
      "underestimation_rate": 0.07179487179487179
    },
    {
      "seed": 2,
      "scenario": "rect_center_0.90",
      "shape": "rect",
      "linear_fraction": 0.9,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15
      ],
      "visible_region_fraction": 1.0,
      "best_val_macro_f1": 0.7330430567236706,
      "epochs": 46,
      "accuracy": 0.8615384615384616,
      "macro_f1": 0.8624121853071269,
      "severity_mae": 0.15128205128205127,
      "underestimation_rate": 0.07179487179487179
    },
    {
      "seed": 2,
      "scenario": "rect_center_0.55",
      "shape": "rect",
      "linear_fraction": 0.55,
      "dx": 0,
      "dy": 0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7330430567236706,
      "epochs": 46,
      "accuracy": 0.8512820512820513,
      "macro_f1": 0.8530861945707469,
      "severity_mae": 0.1564102564102564,
      "underestimation_rate": 0.07948717948717948
    },
    {
      "seed": 2,
      "scenario": "rect_left_0.55",
      "shape": "rect",
      "linear_fraction": 0.55,
      "dx": -1,
      "dy": 0,
      "visible_regions": [
        4,
        5,
        8,
        9
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7330430567236706,
      "epochs": 46,
      "accuracy": 0.8153846153846154,
      "macro_f1": 0.8163418766044493,
      "severity_mae": 0.20256410256410257,
      "underestimation_rate": 0.07435897435897436
    },
    {
      "seed": 2,
      "scenario": "rect_right_0.55",
      "shape": "rect",
      "linear_fraction": 0.55,
      "dx": 1,
      "dy": 0,
      "visible_regions": [
        6,
        7,
        10,
        11
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7330430567236706,
      "epochs": 46,
      "accuracy": 0.7948717948717948,
      "macro_f1": 0.7967844045374387,
      "severity_mae": 0.21025641025641026,
      "underestimation_rate": 0.11794871794871795
    },
    {
      "seed": 2,
      "scenario": "rect_up_0.55",
      "shape": "rect",
      "linear_fraction": 0.55,
      "dx": 0,
      "dy": -1,
      "visible_regions": [
        1,
        2,
        5,
        6
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7330430567236706,
      "epochs": 46,
      "accuracy": 0.8,
      "macro_f1": 0.8022782373734568,
      "severity_mae": 0.2128205128205128,
      "underestimation_rate": 0.09487179487179487
    },
    {
      "seed": 2,
      "scenario": "rect_down_0.55",
      "shape": "rect",
      "linear_fraction": 0.55,
      "dx": 0,
      "dy": 1,
      "visible_regions": [
        9,
        10,
        13,
        14
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7330430567236706,
      "epochs": 46,
      "accuracy": 0.8282051282051283,
      "macro_f1": 0.8293406326034063,
      "severity_mae": 0.18974358974358974,
      "underestimation_rate": 0.08974358974358974
    },
    {
      "seed": 2,
      "scenario": "circle_center_0.35",
      "shape": "circle",
      "linear_fraction": 0.35,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7330430567236706,
      "epochs": 46,
      "accuracy": 0.8512820512820513,
      "macro_f1": 0.8530861945707469,
      "severity_mae": 0.1564102564102564,
      "underestimation_rate": 0.07948717948717948
    },
    {
      "seed": 2,
      "scenario": "circle_center_0.45",
      "shape": "circle",
      "linear_fraction": 0.45,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7330430567236706,
      "epochs": 46,
      "accuracy": 0.8512820512820513,
      "macro_f1": 0.8530861945707469,
      "severity_mae": 0.1564102564102564,
      "underestimation_rate": 0.07948717948717948
    },
    {
      "seed": 2,
      "scenario": "circle_center_0.55",
      "shape": "circle",
      "linear_fraction": 0.55,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7330430567236706,
      "epochs": 46,
      "accuracy": 0.8512820512820513,
      "macro_f1": 0.8530861945707469,
      "severity_mae": 0.1564102564102564,
      "underestimation_rate": 0.07948717948717948
    },
    {
      "seed": 2,
      "scenario": "circle_center_0.65",
      "shape": "circle",
      "linear_fraction": 0.65,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7330430567236706,
      "epochs": 46,
      "accuracy": 0.8512820512820513,
      "macro_f1": 0.8530861945707469,
      "severity_mae": 0.1564102564102564,
      "underestimation_rate": 0.07948717948717948
    },
    {
      "seed": 2,
      "scenario": "circle_center_0.75",
      "shape": "circle",
      "linear_fraction": 0.75,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        1,
        2,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        13,
        14
      ],
      "visible_region_fraction": 0.75,
      "best_val_macro_f1": 0.7330430567236706,
      "epochs": 46,
      "accuracy": 0.8641025641025641,
      "macro_f1": 0.8650022492127757,
      "severity_mae": 0.14615384615384616,
      "underestimation_rate": 0.07692307692307693
    },
    {
      "seed": 2,
      "scenario": "circle_center_0.90",
      "shape": "circle",
      "linear_fraction": 0.9,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        1,
        2,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        13,
        14
      ],
      "visible_region_fraction": 0.75,
      "best_val_macro_f1": 0.7330430567236706,
      "epochs": 46,
      "accuracy": 0.8641025641025641,
      "macro_f1": 0.8650022492127757,
      "severity_mae": 0.14615384615384616,
      "underestimation_rate": 0.07692307692307693
    },
    {
      "seed": 3,
      "scenario": "rect_center_0.35",
      "shape": "rect",
      "linear_fraction": 0.35,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7260609873680748,
      "epochs": 51,
      "accuracy": 0.8435897435897436,
      "macro_f1": 0.845651714849323,
      "severity_mae": 0.1641025641025641,
      "underestimation_rate": 0.08461538461538462
    },
    {
      "seed": 3,
      "scenario": "rect_center_0.45",
      "shape": "rect",
      "linear_fraction": 0.45,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7260609873680748,
      "epochs": 51,
      "accuracy": 0.8435897435897436,
      "macro_f1": 0.845651714849323,
      "severity_mae": 0.1641025641025641,
      "underestimation_rate": 0.08461538461538462
    },
    {
      "seed": 3,
      "scenario": "rect_center_0.55",
      "shape": "rect",
      "linear_fraction": 0.55,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7260609873680748,
      "epochs": 51,
      "accuracy": 0.8435897435897436,
      "macro_f1": 0.845651714849323,
      "severity_mae": 0.1641025641025641,
      "underestimation_rate": 0.08461538461538462
    },
    {
      "seed": 3,
      "scenario": "rect_center_0.65",
      "shape": "rect",
      "linear_fraction": 0.65,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7260609873680748,
      "epochs": 51,
      "accuracy": 0.8435897435897436,
      "macro_f1": 0.845651714849323,
      "severity_mae": 0.1641025641025641,
      "underestimation_rate": 0.08461538461538462
    },
    {
      "seed": 3,
      "scenario": "rect_center_0.75",
      "shape": "rect",
      "linear_fraction": 0.75,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15
      ],
      "visible_region_fraction": 1.0,
      "best_val_macro_f1": 0.7260609873680748,
      "epochs": 51,
      "accuracy": 0.8487179487179487,
      "macro_f1": 0.8497622895443332,
      "severity_mae": 0.16153846153846155,
      "underestimation_rate": 0.07435897435897436
    },
    {
      "seed": 3,
      "scenario": "rect_center_0.90",
      "shape": "rect",
      "linear_fraction": 0.9,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15
      ],
      "visible_region_fraction": 1.0,
      "best_val_macro_f1": 0.7260609873680748,
      "epochs": 51,
      "accuracy": 0.8487179487179487,
      "macro_f1": 0.8497622895443332,
      "severity_mae": 0.16153846153846155,
      "underestimation_rate": 0.07435897435897436
    },
    {
      "seed": 3,
      "scenario": "rect_center_0.55",
      "shape": "rect",
      "linear_fraction": 0.55,
      "dx": 0,
      "dy": 0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7260609873680748,
      "epochs": 51,
      "accuracy": 0.8435897435897436,
      "macro_f1": 0.845651714849323,
      "severity_mae": 0.1641025641025641,
      "underestimation_rate": 0.08461538461538462
    },
    {
      "seed": 3,
      "scenario": "rect_left_0.55",
      "shape": "rect",
      "linear_fraction": 0.55,
      "dx": -1,
      "dy": 0,
      "visible_regions": [
        4,
        5,
        8,
        9
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7260609873680748,
      "epochs": 51,
      "accuracy": 0.8076923076923077,
      "macro_f1": 0.8092121745010191,
      "severity_mae": 0.2128205128205128,
      "underestimation_rate": 0.08461538461538462
    },
    {
      "seed": 3,
      "scenario": "rect_right_0.55",
      "shape": "rect",
      "linear_fraction": 0.55,
      "dx": 1,
      "dy": 0,
      "visible_regions": [
        6,
        7,
        10,
        11
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7260609873680748,
      "epochs": 51,
      "accuracy": 0.7846153846153846,
      "macro_f1": 0.7861419619798832,
      "severity_mae": 0.2230769230769231,
      "underestimation_rate": 0.13076923076923078
    },
    {
      "seed": 3,
      "scenario": "rect_up_0.55",
      "shape": "rect",
      "linear_fraction": 0.55,
      "dx": 0,
      "dy": -1,
      "visible_regions": [
        1,
        2,
        5,
        6
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7260609873680748,
      "epochs": 51,
      "accuracy": 0.8128205128205128,
      "macro_f1": 0.8137403848785963,
      "severity_mae": 0.19487179487179487,
      "underestimation_rate": 0.10512820512820513
    },
    {
      "seed": 3,
      "scenario": "rect_down_0.55",
      "shape": "rect",
      "linear_fraction": 0.55,
      "dx": 0,
      "dy": 1,
      "visible_regions": [
        9,
        10,
        13,
        14
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7260609873680748,
      "epochs": 51,
      "accuracy": 0.8025641025641026,
      "macro_f1": 0.804084481014628,
      "severity_mae": 0.21025641025641026,
      "underestimation_rate": 0.09743589743589744
    },
    {
      "seed": 3,
      "scenario": "circle_center_0.35",
      "shape": "circle",
      "linear_fraction": 0.35,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7260609873680748,
      "epochs": 51,
      "accuracy": 0.8435897435897436,
      "macro_f1": 0.845651714849323,
      "severity_mae": 0.1641025641025641,
      "underestimation_rate": 0.08461538461538462
    },
    {
      "seed": 3,
      "scenario": "circle_center_0.45",
      "shape": "circle",
      "linear_fraction": 0.45,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7260609873680748,
      "epochs": 51,
      "accuracy": 0.8435897435897436,
      "macro_f1": 0.845651714849323,
      "severity_mae": 0.1641025641025641,
      "underestimation_rate": 0.08461538461538462
    },
    {
      "seed": 3,
      "scenario": "circle_center_0.55",
      "shape": "circle",
      "linear_fraction": 0.55,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7260609873680748,
      "epochs": 51,
      "accuracy": 0.8435897435897436,
      "macro_f1": 0.845651714849323,
      "severity_mae": 0.1641025641025641,
      "underestimation_rate": 0.08461538461538462
    },
    {
      "seed": 3,
      "scenario": "circle_center_0.65",
      "shape": "circle",
      "linear_fraction": 0.65,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7260609873680748,
      "epochs": 51,
      "accuracy": 0.8435897435897436,
      "macro_f1": 0.845651714849323,
      "severity_mae": 0.1641025641025641,
      "underestimation_rate": 0.08461538461538462
    },
    {
      "seed": 3,
      "scenario": "circle_center_0.75",
      "shape": "circle",
      "linear_fraction": 0.75,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        1,
        2,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        13,
        14
      ],
      "visible_region_fraction": 0.75,
      "best_val_macro_f1": 0.7260609873680748,
      "epochs": 51,
      "accuracy": 0.8487179487179487,
      "macro_f1": 0.8497649323755351,
      "severity_mae": 0.16153846153846155,
      "underestimation_rate": 0.07692307692307693
    },
    {
      "seed": 3,
      "scenario": "circle_center_0.90",
      "shape": "circle",
      "linear_fraction": 0.9,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        1,
        2,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        13,
        14
      ],
      "visible_region_fraction": 0.75,
      "best_val_macro_f1": 0.7260609873680748,
      "epochs": 51,
      "accuracy": 0.8487179487179487,
      "macro_f1": 0.8497649323755351,
      "severity_mae": 0.16153846153846155,
      "underestimation_rate": 0.07692307692307693
    },
    {
      "seed": 4,
      "scenario": "rect_center_0.35",
      "shape": "rect",
      "linear_fraction": 0.35,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7121396478876013,
      "epochs": 65,
      "accuracy": 0.8282051282051283,
      "macro_f1": 0.8307177918583403,
      "severity_mae": 0.1794871794871795,
      "underestimation_rate": 0.08461538461538462
    },
    {
      "seed": 4,
      "scenario": "rect_center_0.45",
      "shape": "rect",
      "linear_fraction": 0.45,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7121396478876013,
      "epochs": 65,
      "accuracy": 0.8282051282051283,
      "macro_f1": 0.8307177918583403,
      "severity_mae": 0.1794871794871795,
      "underestimation_rate": 0.08461538461538462
    },
    {
      "seed": 4,
      "scenario": "rect_center_0.55",
      "shape": "rect",
      "linear_fraction": 0.55,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7121396478876013,
      "epochs": 65,
      "accuracy": 0.8282051282051283,
      "macro_f1": 0.8307177918583403,
      "severity_mae": 0.1794871794871795,
      "underestimation_rate": 0.08461538461538462
    },
    {
      "seed": 4,
      "scenario": "rect_center_0.65",
      "shape": "rect",
      "linear_fraction": 0.65,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7121396478876013,
      "epochs": 65,
      "accuracy": 0.8282051282051283,
      "macro_f1": 0.8307177918583403,
      "severity_mae": 0.1794871794871795,
      "underestimation_rate": 0.08461538461538462
    },
    {
      "seed": 4,
      "scenario": "rect_center_0.75",
      "shape": "rect",
      "linear_fraction": 0.75,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15
      ],
      "visible_region_fraction": 1.0,
      "best_val_macro_f1": 0.7121396478876013,
      "epochs": 65,
      "accuracy": 0.8333333333333334,
      "macro_f1": 0.8354733858327735,
      "severity_mae": 0.17692307692307693,
      "underestimation_rate": 0.07435897435897436
    },
    {
      "seed": 4,
      "scenario": "rect_center_0.90",
      "shape": "rect",
      "linear_fraction": 0.9,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15
      ],
      "visible_region_fraction": 1.0,
      "best_val_macro_f1": 0.7121396478876013,
      "epochs": 65,
      "accuracy": 0.8333333333333334,
      "macro_f1": 0.8354733858327735,
      "severity_mae": 0.17692307692307693,
      "underestimation_rate": 0.07435897435897436
    },
    {
      "seed": 4,
      "scenario": "rect_center_0.55",
      "shape": "rect",
      "linear_fraction": 0.55,
      "dx": 0,
      "dy": 0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7121396478876013,
      "epochs": 65,
      "accuracy": 0.8282051282051283,
      "macro_f1": 0.8307177918583403,
      "severity_mae": 0.1794871794871795,
      "underestimation_rate": 0.08461538461538462
    },
    {
      "seed": 4,
      "scenario": "rect_left_0.55",
      "shape": "rect",
      "linear_fraction": 0.55,
      "dx": -1,
      "dy": 0,
      "visible_regions": [
        4,
        5,
        8,
        9
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7121396478876013,
      "epochs": 65,
      "accuracy": 0.8051282051282052,
      "macro_f1": 0.8063523017799515,
      "severity_mae": 0.2205128205128205,
      "underestimation_rate": 0.09230769230769231
    },
    {
      "seed": 4,
      "scenario": "rect_right_0.55",
      "shape": "rect",
      "linear_fraction": 0.55,
      "dx": 1,
      "dy": 0,
      "visible_regions": [
        6,
        7,
        10,
        11
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7121396478876013,
      "epochs": 65,
      "accuracy": 0.782051282051282,
      "macro_f1": 0.7844324807792167,
      "severity_mae": 0.22564102564102564,
      "underestimation_rate": 0.11282051282051282
    },
    {
      "seed": 4,
      "scenario": "rect_up_0.55",
      "shape": "rect",
      "linear_fraction": 0.55,
      "dx": 0,
      "dy": -1,
      "visible_regions": [
        1,
        2,
        5,
        6
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7121396478876013,
      "epochs": 65,
      "accuracy": 0.7846153846153846,
      "macro_f1": 0.7865486039001791,
      "severity_mae": 0.2282051282051282,
      "underestimation_rate": 0.11025641025641025
    },
    {
      "seed": 4,
      "scenario": "rect_down_0.55",
      "shape": "rect",
      "linear_fraction": 0.55,
      "dx": 0,
      "dy": 1,
      "visible_regions": [
        9,
        10,
        13,
        14
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7121396478876013,
      "epochs": 65,
      "accuracy": 0.8153846153846154,
      "macro_f1": 0.8177077999658645,
      "severity_mae": 0.19487179487179487,
      "underestimation_rate": 0.08974358974358974
    },
    {
      "seed": 4,
      "scenario": "circle_center_0.35",
      "shape": "circle",
      "linear_fraction": 0.35,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7121396478876013,
      "epochs": 65,
      "accuracy": 0.8282051282051283,
      "macro_f1": 0.8307177918583403,
      "severity_mae": 0.1794871794871795,
      "underestimation_rate": 0.08461538461538462
    },
    {
      "seed": 4,
      "scenario": "circle_center_0.45",
      "shape": "circle",
      "linear_fraction": 0.45,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7121396478876013,
      "epochs": 65,
      "accuracy": 0.8282051282051283,
      "macro_f1": 0.8307177918583403,
      "severity_mae": 0.1794871794871795,
      "underestimation_rate": 0.08461538461538462
    },
    {
      "seed": 4,
      "scenario": "circle_center_0.55",
      "shape": "circle",
      "linear_fraction": 0.55,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7121396478876013,
      "epochs": 65,
      "accuracy": 0.8282051282051283,
      "macro_f1": 0.8307177918583403,
      "severity_mae": 0.1794871794871795,
      "underestimation_rate": 0.08461538461538462
    },
    {
      "seed": 4,
      "scenario": "circle_center_0.65",
      "shape": "circle",
      "linear_fraction": 0.65,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        5,
        6,
        9,
        10
      ],
      "visible_region_fraction": 0.25,
      "best_val_macro_f1": 0.7121396478876013,
      "epochs": 65,
      "accuracy": 0.8282051282051283,
      "macro_f1": 0.8307177918583403,
      "severity_mae": 0.1794871794871795,
      "underestimation_rate": 0.08461538461538462
    },
    {
      "seed": 4,
      "scenario": "circle_center_0.75",
      "shape": "circle",
      "linear_fraction": 0.75,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        1,
        2,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        13,
        14
      ],
      "visible_region_fraction": 0.75,
      "best_val_macro_f1": 0.7121396478876013,
      "epochs": 65,
      "accuracy": 0.8384615384615385,
      "macro_f1": 0.8402961564640538,
      "severity_mae": 0.1717948717948718,
      "underestimation_rate": 0.07692307692307693
    },
    {
      "seed": 4,
      "scenario": "circle_center_0.90",
      "shape": "circle",
      "linear_fraction": 0.9,
      "dx": 0.0,
      "dy": 0.0,
      "visible_regions": [
        1,
        2,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        13,
        14
      ],
      "visible_region_fraction": 0.75,
      "best_val_macro_f1": 0.7121396478876013,
      "epochs": 65,
      "accuracy": 0.8384615384615385,
      "macro_f1": 0.8402961564640538,
      "severity_mae": 0.1717948717948718,
      "underestimation_rate": 0.07692307692307693
    }
  ],
  "aggregate": {
    "rect_center_0.35": {
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
    "rect_center_0.45": {
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
    "rect_center_0.55": {
      "accuracy": {
        "mean": 0.8348717948717947,
        "std": 0.012279169228080653
      },
      "macro_f1": {
        "mean": 0.8368058994361551,
        "std": 0.012351718170198546
      },
      "severity_mae": {
        "mean": 0.1753846153846154,
        "std": 0.014363043786393165
      },
      "underestimation_rate": {
        "mean": 0.08410256410256411,
        "std": 0.0035856712757953916
      }
    },
    "rect_center_0.65": {
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
    "rect_center_0.75": {
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
    "rect_center_0.90": {
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
    "rect_left_0.55": {
      "accuracy": {
        "mean": 0.8112820512820512,
        "std": 0.006435846357954405
      },
      "macro_f1": {
        "mean": 0.8124116322421369,
        "std": 0.006379566262118102
      },
      "severity_mae": {
        "mean": 0.21025641025641026,
        "std": 0.007692307692307688
      },
      "underestimation_rate": {
        "mean": 0.08512820512820514,
        "std": 0.009830917698810674
      }
    },
    "rect_right_0.55": {
      "accuracy": {
        "mean": 0.7815384615384615,
        "std": 0.009137707528823282
      },
      "macro_f1": {
        "mean": 0.7834598423032915,
        "std": 0.009095560796946369
      },
      "severity_mae": {
        "mean": 0.22666666666666666,
        "std": 0.011264555198199383
      },
      "underestimation_rate": {
        "mean": 0.12256410256410258,
        "std": 0.0073424723401417195
      }
    },
    "rect_up_0.55": {
      "accuracy": {
        "mean": 0.7974358974358975,
        "std": 0.013688561861578612
      },
      "macro_f1": {
        "mean": 0.7991829752428582,
        "std": 0.013590109899130322
      },
      "severity_mae": {
        "mean": 0.21435897435897436,
        "std": 0.01423019171847344
      },
      "underestimation_rate": {
        "mean": 0.10461538461538462,
        "std": 0.011524207720125247
      }
    },
    "rect_down_0.55": {
      "accuracy": {
        "mean": 0.8097435897435897,
        "std": 0.011944425332156016
      },
      "macro_f1": {
        "mean": 0.8114514773945485,
        "std": 0.01180146658865583
      },
      "severity_mae": {
        "mean": 0.2061538461538462,
        "std": 0.013274029851840808
      },
      "underestimation_rate": {
        "mean": 0.09230769230769231,
        "std": 0.0036261886214694738
      }
    },
    "circle_center_0.35": {
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
    "circle_center_0.45": {
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
    "circle_center_0.55": {
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
    "circle_center_0.65": {
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
    "circle_center_0.75": {
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
    },
    "circle_center_0.90": {
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
  },
  "notes": [
    "Visibility is determined by 4x4 regional-cell centers within a rectangle or area-matched circular aperture.",
    "This is a geometric visibility proxy over frozen full-image regional embeddings, not a real camera acquisition.",
    "All models are trained with 30% random region masking."
  ]
}
```
