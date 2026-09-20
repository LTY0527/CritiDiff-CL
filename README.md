# CritiDiff-CL: Fault-Semantic Frequency-Selective Diffusion for Industrial Time-Series Contrastive Learning

Tag v1.0-submission 于 2026-09-18 补充缺失配置文件并做注释级清理；实验代码与全部结果未变。

Code and frozen evidence for the IEEE BigData 2026 Special Session submission *CritiDiff-CL: Fault-Semantic Frequency-Selective Diffusion for Industrial Time-Series Contrastive Learning*. The method is evaluated on two heterogeneous industrial process datasets under grouped protocols.

## Method overview

CritiDiff-CL estimates fault-semantic frequency criticality from fault discriminativeness (`D`) and early-stage sensitivity (`E`). A continuous criticality mask drives budget-matched, soft frequency-selective forward diffusion. Forward diffusion is used only as a perturbation operator: no denoiser is trained and no reverse diffusion is performed. Lightweight Domain-Calibrated Budget Routing (DCBR) selects a domain-level budget ratio using inner validation only; the outer test split is not used for routing.

## Result snapshot

The values below are copied from the frozen [`outer summary`](results/outer/paper_final_outer_summary.csv) and [`paired-bootstrap results`](results/outer/paper_final_outer_bootstrap.csv); no metrics were recomputed.

### 3W

| Result | Frozen value |
|---|---:|
| CritiDiff-CL (FINAL_QDIFFCL) AUPRC | 0.7873 |
| CritiDiff-CL Early Recall | 0.9114 |
| CritiDiff-CL Macro-F1 | 0.3216 ± 0.0324 |
| FreRA Macro-F1 | 0.3334 ± 0.0974 |
| FreRA − CritiDiff-CL paired 95% CI | [−0.0514, +0.0415] |

CritiDiff-CL has the highest AUPRC and Early Recall and the lowest across-split Macro-F1 SD among the methods in Table I. For the FreRA Macro-F1 comparison, the paired 95% CI includes zero.

### TEP

The frozen main-table Macro-F1 values lie in a narrow range from 0.9458 to 0.9496. CritiDiff-CL reaches an Early Recall of 0.8838, tied with JITTER_SCALING for the highest value in Table I.

TF-C, SoftCLT, AutoTCL, and TS2Vec were added after the frozen main experiments as a recent-baseline extension. On TEP, the frozen [`post-hoc paired results`](results/posthoc_baselines/posthoc_recent_baselines_5seed_bootstrap.csv) show that all four paired Macro-F1 effects relative to FINAL_QDIFFCL are negative, and all four paired 95% confidence intervals exclude zero in favor of CritiDiff-CL.

Complete results, including the 3W post-hoc comparisons, paired effects, and confidence intervals, are retained under [`results/`](results/).

## Repository map

[`docs/EVIDENCE.md`](docs/EVIDENCE.md) defines the evidence classes. The table below gives the concrete source files for every paper table.

| Paper item | Evidence and files |
|---|---|
| Table I — grouped outer evaluation | [`summary`](results/outer/paper_final_outer_summary.csv), [`raw cells`](results/outer/paper_final_outer_raw.csv), [`paired bootstrap`](results/outer/paper_final_outer_bootstrap.csv), [`groupwise metrics`](results/outer/paper_final_outer_groupwise.csv), and [`manifest`](results/outer/paper_final_outer_manifest.json) |
| Table II — five-seed reliability audit | [`QDIFFCL results`](results/reliability/qdiffcl_final_5seed_results.csv), [`paired results`](results/reliability/qdiffcl_final_5seed_paired.csv), [`external baselines`](results/reliability/external_baseline_results.csv), and [`DCBR extension ablation`](results/reliability/dcbr_extension_ablation.csv) |
| Table III — matched-budget allocation ablation | [`validation results`](results/ablation/mechanism_ablation_validation.csv) and [`paired results`](results/ablation/mechanism_ablation_validation_paired.csv) |
| Table IV — fault-semantic component ablation | [`component results`](results/ablation/qdiffcl_final_component_ablation.csv) and [`report`](results/ablation/qdiffcl_final_component_ablation.md) |
| Table V — Paderborn external validation | [`summary`](results/paderborn/paderborn_external_v2_summary.csv), [`paired bootstrap`](results/paderborn/paderborn_external_v2_paired_bootstrap.csv), [`OOF bearings`](results/paderborn/paderborn_external_v2_oof_bearings.csv), and [`protocol audit`](results/paderborn/paderborn_external_v2_protocol_audit.json) |
| Table VI — critical-ratio sensitivity | [`results`](results/ablation/paper_ratio_sensitivity.csv) and [`report`](results/ablation/paper_ratio_sensitivity.md) |
| Table VII — efficiency | [`benchmark`](results/efficiency/paper_efficiency.csv) and [`report`](results/efficiency/paper_efficiency.md) |
| Table S1 — recent post-hoc baselines | [`supplementary table`](supplementary/Table_S1.md), [`raw cells`](results/posthoc_baselines/posthoc_recent_baselines_5seed_raw.csv), [`summary`](results/posthoc_baselines/posthoc_recent_baselines_5seed_summary.csv), and [`paired bootstrap`](results/posthoc_baselines/posthoc_recent_baselines_5seed_bootstrap.csv) |
| DCBR rho routing | [`outer raw cells`](results/outer/paper_final_outer_raw.csv) and [`outer manifest`](results/outer/paper_final_outer_manifest.json) |

The per-file migration lineage is recorded in [`docs/MIGRATION.md`](docs/MIGRATION.md). The frozen table and paired-CI checks are recorded in [`docs/TABLE_AUDIT.md`](docs/TABLE_AUDIT.md).

## Evidence hierarchy

The repeated grouped outer protocol is the only evidence used for cross-method generalization claims. The single-split five-seed experiments are reliability audits, while validation-only experiments support mechanism and ablation analysis. The recent-baseline extension and Table S1 are post-hoc evidence and were not preregistered.

## Reproduction

### Environment

The frozen runs used Python 3.10.20, PyTorch 2.6.0 with CUDA 12.4, and an NVIDIA GeForce RTX 4060 Laptop GPU. The package declares Python 3.10–3.12 and the required Python dependencies in [`pyproject.toml`](pyproject.toml).

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[data,test]"
python -m pytest tests -q
```

### Data preparation

Datasets are not redistributed. A convenient local layout is:

```text
data/
├── 3w/                         # class directories 0/, 1/, ... containing Parquet files
├── tep/                        # four Rieth 2017 RData files
└── paderborn/                  # original Paderborn .mat hierarchy
```

- **3W:** obtain the public Petrobras 3W dataset from <https://github.com/petrobras/3W>. The loader expects files matching `<root>/<class>/*.parquet`.
- **TEP:** obtain the Rieth et al. Tennessee Eastman Process data from Harvard Dataverse, DOI [`10.7910/DVN/6C3JR1`](https://doi.org/10.7910/DVN/6C3JR1). Place `TEP_FaultFree_Training.RData`, `TEP_FaultFree_Testing.RData`, `TEP_Faulty_Training.RData`, and `TEP_Faulty_Testing.RData` in the same directory.
- **Paderborn:** obtain the bearing data from the [Paderborn University Bearing Data Center](https://mb.uni-paderborn.de/kat/forschung/datacenter/bearing-datacenter) and retain its `.mat` files below one root directory.

Before running an experiment, set only the local `data_root` fields in [`configs/paper_final_outer.yaml`](configs/paper_final_outer.yaml) and [`configs/paderborn_external_v2.yaml`](configs/paderborn_external_v2.yaml), or pass the 3W root through the ablation command below. Do not change protocol, split, seed, or statistic fields. The repository intentionally excludes datasets, checkpoints, and third-party source trees.

For the post-hoc benchmark, place the official TF-C, SoftCLT, and TS2Vec repositories under the paths declared in [`configs/posthoc_recent_baselines.yaml`](configs/posthoc_recent_baselines.yaml). Checkout the exact commits recorded in [`configs/posthoc_baseline_5seed_extension.yaml`](configs/posthoc_baseline_5seed_extension.yaml); the adapter fails closed when an official commit does not match.

### Entry points

Run commands from the repository root. These are the three reproduction workflows; they write new artifacts below ignored output directories and do not overwrite the frozen files in `results/`.

```bash
# 1. Repeated grouped outer evaluation on 3W and TEP
python -m scripts.run_paper_final_outer --dataset both
```

```bash
# 2. Validation-only mechanism ablation
python -m scripts.run_paper_mechanism_ablation --data-root data/3w --dataset both
```

```powershell
# 3. Paderborn external validation followed by the separately labeled post-hoc benchmark
python -m scripts.run_paderborn_external_v2 --phase all
python -m scripts.run_posthoc_baseline_5seed_extension --prepare
python -m scripts.run_posthoc_baseline_5seed_extension --benchmark
python -m scripts.summarize_posthoc_baseline_5seed_extension
```

The outer matrix is computationally substantial. `--prepare-only`, `--outer-seed`, `--max-cells`, and method/dataset filters are available for protocol checks and bounded runs; use `--help` on an entry point for the exact options.

## Scope and notes

- The 3W grouped cross-WELL setting exhibits a relatively high false-alarm rate; the reported results evaluate representation learning under the frozen grouped protocol rather than deployment-time alarm calibration.
- DCBR is a validation-routed configuration-selection mechanism. Its outer paired confidence intervals include zero on both datasets, and the repository retains these results as part of the frozen evidence.
- The early-stage statistic `E` requires genuine early-stage annotations during training-data analysis and is only used when such stage information is identifiable.
- Paderborn D-only external validation is retained as an additional external component experiment outside the v9 paper's main narrative; complete results remain available under [`results/paderborn/`](results/paderborn/).

## License and citation

The code and documentation in this repository are released under the [MIT License](LICENSE). Copyright (c) 2026 LTY0527.

The submission is under anonymous review; the citation therefore uses an anonymous author entry until the archival metadata is available.

```bibtex
@inproceedings{anonymous2026critidiffcl,
  title     = {CritiDiff-CL: Fault-Semantic Frequency-Selective Diffusion for Industrial Time-Series Contrastive Learning},
  author    = {Anonymous Authors},
  booktitle = {2026 IEEE International Conference on Big Data (BigData), Special Session on Machine Learning for Big Data},
  year      = {2026},
  url       = {https://github.com/LTY0527/CritiDiff-CL}
}
```
