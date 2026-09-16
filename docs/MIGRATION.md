# Migration lineage

This repository was assembled without the original Git history. Every migrated file is listed below with its selected source branch and source path. Files marked “artifact assembly” were created for the public artifact and contain no experimental measurements.

## Pre-migration safety gates

| Gate | Result |
|---|---|
| Paper-draft identifier scan | FINAL_QDIFFCL, DCBR, Data-Regime, reliability, Paderborn, D/E ablations, outer evaluation, rho routing, sensitivity, efficiency, and post-hoc baselines retained. EWIC, DRFD, DSFD, HFSC, R2, R3, RRDC, SVR, and UG-R1 do not occur as paper identifiers. |
| fixed-FAR dual-source comparison | All same-name DRFD blobs in `exp/cross-domain-validated-safety` and `origin/exp/paper-evidence-chain` are identical. The earlier `exp/domain-reliable-safe-frequency-diffusion` lacks four later audit files and differs only by those additions. |
| Local backup | Private ZIP created before migration; 17,487 entries; SHA-256 `CCC3FBDDE22736851633B48D20A3806B21E16795E151E6B55CEB28BFF135DB8B`. |
| History policy | No original `.git` history was copied. |
| Checkpoint policy | No checkpoints, raw datasets, external repository clones, or ignored output directories were copied. |

## Source-selection decisions

- Frozen outer results come from `exp/paper-final-outer`.
- Paderborn evidence comes from `exp/paderborn-external-validation-v2`, including the negative result.
- Post-hoc evidence comes from `exp/posthoc-baseline-expansion`; Table S1 copies its Markdown values verbatim.
- fixed-FAR files are attributed to `exp/cross-domain-validated-safety`. The corresponding remote evidence-chain blobs are identical; the older DRFD branch is incomplete.
- Core runtime files use the consolidated `exp/paderborn-external-validation-v2` snapshot so that final fixes are preserved. No exploratory configurations, reports, checkpoints, or result directories were migrated.

## Artifact path adaptations

- Seven frozen JSON manifests were moved from ignored `outputs/` locations into `configs/protocol_manifests/`. Their bytes and SHA-256 digests were preserved exactly.
- `configs/paper_final_outer.yaml`, `configs/paper_final_protocol.yaml`, and `configs/paper_final_freeze.yaml` only replace those old `outputs/` references with repository-relative manifest paths.
- `configs/qdiffcl_data_regime_v1.yaml` only replaces old absolute/local result references with their migrated repository-relative paths.
- `tests/test_paper_final_protocol_amendment.py` and `docs/paper_final_freeze.md` only follow the manifest relocation.
- `scripts/audit_semantic_diffusion_augmentation.py` contains the source helper `_simple_interpolate` copied verbatim from the excluded exploratory runner, allowing the public artifact to remain self-contained without migrating that runner.

## Per-file lineage

| Source branch | Source path | New repository path |
|---|---|---|
| `exp/paper-evidence-chain@848b493` | `scripts/audit_paper_final_protocol.py` | `scripts/audit_paper_final_protocol.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `scripts/amend_paper_final_protocol.py` | `scripts/amend_paper_final_protocol.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `scripts/reconcile_paderborn_sampling.py` | `scripts/reconcile_paderborn_sampling.py` |
| `artifact assembly` | `generated` | `.gitignore` |
| `artifact assembly` | `generated` | `docs/MIGRATION.md` |
| `artifact assembly` | `generated from the pre-migration verification record` | `docs/TABLE_AUDIT.md` |
| `artifact assembly` | `generated` | `README.md` |
| `exp/paper-evidence-chain@848b493` | `outputs/paper_final_protocol/dry_run_manifest.json` | `configs/protocol_manifests/dry_run_manifest.json` |
| `exp/paper-evidence-chain@848b493` | `outputs/paper_final_protocol/leakage_audit.json` | `configs/protocol_manifests/leakage_audit.json` |
| `exp/paper-evidence-chain@848b493` | `outputs/paper_final_protocol/pre_amendment_dry_run_manifest.json` | `configs/protocol_manifests/pre_amendment_dry_run_manifest.json` |
| `exp/paper-evidence-chain@848b493` | `outputs/paper_final_protocol/protocol_amendment_audit.json` | `configs/protocol_manifests/protocol_amendment_audit.json` |
| `paper-final-freeze-pre-outer-v4@02b1e52` | `outputs/paper_final_freeze/freeze_manifest.json` | `configs/protocol_manifests/freeze_manifest.json` |
| `local working tree on exp/paderborn-external-validation-v2` | `outputs/fixed_diffusion_views/views_manifest.json` (SHA-256 `1824E2CFA0B86EF71AFE2D38913134EA418D9D7DDA5BBF9E624A496FAFF88EB1`) | `configs/protocol_manifests/fixed_diffusion_views_manifest.json` |
| `local working tree on exp/paderborn-external-validation-v2` | `outputs/3w_final_primary_grouped_seed42/grouped_split_manifest.json` (SHA-256 `E44B0CA1BEE997086B3B696C6E4CC8304B1A7A8ED197EB3D22AB6F5925A940CE`) | `configs/protocol_manifests/3w_grouped_split_manifest.json` |
| `exp/paderborn-external-validation-v2@7a25b21` | `configs/3w_final_primary_grouped.yaml` | `configs/3w_final_primary_grouped.yaml` |
| `exp/paderborn-external-validation-v2@7a25b21` | `configs/3w_primary_well_split.csv` | `configs/3w_primary_well_split.csv` |
| `exp/paderborn-external-validation-v2@7a25b21` | `configs/3w_strict_split_manifest.json` | `configs/3w_strict_split_manifest.json` |
| `exp/cross-domain-validated-safety@0efdad7` | `configs/cross_domain_validated_safety.yaml` | `configs/cross_domain_validated_safety.yaml` |
| `exp/qdiffcl-data-regime@dc8d12c` | `configs/data_regime_manifests/3w_outer_31001.json` | `configs/data_regime_manifests/3w_outer_31001.json` |
| `exp/qdiffcl-data-regime@dc8d12c` | `configs/data_regime_manifests/3w_outer_31002.json` | `configs/data_regime_manifests/3w_outer_31002.json` |
| `exp/qdiffcl-data-regime@dc8d12c` | `configs/data_regime_manifests/3w_outer_31003.json` | `configs/data_regime_manifests/3w_outer_31003.json` |
| `exp/qdiffcl-data-regime@dc8d12c` | `configs/data_regime_manifests/tep_outer_32001.json` | `configs/data_regime_manifests/tep_outer_32001.json` |
| `exp/qdiffcl-data-regime@dc8d12c` | `configs/data_regime_manifests/tep_outer_32002.json` | `configs/data_regime_manifests/tep_outer_32002.json` |
| `exp/qdiffcl-data-regime@dc8d12c` | `configs/data_regime_manifests/tep_outer_32003.json` | `configs/data_regime_manifests/tep_outer_32003.json` |
| `exp/paderborn-external-validation-v2@7a25b21` | `configs/diffusion_quality_retest.yaml` | `configs/diffusion_quality_retest.yaml` |
| `exp/domain-calibrated-budget-routing@322f45a` | `configs/domain_calibrated_budget_routing_final.yaml` | `configs/domain_calibrated_budget_routing_final.yaml` |
| `exp/paderborn-external-validation-v2@7a25b21` | `configs/external_baselines.yaml` | `configs/external_baselines.yaml` |
| `exp/paderborn-external-validation-v2@7a25b21` | `configs/fixed_diffusion_views_manifest.json` | `configs/fixed_diffusion_views_manifest.json` |
| `exp/paderborn-external-validation-v2@7a25b21` | `configs/paderborn_external_v2.yaml` | `configs/paderborn_external_v2.yaml` |
| `exp/paderborn-external-validation-v2@7a25b21` | `configs/paderborn_primary_5fold.csv` | `configs/paderborn_primary_5fold.csv` |
| `exp/paderborn-external-validation-v2@7a25b21` | `configs/paderborn_sampling_policy_v2.yaml` | `configs/paderborn_sampling_policy_v2.yaml` |
| `exp/paper-evidence-chain@848b493` | `configs/paper_contrastive_ablation.yaml` | `configs/paper_contrastive_ablation.yaml` |
| `exp/paper-evidence-chain@848b493` | `configs/paper_efficiency.yaml` | `configs/paper_efficiency.yaml` |
| `exp/paper-evidence-chain@848b493` | `configs/paper_evidence_chain.yaml` | `configs/paper_evidence_chain.yaml` |
| `exp/paper-evidence-chain@848b493` | `configs/paper_fault_trajectory.yaml` | `configs/paper_fault_trajectory.yaml` |
| `exp/paderborn-external-validation-v2@7a25b21` | `configs/paper_final_freeze.yaml` | `configs/paper_final_freeze.yaml` |
| `exp/paper-final-outer@276416f` | `configs/paper_final_outer.yaml` | `configs/paper_final_outer.yaml` |
| `exp/paper-evidence-chain@848b493` | `configs/paper_final_protocol.yaml` | `configs/paper_final_protocol.yaml` |
| `exp/paper-evidence-chain@848b493` | `configs/paper_mechanism_ablation.yaml` | `configs/paper_mechanism_ablation.yaml` |
| `exp/paper-evidence-chain@848b493` | `configs/paper_ratio_sensitivity.yaml` | `configs/paper_ratio_sensitivity.yaml` |
| `exp/posthoc-baseline-expansion@ea79099` | `configs/posthoc_baseline_5seed_extension.yaml` | `configs/posthoc_baseline_5seed_extension.yaml` |
| `exp/posthoc-baseline-expansion@ea79099` | `configs/posthoc_recent_baselines.yaml` | `configs/posthoc_recent_baselines.yaml` |
| `exp/qdiffcl-data-regime@dc8d12c` | `configs/qdiffcl_data_regime_v1.yaml` | `configs/qdiffcl_data_regime_v1.yaml` |
| `exp/qdiffcl-final-reliability@3790928` | `configs/qdiffcl_final.yaml` | `configs/qdiffcl_final.yaml` |
| `exp/qdiffcl-final-reliability@3790928` | `configs/qdiffcl_final_5seed.yaml` | `configs/qdiffcl_final_5seed.yaml` |
| `exp/r1-des-weight-tuning@7d63bd5` | `configs/r1_des_ablation.yaml` | `configs/r1_des_ablation.yaml` |
| `exp/r1-des-weight-tuning@7d63bd5` | `configs/r1_des_weight_search.yaml` | `configs/r1_des_weight_search.yaml` |
| `exp/paderborn-external-validation-v2@7a25b21` | `configs/stage_frequency_diffusion_mvp.yaml` | `configs/stage_frequency_diffusion_mvp.yaml` |
| `artifact assembly` | `generated` | `docs/EVIDENCE.md` |
| `exp/paderborn-external-validation-v2@7a25b21` | `docs/PADERBORN_EXTERNAL_VALIDATION_V2_REPORT.md` | `docs/PADERBORN_EXTERNAL_VALIDATION_V2_REPORT.md` |
| `exp/paderborn-external-validation-v2@7a25b21` | `docs/PADERBORN_FREQUENCY_GRID_FREEZE.md` | `docs/PADERBORN_FREQUENCY_GRID_FREEZE.md` |
| `exp/paderborn-external-validation-v2@7a25b21` | `docs/PADERBORN_PRIMARY_PROTOCOL_FROZEN_V2.md` | `docs/PADERBORN_PRIMARY_PROTOCOL_FROZEN_V2.md` |
| `exp/paderborn-external-validation-v2@7a25b21` | `docs/PADERBORN_SAMPLING_RECONCILIATION.md` | `docs/PADERBORN_SAMPLING_RECONCILIATION.md` |
| `exp/qdiffcl-data-regime@dc8d12c` | `docs/QDIFFCL_DATA_REGIME_E_IDENTIFIABILITY_AUDIT.md` | `docs/QDIFFCL_DATA_REGIME_E_IDENTIFIABILITY_AUDIT.md` |
| `exp/qdiffcl-data-regime@dc8d12c` | `docs/QDIFFCL_DATA_REGIME_FAIRNESS_AUDIT.md` | `docs/QDIFFCL_DATA_REGIME_FAIRNESS_AUDIT.md` |
| `exp/qdiffcl-data-regime@dc8d12c` | `docs/QDIFFCL_DATA_REGIME_FRACTION_COMPARABILITY_AUDIT.md` | `docs/QDIFFCL_DATA_REGIME_FRACTION_COMPARABILITY_AUDIT.md` |
| `exp/qdiffcl-data-regime@dc8d12c` | `docs/QDIFFCL_DATA_REGIME_LINEAGE.md` | `docs/QDIFFCL_DATA_REGIME_LINEAGE.md` |
| `exp/qdiffcl-data-regime@dc8d12c` | `docs/QDIFFCL_DATA_REGIME_PROTOCOL_V1.md` | `docs/QDIFFCL_DATA_REGIME_PROTOCOL_V1.md` |
| `exp/qdiffcl-data-regime@dc8d12c` | `docs/QDIFFCL_DATA_REGIME_REPORT.md` | `docs/QDIFFCL_DATA_REGIME_REPORT.md` |
| `exp/qdiffcl-data-regime@dc8d12c` | `docs/QDIFFCL_DATA_REGIME_STATISTICS_AUDIT.md` | `docs/QDIFFCL_DATA_REGIME_STATISTICS_AUDIT.md` |
| `exp/qdiffcl-r-reliability-correctness@1bd0779` | `docs/QDIFFCL_R_V2_CORRECTNESS_AUDIT.md` | `docs/QDIFFCL_R_V2_CORRECTNESS_AUDIT.md` |
| `exp/qdiffcl-r-reliability-correctness@1bd0779` | `docs/QDIFFCL_R_V2_PAPER_IMPLICATIONS.md` | `docs/QDIFFCL_R_V2_PAPER_IMPLICATIONS.md` |
| `exp/paderborn-external-validation-v2@7a25b21` | `docs/dataset_protocol.md (consolidated evidence snapshot)` | `docs/dataset_protocol.md` |
| `exp/cross-domain-validated-safety@0efdad7` | `docs/drfd_failure_audit.md` | `docs/drfd_failure_audit.md` |
| `exp/paderborn-external-validation-v2@7a25b21` | `docs/environment.md (consolidated evidence snapshot)` | `docs/environment.md` |
| `exp/paderborn-external-validation-v2@7a25b21` | `docs/paper_evidence_chain_summary.md (consolidated evidence snapshot)` | `docs/paper_evidence_chain_summary.md` |
| `exp/paderborn-external-validation-v2@7a25b21` | `docs/paper_evidence_matrix.md (consolidated evidence snapshot)` | `docs/paper_evidence_matrix.md` |
| `exp/paderborn-external-validation-v2@7a25b21` | `docs/paper_final_claims.md (consolidated evidence snapshot)` | `docs/paper_final_claims.md` |
| `exp/paderborn-external-validation-v2@7a25b21` | `docs/paper_final_freeze.md (consolidated evidence snapshot)` | `docs/paper_final_freeze.md` |
| `exp/paderborn-external-validation-v2@7a25b21` | `docs/paper_final_outer_failure_analysis.md (consolidated evidence snapshot)` | `docs/paper_final_outer_failure_analysis.md` |
| `exp/paderborn-external-validation-v2@7a25b21` | `docs/paper_final_outer_summary.md (consolidated evidence snapshot)` | `docs/paper_final_outer_summary.md` |
| `exp/paderborn-external-validation-v2@7a25b21` | `docs/paper_final_protocol.md (consolidated evidence snapshot)` | `docs/paper_final_protocol.md` |
| `exp/paderborn-external-validation-v2@7a25b21` | `docs/paper_final_protocol_amendment.md (consolidated evidence snapshot)` | `docs/paper_final_protocol_amendment.md` |
| `exp/posthoc-baseline-expansion@ea79099` | `docs/posthoc_baseline_5seed_extension_protocol.md` | `docs/posthoc_baseline_5seed_extension_protocol.md` |
| `exp/posthoc-baseline-expansion@ea79099` | `docs/posthoc_baseline_5seed_extension_resume_audit.md` | `docs/posthoc_baseline_5seed_extension_resume_audit.md` |
| `exp/posthoc-baseline-expansion@ea79099` | `docs/posthoc_baseline_protocol.md` | `docs/posthoc_baseline_protocol.md` |
| `exp/posthoc-baseline-expansion@ea79099` | `docs/posthoc_baseline_reproducibility_audit.md` | `docs/posthoc_baseline_reproducibility_audit.md` |
| `exp/posthoc-baseline-expansion@ea79099` | `docs/posthoc_baseline_selection_lock.md` | `docs/posthoc_baseline_selection_lock.md` |
| `exp/posthoc-baseline-expansion@ea79099` | `docs/posthoc_recent_baselines_5seed.md` | `docs/posthoc_recent_baselines_5seed.md` |
| `exp/paper-evidence-chain@848b493` | `docs/paper_evidence/repository_result_inventory.md` | `docs/repository_result_inventory.md` |
| `artifact assembly` | `generated` | `pyproject.toml` |
| `exp/paper-evidence-chain@848b493` | `docs/paper_evidence/mechanism_ablation_validation.csv` | `results/ablation/mechanism_ablation_validation.csv` |
| `exp/paper-evidence-chain@848b493` | `docs/paper_evidence/mechanism_ablation_validation.md` | `results/ablation/mechanism_ablation_validation.md` |
| `exp/paper-evidence-chain@848b493` | `docs/paper_evidence/mechanism_ablation_validation_paired.csv` | `results/ablation/mechanism_ablation_validation_paired.csv` |
| `exp/paper-evidence-chain@848b493` | `analysis/results/paper_contrastive_ablation.csv` | `results/ablation/paper_contrastive_ablation.csv` |
| `exp/paper-evidence-chain@848b493` | `docs/paper_contrastive_ablation.md` | `results/ablation/paper_contrastive_ablation.md` |
| `exp/paper-evidence-chain@848b493` | `analysis/results/paper_ratio_sensitivity.csv` | `results/ablation/paper_ratio_sensitivity.csv` |
| `exp/paper-evidence-chain@848b493` | `docs/paper_ratio_sensitivity.md` | `results/ablation/paper_ratio_sensitivity.md` |
| `exp/qdiffcl-final-reliability@3790928` | `docs/qdiffcl_final_component_ablation.csv` | `results/ablation/qdiffcl_final_component_ablation.csv` |
| `exp/qdiffcl-final-reliability@3790928` | `docs/qdiffcl_final_component_ablation.md` | `results/ablation/qdiffcl_final_component_ablation.md` |
| `exp/paper-evidence-chain@848b493` | `analysis/results/paper_efficiency.csv` | `results/efficiency/paper_efficiency.csv` |
| `exp/paper-evidence-chain@848b493` | `docs/paper_efficiency.md` | `results/efficiency/paper_efficiency.md` |
| `exp/paper-final-outer@276416f` | `analysis/results/paper_final_outer_bootstrap.csv` | `results/outer/paper_final_outer_bootstrap.csv` |
| `exp/paper-final-outer@276416f` | `analysis/results/paper_final_outer_groupwise.csv` | `results/outer/paper_final_outer_groupwise.csv` |
| `exp/paper-final-outer@276416f` | `analysis/results/paper_final_outer_manifest.json` | `results/outer/paper_final_outer_manifest.json` |
| `exp/paper-final-outer@276416f` | `analysis/results/paper_final_outer_protocol_audit.json` | `results/outer/paper_final_outer_protocol_audit.json` |
| `exp/paper-final-outer@276416f` | `analysis/results/paper_final_outer_raw.csv` | `results/outer/paper_final_outer_raw.csv` |
| `exp/paper-final-outer@276416f` | `analysis/results/paper_final_outer_summary.csv` | `results/outer/paper_final_outer_summary.csv` |
| `exp/paderborn-external-validation-v2@7a25b21` | `docs/PADERBORN_EXTERNAL_VALIDATION_V2_REPORT.md` | `results/paderborn/PADERBORN_EXTERNAL_VALIDATION_V2_REPORT.md` |
| `exp/paderborn-external-validation-v2@7a25b21` | `analysis/results/paderborn_external_v2_bearing_grouped_bootstrap.csv` | `results/paderborn/paderborn_external_v2_bearing_grouped_bootstrap.csv` |
| `exp/paderborn-external-validation-v2@7a25b21` | `analysis/results/paderborn_external_v2_cells.csv` | `results/paderborn/paderborn_external_v2_cells.csv` |
| `exp/paderborn-external-validation-v2@7a25b21` | `analysis/results/paderborn_external_v2_oof_bearings.csv` | `results/paderborn/paderborn_external_v2_oof_bearings.csv` |
| `exp/paderborn-external-validation-v2@7a25b21` | `analysis/results/paderborn_external_v2_oof_measurements.csv` | `results/paderborn/paderborn_external_v2_oof_measurements.csv` |
| `exp/paderborn-external-validation-v2@7a25b21` | `analysis/results/paderborn_external_v2_paired_bootstrap.csv` | `results/paderborn/paderborn_external_v2_paired_bootstrap.csv` |
| `exp/paderborn-external-validation-v2@7a25b21` | `analysis/results/paderborn_external_v2_protocol_audit.json` | `results/paderborn/paderborn_external_v2_protocol_audit.json` |
| `exp/paderborn-external-validation-v2@7a25b21` | `analysis/results/paderborn_external_v2_run_manifest.json` | `results/paderborn/paderborn_external_v2_run_manifest.json` |
| `exp/paderborn-external-validation-v2@7a25b21` | `analysis/results/paderborn_external_v2_summary.csv` | `results/paderborn/paderborn_external_v2_summary.csv` |
| `exp/posthoc-baseline-expansion@ea79099` | `analysis/results/posthoc_baseline_5seed_extension_manifest.json` | `results/posthoc_baselines/posthoc_baseline_5seed_extension_manifest.json` |
| `exp/posthoc-baseline-expansion@ea79099` | `docs/posthoc_recent_baselines_5seed.md` | `results/posthoc_baselines/posthoc_recent_baselines_5seed.md` |
| `exp/posthoc-baseline-expansion@ea79099` | `analysis/results/posthoc_recent_baselines_5seed_bootstrap.csv` | `results/posthoc_baselines/posthoc_recent_baselines_5seed_bootstrap.csv` |
| `exp/posthoc-baseline-expansion@ea79099` | `analysis/results/posthoc_recent_baselines_5seed_raw.csv` | `results/posthoc_baselines/posthoc_recent_baselines_5seed_raw.csv` |
| `exp/posthoc-baseline-expansion@ea79099` | `analysis/results/posthoc_recent_baselines_5seed_summary.csv` | `results/posthoc_baselines/posthoc_recent_baselines_5seed_summary.csv` |
| `exp/qdiffcl-r-reliability-correctness@1bd0779` | `analysis/results/qdiffcl_r_v2_artifact_inventory.json` | `results/reliability/criticality_r_v2/qdiffcl_r_v2_artifact_inventory.json` |
| `exp/qdiffcl-r-reliability-correctness@1bd0779` | `analysis/results/qdiffcl_r_v2_cells.csv` | `results/reliability/criticality_r_v2/qdiffcl_r_v2_cells.csv` |
| `exp/qdiffcl-r-reliability-correctness@1bd0779` | `analysis/results/qdiffcl_r_v2_environment.json` | `results/reliability/criticality_r_v2/qdiffcl_r_v2_environment.json` |
| `exp/qdiffcl-r-reliability-correctness@1bd0779` | `analysis/results/qdiffcl_r_v2_reference_parity.csv` | `results/reliability/criticality_r_v2/qdiffcl_r_v2_reference_parity.csv` |
| `exp/qdiffcl-r-reliability-correctness@1bd0779` | `analysis/results/qdiffcl_r_v2_run_manifest.json` | `results/reliability/criticality_r_v2/qdiffcl_r_v2_run_manifest.json` |
| `exp/qdiffcl-r-reliability-correctness@1bd0779` | `analysis/results/qdiffcl_r_v2_validation_association.json` | `results/reliability/criticality_r_v2/qdiffcl_r_v2_validation_association.json` |
| `exp/qdiffcl-r-reliability-correctness@1bd0779` | `analysis/results/qdiffcl_r_v2_validation_safety.csv` | `results/reliability/criticality_r_v2/qdiffcl_r_v2_validation_safety.csv` |
| `exp/qdiffcl-r-reliability-correctness@1bd0779` | `analysis/results/qdiffcl_r_v2_within_vs_cross_regime.csv` | `results/reliability/criticality_r_v2/qdiffcl_r_v2_within_vs_cross_regime.csv` |
| `exp/qdiffcl-data-regime@dc8d12c` | `analysis/results/qdiffcl_data_regime_e_identifiability.csv` | `results/reliability/data_regime/qdiffcl_data_regime_e_identifiability.csv` |
| `exp/qdiffcl-data-regime@dc8d12c` | `analysis/results/qdiffcl_data_regime_fraction_comparability.json` | `results/reliability/data_regime/qdiffcl_data_regime_fraction_comparability.json` |
| `exp/qdiffcl-data-regime@dc8d12c` | `analysis/results/qdiffcl_data_regime_fraction_composition.csv` | `results/reliability/data_regime/qdiffcl_data_regime_fraction_composition.csv` |
| `exp/qdiffcl-data-regime@dc8d12c` | `analysis/results/qdiffcl_data_regime_fraction_groups.csv` | `results/reliability/data_regime/qdiffcl_data_regime_fraction_groups.csv` |
| `exp/qdiffcl-data-regime@dc8d12c` | `analysis/results/qdiffcl_data_regime_manifest.json` | `results/reliability/data_regime/qdiffcl_data_regime_manifest.json` |
| `exp/qdiffcl-data-regime@dc8d12c` | `analysis/results/qdiffcl_data_regime_manifest_audit.json` | `results/reliability/data_regime/qdiffcl_data_regime_manifest_audit.json` |
| `exp/qdiffcl-data-regime@dc8d12c` | `analysis/results/qdiffcl_data_regime_mask_stability.csv` | `results/reliability/data_regime/qdiffcl_data_regime_mask_stability.csv` |
| `exp/qdiffcl-data-regime@dc8d12c` | `analysis/results/qdiffcl_data_regime_no_aug_per_class.csv` | `results/reliability/data_regime/qdiffcl_data_regime_no_aug_per_class.csv` |
| `exp/qdiffcl-data-regime@dc8d12c` | `analysis/results/qdiffcl_data_regime_paired.csv` | `results/reliability/data_regime/qdiffcl_data_regime_paired.csv` |
| `exp/qdiffcl-data-regime@dc8d12c` | `analysis/results/qdiffcl_data_regime_protocol_audit.json` | `results/reliability/data_regime/qdiffcl_data_regime_protocol_audit.json` |
| `exp/qdiffcl-data-regime@dc8d12c` | `analysis/results/qdiffcl_data_regime_protocol_lock.json` | `results/reliability/data_regime/qdiffcl_data_regime_protocol_lock.json` |
| `exp/qdiffcl-data-regime@dc8d12c` | `analysis/results/qdiffcl_data_regime_raw.csv` | `results/reliability/data_regime/qdiffcl_data_regime_raw.csv` |
| `exp/qdiffcl-data-regime@dc8d12c` | `analysis/results/qdiffcl_data_regime_rho.csv` | `results/reliability/data_regime/qdiffcl_data_regime_rho.csv` |
| `exp/qdiffcl-data-regime@dc8d12c` | `analysis/results/qdiffcl_data_regime_scarcity_dod.csv` | `results/reliability/data_regime/qdiffcl_data_regime_scarcity_dod.csv` |
| `exp/qdiffcl-data-regime@dc8d12c` | `analysis/results/qdiffcl_data_regime_summary.csv` | `results/reliability/data_regime/qdiffcl_data_regime_summary.csv` |
| `exp/qdiffcl-data-regime@dc8d12c` | `analysis/results/qdiffcl_data_regime_summary.json` | `results/reliability/data_regime/qdiffcl_data_regime_summary.json` |
| `exp/paper-evidence-chain@848b493` | `docs/paper_evidence/dcbr_extension_ablation.csv` | `results/reliability/dcbr_extension_ablation.csv` |
| `exp/qdiffcl-external-baselines@253c255` | `docs/external_baseline_paired.csv` | `results/reliability/external_baseline_paired.csv` |
| `exp/qdiffcl-external-baselines@253c255` | `docs/external_baseline_results.csv` | `results/reliability/external_baseline_results.csv` |
| `exp/qdiffcl-external-baselines@253c255` | `docs/external_baseline_summary.md` | `results/reliability/external_baseline_summary.md` |
| `exp/paper-evidence-chain@848b493` | `analysis/results/paper_fault_trajectory.csv` | `results/reliability/fault_trajectory/paper_fault_trajectory.csv` |
| `exp/paper-evidence-chain@848b493` | `docs/paper_fault_trajectory.md` | `results/reliability/fault_trajectory/paper_fault_trajectory.md` |
| `exp/cross-domain-validated-safety@0efdad7` | `docs/drfd_failure_audit.md` | `results/reliability/fixed_far/drfd_failure_audit.md` |
| `exp/cross-domain-validated-safety@0efdad7` | `docs/drfd_fixed_far_paired.csv` | `results/reliability/fixed_far/drfd_fixed_far_paired.csv` |
| `exp/cross-domain-validated-safety@0efdad7` | `docs/drfd_paired.csv` | `results/reliability/fixed_far/drfd_paired.csv` |
| `exp/cross-domain-validated-safety@0efdad7` | `docs/drfd_reliability_profiles.csv` | `results/reliability/fixed_far/drfd_reliability_profiles.csv` |
| `exp/cross-domain-validated-safety@0efdad7` | `docs/drfd_seed44_trajectory.csv` | `results/reliability/fixed_far/drfd_seed44_trajectory.csv` |
| `exp/qdiffcl-final-reliability@3790928` | `docs/qdiffcl_final_5seed_mask_audit.json` | `results/reliability/qdiffcl_final_5seed_mask_audit.json` |
| `exp/qdiffcl-final-reliability@3790928` | `docs/qdiffcl_final_5seed_paired.csv` | `results/reliability/qdiffcl_final_5seed_paired.csv` |
| `exp/qdiffcl-final-reliability@3790928` | `docs/qdiffcl_final_5seed_results.csv` | `results/reliability/qdiffcl_final_5seed_results.csv` |
| `exp/qdiffcl-final-reliability@3790928` | `docs/qdiffcl_final_5seed_summary.md` | `results/reliability/qdiffcl_final_5seed_summary.md` |
| `exp/paper-evidence-chain@848b493` | `docs/paper_evidence/stability.md` | `results/reliability/stability.md` |
| `exp/paper-evidence-chain@848b493` | `docs/paper_evidence/stability_loso.csv` | `results/reliability/stability_loso.csv` |
| `exp/paper-evidence-chain@848b493` | `docs/paper_evidence/stability_paired.csv` | `results/reliability/stability_paired.csv` |
| `exp/paderborn-external-validation-v2@7a25b21` | `scripts/__init__.py (runtime dependency)` | `scripts/__init__.py` |
| `exp/paderborn-external-validation-v2@7a25b21` plus `exp/semantic-diffusion-3seed@504bc00` | `scripts/audit_semantic_diffusion_augmentation.py` plus verbatim `_simple_interpolate` from `scripts/run_rapid_idea_validation.py` | `scripts/audit_semantic_diffusion_augmentation.py` |
| `exp/r1-des-weight-tuning@7d63bd5` | `scripts/diagnose_frequency_selective_far.py` | `scripts/diagnose_frequency_selective_far.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `scripts/reconcile_paderborn_sampling_v2.py` | `scripts/reconcile_paderborn_sampling_v2.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `scripts/run_3w_clean_baseline.py (runtime dependency)` | `scripts/run_3w_clean_baseline.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `scripts/run_3w_clean_collapse_diagnosis.py (runtime dependency)` | `scripts/run_3w_clean_collapse_diagnosis.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `scripts/run_3w_diffusion_1seed.py (runtime dependency)` | `scripts/run_3w_diffusion_1seed.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `scripts/run_3w_final_primary_grouped.py (runtime dependency)` | `scripts/run_3w_final_primary_grouped.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `scripts/run_3w_strict_mask_ablation.py (runtime dependency)` | `scripts/run_3w_strict_mask_ablation.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `scripts/run_budget_shrinkage_diagnostic.py (runtime dependency)` | `scripts/run_budget_shrinkage_diagnostic.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `scripts/run_diffusion_quality_retest.py (runtime dependency)` | `scripts/run_diffusion_quality_retest.py` |
| `exp/domain-calibrated-budget-routing@322f45a` | `scripts/run_domain_budget_routing.py` | `scripts/run_domain_budget_routing.py` |
| `exp/r1-des-weight-tuning@7d63bd5` | `scripts/run_domain_reliable_safe_frequency_diffusion.py` | `scripts/run_domain_reliable_safe_frequency_diffusion.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `scripts/run_external_baselines.py (runtime dependency)` | `scripts/run_external_baselines.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `scripts/run_frequency_selective_r1_3seed.py` | `scripts/run_frequency_selective_r1_3seed.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `scripts/run_paderborn_external_v2.py` | `scripts/run_paderborn_external_v2.py` |
| `exp/paper-final-outer@276416f` | `scripts/run_paper_final_outer.py` | `scripts/run_paper_final_outer.py` |
| `exp/paper-evidence-chain@848b493` | `scripts/run_paper_mechanism_ablation.py` | `scripts/run_paper_mechanism_ablation.py` |
| `exp/posthoc-baseline-expansion@ea79099` | `scripts/run_posthoc_baseline_5seed_extension.py` | `scripts/run_posthoc_baseline_5seed_extension.py` |
| `exp/posthoc-baseline-expansion@ea79099` | `scripts/run_posthoc_recent_baselines.py` | `scripts/run_posthoc_recent_baselines.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `scripts/run_stage_frequency_diffusion_mvp.py (runtime dependency)` | `scripts/run_stage_frequency_diffusion_mvp.py` |
| `exp/paper-evidence-chain@848b493` | `scripts/summarize_paper_evidence_chain.py` | `scripts/summarize_paper_evidence_chain.py` |
| `exp/paper-evidence-chain@848b493` | `scripts/summarize_paper_mechanism_ablation.py` | `scripts/summarize_paper_mechanism_ablation.py` |
| `exp/posthoc-baseline-expansion@ea79099` | `scripts/summarize_posthoc_baseline_5seed_extension.py` | `scripts/summarize_posthoc_baseline_5seed_extension.py` |
| `exp/posthoc-baseline-expansion@ea79099` | `scripts/summarize_posthoc_recent_baselines.py` | `scripts/summarize_posthoc_recent_baselines.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `augmentations/__init__.py` | `src/augmentations/__init__.py` |
| `exp/domain-calibrated-budget-routing@322f45a` | `augmentations/domain_budget_routing.py` | `src/augmentations/domain_budget_routing.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `augmentations/stochastic_view_routing.py` | `src/augmentations/stochastic_view_routing.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `baselines/__init__.py (consolidated core snapshot)` | `src/baselines/__init__.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `baselines/external_augmentations.py (consolidated core snapshot)` | `src/baselines/external_augmentations.py` |
| `exp/posthoc-baseline-expansion@ea79099` | `baselines/posthoc_recent.py` | `src/baselines/posthoc_recent.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `datasets/__init__.py (consolidated core snapshot)` | `src/datasets/__init__.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `datasets/paderborn.py` | `src/datasets/paderborn.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `datasets/protocol.py (consolidated core snapshot)` | `src/datasets/protocol.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `datasets/synthetic.py (consolidated core snapshot)` | `src/datasets/synthetic.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `datasets/tep.py (consolidated core snapshot)` | `src/datasets/tep.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `datasets/three_w.py (consolidated core snapshot)` | `src/datasets/three_w.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `diffusion/__init__.py (consolidated core snapshot)` | `src/diffusion/__init__.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `diffusion/candidate_generation.py (consolidated core snapshot)` | `src/diffusion/candidate_generation.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `diffusion/cross_domain_safe_allocation.py (consolidated core snapshot)` | `src/diffusion/cross_domain_safe_allocation.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `diffusion/domain_shortcut_selective.py (consolidated core snapshot)` | `src/diffusion/domain_shortcut_selective.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `diffusion/fixed_views.py (consolidated core snapshot)` | `src/diffusion/fixed_views.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `diffusion/frequency_selective.py (consolidated core snapshot)` | `src/diffusion/frequency_selective.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `diffusion/process.py (consolidated core snapshot)` | `src/diffusion/process.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `diffusion/safe_frequency_allocation.py (consolidated core snapshot)` | `src/diffusion/safe_frequency_allocation.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `diffusion/semantic_augmentation.py (consolidated core snapshot)` | `src/diffusion/semantic_augmentation.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `diffusion/stage_budget.py (consolidated core snapshot)` | `src/diffusion/stage_budget.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `diffusion/stage_curriculum.py (consolidated core snapshot)` | `src/diffusion/stage_curriculum.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `frequency/__init__.py (consolidated core snapshot)` | `src/frequency/__init__.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `frequency/budget_demand.py (consolidated core snapshot)` | `src/frequency/budget_demand.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `frequency/criticality.py (consolidated core snapshot)` | `src/frequency/criticality.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `frequency/cross_channel_structure.py (consolidated core snapshot)` | `src/frequency/cross_channel_structure.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `frequency/cross_domain_safety.py (consolidated core snapshot)` | `src/frequency/cross_domain_safety.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `frequency/domain_reliability.py (consolidated core snapshot)` | `src/frequency/domain_reliability.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `frequency/domain_shortcut.py (consolidated core snapshot)` | `src/frequency/domain_shortcut.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `frequency/early_criticality.py (consolidated core snapshot)` | `src/frequency/early_criticality.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `frequency/hierarchical.py (consolidated core snapshot)` | `src/frequency/hierarchical.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `frequency/rival_aware.py (consolidated core snapshot)` | `src/frequency/rival_aware.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `frequency/safe_capacity.py (consolidated core snapshot)` | `src/frequency/safe_capacity.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `frequency/uncertainty.py (consolidated core snapshot)` | `src/frequency/uncertainty.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `losses/__init__.py (consolidated core snapshot)` | `src/losses/__init__.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `losses/quality.py (consolidated core snapshot)` | `src/losses/quality.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `losses/semantic_consistency.py (consolidated core snapshot)` | `src/losses/semantic_consistency.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `losses/supcon.py (consolidated core snapshot)` | `src/losses/supcon.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `metrics/__init__.py (consolidated core snapshot)` | `src/metrics/__init__.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `metrics/classification.py (consolidated core snapshot)` | `src/metrics/classification.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `metrics/fixed_far.py (consolidated core snapshot)` | `src/metrics/fixed_far.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `metrics/representation.py (consolidated core snapshot)` | `src/metrics/representation.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `models/__init__.py (consolidated core snapshot)` | `src/models/__init__.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `models/backbones.py (consolidated core snapshot)` | `src/models/backbones.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `models/minimal_diffusion.py (consolidated core snapshot)` | `src/models/minimal_diffusion.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `trainers/__init__.py (consolidated core snapshot)` | `src/trainers/__init__.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `trainers/balanced.py (consolidated core snapshot)` | `src/trainers/balanced.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `trainers/baseline.py (consolidated core snapshot)` | `src/trainers/baseline.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `utils.py (consolidated core snapshot)` | `src/utils.py` |
| `exp/posthoc-baseline-expansion@ea79099` | `docs/posthoc_recent_baselines_5seed.md (verbatim table rows)` | `supplementary/Table_S1.md` |
| `exp/domain-calibrated-budget-routing@322f45a` | `tests/test_domain_budget_routing.py` | `tests/test_domain_budget_routing.py` |
| `exp/paper-evidence-chain@848b493` | `tests/test_frequency_selective_diffusion.py` | `tests/test_frequency_selective_diffusion.py` |
| `exp/paderborn-external-validation-v2@7a25b21` | `tests/test_paderborn.py` | `tests/test_paderborn.py` |
| `exp/paper-evidence-chain@848b493` | `tests/test_paper_evidence_chain.py` | `tests/test_paper_evidence_chain.py` |
| `exp/paper-final-outer@276416f` | `tests/test_paper_final_outer.py` | `tests/test_paper_final_outer.py` |
| `exp/paper-evidence-chain@848b493` | `tests/test_paper_final_protocol_amendment.py` | `tests/test_paper_final_protocol_amendment.py` |
| `exp/posthoc-baseline-expansion@ea79099` | `tests/test_posthoc_baseline_5seed_extension.py` | `tests/test_posthoc_baseline_5seed_extension.py` |
| `exp/posthoc-baseline-expansion@ea79099` | `tests/test_posthoc_recent_baselines.py` | `tests/test_posthoc_recent_baselines.py` |
| `exp/paper-evidence-chain@848b493` | `tests/test_protocol.py` | `tests/test_protocol.py` |
