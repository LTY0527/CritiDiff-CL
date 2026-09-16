# Paderborn External Validation v2 Report

Final status: `PADERBORN_D_ONLY_EXTERNAL_NO_SUPPORT`

Evidence status: `QDIFFCL_EVIDENCE_MATRIX_20260910_CONSOLIDATED`

## Scope and correctness

This external experiment evaluates only the transferable D component and its
soft frequency allocation. Paderborn has no valid onset or early/established
stage labels, so E was not constructed. DCBR and an R-based controller were not
used.

- Primary data: 15 bearings, 1200/1200 readable measurements
- Canonical grid: sample-index resampling, 64000 Hz, 4 s, 256000 samples
- Protocol: five bearing-grouped folds; 9/3/3 train/validation/test bearings
- Formal matrix: 3 seeds x 5 folds x 3 methods = 45/45 cells
- Shared TCN, Hard SupCon, original batching, and frozen linear probe
- Normalization and D/frequency statistics: training bearings only
- Test access: after representation/probe training only
- Result/model artifact SHA256 validation: 45/45 PASS
- Maximum Uniform/D-only spectral budget error: `1.862645e-09`
- Pseudo-E: NO

## Formal results

The primary aggregation is the mean of 15 seed-fold cell metrics, preserving the
paired design.

| Method | Measurement Macro-F1 | Measurement balanced accuracy | Bearing Macro-F1 | Bearing accuracy |
|---|---:|---:|---:|---:|
| NO_AUG | 0.512904 ± 0.140807 | 0.586111 ± 0.139012 | 0.451852 ± 0.158346 | 0.555556 ± 0.162650 |
| UNIFORM_DIFFUSION | 0.530822 ± 0.148288 | 0.601389 ± 0.140274 | 0.474074 ± 0.146786 | 0.577778 ± 0.152579 |
| QDIFFCL_D_ONLY_EXTERNAL_COMPONENT | 0.527816 ± 0.140260 | 0.595000 ± 0.136060 | 0.451852 ± 0.158346 | 0.555556 ± 0.162650 |

Paired D-only minus Uniform results:

| Metric | Mean delta | 95% bootstrap interval | P(delta > 0) |
|---|---:|---:|---:|
| Measurement Macro-F1 | -0.003006 | [-0.049063, 0.053797] | 0.418 |
| Measurement balanced accuracy | -0.006389 | [-0.051118, 0.041667] | 0.369 |
| Bearing Macro-F1 | -0.022222 | [-0.100000, 0.077778] | 0.294 |
| Bearing accuracy | -0.022222 | [-0.088889, 0.044444] | 0.182 |

The preregistered support rule is not met. The mean primary and bearing deltas
are both negative, and both intervals cross zero.

As an additional descriptive analysis, a grouped bootstrap resampled the 15
independent `bearing_id` values and retained all three seed predictions per
draw. D-only minus Uniform bearing OOF Macro-F1 was `-0.026025`, with 95%
interval `[-0.092041, 0.039246]`; bearing accuracy was `-0.022222`, with
interval `[-0.088889, 0.044444]`. This agrees with, but does not replace, the
preregistered seed-fold analysis.

## Aggregated OOF error structure

Across all three OOF seed replications, the D-only measurement confusion matrix
(rows=true, columns=predicted) is:

```text
[[1069,  99,  32],
 [ 180, 664, 356],
 [  60, 731, 409]]
```

| Class | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| Healthy | 0.816654 | 0.890833 | 0.852132 | 1200 |
| Real outer-ring | 0.444444 | 0.553333 | 0.492947 | 1200 |
| Real inner-ring | 0.513174 | 0.340833 | 0.409614 | 1200 |

The dominant error is real inner-ring being predicted as real outer-ring. This
is consistent with the bearing dataset's difficult damage-location separation
and must not be reframed as early-fault behavior.

D-only measurement Macro-F1 by operating condition (pooled OOF predictions):

| Condition | Macro-F1 | Balanced accuracy |
|---|---:|---:|
| N09_M07_F10 | 0.651223 | 0.670000 |
| N15_M01_F10 | 0.572196 | 0.581111 |
| N15_M07_F04 | 0.552661 | 0.561111 |
| N15_M07_F10 | 0.559015 | 0.567778 |

## D reliability diagnostic

Leave-one-training-bearing-out D reliability averaged across the five folds:

- Spearman: `0.913304`
- Top-30% Jaccard: `0.741370`

D is therefore reasonably stable inside each frozen training regime, but that
stability does not predict an advantage over matched-budget Uniform diffusion.
Reliability remains diagnostic only and does not route rho.

## Paper implication

Paderborn does not provide external support for a universal claim that D-guided
frequency allocation outperforms matched-budget Uniform diffusion. It is valid
negative/boundary evidence for transfer across datasets with different fault
semantics. Existing 3W/TEP claims remain dataset-specific; D+E and DCBR are not
modified by this external result.
