import csv
import inspect
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from datasets.paderborn import (
    PRIMARY_BY_LABEL,
    bearing_metadata,
    canonicalize_signal,
    discover_measurements,
    load_measurement,
    parse_measurement_filename,
    primary_five_fold_protocol,
    validate_bearing_split,
    window_signal,
)
from scripts.reconcile_paderborn_sampling import select_formal_policy
from scripts.reconcile_paderborn_sampling_v2 import (
    aggregate_with_frozen_thresholds,
    select_formal_policy as select_formal_policy_v2,
)
from scripts.run_paderborn_external_v2 import (
    METHODS as PADERBORN_METHODS,
    aggregate_predictions,
    bearing_grouped_bootstrap,
    d_only_criticality,
    label_for_bearing,
    protocol_lock_check,
    selected_starts,
)


def test_filename_parsing_extracts_bearing_condition_and_index():
    item = parse_measurement_filename("N15_M07_F10_KA04_20.mat")
    assert item.bearing_id == "KA04"
    assert item.operating_condition == "N15_M07_F10"
    assert (item.speed_code, item.torque_code, item.force_code) == ("N15", "M07", "F10")
    assert item.measurement_index == 20


def test_filename_parser_rejects_unrecognized_names():
    with pytest.raises(ValueError, match="unrecognized Paderborn filename"):
        parse_measurement_filename("K001_measurement.mat")


def test_recursive_discovery_supports_nested_bearing_directory(tmp_path: Path):
    nested = tmp_path / "K001" / "K001"
    nested.mkdir(parents=True)
    (nested / "N09_M07_F10_K001_1.mat").touch()
    items = discover_measurements(tmp_path)
    assert len(items) == 1
    assert items[0].relative_path == "K001/K001/N09_M07_F10_K001_1.mat"


def _mock_mat(channel_name: str = "vibration_1", x_index: int = 2, signal_length: int = 4):
    x = [
        SimpleNamespace(Data=np.arange(2.0), _fieldnames=["Data"]),
        SimpleNamespace(Data=np.arange(signal_length, dtype=float) / 10, _fieldnames=["Data"]),
    ]
    y = [
        SimpleNamespace(Name="force", Data=np.arange(2.0), XIndex=1, DownSampling=1),
        SimpleNamespace(
            Name=channel_name, Data=np.arange(signal_length, dtype=float),
            XIndex=x_index, DownSampling=1,
        ),
    ]
    root = SimpleNamespace(
        Info=SimpleNamespace(_fieldnames=["Date"]), X=np.asarray(x, dtype=object),
        Y=np.asarray(y, dtype=object), Description="fixture",
        _fieldnames=["Info", "X", "Y", "Description"],
    )
    return {"fixture": root}


def test_mat_loader_locates_channel_by_name_and_converts_matlab_xindex(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("scipy.io.loadmat", lambda *args, **kwargs: _mock_mat())
    loaded = load_measurement(Path("fixture.mat"))
    assert loaded.channel_name == "vibration_1"
    assert loaded.x_index_matlab == 2
    np.testing.assert_array_equal(loaded.timestamps, np.arange(4, dtype=float) / 10)
    np.testing.assert_array_equal(loaded.signal, np.arange(4, dtype=float))


def test_mat_loader_rejects_missing_vibration_channel(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("scipy.io.loadmat", lambda *args, **kwargs: _mock_mat("not_vibration"))
    with pytest.raises(ValueError, match="exactly one 'vibration_1'"):
        load_measurement(Path("fixture.mat"))


def test_mat_loader_rejects_invalid_xindex(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("scipy.io.loadmat", lambda *args, **kwargs: _mock_mat(x_index=3))
    with pytest.raises(ValueError, match="invalid MATLAB XIndex"):
        load_measurement(Path("fixture.mat"))


def test_bearing_metadata_keeps_mixed_damage_separate():
    metadata = bearing_metadata()
    assert len(metadata) == 32
    assert metadata["KB23"].damage_location == "mixed_combined"
    assert not metadata["KB23"].primary_candidate
    assert metadata["KI17"].damage_location == "inner_ring_dominant"
    assert not metadata["KI17"].primary_candidate


def test_primary_folds_are_balanced_and_bearing_disjoint():
    folds = primary_five_fold_protocol()
    assert len(folds) == 5
    expected = set().union(*map(set, PRIMARY_BY_LABEL.values()))
    for split in folds:
        assert tuple(map(len, (split["train"], split["validation"], split["test"]))) == (9, 3, 3)
        assert set(split["train"]) | set(split["validation"]) | set(split["test"]) == expected
        validate_bearing_split(split)


def test_bearing_leakage_is_rejected():
    split = primary_five_fold_protocol()[0]
    leaking = {name: tuple(values) for name, values in split.items()}
    leaking["test"] = leaking["test"] + (leaking["train"][0],)
    with pytest.raises(ValueError, match="bearing leakage"):
        validate_bearing_split(leaking)


def test_window_shape_is_batch_channel_time_float32():
    windows = window_signal(np.arange(12, dtype=np.float64), length=4, stride=2)
    assert windows.shape == (5, 1, 4)
    assert windows.dtype == np.float32
    assert np.isfinite(windows).all()


def test_windowing_rejects_short_signal():
    with pytest.raises(ValueError, match="shorter"):
        window_signal(np.arange(3), length=4, stride=1)


@pytest.mark.parametrize(
    "policy", ["timestamp_uniform_interpolation", "sample_index_resample", "crop_edge_pad"]
)
def test_canonicalization_policies_are_fixed_length_finite_and_label_free(policy: str):
    timestamps = np.linspace(-1e-5, 1.0, 1001)
    signal = np.sin(2 * np.pi * 10 * (timestamps - timestamps[0]))
    output = canonicalize_signal(signal, timestamps, policy, target_length=1000, target_hz=1000)
    assert output.shape == (1000,)
    assert output.dtype == np.float32
    assert np.isfinite(output).all()


def test_timestamp_canonicalization_rejects_nonmonotonic_axis():
    with pytest.raises(ValueError, match="strictly increasing"):
        canonicalize_signal(np.arange(3), np.asarray([0.0, 0.2, 0.1]), "timestamp_uniform_interpolation", 3, 10)


def test_crop_pad_control_cannot_be_selected_as_formal_policy():
    rows = [
        {"policy": "timestamp_uniform_interpolation", "preservation_pass": False, "distortion_score": 0.2},
        {"policy": "sample_index_resample", "preservation_pass": True, "distortion_score": 0.1},
        {"policy": "crop_edge_pad", "preservation_pass": True, "distortion_score": 0.0},
    ]
    assert select_formal_policy(rows) == "sample_index_resample"
    rows[1]["preservation_pass"] = False
    assert select_formal_policy(rows) is None


def test_frozen_primary_csv_matches_adapter_folds():
    with Path("configs/paderborn_primary_5fold.csv").open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 75
    folds = primary_five_fold_protocol()
    for fold_index, fold in enumerate(folds):
        for split, bearings in fold.items():
            actual = {
                row["bearing_id"] for row in rows
                if int(row["fold"]) == fold_index and row["split"] == split
            }
            assert actual == set(bearings)


def test_v2_sampling_gate_uses_frozen_signal_thresholds() -> None:
    thresholds = {
        "rms_ratio_median_absolute_error_max": 0.02,
        "welch_psd_cosine_p05_min": 0.95,
        "log_psd_correlation_p05_min": 0.90,
        "band_energy_max_relative_error_p95_max": 0.10,
        "dominant_frequency_displacement_hz_p95_max": 32.0,
    }
    rows = []
    for policy, psd in (("timestamp_uniform_interpolation", 0.80), ("sample_index_resample", 0.99),
                        ("crop_edge_pad", 1.0)):
        for _ in range(20):
            rows.append({
                "policy": policy, "rms_ratio": 1.0, "peak_to_peak_ratio": 1.0,
                "waveform_correlation": 1.0, "welch_psd_cosine": psd,
                "log_psd_correlation": psd, "band_energy_max_relative_error": 0.01,
                "dominant_frequency_displacement_hz": 0.0,
            })
    summaries = [aggregate_with_frozen_thresholds(rows, policy, thresholds) for policy in (
        "timestamp_uniform_interpolation", "sample_index_resample", "crop_edge_pad"
    )]
    assert select_formal_policy_v2(summaries) == "sample_index_resample"
    assert summaries[2]["preservation_pass"] is True
    assert summaries[2]["formal_candidate"] is False


def test_external_v2_frozen_matrix_and_d_only_labels() -> None:
    assert PADERBORN_METHODS == (
        "NO_AUG", "UNIFORM_DIFFUSION", "QDIFFCL_D_ONLY_EXTERNAL_COMPONENT"
    )
    assert label_for_bearing("K001") == 0
    assert label_for_bearing("KA04") == 1
    assert label_for_bearing("KI04") == 2


def test_even_stride_grid_window_selection_is_deterministic() -> None:
    first = selected_starts(4096, 2048, 256000, 16)
    second = selected_starts(4096, 2048, 256000, 16)
    np.testing.assert_array_equal(first, second)
    assert len(first) == len(np.unique(first)) == 16
    assert first[0] == 0
    assert first[-1] == 251904
    assert np.all(first % 2048 == 0)


def test_measurement_and_bearing_aggregation_do_not_mix_groups() -> None:
    bundle = {
        "relative_path": np.asarray(["a", "a", "b", "b"]),
        "bearing_id": np.asarray(["K001", "K001", "KA04", "KA04"]),
        "condition": np.asarray(["c1", "c1", "c2", "c2"]),
        "label": np.asarray([0, 0, 1, 1]),
    }
    probability = np.asarray([[.8, .1, .1], [.6, .3, .1], [.1, .7, .2], [.2, .6, .2]])
    measurements, bearings = aggregate_predictions(bundle, probability)
    assert len(measurements) == 2
    assert len(bearings) == 2
    assert {row["bearing_id"] for row in measurements} == {"K001", "KA04"}


def test_d_only_criticality_is_train_bearing_grouped_and_has_no_e() -> None:
    rng = np.random.default_rng(4)
    bearings = np.repeat(np.asarray(["K001", "K002", "KA04", "KI04"]), 3)
    labels = np.repeat(np.asarray([0, 0, 1, 2]), 3)
    values = rng.normal(size=(12, 1, 64)).astype(np.float32)
    values[labels != 0, :, 8:16] += 0.5
    result = d_only_criticality({"x": values, "bearing_id": bearings}, 0.30)
    assert result["D"].shape == result["soft_mask"].shape == (1, 33)
    assert result["frequency_scaler_fit_scope"] == "training_bearings_only"
    assert "E" not in result
    assert len(result["reliability_spearman"]) == 4


def test_protocol_lock_uses_frozen_ancestor_and_explicit_utf8() -> None:
    source = inspect.getsource(protocol_lock_check)
    assert 'encoding="utf-8"' in source
    assert "merge-base" in source
    assert "protocol_lock_commit" in source


def test_bearing_grouped_bootstrap_retains_seed_replicates_and_is_deterministic() -> None:
    rows = []
    bearings = [bearing for values in PRIMARY_BY_LABEL.values() for bearing in values]
    for method in PADERBORN_METHODS:
        for seed in (7, 42, 2026):
            for bearing in bearings:
                label = label_for_bearing(bearing)
                prediction = label if method != "NO_AUG" else 0
                rows.append({"method": method, "seed": seed, "bearing_id": bearing,
                             "label": label, "prediction": prediction})
    first = bearing_grouped_bootstrap(
        rows, "QDIFFCL_D_ONLY_EXTERNAL_COMPONENT", "NO_AUG", 20, 11
    )
    second = bearing_grouped_bootstrap(
        rows, "QDIFFCL_D_ONLY_EXTERNAL_COMPONENT", "NO_AUG", 20, 11
    )
    assert first == second
    assert all(row["bootstrap_unit"] == "bearing_id" for row in first)
    assert all(row["independent_bearings"] == 15 for row in first)
    assert all(row["seed_replications_retained"] == 3 for row in first)
