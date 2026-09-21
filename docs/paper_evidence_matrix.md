# Paper Evidence Matrix

## Evidence used in manuscript v10.6

| Claim | Evidence | Status |
|---|---|---|
| Grouped evaluation | Completed nested/grouped outer matrix with split-first aggregation and 2,000× WELL/Run bootstrap | `TABLE I; COMPLETE; DATASET-SPECIFIC EFFECTS` |
| Selective versus Uniform allocation | 3-seed validation matched-budget ablation | `TABLE II; SUPPORTED ON 3W` |
| Soft allocation matters | Hard versus Soft 3-seed validation ablation | `TABLE II; SUPPORTED ON 3W` |
| Gain is not explained only by less total noise | Soft matched versus unmatched plus equal-budget Uniform | `TABLE II; SUPPORTED ON 3W` |
| D/E captures fault semantics | D-only/E-only/D+E component ablation | `TABLE III; D PRIMARY, E COMPLEMENTARY` |
| Critical-ratio sensitivity | 0.20/0.30/0.40 3W results | `TABLE IV; LOCAL SENSITIVITY, NOT A UNIVERSAL OPTIMUM` |
| Practicality | Canonical timing, peak GPU memory, parameters, and repeated augmentation/inference benchmark | `TABLE V; FRERA AUGMENTATION-TIMING LIMITATION RETAINED` |
| DCBR validation calibration | Fixed-split five-seed evidence and outer route records | `SEC. IV-D; OPTIONAL TRAINING-TIME EXTENSION` |

## Repository-only / not in v10.6 main text

| Evidence | Result status |
|---|---|
| TEP selective/soft matched-budget mechanism | `NOT SUPPORTED CONSISTENTLY ON TEP` |
| Diffusion and contrastive-learning interaction | 3W positive interaction `+0.1483`, 3/3 positive; TEP inverse interaction `-0.0206`, 0/3 positive | `DATASET-DEPENDENT` |
| TEP critical-ratio sensitivity | 0.30 is a local trough | `REPOSITORY-ONLY; FROZEN VALUE NOT REOPENED` |
| DCBR mitigation of over-augmentation | TEP fixed-split development evidence | `REPOSITORY-ONLY CALIBRATION EVIDENCE` |
| Cross-WELL benefit | Per-WELL replay and bootstrap | `PARTIAL; CI INCLUDES ZERO` |
| Early-fault score rise | 40 TEP fault-run checkpoint replay with onset alignment and bootstrap bands | `REPOSITORY-ONLY DEVELOPMENT EVIDENCE` |
| AutoDA-Timeseries | Source/protocol audit | `METHOD-NATIVE ONLY; REPOSITORY-ONLY` |
| AutoTCL, SoftCLT, TF-C, and TS2Vec | Three grouped outer splits, five matched seeds, paired group bootstrap | `POST-HOC COMPLETE; REPOSITORY-ONLY` |
| Industrial diffusion+contrastive DiCL | GitHub/scholarly-source feasibility audit | `NOT FAIRLY REPRODUCIBLE / DO NOT RANK` |
| Limited-data robustness | 3W 100/25/10%; TEP 100/25%; TEP10 E-identifiability hold | `COMPLETE LEGAL MATRIX; DATASET/REGIME-DEPENDENT` |
| Missingness robustness | TEP MCAR30 only; 3W native missingness | `PARTIAL; REPOSITORY-ONLY` |
| Criticality reliability | R-v1 superseded by 15-cell grouped-bootstrap R-v2 | `CORRECTNESS PASS; DIAGNOSTIC ONLY; NOT A CONTROLLER` |
| Paderborn external validation | 1200/1200 grid audit and 45-cell bearing-grouped D-only matrix; paired D-only versus Uniform Macro-F1 delta `-0.0030`, 95% CI `[-0.0491, 0.0538]` | `NO EXTERNAL SUPPORT; REPOSITORY-ONLY BOUNDARY EVIDENCE` |

## Current v10.6 contribution mapping

- Contribution 1: Fault-Semantic Frequency Criticality.
- Contribution 2: Continuous Frequency-Selective Forward Diffusion.
- Contribution 3: Matched Spectral Perturbation Budget.
- DCBR: optional training-time validation calibration extension.

Unsupported, partial, or repository-only claims must not enter the v10.6 abstract, contribution list, main tables, or conclusion. SVR remains `NO_GO_SVR` and is excluded from the method.
