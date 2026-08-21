# Exp18：最终候选模型 bootstrap 与成对比较

对 Exp17 的测试集风险分数进行 2000 次 bootstrap，报告 AUROC、AP、Brier、ECE及最终候选模型与各消融模型的成对 AUROC 差异。

完整结果见 `results.json`。

最终候选 AUROC=0.757，95% CI [0.690, 0.824]；相对67维基线的成对差异为 0.064，95% CI [0.028, 0.099]。
