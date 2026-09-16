# Q-DiffCL R-v2 Correctness Audit

Status: **QDIFFCL_R_V2_CONTROLLER_NOT_SUPPORTED**
Scientific route: **R_DIAGNOSTIC_ONLY_ROUTE**

## Correctness result

R-v1 measured sensitivity of saved D/E maps to small Gaussian numerical perturbations. That is not a grouped estimator bootstrap, because no independent TRAIN unit was resampled and D/E were not re-estimated. R-v1 and its `QDIFFCL_R_FEASIBILITY_NO_GO` artifacts remain untouched.

R-v2 reconstructs the exact fraction-local TRAIN windows and frequency scaler, forms one coupled record per independent unit (`instance_id` for 3W, `run_uid` for TEP), resamples those records with replacement within normal/fault-class strata, and recomputes frozen D, E and `C=0.5D+0.5E`. A fault Run's normal/fault/early contributions remain coupled and duplicate draws retain multiplicity. No Gaussian-map bootstrap is used.

- Reference parity: 15/15 PASS (D/E/C allclose at rtol=1e-6, atol=1e-8; top-30% mask equal)
- Real grouped bootstrap: YES, 64 repeats/cell, seed 22042
- Test leakage: NO
- TEP10: `E_IDENTIFIABILITY_HOLD`; no complete D+E R was computed
- D+E parity with frozen FINAL: YES

## Group counts and R-v2

| dataset | fraction | outer | independent | normal | fault | early | R_v2 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 3W | f100 | 31001 | 248 | 234 | 14 | 14 | 0.726536 |
| 3W | f100 | 31002 | 440 | 411 | 29 | 29 | 0.724777 |
| 3W | f100 | 31003 | 601 | 576 | 25 | 25 | 0.707969 |
| 3W | f025 | 31001 | 68 | 58 | 10 | 10 | 0.672608 |
| 3W | f025 | 31002 | 115 | 103 | 12 | 12 | 0.716171 |
| 3W | f025 | 31003 | 156 | 146 | 10 | 10 | 0.826927 |
| 3W | f010 | 31001 | 29 | 23 | 6 | 6 | 0.736216 |
| 3W | f010 | 31002 | 48 | 41 | 7 | 7 | 0.654361 |
| 3W | f010 | 31003 | 65 | 58 | 7 | 7 | 0.777070 |
| TEP | f100 | 32001 | 248 | 151 | 120 | 120 | 0.936882 |
| TEP | f100 | 32002 | 248 | 154 | 120 | 120 | 0.939740 |
| TEP | f100 | 32003 | 248 | 151 | 120 | 120 | 0.933420 |
| TEP | f025 | 32001 | 62 | 31 | 40 | 40 | 0.883245 |
| TEP | f025 | 32002 | 62 | 31 | 40 | 40 | 0.884459 |
| TEP | f025 | 32003 | 62 | 29 | 40 | 40 | 0.865043 |

- 3W-f100: min/mean/max = 0.707969/0.719761/0.726536
- 3W-f025: min/mean/max = 0.672608/0.738568/0.826927
- 3W-f010: min/mean/max = 0.654361/0.722549/0.777070
- TEP-f100: min/mean/max = 0.933420/0.936681/0.939740
- TEP-f025: min/mean/max = 0.865043/0.877582/0.884459

These are within-regime reliability estimates. They are distinct from cross-regime invariance; the latter compares maps after changing the amount of TRAIN data.

## Validation safety target

Primary target: `max_rho mean(validation Macro-F1) - mean(validation Macro-F1 at rho=1)` using the frozen rho-selection seeds. Range: 0.00000000 to 0.11541730. The former arbitrary `10000*F1 + 100*AUPRC - FAR - 0.01*rho` scalar regret is not used. Exact lexicographic rho* is retained only as `rho_star_exact`; AUPRC regret and FAR change are descriptive secondary fields.

## Association

- 3W: Spearman=0.406838, 90% bootstrap interval [-0.415619, 0.969779]
- TEP: Spearman=-0.600000, 90% bootstrap interval [-1.000000, -0.090909]
- pooled (equal dataset weight): -0.096581, interval [-0.616901, 0.439435], P(association<0)=0.636

The bootstrap is dataset-stratified and resamples outer IDs with replacement while retaining repeated draws and all regime rows belonging to each draw. Controller and diagnostic claims follow the frozen Gate B thresholds; no R threshold, R weight, rho grid, or new controller was searched.

## Scientific interpretation

D+E remains the frozen WHERE mechanism. DCBR remains the validation-calibrated HOW MUCH mechanism. R-v2 is interpreted according to **R_DIAGNOSTIC_ONLY_ROUTE** and does not enter the forward path. Paderborn remains untouched; its next gate is the canonical frequency-grid gate with D-only and no pseudo-E.
