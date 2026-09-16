from __future__ import annotations

"""Run the frozen 5-fold Paderborn D-only external-validation matrix."""

import argparse
import copy
import csv
import gc
import hashlib
import json
import os
import subprocess
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn.functional as F
import yaml
from scipy.stats import spearmanr
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)

from datasets.paderborn import (
    PRIMARY_BY_LABEL,
    PRIMARY_LABEL_NAMES,
    canonicalize_signal,
    discover_measurements,
    load_measurement,
    primary_five_fold_protocol,
)
from diffusion import DiffusionSchedule, FrequencyForwardDiffusion, fit_spectral_statistics
from diffusion.frequency_selective import spectral_noise_variance
from frequency.criticality import _fisher, _robust_normalize, _top_mask, mask_jaccard
from scripts.reconcile_paderborn_sampling_v2 import require_safe_ram
from scripts.run_diffusion_quality_retest import _fit_supcon, epoch_orders
from trainers import build_model
from utils import seed_everything


REPO = Path(__file__).resolve().parents[1]
METHODS = ("NO_AUG", "UNIFORM_DIFFUSION", "QDIFFCL_D_ONLY_EXTERNAL_COMPONENT")
RESULTS = REPO / "analysis/results"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    os.replace(temporary, path)


def atomic_json(path: Path, value: Any) -> None:
    atomic_text(path, json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = list(dict.fromkeys(key for row in rows for key in row))
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temporary, path)


class Reporter:
    def __init__(self, config: dict[str, Any]) -> None:
        self.started = time.perf_counter()
        self.status_path = REPO / config["runtime"]["status"]
        self.log_path = REPO / config["runtime"]["log_dir"] / "night.log"

    def log(self, message: str) -> None:
        print(message, flush=True)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(f"[{now()}] {message}\n")

    def status(self, **updates: Any) -> None:
        payload = {
            "timestamp": now(), "phase": "initializing", "completed_cells": 0,
            "expected_cells": 45, "current_seed": None, "current_fold": None,
            "current_method": None, "last_artifact": None,
            "elapsed_seconds": round(time.perf_counter() - self.started, 3),
            "warnings": [], "failures": [],
        }
        if self.status_path.exists():
            try:
                payload.update(json.loads(self.status_path.read_text(encoding="utf-8")))
            except Exception:
                pass
        payload.update(updates)
        payload["timestamp"] = now()
        payload["elapsed_seconds"] = round(time.perf_counter() - self.started, 3)
        atomic_json(self.status_path, payload)


def load_config(path: Path) -> dict[str, Any]:
    config = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not config["frozen"] or config["status"] != "PADERBORN_PROTOCOL_FROZEN_V2":
        raise RuntimeError("Paderborn protocol is not frozen")
    if tuple(config["methods"]) != METHODS or list(map(int, config["seeds"])) != [7, 42, 2026]:
        raise RuntimeError("formal method/seed matrix changed")
    if config["criticality"]["component"] != "D_only" or float(config["criticality"]["critical_ratio"]) != .30:
        raise RuntimeError("Paderborn must remain D-only with critical_ratio=0.30")
    if config["training"]["contrastive"] != "Hard SupCon" or config["training"]["probe"] != "frozen linear probe":
        raise RuntimeError("frozen training protocol changed")
    sampling = yaml.safe_load((REPO / config["sampling_policy"]).read_text(encoding="utf-8"))
    if sampling["status"] != "PADERBORN_FREQUENCY_GRID_GO" or sampling["policy"] != "sample_index_resample":
        raise RuntimeError("PADERBORN_FREQUENCY_GRID_HOLD")
    return config


def label_for_bearing(bearing: str) -> int:
    matches = [label for label, values in PRIMARY_BY_LABEL.items() if bearing in values]
    if len(matches) != 1:
        raise ValueError(f"bearing is not uniquely labelled in Primary: {bearing}")
    return int(matches[0])


def selected_starts(length: int, stride: int, signal_length: int, count: int) -> np.ndarray:
    starts = np.arange(0, signal_length - length + 1, stride, dtype=np.int64)
    if len(starts) < count:
        raise ValueError("canonical signal has too few stride-grid windows")
    positions = np.rint(np.linspace(0, len(starts) - 1, count)).astype(np.int64)
    result = starts[positions]
    if len(np.unique(result)) != count:
        raise RuntimeError("evenly-spaced window selection produced duplicates")
    return result


def _cache_paths(cache_root: Path, relative_path: str) -> tuple[Path, Path]:
    key = hashlib.sha256(relative_path.encode("utf-8")).hexdigest()[:24]
    return cache_root / "measurements" / f"{key}.npy", cache_root / "measurements" / f"{key}.json"


def build_cache(config: dict[str, Any], reporter: Reporter) -> list[dict[str, Any]]:
    require_safe_ram()
    data_root = Path(config["data_root"])
    cache_root = REPO / config["runtime"]["cache_root"]
    primary = set().union(*map(set, PRIMARY_BY_LABEL.values()))
    measurements = [item for item in discover_measurements(data_root) if item.bearing_id in primary]
    if len(measurements) != 1200:
        raise RuntimeError(f"PADERBORN_PRIMARY_DATA_HOLD: {len(measurements)}")
    window = config["window"]
    sampling = yaml.safe_load((REPO / config["sampling_policy"]).read_text(encoding="utf-8"))
    records = []
    for index, item in enumerate(measurements, 1):
        if index == 1 or index % 25 == 0:
            require_safe_ram()
        array_path, record_path = _cache_paths(cache_root, item.relative_path)
        raw_hash = sha256_file(item.path)
        existing = None
        if array_path.exists() and record_path.exists():
            candidate = json.loads(record_path.read_text(encoding="utf-8"))
            if candidate.get("raw_sha256") == raw_hash and candidate.get("array_sha256") == sha256_file(array_path):
                existing = candidate
        if existing is None:
            loaded = load_measurement(item)
            signal = canonicalize_signal(
                loaded.signal, loaded.timestamps, sampling["policy"],
                int(sampling["target_length"]), float(sampling["target_hz"]),
            )
            starts = selected_starts(
                int(window["length"]), int(window["stride"]), len(signal),
                int(window["windows_per_measurement"]),
            )
            values = np.stack([signal[start:start + int(window["length"])] for start in starts])[:, None, :]
            values = values.astype(np.float32, copy=False)
            array_path.parent.mkdir(parents=True, exist_ok=True)
            temporary = array_path.with_suffix(".npy.tmp")
            with temporary.open("wb") as handle:
                np.save(handle, values, allow_pickle=False)
            os.replace(temporary, array_path)
            existing = {
                "relative_path": item.relative_path, "bearing_id": item.bearing_id,
                "condition": item.operating_condition, "measurement_index": item.measurement_index,
                "label": label_for_bearing(item.bearing_id), "raw_sha256": raw_hash,
                "array_path": array_path.relative_to(REPO).as_posix(),
                "array_sha256": sha256_file(array_path), "shape": list(values.shape),
                "starts": starts.tolist(), "signal_count": int(signal.size),
                "signal_sum": float(signal.astype(np.float64).sum()),
                "signal_sum_squares": float(np.square(signal.astype(np.float64)).sum()),
            }
            atomic_json(record_path, existing)
        records.append(existing)
        if index % 50 == 0:
            reporter.log(f"[PADERBORN-CACHE] {index}/1200")
            reporter.status(phase="cache", last_artifact=existing["array_path"])
    manifest = {
        "status": "PADERBORN_CACHE_COMPLETE", "measurements": len(records),
        "records": records, "sampling_policy_sha256": sha256_file(REPO / config["sampling_policy"]),
        "window_protocol": window, "generated_at": now(),
    }
    atomic_json(cache_root / "manifest.json", manifest)
    reporter.status(phase="cache_complete", last_artifact=(cache_root / "manifest.json").relative_to(REPO).as_posix())
    return records


def load_cache(config: dict[str, Any]) -> list[dict[str, Any]]:
    path = REPO / config["runtime"]["cache_root"] / "manifest.json"
    if not path.exists():
        raise RuntimeError("Paderborn cache is absent; run --phase cache first")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest["measurements"] != 1200 or manifest["sampling_policy_sha256"] != sha256_file(REPO / config["sampling_policy"]):
        raise RuntimeError("Paderborn cache manifest mismatch")
    for row in manifest["records"]:
        path = REPO / row["array_path"]
        if not path.exists() or sha256_file(path) != row["array_sha256"]:
            raise RuntimeError(f"Paderborn cache artifact hash mismatch: {path}")
    return manifest["records"]


def split_records(records: list[dict[str, Any]], fold: int) -> dict[str, list[dict[str, Any]]]:
    protocol = primary_five_fold_protocol()[fold]
    result = {name: [row for row in records if row["bearing_id"] in bearings] for name, bearings in protocol.items()}
    expected = {"train": 720, "validation": 240, "test": 240}
    if {name: len(rows) for name, rows in result.items()} != expected:
        raise RuntimeError("measurement split counts changed")
    return result


def fit_time_scaler(rows: list[dict[str, Any]]) -> tuple[float, float]:
    count = sum(int(row["signal_count"]) for row in rows)
    total = sum(float(row["signal_sum"]) for row in rows)
    squares = sum(float(row["signal_sum_squares"]) for row in rows)
    mean = total / count
    variance = max(squares / count - mean * mean, 1e-12)
    return float(mean), float(np.sqrt(variance))


def materialize(rows: list[dict[str, Any]], mean: float, scale: float) -> dict[str, np.ndarray]:
    arrays = []
    metadata: dict[str, list[Any]] = defaultdict(list)
    for row in rows:
        values = np.load(REPO / row["array_path"], allow_pickle=False)
        arrays.append(((values - mean) / scale).astype(np.float32))
        count = len(values)
        for key in ("bearing_id", "condition", "relative_path", "label"):
            metadata[key].extend([row[key]] * count)
        metadata["start"].extend(row["starts"])
    return {"x": np.concatenate(arrays), **{key: np.asarray(value) for key, value in metadata.items()}}


def d_only_criticality(train: dict[str, np.ndarray], ratio: float) -> dict[str, Any]:
    x = train["x"]
    bearings = train["bearing_id"]
    sums: dict[str, np.ndarray] = {}
    counts = Counter()
    global_sum = None
    global_squares = None
    global_count = 0
    for start in range(0, len(x), 256):
        spectrum = np.log1p(np.abs(np.fft.rfft(x[start:start + 256], axis=-1)))
        batch_sum = spectrum.sum(0)
        batch_squares = np.square(spectrum).sum(0)
        global_sum = batch_sum if global_sum is None else global_sum + batch_sum
        global_squares = batch_squares if global_squares is None else global_squares + batch_squares
        global_count += len(spectrum)
        for bearing in np.unique(bearings[start:start + len(spectrum)]):
            mask = bearings[start:start + len(spectrum)] == bearing
            sums[bearing] = sums.get(bearing, np.zeros(spectrum.shape[1:], np.float64)) + spectrum[mask].sum(0)
            counts[bearing] += int(mask.sum())
    frequency_mean = global_sum / global_count
    frequency_variance = np.maximum(global_squares / global_count - np.square(frequency_mean), 0.0)
    frequency_scale = np.where(np.sqrt(frequency_variance) > 1e-8, np.sqrt(frequency_variance), 1.0)
    means = {
        bearing: (sums[bearing] / counts[bearing] - frequency_mean) / frequency_scale
        for bearing in sums
    }

    def score(excluded: str | None = None) -> np.ndarray:
        normal = np.stack([value for bearing, value in means.items() if bearing != excluded and label_for_bearing(bearing) == 0])
        fault = np.stack([value for bearing, value in means.items() if bearing != excluded and label_for_bearing(bearing) != 0])
        return _fisher(normal, fault)

    d_score = score()
    normalized = _robust_normalize(d_score)
    mask = _top_mask(normalized, ratio)
    threshold = float(np.min(normalized[mask]))
    scale = max(float(np.quantile(normalized, .75) - np.quantile(normalized, .25)), 1e-8)
    soft = 1 / (1 + np.exp(np.clip(-(normalized - threshold) / scale, -30, 30)))
    ranks, overlaps = [], []
    for bearing in sorted(means):
        held = score(bearing)
        ranks.append(float(spearmanr(d_score.reshape(-1), held.reshape(-1)).statistic))
        overlaps.append(mask_jaccard(mask, _top_mask(_robust_normalize(held), ratio)))
    return {
        "D": d_score.astype(np.float32), "soft_mask": soft.astype(np.float32),
        "hard_mask": mask, "bearing_counts": dict(counts),
        "frequency_scaler_mean": frequency_mean.astype(np.float32),
        "frequency_scaler_scale": frequency_scale.astype(np.float32),
        "frequency_scaler_fit_scope": "training_bearings_only",
        "reliability_spearman": ranks, "reliability_jaccard": overlaps,
        "reliability_spearman_median": float(np.median(ranks)),
        "reliability_jaccard_median": float(np.median(overlaps)),
    }


def probabilities(model: torch.nn.Module, x: np.ndarray, batch: int, device: str) -> np.ndarray:
    model.eval()
    result = []
    with torch.no_grad():
        for start in range(0, len(x), batch):
            logits = model(torch.from_numpy(x[start:start + batch]).float().to(device))["logits"]
            result.append(torch.softmax(logits, 1).cpu().numpy())
    return np.concatenate(result)


def metrics(y: np.ndarray, probability: np.ndarray) -> dict[str, Any]:
    prediction = probability.argmax(1)
    precision, recall, f1, support = precision_recall_fscore_support(
        y, prediction, labels=np.arange(3), zero_division=0
    )
    return {
        "macro_f1": float(f1_score(y, prediction, average="macro", zero_division=0)),
        "balanced_accuracy": float(balanced_accuracy_score(y, prediction)),
        "accuracy": float(accuracy_score(y, prediction)),
        "confusion_matrix": confusion_matrix(y, prediction, labels=np.arange(3)).tolist(),
        "per_class": {
            PRIMARY_LABEL_NAMES[index]: {
                "precision": float(precision[index]), "recall": float(recall[index]),
                "f1": float(f1[index]), "support": int(support[index]),
            } for index in range(3)
        },
    }


def fit_probe(
    model: torch.nn.Module, train: dict[str, np.ndarray], validation: dict[str, np.ndarray],
    orders: list[np.ndarray], runtime: dict[str, Any], device: str,
) -> list[dict[str, Any]]:
    for parameter in model.parameters():
        parameter.requires_grad = False
    for parameter in model.classification_head.parameters():
        parameter.requires_grad = True
    optimizer = torch.optim.Adam(model.classification_head.parameters(), lr=float(runtime["learning_rate"]))
    best_state = None
    best_rank = None
    history = []
    stale = 0
    for epoch, order in enumerate(orders):
        model.train()
        losses = []
        for start in range(0, len(order), int(runtime["batch_size"])):
            indices = order[start:start + int(runtime["batch_size"])]
            xb = torch.from_numpy(train["x"][indices]).float().to(device)
            yb = torch.from_numpy(train["label"][indices].astype(np.int64)).long().to(device)
            optimizer.zero_grad()
            loss = F.cross_entropy(model(xb)["logits"], yb)
            loss.backward()
            optimizer.step()
            losses.append(float(loss.detach()))
        value = metrics(validation["label"].astype(np.int64), probabilities(
            model, validation["x"], int(runtime["batch_size"]), device
        ))
        record = {"epoch": epoch, "loss": float(np.mean(losses)), **{
            f"validation_{key}": value[key] for key in ("macro_f1", "balanced_accuracy", "accuracy")
        }}
        history.append(record)
        rank = (record["validation_macro_f1"], record["validation_balanced_accuracy"], record["validation_accuracy"])
        if best_rank is None or rank > best_rank:
            best_rank = rank
            best_state = copy.deepcopy(model.state_dict())
            stale = 0
        else:
            stale += 1
            if stale >= int(runtime["probe_early_stopping_patience"]):
                break
    if best_state is not None:
        model.load_state_dict(best_state)
    return history


def aggregate_predictions(bundle: dict[str, np.ndarray], probability: np.ndarray) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    measurement_rows = []
    for relative in np.unique(bundle["relative_path"]):
        selector = bundle["relative_path"] == relative
        p = probability[selector].mean(0)
        measurement_rows.append({
            "relative_path": str(relative), "bearing_id": str(bundle["bearing_id"][selector][0]),
            "condition": str(bundle["condition"][selector][0]), "label": int(bundle["label"][selector][0]),
            "prediction": int(p.argmax()), **{f"probability_{index}": float(p[index]) for index in range(3)},
        })
    bearing_rows = []
    for bearing in sorted({row["bearing_id"] for row in measurement_rows}):
        group = [row for row in measurement_rows if row["bearing_id"] == bearing]
        p = np.asarray([[row[f"probability_{index}"] for index in range(3)] for row in group]).mean(0)
        bearing_rows.append({
            "bearing_id": bearing, "label": int(group[0]["label"]), "prediction": int(p.argmax()),
            **{f"probability_{index}": float(p[index]) for index in range(3)},
        })
    return measurement_rows, bearing_rows


def per_condition_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    result = {}
    for condition in sorted({row["condition"] for row in rows}):
        group = [row for row in rows if row["condition"] == condition]
        y = np.asarray([row["label"] for row in group])
        p = np.asarray([[row[f"probability_{index}"] for index in range(3)] for row in group])
        result[condition] = metrics(y, p)
    return result


def protocol_lock_check(config: dict[str, Any]) -> dict[str, str]:
    def git(*args: str) -> str:
        return subprocess.check_output(
            ["git", *args], text=True, encoding="utf-8", errors="strict"
        ).strip()

    branch = git("branch", "--show-current")
    head = git("rev-parse", "HEAD")
    lock = str(config["protocol_lock_commit"])
    subject = git("show", "-s", "--format=%s", lock)
    dirty = git("status", "--porcelain")
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", lock, head], check=False
    ).returncode == 0
    if branch != "exp/paderborn-external-validation-v2" or not ancestor or subject != config["protocol_lock_subject"] or dirty:
        raise RuntimeError(
            f"PADERBORN_PROTOCOL_FREEZE_HOLD: branch={branch} lock_ancestor={ancestor} "
            f"subject={subject!r} dirty={bool(dirty)}"
        )
    return {"branch": branch, "head": head, "lock": lock, "subject": subject}


def protocol_audit(config: dict[str, Any]) -> dict[str, Any]:
    folds = primary_five_fold_protocol()
    split_rows = []
    for fold, split in enumerate(folds):
        for name, bearings in split.items():
            for bearing in bearings:
                split_rows.append({"fold": fold, "split": name, "bearing": bearing,
                                   "label": label_for_bearing(bearing)})
    for fold in range(5):
        rows = [row for row in split_rows if row["fold"] == fold]
        sets = {name: {row["bearing"] for row in rows if row["split"] == name}
                for name in ("train", "validation", "test")}
        if any(sets[first] & sets[second] for first in sets for second in sets if first < second):
            raise RuntimeError("Paderborn protocol bearing leakage")
    spectral = config["spectral_diffusion"]
    schedule = DiffusionSchedule.cosine(int(spectral["diffusion_steps"]), "cpu")
    soft = torch.linspace(0, 1, 2049, dtype=torch.float32)[None, :]
    uniform = spectral_noise_variance(
        schedule.alpha_bars, 1, 2049, "uniform", int(spectral["t_uniform"]),
        bool(spectral["preserve_dc"]),
    )
    selective = spectral_noise_variance(
        schedule.alpha_bars, 1, 2049, "selective", int(spectral["t_uniform"]),
        bool(spectral["preserve_dc"]), soft, int(spectral["t_critical"]),
        int(spectral["t_noncritical"]),
    )
    budget_error = abs(float(uniform.mean()) - float(selective.mean()))
    output_root = REPO / config["runtime"]["output_root"] / "cells"
    existing_test_results = len(list(output_root.glob("seed_*/fold_*/*/result.json"))) if output_root.exists() else 0
    result = {
        "status": "PADERBORN_PROTOCOL_AUDIT_PASS",
        "config_sha256": sha256_file(REPO / "configs/paderborn_external_v2.yaml"),
        "frequency_grid_gate": "PADERBORN_FREQUENCY_GRID_GO",
        "split_unit": "bearing", "folds": 5, "split_rows": len(split_rows),
        "train_bearings_per_fold": 9, "validation_bearings_per_fold": 3,
        "test_bearings_per_fold": 3, "bearing_overlap": False,
        "methods": list(METHODS), "seeds": config["seeds"], "formal_cells": 45,
        "component": "D_only", "E_used": False, "pseudo_E": False,
        "normalization_fit_scope": "training_bearings_only",
        "frequency_scaler_fit_scope": "training_bearings_only",
        "matched_budget_absolute_error": budget_error,
        "matched_budget_pass": budget_error <= float(spectral["matched_budget_absolute_tolerance"]),
        "test_metrics_produced_before_lock": existing_test_results > 0,
        "test_metrics_used_for_protocol_selection": False,
        "archive_branch_merged": False,
        "generated_at": now(),
    }
    if not result["matched_budget_pass"] or result["test_metrics_produced_before_lock"]:
        raise RuntimeError(f"PADERBORN_PROTOCOL_FREEZE_HOLD: {result}")
    atomic_json(RESULTS / "paderborn_external_v2_protocol_audit.json", result)
    return result


def run_cell(
    config: dict[str, Any], records: list[dict[str, Any]], seed: int, fold: int,
    method: str, device: str,
) -> dict[str, Any]:
    require_safe_ram()
    output = REPO / config["runtime"]["output_root"] / "cells" / f"seed_{seed}" / f"fold_{fold}" / method
    result_path = output / "result.json"
    protocol_hash = sha256_file(REPO / "configs/paderborn_external_v2.yaml")
    metadata = {"seed": seed, "fold": fold, "method": method, "protocol_sha256": protocol_hash}
    if result_path.exists():
        artifact_path = output / "artifact_manifest.json"
        checkpoint_path = output / "model.pt"
        if not artifact_path.exists() or not checkpoint_path.exists():
            raise RuntimeError(f"incomplete cell cannot be resumed: {output}")
        artifacts = json.loads(artifact_path.read_text(encoding="utf-8"))
        if artifacts.get("result_sha256") != sha256_file(result_path):
            raise RuntimeError(f"result hash mismatch: {result_path}")
        if artifacts.get("model_sha256") != sha256_file(checkpoint_path):
            raise RuntimeError(f"model hash mismatch: {checkpoint_path}")
        existing = json.loads(result_path.read_text(encoding="utf-8"))
        if existing["metadata"] != metadata:
            raise RuntimeError(f"resume metadata mismatch: {result_path}")
        existing["resumed"] = True
        return existing

    grouped = split_records(records, fold)
    mean, scale = fit_time_scaler(grouped["train"])
    bundles = {name: materialize(rows, mean, scale) for name, rows in grouped.items()}
    critical = d_only_criticality(bundles["train"], float(config["criticality"]["critical_ratio"]))
    spectral = config["spectral_diffusion"]
    schedule = DiffusionSchedule.cosine(int(spectral["diffusion_steps"]), device)
    statistics = fit_spectral_statistics(bundles["train"]["x"], float(spectral["clip_quantile"]), "train")
    augmenter = FrequencyForwardDiffusion(
        statistics, schedule.alpha_bars, critical["soft_mask"], int(spectral["t_uniform"]),
        int(spectral["t_critical"]), bool(spectral["preserve_phase"]),
        bool(spectral["preserve_dc"]), device,
    )
    uniform_budget = float(augmenter.variance("uniform").mean())
    selective_budget = float(augmenter.variance("selective", int(spectral["t_noncritical"])).mean())
    budget_error = abs(uniform_budget - selective_budget)
    if budget_error > float(spectral["matched_budget_absolute_tolerance"]):
        raise RuntimeError(f"PADERBORN_MATCHED_BUDGET_HOLD: error={budget_error}")

    views = {}
    augmentation_audit = {}
    for name, offset in (("train", 0), ("validation", 100)):
        clean = bundles[name]["x"]
        if method == "NO_AUG":
            views[name] = clean.copy()
            augmentation_audit[name] = {"mode": "clean_pair", "expected_total_noise_budget": 0.0}
        else:
            mode = "uniform" if method == "UNIFORM_DIFFUSION" else "selective"
            values, audit = augmenter.augment(
                clean, mode, seed + fold * 1000 + int(spectral["sampling_seed_offset"]) + offset,
                int(spectral["t_noncritical"]) if mode == "selective" else None,
                int(config["training"]["batch_size"]), noise_structure="iid",
            )
            views[name] = values
            augmentation_audit[name] = audit

    runtime = dict(config["training"])
    seed_everything(seed)
    model = build_model(runtime["model"], 1, 3).to(device)
    pre_orders = epoch_orders(len(bundles["train"]["x"]), int(runtime["epochs"]), seed + fold * 100 + 10_000)
    probe_orders = epoch_orders(len(bundles["train"]["x"]), int(runtime["probe_epochs"]), seed + fold * 100 + 20_000)
    started = time.perf_counter()
    pretrain = _fit_supcon(
        model,
        {"clean": bundles["train"]["x"], "restored": views["train"], "labels": bundles["train"]["label"].astype(np.int64)},
        {"clean": bundles["validation"]["x"], "restored": views["validation"], "labels": bundles["validation"]["label"].astype(np.int64)},
        np.ones(len(bundles["train"]["x"]), np.float32),
        np.ones(len(bundles["validation"]["x"]), np.float32),
        pre_orders, runtime, device,
    )
    seed_everything(seed + 1)
    probe = fit_probe(model, bundles["train"], bundles["validation"], probe_orders, runtime, device)
    test_probability = probabilities(model, bundles["test"]["x"], int(runtime["batch_size"]), device)
    measurement_rows, bearing_rows = aggregate_predictions(bundles["test"], test_probability)
    measurement_probability = np.asarray([[row[f"probability_{index}"] for index in range(3)] for row in measurement_rows])
    bearing_probability = np.asarray([[row[f"probability_{index}"] for index in range(3)] for row in bearing_rows])
    measurement_result = metrics(np.asarray([row["label"] for row in measurement_rows]), measurement_probability)
    bearing_result = metrics(np.asarray([row["label"] for row in bearing_rows]), bearing_probability)
    result = {
        "metadata": metadata, "resumed": False, "outer_test_read_after_training_only": True,
        "normalization": {"fit_scope": "training_bearings_only", "mean": mean, "scale": scale},
        "split_bearings": primary_five_fold_protocol()[fold],
        "split_measurements": {name: len(rows) for name, rows in grouped.items()},
        "windows_per_measurement": int(config["window"]["windows_per_measurement"]),
        "criticality": {
            "component": "D_only", "E_used": False, "critical_ratio": float(config["criticality"]["critical_ratio"]),
            "D_sha256": hashlib.sha256(critical["D"].tobytes()).hexdigest(),
            "soft_mask_sha256": hashlib.sha256(critical["soft_mask"].tobytes()).hexdigest(),
            "frequency_scaler_mean_sha256": hashlib.sha256(critical["frequency_scaler_mean"].tobytes()).hexdigest(),
            "frequency_scaler_scale_sha256": hashlib.sha256(critical["frequency_scaler_scale"].tobytes()).hexdigest(),
            "frequency_scaler_fit_scope": critical["frequency_scaler_fit_scope"],
            "reliability_spearman_median": critical["reliability_spearman_median"],
            "reliability_jaccard_median": critical["reliability_jaccard_median"],
        },
        "matched_budget": {"uniform": uniform_budget, "selective": selective_budget, "absolute_error": budget_error},
        "augmentation_audit": augmentation_audit,
        "measurement_metrics": measurement_result, "bearing_metrics": bearing_result,
        "per_condition": per_condition_metrics(measurement_rows),
        "measurement_rows": measurement_rows, "bearing_rows": bearing_rows,
        "pretrain_history": pretrain, "probe_history": probe,
        "training_seconds": time.perf_counter() - started,
        "peak_gpu_mib": torch.cuda.max_memory_allocated() / 1024 ** 2 if torch.cuda.is_available() else 0.0,
    }
    output.mkdir(parents=True, exist_ok=False)
    torch.save({"metadata": metadata, "model_state_dict": model.state_dict()}, output / "model.pt")
    atomic_json(result_path, result)
    atomic_json(output / "artifact_manifest.json", {
        "result_sha256": sha256_file(result_path), "model_sha256": sha256_file(output / "model.pt"),
    })
    del model, bundles, views, augmenter, statistics
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    return result


def collect_results(config: dict[str, Any]) -> list[dict[str, Any]]:
    root = REPO / config["runtime"]["output_root"] / "cells"
    results = []
    for seed in config["seeds"]:
        for fold in range(5):
            for method in METHODS:
                path = root / f"seed_{seed}" / f"fold_{fold}" / method / "result.json"
                if path.exists():
                    results.append(json.loads(path.read_text(encoding="utf-8")))
    return results


def audit_cell_artifacts(config: dict[str, Any]) -> dict[str, Any]:
    root = REPO / config["runtime"]["output_root"] / "cells"
    expected_protocol = sha256_file(REPO / "configs/paderborn_external_v2.yaml")
    records = []
    for seed in config["seeds"]:
        for fold in range(5):
            for method in METHODS:
                cell = root / f"seed_{seed}" / f"fold_{fold}" / method
                result_path = cell / "result.json"
                model_path = cell / "model.pt"
                artifact_path = cell / "artifact_manifest.json"
                if not all(path.exists() for path in (result_path, model_path, artifact_path)):
                    raise RuntimeError(f"missing formal cell artifact: {cell}")
                manifest = json.loads(artifact_path.read_text(encoding="utf-8"))
                result = json.loads(result_path.read_text(encoding="utf-8"))
                if manifest.get("result_sha256") != sha256_file(result_path):
                    raise RuntimeError(f"formal result hash mismatch: {cell}")
                if manifest.get("model_sha256") != sha256_file(model_path):
                    raise RuntimeError(f"formal model hash mismatch: {cell}")
                if result["metadata"] != {
                    "seed": int(seed), "fold": fold, "method": method,
                    "protocol_sha256": expected_protocol,
                }:
                    raise RuntimeError(f"formal metadata mismatch: {cell}")
                records.append({
                    "seed": int(seed), "fold": fold, "method": method,
                    "result_sha256": manifest["result_sha256"],
                    "model_sha256": manifest["model_sha256"],
                })
    return {"status": "PASS", "valid_cells": len(records), "expected_cells": 45, "records": records}


def bootstrap_delta(values: np.ndarray, repeats: int, seed: int) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    samples = np.asarray([np.mean(values[rng.integers(0, len(values), len(values))]) for _ in range(repeats)])
    return {
        "mean_delta": float(values.mean()), "q025": float(np.quantile(samples, .025)),
        "q975": float(np.quantile(samples, .975)), "p_delta_gt_zero": float(np.mean(samples > 0)),
    }


def bearing_grouped_bootstrap(
    rows: list[dict[str, Any]], candidate: str, reference: str, repeats: int, seed: int,
) -> list[dict[str, Any]]:
    bearings = sorted({str(row["bearing_id"]) for row in rows})
    if len(bearings) != 15:
        raise ValueError(f"bearing bootstrap requires 15 independent bearings, found {len(bearings)}")
    by_key = {
        (str(row["method"]), int(row["seed"]), str(row["bearing_id"])): row
        for row in rows
    }
    seeds = sorted({int(row["seed"]) for row in rows})

    def evaluate(sampled: list[str], method: str) -> tuple[float, float]:
        selected = [by_key[(method, model_seed, bearing)] for bearing in sampled for model_seed in seeds]
        y = np.asarray([int(row["label"]) for row in selected])
        prediction = np.asarray([int(row["prediction"]) for row in selected])
        return (
            float(f1_score(y, prediction, average="macro", zero_division=0)),
            float(accuracy_score(y, prediction)),
        )

    point_candidate = evaluate(bearings, candidate)
    point_reference = evaluate(bearings, reference)
    rng = np.random.default_rng(seed)
    sampled_deltas = np.empty((repeats, 2), dtype=np.float64)
    for index in range(repeats):
        sampled = [bearings[value] for value in rng.integers(0, len(bearings), len(bearings))]
        left = evaluate(sampled, candidate)
        right = evaluate(sampled, reference)
        sampled_deltas[index] = np.asarray(left) - np.asarray(right)
    records = []
    for index, metric in enumerate(("bearing_oof_macro_f1", "bearing_oof_accuracy")):
        records.append({
            "candidate": candidate, "reference": reference, "metric": metric,
            "bootstrap_unit": "bearing_id", "independent_bearings": len(bearings),
            "seed_replications_retained": len(seeds), "bootstrap_repeats": repeats,
            "point_delta": point_candidate[index] - point_reference[index],
            "q025": float(np.quantile(sampled_deltas[:, index], .025)),
            "q975": float(np.quantile(sampled_deltas[:, index], .975)),
            "p_delta_gt_zero": float(np.mean(sampled_deltas[:, index] > 0)),
        })
    return records


def finalize(config: dict[str, Any], results: list[dict[str, Any]]) -> dict[str, Any]:
    if len(results) != 45:
        raise RuntimeError(f"formal matrix incomplete: {len(results)}/45")
    cell_artifact_audit = audit_cell_artifacts(config)
    cell_rows, measurement_rows, bearing_rows = [], [], []
    for result in results:
        meta = result["metadata"]
        cell_rows.append({
            **meta, "measurement_macro_f1": result["measurement_metrics"]["macro_f1"],
            "measurement_balanced_accuracy": result["measurement_metrics"]["balanced_accuracy"],
            "measurement_accuracy": result["measurement_metrics"]["accuracy"],
            "bearing_macro_f1": result["bearing_metrics"]["macro_f1"],
            "bearing_accuracy": result["bearing_metrics"]["accuracy"],
            "D_reliability_spearman": result["criticality"]["reliability_spearman_median"],
            "D_reliability_jaccard": result["criticality"]["reliability_jaccard_median"],
            "budget_error": result["matched_budget"]["absolute_error"],
            "training_seconds": result["training_seconds"], "peak_gpu_mib": result["peak_gpu_mib"],
        })
        measurement_rows.extend([{**meta, **row} for row in result["measurement_rows"]])
        bearing_rows.extend([{**meta, **row} for row in result["bearing_rows"]])
    write_csv(RESULTS / "paderborn_external_v2_cells.csv", cell_rows)
    write_csv(RESULTS / "paderborn_external_v2_oof_measurements.csv", measurement_rows)
    write_csv(RESULTS / "paderborn_external_v2_oof_bearings.csv", bearing_rows)

    summary = []
    for method in METHODS:
        rows = [row for row in cell_rows if row["method"] == method]
        summary.append({
            "method": method, "cells": len(rows),
            **{f"{metric}_mean": float(np.mean([row[metric] for row in rows])) for metric in (
                "measurement_macro_f1", "measurement_balanced_accuracy", "bearing_macro_f1", "bearing_accuracy"
            )},
            **{f"{metric}_std": float(np.std([row[metric] for row in rows], ddof=1)) for metric in (
                "measurement_macro_f1", "measurement_balanced_accuracy", "bearing_macro_f1", "bearing_accuracy"
            )},
        })
    write_csv(RESULTS / "paderborn_external_v2_summary.csv", summary)

    keyed = {(row["seed"], row["fold"], row["method"]): row for row in cell_rows}
    comparisons = []
    for reference in ("NO_AUG", "UNIFORM_DIFFUSION"):
        for metric in ("measurement_macro_f1", "measurement_balanced_accuracy", "bearing_macro_f1", "bearing_accuracy"):
            values = np.asarray([
                keyed[(seed, fold, "QDIFFCL_D_ONLY_EXTERNAL_COMPONENT")][metric]
                - keyed[(seed, fold, reference)][metric]
                for seed in config["seeds"] for fold in range(5)
            ])
            comparisons.append({"candidate": "QDIFFCL_D_ONLY_EXTERNAL_COMPONENT", "reference": reference,
                                "metric": metric, "paired_cells": len(values), **bootstrap_delta(
                                    values, int(config["statistics"]["bootstrap_repeats"]),
                                    int(config["statistics"]["bootstrap_seed"]) + len(comparisons),
                                )})
    write_csv(RESULTS / "paderborn_external_v2_paired_bootstrap.csv", comparisons)
    bearing_comparisons = []
    for offset, reference in enumerate(("NO_AUG", "UNIFORM_DIFFUSION")):
        bearing_comparisons.extend(bearing_grouped_bootstrap(
            bearing_rows, "QDIFFCL_D_ONLY_EXTERNAL_COMPONENT", reference,
            int(config["statistics"]["bootstrap_repeats"]),
            int(config["statistics"]["bootstrap_seed"]) + 100 + offset,
        ))
    write_csv(RESULTS / "paderborn_external_v2_bearing_grouped_bootstrap.csv", bearing_comparisons)
    primary = next(row for row in comparisons if row["reference"] == "UNIFORM_DIFFUSION" and row["metric"] == "measurement_macro_f1")
    secondary = next(row for row in comparisons if row["reference"] == "UNIFORM_DIFFUSION" and row["metric"] == "bearing_macro_f1")
    if primary["mean_delta"] > 0 and primary["q025"] > 0 and secondary["mean_delta"] >= 0:
        status = "PADERBORN_D_ONLY_EXTERNAL_SUPPORT"
    elif primary["mean_delta"] > 0 or secondary["mean_delta"] > 0:
        status = "PADERBORN_D_ONLY_EXTERNAL_MIXED"
    else:
        status = "PADERBORN_D_ONLY_EXTERNAL_NO_SUPPORT"
    manifest = {
        "status": status, "evidence_matrix": "QDIFFCL_EVIDENCE_MATRIX_20260910_CONSOLIDATED",
        "cells": len(cell_rows), "seeds": config["seeds"], "folds": 5, "methods": list(METHODS),
        "primary_comparison": primary, "bearing_comparison": secondary,
        "bearing_grouped_comparisons": bearing_comparisons,
        "maximum_budget_error": max(row["budget_error"] for row in cell_rows),
        "test_metrics_used_for_protocol_selection": False, "E_used": False,
        "R_controller_used": False, "generated_at": now(),
        "cell_artifact_audit": cell_artifact_audit,
        "environment": {
            "python": os.path.realpath(sys.executable), "torch": torch.__version__,
            "cuda": torch.version.cuda, "cuda_available": torch.cuda.is_available(),
            "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
            "protocol_lock_commit": config["protocol_lock_commit"],
            "formal_execution_head": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], text=True, encoding="utf-8"
            ).strip(),
        },
    }
    manifest["summary_artifacts"] = {
        path.name: sha256_file(path) for path in (
            RESULTS / "paderborn_external_v2_cells.csv",
            RESULTS / "paderborn_external_v2_oof_measurements.csv",
            RESULTS / "paderborn_external_v2_oof_bearings.csv",
            RESULTS / "paderborn_external_v2_summary.csv",
            RESULTS / "paderborn_external_v2_paired_bootstrap.csv",
            RESULTS / "paderborn_external_v2_bearing_grouped_bootstrap.csv",
        )
    }
    atomic_json(RESULTS / "paderborn_external_v2_run_manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/paderborn_external_v2.yaml"))
    parser.add_argument("--phase", choices=("audit", "cache", "formal", "finalize", "all"), default="all")
    parser.add_argument("--max-cells", type=int)
    args = parser.parse_args()
    os.chdir(REPO)
    config = load_config(args.config)
    reporter = Reporter(config)
    try:
        require_safe_ram()
        reporter.status(phase="initializing", warnings=[], failures=[])
        if args.phase == "audit":
            audit = protocol_audit(config)
            reporter.status(phase="protocol_audit_complete", expected_cells=45,
                            last_artifact="analysis/results/paderborn_external_v2_protocol_audit.json",
                            warnings=[], failures=[])
            reporter.log(
                f"[PADERBORN] protocol-audit={audit['status']} cells={audit['formal_cells']} "
                f"budget_error={audit['matched_budget_absolute_error']:.3e}"
            )
            return
        records = build_cache(config, reporter) if args.phase in {"cache", "all"} else load_cache(config)
        if args.phase in {"formal", "all"}:
            lock = protocol_lock_check(config)
            reporter.log(f"[PADERBORN] protocol-lock={lock['head']}")
            completed = len(collect_results(config))
            stop = completed + args.max_cells if args.max_cells else 45
            for seed in config["seeds"]:
                for fold in range(5):
                    for method in METHODS:
                        existing = len(collect_results(config))
                        if existing >= stop:
                            break
                        reporter.status(phase="formal", completed_cells=existing, current_seed=seed,
                                        current_fold=fold, current_method=method)
                        result = run_cell(config, records, int(seed), fold, method, config["device"])
                        completed = len(collect_results(config))
                        reporter.log(
                            f"[PADERBORN][{completed:02d}/45] seed={seed} fold={fold} method={method} "
                            f"measurement_macro_f1={result['measurement_metrics']['macro_f1']:.6f} "
                            f"bearing_macro_f1={result['bearing_metrics']['macro_f1']:.6f} "
                            f"budget_error={result['matched_budget']['absolute_error']:.3e}"
                        )
                    if len(collect_results(config)) >= stop:
                        break
                if len(collect_results(config)) >= stop:
                    break
        results = collect_results(config)
        if args.phase in {"finalize", "all"} and len(results) == 45:
            manifest = finalize(config, results)
            reporter.status(phase="complete", completed_cells=45,
                            last_artifact="analysis/results/paderborn_external_v2_run_manifest.json",
                            warnings=[], failures=[])
            reporter.log(f"[PADERBORN] complete status={manifest['status']} cells=45/45")
        else:
            reporter.status(phase="paused", completed_cells=len(results), warnings=[], failures=[])
    except Exception as error:
        reporter.status(phase="hold", failures=[f"{type(error).__name__}: {error}"])
        reporter.log(f"[PADERBORN] HOLD {type(error).__name__}: {error}")
        raise


if __name__ == "__main__":
    main()
