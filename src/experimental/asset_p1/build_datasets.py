#!/usr/bin/env python3
"""Build ASSET-P1-D1-001 asset×segment historical datasets.

This prepares data for Execution Freeze. It does not execute D1 methods.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from p1_data import (
    DATASET_SCHEMA_VERSION,
    SERIALIZATION_ID,
    P1DataError,
    fetch_verified_archive,
    iso_to_us,
    parse_binance_zip,
    resample_hourly,
    validate_native_hourly,
    write_json,
    write_jsonl,
)

ASSETS = ("BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT")
SEGMENTS = (
    ("DEV", "DEV-01", "2021-01-01T00:00:00Z", "2021-07-01T00:00:00Z"),
    ("DEV", "DEV-02", "2022-06-01T00:00:00Z", "2022-12-01T00:00:00Z"),
    ("VAL", "VAL-01", "2023-01-01T00:00:00Z", "2023-07-01T00:00:00Z"),
    ("VAL", "VAL-02", "2023-07-01T00:00:00Z", "2024-01-01T00:00:00Z"),
    ("HOLDOUT", "HOLD-01", "2024-01-01T00:00:00Z", "2024-07-01T00:00:00Z"),
    ("HOLDOUT", "HOLD-02", "2024-07-01T00:00:00Z", "2025-01-01T00:00:00Z"),
)


def months_between(start_iso: str, end_iso: str) -> list[str]:
    start = datetime.fromisoformat(start_iso.replace("Z", "+00:00"))
    end = datetime.fromisoformat(end_iso.replace("Z", "+00:00"))
    y, m = start.year, start.month
    result: list[str] = []
    while (y, m) < (end.year, end.month):
        result.append(f"{y:04d}-{m:02d}")
        m += 1
        if m == 13:
            y += 1
            m = 1
    return result


def expected_counts(start_iso: str, end_iso: str) -> tuple[int, int, int]:
    start = datetime.fromisoformat(start_iso.replace("Z", "+00:00"))
    end = datetime.fromisoformat(end_iso.replace("Z", "+00:00"))
    hours = int((end - start).total_seconds() // 3600)
    if hours % 24 or hours % 4:
        raise P1DataError("Frozen P1 segment is not aligned to full UTC days/4h.")
    return hours, hours // 4, hours // 24


def build_dataset(
    instrument: str,
    phase: str,
    segment_id: str,
    start_iso: str,
    end_iso: str,
    output_root: Path,
    cache_root: Path,
) -> dict:
    version = f"ASSET-P1-{instrument}-{segment_id}-v0.1.0"
    dataset_id = f"ASSET-P1-{instrument}-{segment_id}"
    candles: list[dict] = []
    archives: list[dict] = []

    for ym in months_between(start_iso, end_iso):
        archive, provenance = fetch_verified_archive(instrument, ym, cache_root)
        candles.extend(
            parse_binance_zip(
                archive,
                instrument=instrument,
                dataset_version=version,
                source_timestamp_unit="ms",
            )
        )
        archives.append(provenance)

    start_us = iso_to_us(start_iso)
    end_us = iso_to_us(end_iso)
    validated = validate_native_hourly(
        candles,
        expected_start_us=start_us,
        expected_end_us=end_us,
    )
    if validated.critical_errors:
        raise P1DataError(
            f"{dataset_id} failed native validation: {validated.critical_errors}"
        )

    derived_4h = resample_hourly(validated.candles, "4h")
    derived_1d = resample_hourly(validated.candles, "1d")
    expected_1h, expected_4h, expected_1d = expected_counts(start_iso, end_iso)

    if len(validated.candles) != expected_1h:
        raise P1DataError(
            f"{dataset_id}: expected {expected_1h} 1h, got {len(validated.candles)}"
        )
    if len(derived_4h) != expected_4h or any(not c["complete"] for c in derived_4h):
        raise P1DataError(f"{dataset_id}: 4h count/completeness mismatch")
    if len(derived_1d) != expected_1d or any(not c["complete"] for c in derived_1d):
        raise P1DataError(f"{dataset_id}: 1d count/completeness mismatch")

    target = output_root / phase.lower() / segment_id / instrument
    hashes = {
        "native_jsonl": write_jsonl(target / "native.jsonl", validated.candles),
        "derived_4h_jsonl": write_jsonl(target / "derived_4h.jsonl", derived_4h),
        "derived_1d_jsonl": write_jsonl(target / "derived_1d.jsonl", derived_1d),
    }

    manifest = {
        "analytical_access": "LOCKED" if phase == "HOLDOUT" else "PRE_EXECUTION_ONLY",
        "archives": archives,
        "asset": instrument[:-4],
        "candle_boundary_policy_id": "asset-p1-utc-boundaries-v0.1.0",
        "checksum": hashes["native_jsonl"],
        "checksum_algorithm": "SHA-256",
        "dataset_id": dataset_id,
        "dataset_version": version,
        "derived_1d_records": len(derived_1d),
        "derived_4h_records": len(derived_4h),
        "end_timestamp": end_iso,
        "expected_native_records": expected_1h,
        "hashes": hashes,
        "ingestion_timestamp": datetime.now(timezone.utc).isoformat(),
        "instrument": instrument,
        "market_type": "spot",
        "missing_data_policy_id": "asset-p1-segment-contiguous-v0.1.0",
        "native_timeframe": "1h",
        "phase": phase,
        "quote_asset": "USDT",
        "raw_record_count": len(candles),
        "schema_version": DATASET_SCHEMA_VERSION,
        "segment_id": segment_id,
        "serialization_id": SERIALIZATION_ID,
        "source_endpoint_or_contract": "Binance Public Data monthly Spot kline archives",
        "source_provider": "Binance Public Data",
        "source_timestamp_unit": "ms",
        "start_timestamp": start_iso,
        "timezone_policy": "UTC",
        "validated_record_count": len(validated.candles),
        "venue": "Binance Spot",
    }
    manifest_sha = write_json(target / "dataset_manifest.json", manifest)
    return {
        "dataset_id": dataset_id,
        "dataset_version": version,
        "phase": phase,
        "segment_id": segment_id,
        "instrument": instrument,
        "manifest_sha256": manifest_sha,
        "hashes": hashes,
        "records": {
            "1h": len(validated.candles),
            "4h": len(derived_4h),
            "1d": len(derived_1d),
        },
    }


def build_all(output_root: Path, cache_root: Path) -> dict:
    datasets: list[dict] = []
    for phase, segment, start, end in SEGMENTS:
        for instrument in ASSETS:
            datasets.append(
                build_dataset(
                    instrument,
                    phase,
                    segment,
                    start,
                    end,
                    output_root,
                    cache_root,
                )
            )
    index = {
        "experiment_id": "ASSET-P1-D1-001",
        "dataset_count": len(datasets),
        "assets": list(ASSETS),
        "segments": [s[1] for s in SEGMENTS],
        "datasets": datasets,
    }
    write_json(output_root / "DATASET_INDEX.json", index)
    return index


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--asset")
    parser.add_argument("--segment")
    args = parser.parse_args()

    if bool(args.asset) != bool(args.segment):
        raise SystemExit("--asset and --segment must be supplied together.")

    if args.asset:
        if args.asset not in ASSETS:
            raise SystemExit(f"Unknown asset: {args.asset}")
        selected = next((s for s in SEGMENTS if s[1] == args.segment), None)
        if selected is None:
            raise SystemExit(f"Unknown segment: {args.segment}")
        phase, segment, start, end = selected
        result = build_dataset(
            args.asset, phase, segment, start, end, args.output, args.cache
        )
    else:
        result = build_all(args.output, args.cache)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
