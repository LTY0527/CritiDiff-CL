from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any, Sequence

import numpy as np


FILENAME_PATTERN = re.compile(
    r"^(?P<speed>N\d+)_(?P<torque>M\d+)_(?P<force>F\d+)_"
    r"(?P<bearing>K[A-Z]?\d+)_(?P<measurement>\d+)\.mat$",
    re.IGNORECASE,
)

HEALTHY = ("K001", "K002", "K003", "K004", "K005", "K006")
ARTIFICIAL_OUTER = ("KA01", "KA03", "KA05", "KA06", "KA07", "KA08", "KA09")
ARTIFICIAL_INNER = ("KI01", "KI03", "KI05", "KI07", "KI08")
REAL_OUTER = ("KA04", "KA15", "KA16", "KA22", "KA30")
REAL_INNER = ("KI04", "KI14", "KI16", "KI17", "KI18", "KI21")
REAL_MIXED = ("KB23", "KB24", "KB27")

PRIMARY_BY_LABEL = {
    0: ("K001", "K002", "K003", "K004", "K005"),
    1: REAL_OUTER,
    2: ("KI04", "KI14", "KI16", "KI18", "KI21"),
}
PRIMARY_LABEL_NAMES = {0: "healthy", 1: "real_outer_ring", 2: "real_inner_ring"}


@dataclass(frozen=True)
class BearingMetadata:
    bearing_id: str
    health_state: str
    damage_source: str
    damage_location: str
    primary_candidate: bool
    notes: str = ""


@dataclass(frozen=True)
class PaderbornMeasurement:
    path: Path
    relative_path: str
    bearing_id: str
    speed_code: str
    torque_code: str
    force_code: str
    operating_condition: str
    measurement_index: int


@dataclass(frozen=True)
class PaderbornSignal:
    signal: np.ndarray
    timestamps: np.ndarray
    channel_name: str
    x_index_matlab: int
    downsampling: int
    top_level_name: str
    channel_names: tuple[str, ...]
    channel_lengths: tuple[int, ...]
    channel_x_indices: tuple[int, ...]
    channel_downsampling: tuple[int, ...]
    x_count: int
    info_fields: tuple[str, ...]


def bearing_metadata() -> dict[str, BearingMetadata]:
    rows: dict[str, BearingMetadata] = {}
    for bearing in HEALTHY:
        rows[bearing] = BearingMetadata(
            bearing, "healthy", "healthy", "none", bearing in PRIMARY_BY_LABEL[0]
        )
    for bearing in ARTIFICIAL_OUTER:
        rows[bearing] = BearingMetadata(bearing, "damaged", "artificial", "outer_ring", False)
    for bearing in ARTIFICIAL_INNER:
        rows[bearing] = BearingMetadata(bearing, "damaged", "artificial", "inner_ring", False)
    for bearing in REAL_OUTER:
        rows[bearing] = BearingMetadata(
            bearing, "damaged", "real", "outer_ring", bearing in PRIMARY_BY_LABEL[1]
        )
    for bearing in REAL_INNER:
        note = "held out from Primary candidate" if bearing == "KI17" else ""
        rows[bearing] = BearingMetadata(
            bearing, "damaged", "real", "inner_ring_dominant",
            bearing in PRIMARY_BY_LABEL[2], note,
        )
    for bearing in REAL_MIXED:
        rows[bearing] = BearingMetadata(
            bearing, "damaged", "real", "mixed_combined", False,
            "mixed damage; never relabel as pure outer or inner",
        )
    return rows


def parse_measurement_filename(path: Path | str, data_root: Path | str | None = None) -> PaderbornMeasurement:
    source = Path(path)
    match = FILENAME_PATTERN.fullmatch(source.name)
    if match is None:
        raise ValueError(f"unrecognized Paderborn filename: {source.name}")
    values = {key: value.upper() for key, value in match.groupdict().items() if key != "measurement"}
    root = Path(data_root) if data_root is not None else source.parent
    try:
        relative = source.relative_to(root).as_posix()
    except ValueError:
        relative = source.name
    return PaderbornMeasurement(
        source,
        relative,
        values["bearing"],
        values["speed"],
        values["torque"],
        values["force"],
        f"{values['speed']}_{values['torque']}_{values['force']}",
        int(match.group("measurement")),
    )


def discover_measurements(data_root: Path | str) -> list[PaderbornMeasurement]:
    root = Path(data_root)
    if not root.is_dir():
        raise FileNotFoundError(f"Paderborn data root not found: {root}")
    metadata = bearing_metadata()
    measurements: list[PaderbornMeasurement] = []
    for path in sorted(root.rglob("*.mat")):
        item = parse_measurement_filename(path, root)
        relative_parts = path.relative_to(root).parts
        if not relative_parts or relative_parts[0].upper() != item.bearing_id:
            raise ValueError(f"bearing directory/filename mismatch: {item.relative_path}")
        if item.bearing_id not in metadata:
            raise ValueError(f"bearing metadata missing for {item.bearing_id}")
        measurements.append(item)
    if not measurements:
        raise FileNotFoundError(f"no Paderborn MAT files found below {root}")
    return measurements


def _struct_array(value: Any) -> list[Any]:
    return list(np.atleast_1d(value).reshape(-1))


def _field_names(value: Any) -> tuple[str, ...]:
    return tuple(getattr(value, "_fieldnames", ()) or ())


def load_measurement(
    measurement: PaderbornMeasurement | Path | str,
    channel_name: str = "vibration_1",
) -> PaderbornSignal:
    from scipy.io import loadmat

    path = measurement.path if isinstance(measurement, PaderbornMeasurement) else Path(measurement)
    payload = loadmat(path, squeeze_me=True, struct_as_record=False)
    roots = [(key, value) for key, value in payload.items() if not key.startswith("__")]
    if len(roots) != 1:
        raise ValueError(f"expected one top-level MATLAB struct in {path.name}, found {len(roots)}")
    top_level_name, root = roots[0]
    required = {"Info", "X", "Y", "Description"}
    if not required.issubset(_field_names(root)):
        raise ValueError(f"MAT schema missing {sorted(required - set(_field_names(root)))} in {path.name}")
    x_axes = _struct_array(root.X)
    channels = _struct_array(root.Y)
    names = tuple(str(getattr(channel, "Name", "")) for channel in channels)
    matches = [channel for channel, name in zip(channels, names) if name == channel_name]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one {channel_name!r} channel in {path.name}, found {len(matches)}")
    channel = matches[0]
    x_index = int(channel.XIndex)
    downsampling = int(channel.DownSampling)
    if not 1 <= x_index <= len(x_axes):
        raise ValueError(f"invalid MATLAB XIndex={x_index} in {path.name}")
    if downsampling <= 0:
        raise ValueError(f"invalid DownSampling={downsampling} in {path.name}")
    signal = np.asarray(channel.Data, dtype=np.float64).reshape(-1)
    base_timestamps = np.asarray(x_axes[x_index - 1].Data, dtype=np.float64).reshape(-1)
    timestamps = base_timestamps[::downsampling]
    if len(timestamps) != len(signal):
        raise ValueError(
            f"timestamp/signal length mismatch in {path.name}: {len(timestamps)} != {len(signal)}"
        )
    return PaderbornSignal(
        signal=signal,
        timestamps=timestamps,
        channel_name=channel_name,
        x_index_matlab=x_index,
        downsampling=downsampling,
        top_level_name=top_level_name,
        channel_names=names,
        channel_lengths=tuple(len(np.asarray(channel.Data).reshape(-1)) for channel in channels),
        channel_x_indices=tuple(int(channel.XIndex) for channel in channels),
        channel_downsampling=tuple(int(channel.DownSampling) for channel in channels),
        x_count=len(x_axes),
        info_fields=_field_names(root.Info),
    )


def window_signal(
    signal: np.ndarray,
    length: int,
    stride: int,
    limit: int | None = None,
) -> np.ndarray:
    if length <= 0 or stride <= 0:
        raise ValueError("window length and stride must be positive")
    values = np.asarray(signal)
    starts = list(range(0, len(values) - length + 1, stride))
    if limit is not None:
        if limit <= 0:
            raise ValueError("window limit must be positive")
        starts = starts[:limit]
    if not starts:
        raise ValueError("signal is shorter than the requested window")
    return np.stack([values[start:start + length] for start in starts])[:, None, :].astype(np.float32)


def canonicalize_signal(
    signal: np.ndarray,
    timestamps: np.ndarray,
    policy: str,
    target_length: int = 256_000,
    target_hz: float = 64_000.0,
) -> np.ndarray:
    """Map one measurement to a fixed, label-independent nominal acquisition grid."""
    values = np.asarray(signal, dtype=np.float64).reshape(-1)
    times = np.asarray(timestamps, dtype=np.float64).reshape(-1)
    if len(values) != len(times) or len(values) < 2:
        raise ValueError("canonicalization requires aligned signal/timestamps with at least two samples")
    if target_length <= 0 or target_hz <= 0:
        raise ValueError("canonical target length and sampling rate must be positive")
    if not np.isfinite(values).all() or not np.isfinite(times).all():
        raise ValueError("canonicalization input contains NaN or Inf")
    if np.any(np.diff(times) <= 0):
        raise ValueError("timestamp interpolation requires a strictly increasing time axis")
    if policy == "timestamp_uniform_interpolation":
        relative = times - times[0]
        target = np.arange(target_length, dtype=np.float64) / float(target_hz)
        output = np.interp(target, relative, values, left=values[0], right=values[-1])
    elif policy == "sample_index_resample":
        from scipy.signal import resample

        output = resample(values, target_length)
    elif policy == "crop_edge_pad":
        if len(values) >= target_length:
            output = values[:target_length].copy()
        else:
            output = np.pad(values, (0, target_length - len(values)), mode="edge")
    else:
        raise ValueError(f"unknown Paderborn canonicalization policy: {policy}")
    output = np.asarray(np.real(output), dtype=np.float32)
    if output.shape != (target_length,) or not np.isfinite(output).all():
        raise ValueError("canonicalization did not produce a finite fixed-length signal")
    return output


def primary_five_fold_protocol() -> list[dict[str, tuple[str, ...]]]:
    folds: list[dict[str, tuple[str, ...]]] = []
    for fold in range(5):
        split: dict[str, list[str]] = {"train": [], "validation": [], "test": []}
        for bearings in PRIMARY_BY_LABEL.values():
            split["test"].append(bearings[fold])
            split["validation"].append(bearings[(fold + 1) % 5])
            split["train"].extend(
                bearing for index, bearing in enumerate(bearings)
                if index not in {fold, (fold + 1) % 5}
            )
        frozen = {name: tuple(sorted(values)) for name, values in split.items()}
        validate_bearing_split(frozen)
        folds.append(frozen)
    return folds


def validate_bearing_split(split: dict[str, Sequence[str]]) -> None:
    names = ("train", "validation", "test")
    if any(name not in split for name in names):
        raise ValueError("bearing split must define train, validation, and test")
    groups = [set(split[name]) for name in names]
    if any(groups[i] & groups[j] for i in range(3) for j in range(i + 1, 3)):
        raise ValueError("bearing leakage detected")
    primary = set().union(*map(set, PRIMARY_BY_LABEL.values()))
    if set().union(*groups) != primary:
        raise ValueError("bearing split must cover the 15 Primary bearings exactly")
    metadata = bearing_metadata()
    for name, expected_per_class in (("train", 3), ("validation", 1), ("test", 1)):
        counts = {label: 0 for label in PRIMARY_BY_LABEL}
        for bearing in split[name]:
            for label, bearings in PRIMARY_BY_LABEL.items():
                counts[label] += int(bearing in bearings)
        if set(counts.values()) != {expected_per_class}:
            raise ValueError(f"{name} does not have balanced bearing-level class coverage: {counts}")
        if any(bearing not in metadata for bearing in split[name]):
            raise ValueError(f"unknown bearing in {name}")
