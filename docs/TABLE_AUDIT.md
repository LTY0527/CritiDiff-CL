# Frozen table audit

This audit was performed before the new repository was published. It compared the paper draft tables against the frozen Markdown/CSV sources and then verified each copied source file by Git blob hash. No metric was recomputed.

| Paper item | Frozen files checked | Result |
|---|---|---|
| Table I | `results/outer/paper_final_outer_{raw,summary,bootstrap,groupwise}.csv`, manifest, protocol audit | Exact source copies; all 3W/TEP rows agree with the draft table. |
| Table II | `results/reliability/qdiffcl_final_5seed_*`, `external_baseline_*`, `dcbr_extension_ablation.csv` | Exact source copies; single-split boundary retained. |
| Table III | `results/ablation/mechanism_ablation_validation.csv` and paired CSV | Exact source copies; matched-budget values retained. |
| Table IV | `results/ablation/qdiffcl_final_component_ablation.csv` | Exact source copy; D-only, E-only, and D+E values retained. |
| Table V | `results/paderborn/paderborn_external_v2_*` | Exact source copies; negative D-only result retained. |
| Table VI | `results/ablation/paper_ratio_sensitivity.csv` and Markdown summary | Exact source copies; TEP ratio 0.30 remains the local low point. |
| Table VII | `results/efficiency/paper_efficiency.csv` and Markdown summary | Exact source copies; training, augmentation, inference, and parameter values retained. |
| rho routing | outer raw CSV and manifest | 3W routes `0.00/0.50/0.25`; TEP routes `0.50/0.25/0.75`. |
| Table S1 | source and generated Markdown table rows | 50/50 Markdown table lines identical. |

The final copy audit verified 223 files against their selected source Git blobs with zero mismatches. Generated and explicitly path-adapted repository files were excluded from the blob comparison and are identified as such in `MIGRATION.md`.

Preserved boundary observations include:

- 3W outer Macro-F1: FreRA `0.3334`; FINAL_QDIFFCL `0.3216`.
- 3W post-hoc Macro-F1: TF-C `0.3392`, SoftCLT `0.3408`, and AutoTCL `0.3387`, each above the FINAL_QDIFFCL point estimate `0.3216`.
- Outer DCBR minus FINAL_QDIFFCL confidence intervals cross zero on both datasets.
- Paderborn measurement Macro-F1: D-only `0.5278`; matched-budget Uniform `0.5308`.
- TEP critical-ratio Macro-F1: `0.9020` at 0.20, `0.8861` at 0.30, and `0.9039` at 0.40.

## Paired-CI consistency audit

The authoritative source for the preregistered outer-protocol paired confidence intervals is `results/outer/paper_final_outer_bootstrap.csv`. Its frozen 2,000-repeat WELL/Run bootstrap outputs are:

| Comparison | Authoritative outer CI | Post-hoc Table S1 CI |
|---|---:|---:|
| 3W, DCBR vs FINAL_QDIFFCL | `[-0.0290, +0.0118]` | `[-0.0301, +0.0112]` |
| TEP, DCBR vs FINAL_QDIFFCL | `[-0.0013, +0.0020]` | `[-0.0014, +0.0021]` |
| 3W, FreRA vs FINAL_QDIFFCL | `[-0.0514, +0.0415]` | `[-0.0505, +0.0379]` |

The point estimates, paired cells, positive/non-worse counts, and worst-cell deltas agree. The interval endpoints differ because the post-hoc extension reran the same 2,000-repeat group-aware bootstrap in `results/posthoc_baselines/posthoc_recent_baselines_5seed_bootstrap.csv`. Both pipelines use base seed `90317`, but derive the per-comparison random seed from the method's index in their respective comparison lists. Adding TF-C, SoftCLT, TS2Vec, and AutoTCL before the frozen reference methods changes that index and therefore changes the finite bootstrap draws. This is a second bootstrap run, not a change in predictions or observed effects.

Recommendation: use the intervals from `results/outer/paper_final_outer_bootstrap.csv` for Sec. IV-D and every claim about the preregistered outer protocol. Retain the post-hoc intervals in Table S1 as provenance-faithful outputs of the separately labeled post-hoc summarization; if a single interval set is required across the paper and supplement, the paper author should decide whether Table S1 will quote the outer intervals instead. No result file was modified by this audit.
