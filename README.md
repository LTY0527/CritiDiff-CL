# CritiDiff-CL

Tag v1.0-submission 于 2026-09-18 补充缺失配置文件并做注释级清理；实验代码与全部结果未变。

Code and frozen evidence for the 2026 IEEE BigData Special Session submission CritiDiff-CL.

## Method overview

CritiDiff-CL first estimates fault-semantic channel-frequency criticality from fault discriminativeness (`D`) over independent Run/WELL units and, when genuine early-stage information is identifiable, early-stage sensitivity (`E`). It then maps continuous criticality to per-frequency DDPM forward-perturbation strength, applying weaker perturbations to highly critical frequencies. Only forward diffusion is used: no denoiser is trained and no reverse sampling is performed. Finally, selective and uniform diffusion are matched in total perturbation variance in the standardized log-spectral domain, separating frequency allocation from total perturbation magnitude.

Domain-Calibrated Budget Routing (DCBR) is an optional training-time validation calibration extension. It selects the augmentation configuration using validation data and does not introduce additional inference parameters. DCBR is not one of the three core contributions in the v10.6 manuscript.

## Result snapshot

The values below are copied from the frozen [`outer summary`](results/outer/paper_final_outer_summary.csv) and [`paired-bootstrap results`](results/outer/paper_final_outer_bootstrap.csv); no metrics were recomputed.

| Dataset | Result | Frozen value |
|---|---|---:|
| 3W | CritiDiff-CL AUPRC | 0.7873 |
| 3W | CritiDiff-CL Early Recall | 0.9114 |
| 3W | CritiDiff-CL Macro-F1 / across-split SD | 0.3216 / 0.0324 |
| 3W | FreRA Macro-F1 | 0.3334 |
| TEP | CritiDiff-CL Macro-F1 | 0.9483 |
| TEP | CritiDiff-CL Early Recall | 0.8838 |

On 3W, CritiDiff-CL has the highest AUPRC and Early Recall and the lowest across-split Macro-F1 SD in Table I. FreRA has the higher Macro-F1 point estimate; the paired difference FreRA minus CritiDiff-CL is `+0.0118` with 95% CI `[−0.0514, +0.0415]`, which includes zero. On TEP, main-table Macro-F1 values lie in `0.9458–0.9496`, and CritiDiff-CL's Early Recall is tied for the highest value.

Complete results and confidence intervals are provided under [`results/`](results/).

## Repository map

[`docs/EVIDENCE.md`](docs/EVIDENCE.md) defines the evidence classes. The current paper-to-repository mapping is:

| Paper item | Evidence and files |
|---|---|
| Table I — grouped outer evaluation | [`summary`](results/outer/paper_final_outer_summary.csv), [`raw cells`](results/outer/paper_final_outer_raw.csv), [`paired bootstrap`](results/outer/paper_final_outer_bootstrap.csv), [`groupwise metrics`](results/outer/paper_final_outer_groupwise.csv), and [`manifest`](results/outer/paper_final_outer_manifest.json) |
| Table II — matched-budget frequency-allocation ablation | [`validation results`](results/ablation/mechanism_ablation_validation.csv) and [`paired results`](results/ablation/mechanism_ablation_validation_paired.csv) |
| Table III — fault-semantic component ablation | [`component results`](results/ablation/qdiffcl_final_component_ablation.csv) and [`report`](results/ablation/qdiffcl_final_component_ablation.md) |
| Table IV — critical-ratio sensitivity | [`results`](results/ablation/paper_ratio_sensitivity.csv) and [`report`](results/ablation/paper_ratio_sensitivity.md) |
| Table V — efficiency | [`benchmark`](results/efficiency/paper_efficiency.csv) and [`report`](results/efficiency/paper_efficiency.md) |
| Sec. IV-D — DCBR rho routing | [`outer raw cells`](results/outer/paper_final_outer_raw.csv) and [`outer manifest`](results/outer/paper_final_outer_manifest.json) |

## Additional repository evidence

The following evidence is not part of the v10.6 manuscript text, but is retained in the repository for completeness and reproducibility.

| Evidence | Scope and files |
|---|---|
| Single-split five-seed reliability | Reliability evidence rather than a separate v10.6 paper table: [`results/reliability/`](results/reliability/) |
| Paderborn external validation | Repository-only external/boundary evidence, not reported in the v10.6 manuscript text: [`results/paderborn/`](results/paderborn/) |
| Recent post-hoc baselines | TF-C, SoftCLT, TS2Vec, and AutoTCL are not included in the v10.6 manuscript text; full five-seed results remain in [`supplementary/Table_S1.md`](supplementary/Table_S1.md) and [`results/posthoc_baselines/`](results/posthoc_baselines/) |
| Other development and reliability evidence | Limited-data, missingness, criticality reliability, early-fault trajectory, fixed-FAR, and other retained analyses under [`results/reliability/`](results/reliability/) |

The per-file migration lineage is recorded in [`docs/MIGRATION.md`](docs/MIGRATION.md). The frozen table and paired-CI checks are recorded in [`docs/TABLE_AUDIT.md`](docs/TABLE_AUDIT.md).

## Evidence hierarchy

Grouped outer evaluation provides generalization evidence. Fixed single-split five-seed experiments are reliability evidence, validation-only experiments support mechanism analysis, recent-baseline experiments are post-hoc evidence, and Paderborn is repository-only external/boundary evidence.

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

### Manuscript-facing reproduction

Run commands from the repository root. These workflows write new artifacts below ignored output directories and do not overwrite the frozen files in `results/`.

```bash
# 1. Repeated grouped outer evaluation on 3W and TEP
python -m scripts.run_paper_final_outer --dataset both
```

```bash
# 2. Validation-only matched-budget mechanism ablation
python -m scripts.run_paper_mechanism_ablation --data-root data/3w --dataset both
```

The component, sensitivity, and efficiency evidence is preserved under [`results/ablation/`](results/ablation/) and [`results/efficiency/`](results/efficiency/). Their legacy standalone runners were not included in the public artifact, so the repository does not invent replacement commands.

### Repository-only reproduction

Repository-only workflows reproduce additional experiments that are retained in the repository but are not reported in the v10.6 manuscript text.

```powershell
# Paderborn external validation followed by the separately labeled post-hoc benchmark
python -m scripts.run_paderborn_external_v2 --phase all
python -m scripts.run_posthoc_baseline_5seed_extension --prepare
python -m scripts.run_posthoc_baseline_5seed_extension --benchmark
python -m scripts.summarize_posthoc_baseline_5seed_extension
```

The outer matrix is computationally substantial. `--prepare-only`, `--outer-seed`, `--max-cells`, and method/dataset filters are available for protocol checks and bounded runs; use `--help` on an entry point for the exact options.

## Manuscript limitations

- The 3W cross-WELL setting has a high false-alarm rate; the grouped outer results should not be read as deployment-ready calibration.
- The early-stage statistic `E` depends on true early-stage annotations during training-data analysis. It is not directly available when those stage boundaries are unknown or unreliable.
- The critical ratio, diffusion schedule, and DCBR rho candidates have not been jointly optimized.

## Additional repository observations

These additional observations are retained in the repository for completeness and are not all discussed in the v10.6 manuscript.

- DCBR is a validation-routed training-time extension, not a guarantee of improvement. Its paired outer confidence intervals include zero on both datasets.
- The Paderborn D-only external validation is a negative boundary result and does not support a universal transfer claim.
- Limited-data and missingness results remain dataset- and regime-dependent development evidence.

## License and citation

The code and documentation in this repository are released under the [MIT License](LICENSE). Copyright (c) 2026 LTY0527.

The submission is under anonymous review; the citation therefore uses an anonymous author entry until the archival metadata is available.

```bibtex
@inproceedings{anonymous2026critidiffcl,
  title     = {CritiDiff-CL: Fault-Semantic Frequency-Selective Diffusion and Domain-Calibrated Contrastive Learning for Heterogeneous Industrial Time Series},
  author    = {Anonymous Authors},
  booktitle = {2026 IEEE International Conference on Big Data (BigData), Special Session on Machine Learning for Big Data},
  year      = {2026},
  url       = {https://github.com/LTY0527/CritiDiff-CL}
}
```
