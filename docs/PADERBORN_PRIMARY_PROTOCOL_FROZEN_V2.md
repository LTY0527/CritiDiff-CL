# Paderborn Primary Protocol Frozen v2

Status: `PADERBORN_PROTOCOL_FROZEN_V2`

This protocol is frozen before any Paderborn formal model or test metric is
produced.

## Scientific scope

- Component: `QDIFFCL_D_ONLY_EXTERNAL_COMPONENT`
- Contribution tested: fault-discriminative criticality D (WHERE) and D-guided
  soft frequency allocation (HOW TO ALLOCATE)
- E: unavailable and not fabricated
- DCBR: not claimed on Paderborn
- R-v2: diagnostic only; never used as a controller

## Data and split

- Primary bearings: 15 (5 healthy, 5 real outer-ring, 5 real inner-ring)
- Measurements: 1200 (80 per bearing)
- Split unit: bearing
- Five folds; each class contributes 3 train, 1 validation, and 1 test bearing
- Per fold: 9 train, 3 validation, and 3 test bearings
- No bearing, measurement, or window overlap across splits

## Signal grid and windows

- Frozen policy: `sample_index_resample`
- Grid: 64000 Hz, 4 seconds, 256000 samples
- Channel: `vibration_1`
- Window length/stride: 4096/2048
- Sixteen positions are selected deterministically and evenly from the complete
  stride grid for every measurement, including its first and final legal starts.
- The same positions are used by every method, seed, and fold.
- This bounded representation keeps each bearing and operating condition equally
  weighted and makes the 45-cell matrix recoverable under the 2048 MiB RAM gate.

## Frozen matrix and fairness

- Seeds: 7, 42, 2026
- Methods: `NO_AUG`, `UNIFORM_DIFFUSION`,
  `QDIFFCL_D_ONLY_EXTERNAL_COMPONENT`
- Matrix: 3 seeds x 5 folds x 3 methods = 45 cells
- Backbone: TCN
- Objective: Hard SupCon followed by a frozen linear probe
- Batching, initialization, orders, optimizer, and augmentation opportunity are
  shared within every seed/fold comparison.
- Uniform and D-only selective diffusion use the same aggregate spectral noise
  budget; only frequency allocation differs.
- D and its frequency scaler are fitted on training bearings only.
- Time-domain normalization is fitted on training bearings only.

## Evaluation and decision

- Primary: measurement-level Macro-F1
- Secondary: measurement balanced accuracy, bearing-level OOF Macro-F1/accuracy,
  per-class metrics, confusion matrix, and per-operating-condition metrics
- Early Recall, Detection Delay, and onset FAR are not defined for this dataset.
- Test predictions are read only after representation and probe training complete.
- External support requires a positive D-only minus Uniform mean paired delta with
  a positive 95% bootstrap lower bound and non-negative bearing-level delta.
- A positive but uncertain or metric-inconsistent effect is classified MIXED;
  otherwise it is NO_SUPPORT.

Runtime and exact constants are frozen in `configs/paderborn_external_v2.yaml`.
