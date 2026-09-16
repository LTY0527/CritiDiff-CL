# Paderborn Frequency Grid Freeze

Status: `PADERBORN_FREQUENCY_GRID_GO`

- Policy: `sample_index_resample`
- Sampling rate: `64000` Hz
- Duration: `4.0` seconds
- Length: `256000` samples
- Input channel: `vibration_1`
- Primary validation: `1200/1200` finite and fixed-length
- Policy config: `configs/paderborn_sampling_policy_v2.yaml`
- Selection source: signal preservation only; no downstream classification
- Raw data: read-only

This grid is frozen before any Paderborn model training or test evaluation.
Changing it requires a new protocol version and invalidates downstream formal cells.
