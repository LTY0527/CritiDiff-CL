# CritiDiff-CL v10.6 Evidence Chain Summary

## Current method hierarchy

1. Fault-semantic frequency criticality from `D` and, when identifiable, `E`.
2. Continuous frequency-selective DDPM forward perturbation with no denoiser training or reverse sampling.
3. Matched spectral perturbation budget in the standardized log-spectral domain.
4. Optional DCBR training-time validation calibration extension with zero additional inference parameters.

The frozen implementation remains `0.5D + 0.5E`, critical ratio `0.30`, selective timesteps `1/5`, continuous soft channel-frequency allocation, TCN, supervised contrastive learning, original batching, and a frozen Linear Probe. DCBR remains a validation-calibrated domain-level scalar; SVR remains `NO_GO_SVR` and is excluded.

## Evidence used in v10.6

- Grouped outer evaluation: the frozen 3W/TEP matrix is complete with WELL/Run grouping and split-first aggregation.
- Matched-budget mechanism: the 3W validation-only Uniform/Hard/Soft/unmatched ablation supports continuous soft allocation under a controlled total budget.
- Semantic components: `D` is the primary discriminative contributor and `E` is complementary when genuine early-stage information is identifiable.
- Critical-ratio sensitivity: v10.6 reports the 3W local sensitivity result and does not claim a universal optimum.
- Practicality: dual-dataset training time, peak GPU memory, parameters, and repeated augmentation/inference benchmarks are complete. Standalone FreRA augmentation timing remains unavailable.
- DCBR: reported separately as an optional validation calibration extension, not a core contribution.

The principal frozen outer values are:

- 3W CritiDiff-CL: Macro-F1 `0.3216`, AUPRC `0.7873`, Early Recall `0.9114`, across-split SD `0.0324`.
- 3W FreRA minus CritiDiff-CL: paired delta `+0.0118`, 95% CI `[-0.0514, +0.0415]`.
- TEP CritiDiff-CL: Macro-F1 `0.9483`, Early Recall `0.8838`.
- DCBR outer extension: 3W paired delta `-0.0012`, 95% CI `[-0.0290, +0.0118]`; TEP paired delta `+0.0003`, 95% CI `[-0.0013, +0.0020]`.

## Repository-only evidence retained in full

- TEP mechanism evidence is inconsistent with the 3W soft-allocation result; the former universal mechanism claim is not made.
- The 2×2 diffusion/contrastive interaction is positive on 3W (`+0.1483`, 3/3 positive) and inverse on TEP (`-0.0206`, 0/3 positive).
- TEP critical ratio `0.30` is a local trough; the frozen parameter is not reopened.
- Existing TEP checkpoints provide 40-run onset-aligned trajectory evidence without representative-case cherry-picking.
- AutoDA-Timeseries remains method-native only; no fairly reproducible industrial DiCL implementation was found.
- Limited-data effects are dataset- and regime-dependent; broader missingness evidence remains partial.
- R-v2 is diagnostic reliability evidence, not a controller.
- Paderborn D-only does not outperform matched-budget Uniform diffusion: paired Macro-F1 delta `-0.0030`, 95% CI `[-0.0491, 0.0538]`.
- AutoTCL, SoftCLT, TF-C, and TS2Vec five-seed results remain complete post-hoc evidence.

These repository-only observations, including negative and boundary results, remain available under `results/` and the historical experiment reports but are not part of the v10.6 manuscript text.

## Reporting boundary

Do not claim universal performance superiority, universal selective superiority, universal cross-WELL or cross-domain gains, universal DCBR improvement, or critical ratio `0.30` as a universal optimum.

See `docs/EVIDENCE.md`, `docs/TABLE_AUDIT.md`, `docs/paper_final_protocol.md`, `docs/paper_final_freeze.md`, and the frozen files under `results/`.
