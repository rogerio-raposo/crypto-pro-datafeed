#!/usr/bin/env python3
"""Build ASSET-P1-D1-001 asset×segment historical datasets.

Prepares immutable data identities for Execution Freeze. It does not execute D1.
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
    assign_analysis_islands,
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

REGISTERED_GAPS_US: dict[str, tuple[int, ...]] = {
    "DEV-01": (
        1613016000000000,
        1614996000000000,
        1618884000000000,
        1618887600000000,
        1619326800000000,
        1619330400000000,
        1619334000000000,
    ),
    "DEV-02": (),
    "VAL-01": (1679662800000000,),
    "VAL-02": (),
    "HOLD-01": (),
    "HOLD-02": (),
}


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
        raise P1DataError("Frozen P1 segment is not aligned to UTC 4h/Daily.")
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
    version = f"ASSET-P1-{instrument}-{segment_id}-v0.2.0"
    dataset_id = f"ASSET-P1-{instrument}-{segment_id}"
    registered_gaps = set(REGISTERED_GAPS_US[segment_id])

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
        allowed_missing_open_times_us=registered_gaps,
    )
    if validated.critical_errors:
        raise P1DataError(
            f"{dataset_id} failed native validation: {validated.critical_errors}"
        )
    actual_gaps = set(validated.missing_open_times_us)
    if actual_gaps != registered_gaps:
        raise P1DataError(
            f"{dataset_id}: gap registry mismatch. "
            f"expected={sorted(registered_gaps)} actual={sorted(actual_gaps)}"
        )

    derived_4h_audit = resample_hourly(validated.candles, "4h")
    derived_1d_audit = resample_hourly(validated.candles, "1d")

    analytical_4h, islands_4h = assign_analysis_islands(
        derived_4h_audit,
        timeframe="4h",
        island_prefix=f"{segment_id}-{instrument}",
    )
    analytical_1d, islands_1d = assign_analysis_islands(
        derived_1d_audit,
        timeframe="1d",
        island_prefix=f"{segment_id}-{instrument}",
    )

    nominal_1h, nominal_4h, nominal_1d = expected_counts(start_iso, end_iso)
    expected_native = nominal_1h - len(registered_gaps)
    if len(validated.candles) != expected_native:
        raise P1DataError(
            f"{dataset_id}: expected {expected_native} native records, "
            f"got {len(validated.candles)}"
        )
    if len(derived_4h_audit) != nominal_4h:
        raise P1DataError(f"{dataset_id}: 4h audit bucket count mismatch")
    if len(derived_1d_audit) != nominal_1d:
        raise P1DataError(f"{dataset_id}: Daily audit bucket count mismatch")

    incomplete_4h = [r for r in derived_4h_audit if not r.get("complete")]
    incomplete_1d = [r for r in derived_1d_audit if not r.get("complete")]

    target = output_root / phase.lower() / segment_id / instrument
    hashes = {
        "native_jsonl": write_jsonl(target / "native.jsonl", validated.candles),
        "derived_4h_audit_jsonl": write_jsonl(
            target / "derived_4h_audit.jsonl", derived_4h_audit
        ),
        "derived_1d_audit_jsonl": write_jsonl(
            target / "derived_1d_audit.jsonl", derived_1d_audit
        ),
        "analytical_4h_jsonl": write_jsonl(
            target / "analytical_4h.jsonl", analytical_4h
        ),
        "analytical_1d_jsonl": write_jsonl(
            target / "analytical_1d.jsonl", analytical_1d
        ),
    }

    manifest = {
        "analytical_access": "LOCKED" if phase == "HOLDOUT" else "PRE_EXECUTION_ONLY",
        "analysis_islands": {"4h": islands_4h, "1d": islands_1d},
        "archives": archives,
        "asset": instrument[:-4],
        "candle_boundary_policy_id": "asset-p1-utc-boundaries-v0.1.0",
        "checksum": hashes["native_jsonl"],
        "checksum_algorithm": "SHA-256",
        "dataset_id": dataset_id,
        "dataset_version": version,
        "end_timestamp": end_iso,
        "gap_policy_id": "asset-p1-synchronized-venue-gap-rev01",
        "hashes": hashes,
        "incomplete_derived_records": {
            "4h": len(incomplete_4h),
            "1d": len(incomplete_1d),
        },
        "ingestion_timestamp": datetime.now(timezone.utc).isoformat(),
        "instrument": instrument,
        "market_type": "spot",
        "native_timeframe": "1h",
        "nominal_records": {"1h": nominal_1h, "4h": nominal_4h, "1d": nominal_1d},
        "analytical_records": {
            "4h": len(analytical_4h),
            "1d": len(analytical_1d),
        },
        "phase": phase,
        "quote_asset": "USDT",
        "raw_record_count": len(candles),
        "registered_gap_open_times_us": sorted(registered_gaps),
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
        "registered_gap_count": len(registered_gaps),
        "records": {
            "native": len(validated.candles),
            "4h_analytical": len(analytical_4h),
            "1d_analytical": len(analytical_1d),
            "4h_incomplete": len(incomplete_4h),
            "1d_incomplete": len(incomplete_1d),
        },
        "island_counts": {"4h": len(islands_4h), "1d": len(islands_1d)},
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
        "design_revision": "01",
        "dataset_count": len(datasets),
        "assets": list(ASSETS),
        "segments": [s[1] for s in SEGMENTS],
        "registered_gaps_us": {
            key: list(value) for key, value in REGISTERED_GAPS_US.items()
        },
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
