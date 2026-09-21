# CritiDiff-CL v10.6 Paper Claims

## Core method claims

1. **Fault-Semantic Frequency Criticality.** Fault discriminativeness `D` is estimated over independent Run/WELL units. Early-stage sensitivity `E` is added only when genuine early-stage information is identifiable, producing channel-frequency criticality.
2. **Continuous Frequency-Selective Forward Diffusion.** Continuous criticality is mapped to per-frequency DDPM forward-perturbation strength so that highly critical frequencies receive weaker perturbations. No denoiser is trained and no reverse sampling is performed.
3. **Matched Spectral Perturbation Budget.** Selective and uniform diffusion are matched in total perturbation variance in the standardized log-spectral domain, separating frequency allocation from total perturbation magnitude.

## Calibration extension

DCBR is validation-routed and training-time only. It selects `rho` using validation data and adds zero inference parameters. It is not a core contribution in manuscript v10.6.

## Main-paper evidence

### 3W grouped outer

- CritiDiff-CL AUPRC: `0.7873`.
- CritiDiff-CL Early Recall: `0.9114`.
- Across-split Macro-F1 SD: `0.0324`.
- These are the best values in their respective columns in the main experimental comparison.

### 3W Macro-F1 boundary

- FreRA Macro-F1: `0.3334`.
- CritiDiff-CL Macro-F1: `0.3216`.
- Paired delta, FreRA minus CritiDiff-CL: `+0.0118`.
- Paired 95% CI: `[-0.0514, +0.0415]`; the interval includes zero.

### TEP

- CritiDiff-CL Macro-F1: `0.9483`.
- Main-table Macro-F1 range: `0.9458–0.9496`.
- CritiDiff-CL Early Recall: `0.8838`, tied for the highest value in the main experimental comparison.

### Matched-budget mechanism

- Uniform diffusion Macro-F1: `0.4258`.
- Hard selective diffusion Macro-F1: `0.4462`.
- Soft selective diffusion Macro-F1: `0.4870`; its paired change versus Uniform is positive for `3/3` seeds.
- Soft selective diffusion without budget matching Macro-F1: `0.4358`.

### D/E ablation

| Variant | Macro-F1 | AUPRC | FAR |
|---|---:|---:|---:|
| Uniform | 0.4542 | 0.5020 | 0.4288 |
| D-only | 0.5128 | 0.5638 | 0.3749 |
| E-only | 0.4628 | 0.5081 | 0.3841 |
| D+E | 0.5188 | 0.5635 | 0.3555 |

### DCBR

DCBR is reported only as a calibration extension. In the fixed single-split TEP five-seed audit, Macro-F1 changes from `0.8903` to `0.9024`, with positive deltas for `5/5` seeds. Grouped outer routing selects `rho` values `0.00/0.50/0.25` on 3W and `0.50/0.25/0.75` on TEP. Its paired outer confidence intervals include zero on both datasets: 3W `[-0.0290, +0.0118]` and TEP `[-0.0013, +0.0020]`.

## Repository-only evidence

Paderborn external validation, recent post-hoc baselines, limited-data experiments, missingness analysis, criticality reliability, early-fault trajectory, fixed-FAR, and other development evidence remain preserved but do not enter the v10.6 manuscript text.

## Do not claim

Do not claim universal superiority, universal selective superiority, universal cross-domain transfer, universal DCBR improvement, `critical_ratio=0.30` as a universal optimum, or that CritiDiff-CL exceeds every baseline on every metric.
