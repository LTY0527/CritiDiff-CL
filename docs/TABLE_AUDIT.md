# v10.6 paper table audit

This audit maps manuscript v10.6 to the frozen repository sources. No metric was recomputed and no result file was modified.

| Paper item | Frozen files checked | Result |
|---|---|---|
| Table I | `results/outer/paper_final_outer_{raw,summary,bootstrap,groupwise}.csv`, manifest, protocol audit | Selected 3W/TEP baseline and CritiDiff-CL rows agree with v10.6. |
| Table II | `results/ablation/mechanism_ablation_validation.csv` and paired CSV | Uniform, Hard, Soft, and unmatched-Soft matched-budget values retained. |
| Table III | `results/ablation/qdiffcl_final_component_ablation.csv` | Uniform, D-only, E-only, and D+E values retained. |
| Table IV | `results/ablation/paper_ratio_sensitivity.csv` and Markdown report | 3W ratios `0.20/0.30/0.40` and all reported values retained. |
| Table V | `results/efficiency/paper_efficiency.csv` and Markdown report | Training, augmentation, inference, and parameter values retained. |
| Sec. IV-D | Outer raw CSV and manifest | 3W routes `0.00/0.50/0.25`; TEP routes `0.50/0.25/0.75`. |

The final copy audit verified 223 files against their selected source Git blobs with zero mismatches. Generated and explicitly path-adapted repository files were excluded from that blob comparison and remain identified in `MIGRATION.md`.

## Repository-only / additional audit

The following completed experiments are retained for reproducibility but are not included in the v10.6 manuscript text:

- Single-split five-seed reliability files under `results/reliability/`.
- Paderborn external validation under `results/paderborn/`. The negative D-only result is preserved: measurement Macro-F1 is `0.5278` for D-only and `0.5308` for matched-budget Uniform.
- Recent post-hoc baselines under `results/posthoc_baselines/` and `supplementary/Table_S1.md`. The complete five-seed tables are unchanged. On 3W, TF-C `0.3392`, SoftCLT `0.3408`, and AutoTCL `0.3387` have point estimates above FINAL_QDIFFCL `0.3216`.
- Limited-data, missingness, criticality R-v2, fixed-FAR, trajectory, and other development evidence.
- TEP critical-ratio results remain preserved as additional evidence: Macro-F1 `0.9020` at 0.20, `0.8861` at 0.30, and `0.9039` at 0.40.

Outer DCBR minus FINAL_QDIFFCL confidence intervals include zero on both datasets.

## Paired-CI consistency audit

The authoritative source for the frozen outer-protocol paired confidence intervals is `results/outer/paper_final_outer_bootstrap.csv`. Its 2,000-repeat WELL/Run bootstrap outputs are:

| Comparison | Authoritative outer CI | Repository post-hoc rerun CI |
|---|---:|---:|
| 3W, DCBR vs FINAL_QDIFFCL | `[-0.0290, +0.0118]` | `[-0.0301, +0.0112]` |
| TEP, DCBR vs FINAL_QDIFFCL | `[-0.0013, +0.0020]` | `[-0.0014, +0.0021]` |
| 3W, FreRA vs FINAL_QDIFFCL | `[-0.0514, +0.0415]` | `[-0.0505, +0.0379]` |

The point estimates, paired cells, positive/non-worse counts, and worst-cell deltas agree. The interval endpoints differ because the post-hoc extension reran the same 2,000-repeat group-aware bootstrap in `results/posthoc_baselines/posthoc_recent_baselines_5seed_bootstrap.csv`. Both pipelines use base seed `90317`, but derive the per-comparison random seed from the method's index in their respective comparison lists. Adding TF-C, SoftCLT, TS2Vec, and AutoTCL before the frozen reference methods changes that index and therefore changes the finite bootstrap draws. This is a second bootstrap run, not a change in predictions or observed effects.

Use the intervals from `results/outer/paper_final_outer_bootstrap.csv` for v10.6 statements about the grouped outer protocol. The post-hoc intervals remain provenance-faithful repository-only outputs. No result file was modified by this audit.
