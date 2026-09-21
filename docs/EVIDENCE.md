# Evidence index

The repository uses the following hierarchy: grouped outer evaluation provides generalization evidence; fixed single-split five-seed runs provide reliability evidence; validation-only runs provide mechanism evidence; recent-baseline extensions are post-hoc evidence; and external experiments are repository-only external/boundary evidence.

## Current v10.6 paper mapping

| Current v10.6 item | Evidence class | Repository source |
|---|---|---|
| Table I | Frozen grouped outer evaluation | `results/outer/` |
| Table II | Validation-only matched-budget allocation ablation | `results/ablation/mechanism_ablation_validation*` |
| Table III | Validation-only D/E component ablation | `results/ablation/qdiffcl_final_component_ablation*` |
| Table IV | Validation-only critical-ratio sensitivity | `results/ablation/paper_ratio_sensitivity*` |
| Table V | Representative efficiency benchmark | `results/efficiency/` |
| Sec. IV-D | DCBR calibration analysis | `results/outer/paper_final_outer_raw.csv`, `results/outer/paper_final_outer_manifest.json` |

DCBR is an optional training-time validation calibration extension with zero additional inference parameters, not a core contribution.

## Repository-only evidence

| Evidence | Repository source and scope |
|---|---|
| Single-split five-seed reliability | `results/reliability/`; reliability evidence, not a separate v10.6 paper table |
| Paderborn external validation | `results/paderborn/`; external/boundary evidence not included in the v10.6 manuscript text |
| Historical Table S1 post-hoc extension | `supplementary/Table_S1.md`, `results/posthoc_baselines/`; full results retained, not included in the v10.6 manuscript text |
| Data-regime analysis | `results/reliability/data_regime/` |
| Criticality R-v2 | `results/reliability/criticality_r_v2/`; diagnostic only, not a controller |
| fixed-FAR analysis | `results/reliability/fixed_far/` |
| Early-fault trajectory | `results/reliability/fault_trajectory/` |
| Missingness and other development evidence | Retained under `results/reliability/` and the associated historical reports |

The lineage of each migrated file is recorded in [`MIGRATION.md`](MIGRATION.md).
