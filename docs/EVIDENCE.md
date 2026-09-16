# Evidence index

The repository separates generalization evidence from development evidence. The grouped outer protocol is the only cross-method generalization evidence. Single-split five-seed runs are reliability audits. Validation-only experiments support mechanism and ablation claims. The recent-baseline extension is post-hoc and was not preregistered.

| Paper item | Evidence class | Repository source |
|---|---|---|
| Table I | Frozen grouped outer evaluation | `results/outer/` |
| Table II | Single-split five-seed reliability audit | `results/reliability/` |
| Table III | Validation-only matched-budget allocation ablation | `results/ablation/mechanism_ablation_validation*` |
| Table IV | Validation-only fault-semantic component ablation | `results/ablation/qdiffcl_final_component_ablation*` |
| Table V | Paderborn external D-only component validation | `results/paderborn/` |
| Table VI | Validation-only critical-ratio sensitivity | `results/ablation/paper_ratio_sensitivity*` |
| Table VII | Representative efficiency benchmark | `results/efficiency/` |
| Table S1 | Post-hoc recent-baseline extension | `supplementary/Table_S1.md`, `results/posthoc_baselines/` |
| DCBR rho routing | Inner-validation route selection within each outer split | `results/outer/paper_final_outer_raw.csv`, `paper_final_outer_manifest.json` |
| Data-Regime boundary analysis | Development/reliability evidence | `results/reliability/data_regime/` |
| Criticality R-v2 | Diagnostic reliability evidence, not a controller | `results/reliability/criticality_r_v2/` |
| fixed-FAR analysis | Failure/calibration audit | `results/reliability/fixed_far/` |
| Early-fault trajectory | Development evidence | `results/reliability/fault_trajectory/` |

The lineage of each migrated file is recorded in [`MIGRATION.md`](MIGRATION.md).
