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
