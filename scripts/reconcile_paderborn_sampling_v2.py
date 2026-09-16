from __future__ import annotations

"""Freeze a label-free canonical frequency grid for Paderborn Primary data."""

import argparse
import ctypes
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from datasets.paderborn import (
    PRIMARY_BY_LABEL,
    canonicalize_signal,
    discover_measurements,
    load_measurement,
)
from scripts import reconcile_paderborn_sampling as v1


FORMAL_POLICIES = ("timestamp_uniform_interpolation", "sample_index_resample")
DIAGNOSTIC_POLICY = "crop_edge_pad"
POLICIES = (*FORMAL_POLICIES, DIAGNOSTIC_POLICY)
MIN_AVAILABLE_RAM_MIB = 2048


def available_ram_mib() -> int:
    class MemoryStatus(ctypes.Structure):
        _fields_ = [
            ("length", ctypes.c_ulong), ("memory_load", ctypes.c_ulong),
            ("total_physical", ctypes.c_ulonglong), ("available_physical", ctypes.c_ulonglong),
            ("total_page_file", ctypes.c_ulonglong), ("available_page_file", ctypes.c_ulonglong),
            ("total_virtual", ctypes.c_ulonglong), ("available_virtual", ctypes.c_ulonglong),
            ("available_extended_virtual", ctypes.c_ulonglong),
        ]

    status = MemoryStatus()
    status.length = ctypes.sizeof(MemoryStatus)
    if os.name != "nt" or not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError("GlobalMemoryStatusEx is required by the Windows runtime protocol")
    return int(status.available_physical // (1024 * 1024))


def require_safe_ram() -> int:
    available = available_ram_mib()
    if available < MIN_AVAILABLE_RAM_MIB:
        raise RuntimeError(
            f"RAM_SAFETY_HOLD: available={available} MiB < {MIN_AVAILABLE_RAM_MIB} MiB"
        )
    return available


def atomic_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(value, encoding="utf-8")
    os.replace(temporary, path)


def load_policy(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if payload["formal_candidates"] != list(FORMAL_POLICIES):
        raise RuntimeError("formal sampling candidates changed")
    if payload["diagnostic_control"] != DIAGNOSTIC_POLICY:
        raise RuntimeError("crop/pad must remain diagnostic-only")
    if any(payload[key] for key in ("uses_labels", "uses_split", "uses_validation_or_test_metrics")):
        raise RuntimeError("sampling policy may not use labels, splits, validation, or test metrics")
    return payload


def aggregate_with_frozen_thresholds(
    rows: list[dict[str, Any]], policy: str, thresholds: dict[str, float]
) -> dict[str, Any]:
    result = v1.aggregate(rows, policy)
    checks = {
        "rms_ratio_median": abs(result["rms_ratio_median"] - 1.0)
        <= float(thresholds["rms_ratio_median_absolute_error_max"]),
        "welch_psd_cosine_p05": result["welch_psd_cosine_p05"]
        >= float(thresholds["welch_psd_cosine_p05_min"]),
        "log_psd_correlation_p05": result["log_psd_correlation_p05"]
        >= float(thresholds["log_psd_correlation_p05_min"]),
        "band_energy_max_relative_error_p95": result["band_energy_max_relative_error_p95"]
        <= float(thresholds["band_energy_max_relative_error_p95_max"]),
        "dominant_frequency_displacement_hz_p95": result["dominant_frequency_displacement_hz_p95"]
        <= float(thresholds["dominant_frequency_displacement_hz_p95_max"]),
    }
    result["threshold_checks"] = checks
    result["preservation_pass"] = bool(all(checks.values()))
    result["formal_candidate"] = policy in FORMAL_POLICIES
    return result


def select_formal_policy(summaries: list[dict[str, Any]]) -> str | None:
    passing = [
        row for row in summaries
        if row["formal_candidate"] and row["preservation_pass"]
    ]
    return min(passing, key=lambda row: row["distortion_score"])["policy"] if passing else None


def _representative_paths(rows: list[dict[str, Any]]) -> set[str]:
    selected = {row["relative_path"] for row in rows if int(row["measurement_index"]) == 1}
    for metric in ("N", "effective_fs", "dt_cv", "max_gap_over_nominal_dt"):
        ordered = sorted(rows, key=lambda row: float(row[metric]))
        selected.update(row["relative_path"] for row in ordered[:5])
        selected.update(row["relative_path"] for row in ordered[-5:])
    return selected


def _report(result: dict[str, Any]) -> str:
    table = []
    for row in result["policy_summary"]:
        table.append(
            f"| {row['policy']} | {row['formal_candidate']} | {row['preservation_pass']} | "
            f"{row['rms_ratio_median']:.6f} | {row['welch_psd_cosine_p05']:.6f} | "
            f"{row['log_psd_correlation_p05']:.6f} | "
            f"{row['band_energy_max_relative_error_p95']:.6f} | "
            f"{row['dominant_frequency_displacement_hz_p95']:.3f} |"
        )
    return f"""# Paderborn Sampling Reconciliation v2

Status: `{result['frequency_grid_gate']}`

The decision uses acquisition metadata and signal-preservation diagnostics only.
No class label, fold assignment, validation metric, test metric, or model result
participates in policy selection.

| Policy | Formal | Pass | Median RMS ratio | PSD cosine p05 | log-PSD corr p05 | band error p95 | dominant shift p95 Hz |
|---|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(table)}

Selected policy: `{result['selected_policy']}`.

- Primary universe: `{result['primary_measurements']}` measurements from `{result['primary_bearings']}` bearings.
- Canonical validation: `{result['canonicalized_files']}/1200` finite measurements.
- Canonical grid: `{result['target_length']}` points at `{result['target_hz']}` Hz.
- Output lengths: `{result['canonical_output_length_values']}`.
- Cross-measurement mixing: `False`.
- Split-dependent policy: `False`.
- Raw MAT mutation: `False`.
- Crop/pad remains diagnostic-only and cannot be selected.
"""


def _freeze_report(result: dict[str, Any], policy_config: Path) -> str:
    return f"""# Paderborn Frequency Grid Freeze

Status: `{result['frequency_grid_gate']}`

- Policy: `{result['selected_policy']}`
- Sampling rate: `{result['target_hz']}` Hz
- Duration: `4.0` seconds
- Length: `{result['target_length']}` samples
- Input channel: `vibration_1`
- Primary validation: `{result['canonicalized_files']}/1200` finite and fixed-length
- Policy config: `{policy_config.as_posix()}`
- Selection source: signal preservation only; no downstream classification
- Raw data: read-only

This grid is frozen before any Paderborn model training or test evaluation.
Changing it requires a new protocol version and invalidates downstream formal cells.
"""


def reconcile(
    data_root: Path,
    results_dir: Path,
    docs_dir: Path,
    policy_path: Path,
) -> dict[str, Any]:
    require_safe_ram()
    policy_config = load_policy(policy_path)
    primary = set().union(*map(set, PRIMARY_BY_LABEL.values()))
    measurements = [item for item in discover_measurements(data_root) if item.bearing_id in primary]
    counts = Counter(item.bearing_id for item in measurements)
    if len(measurements) != 1200 or len(counts) != 15 or set(counts.values()) != {80}:
        raise RuntimeError(f"PADERBORN_PRIMARY_DATA_HOLD: measurements={len(measurements)} counts={counts}")

    deep_rows: list[dict[str, Any]] = []
    for index, item in enumerate(measurements, 1):
        if index == 1 or index % 50 == 0:
            require_safe_ram()
        loaded = load_measurement(item)
        deep_rows.append(v1.deep_row(item, loaded.timestamps))
        if index % 100 == 0:
            print(f"[PADERBORN-GRID] deep-audit={index}/1200", flush=True)
    v1.write_csv(results_dir / "paderborn_primary_sampling_deep_audit.csv", deep_rows)

    representative_paths = _representative_paths(deep_rows)
    by_path = {item.relative_path: item for item in measurements}
    preservation_rows: list[dict[str, Any]] = []
    for index, relative_path in enumerate(sorted(representative_paths), 1):
        if index == 1 or index % 10 == 0:
            require_safe_ram()
        item = by_path[relative_path]
        loaded = load_measurement(item)
        for candidate in POLICIES:
            canonical = canonicalize_signal(
                loaded.signal, loaded.timestamps, candidate,
                int(policy_config["target_length"]), float(policy_config["target_hz"]),
            )
            preservation_rows.append({
                "bearing_id": item.bearing_id,
                "operating_condition": item.operating_condition,
                "measurement_index": item.measurement_index,
                "relative_path": relative_path,
                "policy": candidate,
                **v1.preservation_metrics(loaded.signal, canonical, loaded.timestamps, candidate),
            })
        if index % 10 == 0:
            print(f"[PADERBORN-GRID] preservation={index}/{len(representative_paths)}", flush=True)
    v1.write_csv(results_dir / "paderborn_sampling_policy_preservation_v2.csv", preservation_rows)

    thresholds = policy_config["preservation_thresholds"]
    summaries = [aggregate_with_frozen_thresholds(preservation_rows, item, thresholds) for item in POLICIES]
    selected = select_formal_policy(summaries)
    canonicalized = 0
    finite = True
    lengths: set[int] = set()
    if selected is not None:
        for index, item in enumerate(measurements, 1):
            if index == 1 or index % 50 == 0:
                require_safe_ram()
            loaded = load_measurement(item)
            signal = canonicalize_signal(
                loaded.signal, loaded.timestamps, selected,
                int(policy_config["target_length"]), float(policy_config["target_hz"]),
            )
            canonicalized += 1
            finite = finite and bool(np.isfinite(signal).all())
            lengths.add(len(signal))
            if index % 100 == 0:
                print(f"[PADERBORN-GRID] canonical-validation={index}/1200", flush=True)

    target_length = int(policy_config["target_length"])
    go = selected is not None and canonicalized == 1200 and finite and lengths == {target_length}
    result = {
        "status": "PADERBORN_SAMPLING_RECONCILIATION_V2_COMPLETE",
        "frequency_grid_gate": "PADERBORN_FREQUENCY_GRID_GO" if go else "PADERBORN_FREQUENCY_GRID_HOLD",
        "primary_measurements": len(measurements),
        "primary_bearings": len(counts),
        "measurements_per_bearing": dict(sorted(counts.items())),
        "representative_measurements": len(representative_paths),
        "policy_summary": summaries,
        "selected_policy": selected,
        "canonicalized_files": canonicalized,
        "canonical_all_finite": finite,
        "canonical_output_length_values": sorted(lengths),
        "target_hz": int(policy_config["target_hz"]),
        "target_length": target_length,
        "no_cross_measurement_mixing": True,
        "selection_uses_labels": False,
        "selection_uses_split": False,
        "selection_uses_validation_or_test_metrics": False,
        "raw_data_mutated": False,
    }
    atomic_text(
        results_dir / "paderborn_sampling_reconciliation_v2.json",
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
    )
    atomic_text(docs_dir / "PADERBORN_SAMPLING_RECONCILIATION.md", _report(result))
    atomic_text(docs_dir / "PADERBORN_FREQUENCY_GRID_FREEZE.md", _freeze_report(result, policy_path))
    frozen_config = dict(policy_config)
    frozen_config.update({"status": result["frequency_grid_gate"], "policy": selected})
    atomic_text(policy_path, yaml.safe_dump(frozen_config, sort_keys=False))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--results-dir", type=Path, default=Path("analysis/results"))
    parser.add_argument("--docs-dir", type=Path, default=Path("docs"))
    parser.add_argument("--policy", type=Path, default=Path("configs/paderborn_sampling_policy_v2.yaml"))
    args = parser.parse_args()
    result = reconcile(args.data_root, args.results_dir, args.docs_dir, args.policy)
    print(json.dumps({
        "status": result["status"],
        "selected_policy": result["selected_policy"],
        "canonicalized_files": result["canonicalized_files"],
        "frequency_grid_gate": result["frequency_grid_gate"],
    }, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
