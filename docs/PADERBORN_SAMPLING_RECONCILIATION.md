# Paderborn Sampling Reconciliation v2

Status: `PADERBORN_FREQUENCY_GRID_GO`

The decision uses acquisition metadata and signal-preservation diagnostics only.
No class label, fold assignment, validation metric, test metric, or model result
participates in policy selection.

| Policy | Formal | Pass | Median RMS ratio | PSD cosine p05 | log-PSD corr p05 | band error p95 | dominant shift p95 Hz |
|---|---:|---:|---:|---:|---:|---:|---:|
| timestamp_uniform_interpolation | True | False | 0.977237 | 0.412513 | 0.497045 | 0.479587 | 793.750 |
| sample_index_resample | True | True | 1.000000 | 0.997214 | 0.925693 | 0.008385 | 0.000 |
| crop_edge_pad | False | True | 1.000001 | 0.999661 | 0.999697 | 0.013724 | 0.000 |

Selected policy: `sample_index_resample`.

- Primary universe: `1200` measurements from `15` bearings.
- Canonical validation: `1200/1200` finite measurements.
- Canonical grid: `256000` points at `64000` Hz.
- Output lengths: `[256000]`.
- Cross-measurement mixing: `False`.
- Split-dependent policy: `False`.
- Raw MAT mutation: `False`.
- Crop/pad remains diagnostic-only and cannot be selected.
