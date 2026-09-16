# CritiDiff-CL

Code and frozen evidence for the IEEE BigData Special Session submission *CritiDiff-CL: Fault-Semantic Frequency-Selective Diffusion and Domain-Calibrated Contrastive Learning for Heterogeneous Industrial Time Series*.

## Method overview

CritiDiff-CL estimates frequency criticality from training-fault discriminativeness (`D`) and early-stage sensitivity (`E`). It uses the resulting continuous mask to apply soft frequency-selective forward diffusion while matching the total spectral perturbation budget of the uniform-diffusion reference. Forward diffusion is used only as a perturbation operator; no denoiser or reverse diffusion model is trained. Domain-Calibrated Budget Routing (DCBR) selects a domain-level budget ratio on inner validation data and does not use the outer test split for routing.

## Result snapshot

The values below are copied from the `overall` rows of [`results/outer/paper_final_outer_summary.csv`](results/outer/paper_final_outer_summary.csv) and match Table I of the submission draft. FreRA is the strongest non-CritiDiff-CL baseline by Macro-F1 on both datasets in that table.

| Dataset | Method | Macro-F1 |
|---|---|---:|
| 3W | FreRA | 0.3334 ± 0.0974 |
| 3W | FINAL_QDIFFCL | 0.3216 ± 0.0324 |
| TEP | FreRA | 0.9496 ± 0.0171 |
| TEP | FINAL_QDIFFCL | 0.9483 ± 0.0254 |

Complete results, paired comparisons, and confidence intervals are provided under [`results/`](results/).

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

## Known limitations

- The 3W cross-WELL setting has a high false-alarm rate; the grouped outer results should not be read as deployment-ready calibration.
- DCBR is a validation-routed budget choice, not a guarantee of improvement. Its paired outer confidence intervals cross zero on both datasets.
- The early-stage statistic `E` depends on true early-stage annotations during training-data analysis. It is not directly available when those stage boundaries are unknown or unreliable.
- The Paderborn D-only external validation is a negative boundary result and does not support a universal transfer claim.

## License and citation

**TODO before archival release:** add the MIT `LICENSE` file and replace the copyright holder and year below. The intended license is the MIT License.

```text
MIT License
Copyright (c) TODO_YEAR TODO_COPYRIGHT_HOLDER
```

**TODO before submission:** replace all BibTeX placeholders with the final author list, paper metadata, and public artifact URL.

```bibtex
@inproceedings{TODO_CITATION_KEY,
  title     = {CritiDiff-CL: Fault-Semantic Frequency-Selective Diffusion and Domain-Calibrated Contrastive Learning for Heterogeneous Industrial Time Series},
  author    = {TODO: Author List},
  booktitle = {TODO: IEEE BigData Special Session Name},
  year      = {TODO: Year},
  url       = {TODO: Public Artifact URL}
}
```
