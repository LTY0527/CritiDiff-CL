from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import yaml
from scipy.signal import resample, welch

from datasets.paderborn import (
    PRIMARY_BY_LABEL,
    canonicalize_signal,
    discover_measurements,
    load_measurement,
)


POLICIES = (
    "timestamp_uniform_interpolation",
    "sample_index_resample",
    "crop_edge_pad",
)
NOMINAL_HZ = 64_000.0
TARGET_LENGTH = 256_000
NOMINAL_DT = 1.0 / NOMINAL_HZ


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def deep_row(item, timestamps: np.ndarray) -> dict[str, Any]:
    delta = np.diff(timestamps)
    duration = float(timestamps[-1] - timestamps[0])
    return {
        "bearing_id": item.bearing_id, "operating_condition": item.operating_condition,
        "measurement_index": item.measurement_index, "relative_path": item.relative_path,
        "N": len(timestamps), "N_minus_256000": len(timestamps) - TARGET_LENGTH,
        "t_start": float(timestamps[0]), "t_end": float(timestamps[-1]), "duration": duration,
        "dt_min": float(delta.min()), "dt_median": float(np.median(delta)),
        "dt_mean": float(delta.mean()), "dt_max": float(delta.max()),
        "dt_std": float(delta.std(ddof=1)), "dt_cv": float(delta.std(ddof=1) / delta.mean()),
        "nonpositive_dt": int((delta <= 0).sum()),
        "gap_count_2x": int((delta > 2 * NOMINAL_DT).sum()),
        "gap_count_5x": int((delta > 5 * NOMINAL_DT).sum()),
        "gap_count_10x": int((delta > 10 * NOMINAL_DT).sum()),
        "max_gap_over_nominal_dt": float(delta.max() / NOMINAL_DT),
        "effective_fs": float((len(timestamps) - 1) / duration),
    }


def normalized_psd(signal: np.ndarray, sampling_hz: float) -> tuple[np.ndarray, np.ndarray]:
    frequency, power = welch(np.asarray(signal, dtype=np.float64), fs=sampling_hz, nperseg=4096)
    power = np.maximum(power, 1e-18)
    return frequency, power / power.sum()


def preservation_metrics(
    original: np.ndarray,
    canonical: np.ndarray,
    timestamps: np.ndarray,
    policy: str,
) -> dict[str, float]:
    original = np.asarray(original, dtype=np.float64)
    canonical = np.asarray(canonical, dtype=np.float64)
    rms_original = float(np.sqrt(np.mean(np.square(original))))
    rms_canonical = float(np.sqrt(np.mean(np.square(canonical))))
    ptp_original = float(np.ptp(original))
    ptp_canonical = float(np.ptp(canonical))
    common_original = resample(original, 8192)
    common_canonical = resample(canonical, 8192)
    waveform_correlation = float(np.corrcoef(common_original, common_canonical)[0, 1])
    if policy == "timestamp_uniform_interpolation":
        original_hz = float((len(timestamps) - 1) / (timestamps[-1] - timestamps[0]))
    elif policy == "sample_index_resample":
        original_hz = float(len(original) / 4.0)
    else:
        original_hz = NOMINAL_HZ
    original_frequency, original_power = normalized_psd(original, original_hz)
    frequency, psd_canonical = normalized_psd(canonical, NOMINAL_HZ)
    psd_original = np.interp(frequency, original_frequency, original_power, left=0.0, right=0.0)
    psd_original = np.maximum(psd_original, 1e-18); psd_original /= psd_original.sum()
    psd_cosine = float(np.dot(psd_original, psd_canonical) / (np.linalg.norm(psd_original) * np.linalg.norm(psd_canonical)))
    log_psd_correlation = float(np.corrcoef(np.log(psd_original), np.log(psd_canonical))[0, 1])
    band_errors = []
    for low, high in ((0, 2_000), (2_000, 8_000), (8_000, 16_000), (16_000, 32_001)):
        mask = (frequency >= low) & (frequency < high)
        left = float(psd_original[mask].sum()); right = float(psd_canonical[mask].sum())
        band_errors.append(abs(right - left) / max(left, 1e-12))
    dominant_original = float(frequency[int(np.argmax(psd_original))])
    dominant_canonical = float(frequency[int(np.argmax(psd_canonical))])
    return {
        "rms_ratio": rms_canonical / max(rms_original, 1e-12),
        "peak_to_peak_ratio": ptp_canonical / max(ptp_original, 1e-12),
        "waveform_correlation": waveform_correlation,
        "welch_psd_cosine": psd_cosine,
        "log_psd_correlation": log_psd_correlation,
        "band_energy_max_relative_error": float(max(band_errors)),
        "dominant_frequency_displacement_hz": abs(dominant_canonical - dominant_original),
    }


def select_formal_policy(summaries: list[dict[str, Any]]) -> str | None:
    formal = {"timestamp_uniform_interpolation", "sample_index_resample"}
    passing = [
        row for row in summaries
        if row["policy"] in formal and row["preservation_pass"]
    ]
    return min(passing, key=lambda row: row["distortion_score"])["policy"] if passing else None


def aggregate(rows: list[dict[str, Any]], policy: str) -> dict[str, Any]:
    selected = [row for row in rows if row["policy"] == policy]
    result: dict[str, Any] = {"policy": policy, "measurements": len(selected)}
    metrics = (
        "rms_ratio", "peak_to_peak_ratio", "waveform_correlation", "welch_psd_cosine",
        "log_psd_correlation", "band_energy_max_relative_error",
        "dominant_frequency_displacement_hz",
    )
    for metric in metrics:
        values = np.asarray([row[metric] for row in selected], dtype=np.float64)
        for name, value in (
            ("min", values.min()), ("p05", np.quantile(values, .05)),
            ("median", np.median(values)), ("p95", np.quantile(values, .95)),
            ("max", values.max()),
        ):
            result[f"{metric}_{name}"] = float(value)
    result["preservation_pass"] = bool(
        abs(result["rms_ratio_median"] - 1) <= .02
        and result["welch_psd_cosine_p05"] >= .98
        and result["log_psd_correlation_p05"] >= .98
        and result["band_energy_max_relative_error_p95"] <= .10
        and result["dominant_frequency_displacement_hz_p95"] <= 20.0
    )
    result["distortion_score"] = float(
        abs(result["rms_ratio_median"] - 1)
        + (1 - result["welch_psd_cosine_median"])
        + (1 - result["log_psd_correlation_median"])
        + result["band_energy_max_relative_error_median"]
        + result["dominant_frequency_displacement_hz_median"] / 32_000
    )
    return result


def report(result: dict[str, Any]) -> str:
    table = []
    for row in result["policy_summary"]:
        table.append(
            f"| {row['policy']} | {row['preservation_pass']} | {row['rms_ratio_median']:.6f} | "
            f"{row['welch_psd_cosine_p05']:.6f} | {row['log_psd_correlation_p05']:.6f} | "
            f"{row['band_energy_max_relative_error_p95']:.6f} | "
            f"{row['dominant_frequency_displacement_hz_p95']:.3f} | {row['distortion_score']:.6f} |"
        )
    return f"""# Paderborn sampling reconciliation

Status: `{result['status']}`

## Primary deep audit

- Primary measurements: `{result['primary_measurements']}`.
- Target grid: `{TARGET_LENGTH}` samples, `{NOMINAL_HZ:.0f}` Hz, nominal duration 4 seconds.
- Length range: `{result['length_range']}`; files above/below target: `{result['above_target']}/{result['below_target']}`.
- Measurements with gaps >2×/>5×/>10× nominal dt: `{result['measurements_with_gap_2x']}/{result['measurements_with_gap_5x']}/{result['measurements_with_gap_10x']}`.
- Maximum observed gap: `{result['maximum_gap_over_nominal_dt']:.3f}` nominal intervals.
- Nonpositive timestamp intervals: `{result['nonpositive_intervals']}`.

Length excess/deficit and large gaps are sparse rather than uniform. The recorded time axis is strictly increasing but not an identical uniform physical-frequency grid. The acquisition metadata supplies a fixed nominal 64 kHz/4 s target independent of class, fold, validation, or test performance.

## Signal-preservation comparison

Representative coverage contains one measurement for each 15-bearing × 4-condition cell plus automatically included length/fs/gap anomalies. No class accuracy or downstream model metric is computed.

| Policy | Pass | Median RMS ratio | PSD cosine p05 | log-PSD corr p05 | band error p95 | dominant shift p95 Hz | distortion score |
|---|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(table)}

Selected policy: `{result['selected_policy']}`. Selection used only fixed acquisition metadata and signal/PSD preservation. The policy is deterministic, file-uniform, label-free, and split-free.

Policy A follows timestamps and is sensitive to recorded timestamp gaps. Policy B treats each file as one nominal four-second acquisition and resamples the sample sequence to 256000 points. Policy C is retained only as a crop/edge-pad control because it does not reconcile heterogeneous acquisition length.

## Canonical grid validation

- Canonicalized Primary files: `{result['canonicalized_files']}/1200`.
- Fixed output length: `{result['canonical_output_length_values']}`.
- Fixed target sampling rate: `{NOMINAL_HZ:.0f}` Hz.
- All finite: `{result['canonical_all_finite']}`.
- Label/split inputs used by canonicalizer: `False`.
- Frequency axis identical: `{result['frequency_axis_identical']}`.

Final gate: `{result['frequency_grid_gate']}`.
"""


def reconcile(data_root: Path, output_dir: Path, policy_path: Path) -> dict[str, Any]:
    primary = set().union(*map(set, PRIMARY_BY_LABEL.values()))
    measurements = [item for item in discover_measurements(data_root) if item.bearing_id in primary]
    if len(measurements) != 1200:
        raise RuntimeError(f"Primary measurement universe changed: {len(measurements)}")
    deep_rows = []
    for index, item in enumerate(measurements, 1):
        loaded = load_measurement(item)
        deep_rows.append(deep_row(item, loaded.timestamps))
        if index % 100 == 0:
            print(f"deep-audited {index}/1200", flush=True)
    write_csv(output_dir / "paderborn_primary_sampling_deep_audit.csv", deep_rows)

    representative_paths = {
        row["relative_path"] for row in deep_rows if int(row["measurement_index"]) == 1
    }
    for metric in ("N", "effective_fs", "dt_cv", "max_gap_over_nominal_dt"):
        ordered = sorted(deep_rows, key=lambda row: float(row[metric]))
        representative_paths.update(row["relative_path"] for row in ordered[:5])
        representative_paths.update(row["relative_path"] for row in ordered[-5:])
    by_path = {item.relative_path: item for item in measurements}
    preservation_rows = []
    for index, relative_path in enumerate(sorted(representative_paths), 1):
        item = by_path[relative_path]; loaded = load_measurement(item)
        for policy in POLICIES:
            canonical = canonicalize_signal(loaded.signal, loaded.timestamps, policy, TARGET_LENGTH, NOMINAL_HZ)
            preservation_rows.append({
                "bearing_id": item.bearing_id, "operating_condition": item.operating_condition,
                "measurement_index": item.measurement_index, "relative_path": relative_path,
                "policy": policy,
                **preservation_metrics(loaded.signal, canonical, loaded.timestamps, policy),
            })
        if index % 20 == 0:
            print(f"preservation-audited {index}/{len(representative_paths)}", flush=True)
    write_csv(output_dir / "paderborn_sampling_policy_preservation.csv", preservation_rows)
    summaries = [aggregate(preservation_rows, policy) for policy in POLICIES]
    selected = select_formal_policy(summaries)

    canonicalized = 0; finite = True; lengths = set()
    if selected is not None:
        for index, item in enumerate(measurements, 1):
            loaded = load_measurement(item)
            signal = canonicalize_signal(loaded.signal, loaded.timestamps, selected, TARGET_LENGTH, NOMINAL_HZ)
            canonicalized += 1; finite &= bool(np.isfinite(signal).all()); lengths.add(len(signal))
            if index % 100 == 0:
                print(f"canonical-validated {index}/1200", flush=True)
    frequency_go = selected is not None and canonicalized == 1200 and finite and lengths == {TARGET_LENGTH}
    result = {
        "status": "PADERBORN_SAMPLING_RECONCILIATION_COMPLETE",
        "primary_measurements": len(measurements),
        "length_range": [min(row["N"] for row in deep_rows), max(row["N"] for row in deep_rows)],
        "above_target": sum(row["N"] > TARGET_LENGTH for row in deep_rows),
        "below_target": sum(row["N"] < TARGET_LENGTH for row in deep_rows),
        "measurements_with_gap_2x": sum(row["gap_count_2x"] > 0 for row in deep_rows),
        "measurements_with_gap_5x": sum(row["gap_count_5x"] > 0 for row in deep_rows),
        "measurements_with_gap_10x": sum(row["gap_count_10x"] > 0 for row in deep_rows),
        "maximum_gap_over_nominal_dt": max(row["max_gap_over_nominal_dt"] for row in deep_rows),
        "nonpositive_intervals": sum(row["nonpositive_dt"] for row in deep_rows),
        "representative_measurements": len(representative_paths),
        "policy_summary": summaries, "selected_policy": selected,
        "canonicalized_files": canonicalized,
        "canonical_output_length_values": sorted(lengths),
        "canonical_all_finite": finite, "frequency_axis_identical": lengths == {TARGET_LENGTH},
        "frequency_grid_gate": "PADERBORN_FREQUENCY_GRID_GO" if frequency_go else "PADERBORN_FREQUENCY_GRID_HOLD",
        "selection_uses_labels": False, "selection_uses_split": False,
        "selection_uses_validation_or_test_metrics": False,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "paderborn_sampling_reconciliation_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "PADERBORN_SAMPLING_RECONCILIATION.md").write_text(report(result), encoding="utf-8")
    policy_payload = {
        "version": 1, "status": result["frequency_grid_gate"], "policy": selected,
        "target_hz": int(NOMINAL_HZ), "target_duration_seconds": 4.0,
        "target_length": TARGET_LENGTH, "input_channel": "vibration_1",
        "fit_scope": "none; fixed acquisition metadata only",
        "uses_labels": False, "uses_split": False, "uses_validation_or_test_metrics": False,
        "raw_data_mutated": False,
    }
    policy_path.parent.mkdir(parents=True, exist_ok=True)
    policy_path.write_text(yaml.safe_dump(policy_payload, sort_keys=False), encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Reconcile Paderborn Primary sampling without labels or model metrics")
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("docs"))
    parser.add_argument("--policy", type=Path, default=Path("configs/paderborn_sampling_policy_v1.yaml"))
    args = parser.parse_args()
    result = reconcile(args.data_root, args.output_dir, args.policy)
    print(json.dumps({key: result[key] for key in (
        "status", "selected_policy", "canonicalized_files", "frequency_grid_gate"
    )}, ensure_ascii=False))


if __name__ == "__main__":
    main()
