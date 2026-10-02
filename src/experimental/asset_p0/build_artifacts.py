#!/usr/bin/env python3
"""Build ASSET-P0-001 producer-side fixtures and historical datasets.

Implementation validation only. Formal P0 execution is not performed by this script.
"""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path

from p0_data import (
    DAY_US,
    HOUR_US,
    P0DataError,
    SERIALIZATION_ID,
    canonical_decimal,
    checksum_url,
    daily_archive_url,
    download,
    iso_to_us,
    monthly_archive_url,
    parse_binance_zip,
    resample_hourly,
    source_unit_for_archive_day,
    validate_native_hourly,
    verify_checksum,
    write_json,
    write_jsonl,
)

SYNTHETIC_VERSION = "ASSET-P0-SYNTHETIC-v0.1.0"
REAL_FIXTURE_VERSION = "ASSET-P0-REAL-FIXTURE-v0.1.0"
MAIN_DATASET_VERSION = "ASSET-P0-001-BTCUSDT-SPOT-1H-2025Q1-v0.1.0"


def _native_candle(
    open_time_us: int,
    *,
    open_: str,
    high: str,
    low: str,
    close: str,
    volume: str,
    dataset_version: str,
    source_timestamp_unit: str = "synthetic",
    quote_volume: str = "1000",
    trade_count: int = 10,
) -> dict:
    return {
        "asset": "BTC",
        "close": canonical_decimal(close),
        "data_origin": "NATIVE",
        "data_quality_flags": [],
        "dataset_version": dataset_version,
        "high": canonical_decimal(high),
        "instrument": "BTCUSDT",
        "interval_end_us": open_time_us + HOUR_US,
        "low": canonical_decimal(low),
        "market_type": "spot",
        "open": canonical_decimal(open_),
        "open_time_us": open_time_us,
        "quote_asset": "USDT",
        "quote_volume": canonical_decimal(quote_volume),
        "source_close_time_us": open_time_us + HOUR_US - 1,
        "source_timestamp_unit": source_timestamp_unit,
        "timeframe": "1h",
        "trade_count": trade_count,
        "venue": "Binance Spot",
        "volume": canonical_decimal(volume),
    }


def build_synthetic(output: Path) -> dict:
    start_us = iso_to_us("2025-02-01T00:00:00Z")
    end_us = start_us + 48 * HOUR_US
    missing_index = 7
    extreme_index = 13

    candles: list[dict] = []
    for i in range(48):
        if i == missing_index:
            continue
        base = Decimal("100") + Decimal(i) / Decimal("10")
        open_ = base
        close = base + Decimal("0.05")
        high = base + Decimal("0.20")
        low = base - Decimal("0.20")
        if i == extreme_index:
            high = Decimal("250")
        candles.append(
            _native_candle(
                start_us + i * HOUR_US,
                open_=str(open_),
                high=str(high),
                low=str(low),
                close=str(close),
                volume=str(Decimal("10") + Decimal(i) / Decimal("10")),
                quote_volume=str(Decimal("1000") + i),
                trade_count=10 + i,
                dataset_version=SYNTHETIC_VERSION,
            )
        )

    result = validate_native_hourly(
        candles,
        expected_start_us=start_us,
        expected_end_us=end_us,
        require_contiguous=False,
    )
    if result.critical_errors:
        raise P0DataError(f"Unexpected synthetic critical errors: {result.critical_errors}")

    derived_4h = resample_hourly(result.candles, "4h")
    derived_1d = resample_hourly(result.candles, "1d")

    output.mkdir(parents=True, exist_ok=True)
    hashes = {
        "native_jsonl": write_jsonl(output / "native.jsonl", result.candles),
        "derived_4h_jsonl": write_jsonl(output / "derived_4h.jsonl", derived_4h),
        "derived_1d_jsonl": write_jsonl(output / "derived_1d.jsonl", derived_1d),
    }
    expected = {
        "checkpoint_after_batch_timestamp_us": start_us + DAY_US,
        "dataset_version": SYNTHETIC_VERSION,
        "derived_1d_records": len(derived_1d),
        "derived_4h_records": len(derived_4h),
        "duplicate_open_times_us": result.duplicate_open_times_us,
        "expected_slots": 48,
        "extreme_price_open_times_us": [
            int(c["open_time_us"])
            for c in result.candles
            if "EXTREME_PRICE_MOVE" in c["data_quality_flags"]
        ],
        "hashes": hashes,
        "incomplete_1d_open_times_us": [
            int(c["open_time_us"]) for c in derived_1d if not c["complete"]
        ],
        "incomplete_4h_open_times_us": [
            int(c["open_time_us"]) for c in derived_4h if not c["complete"]
        ],
        "missing_open_times_us": result.missing_open_times_us,
        "native_records": len(result.candles),
        "serialization_id": SERIALIZATION_ID,
    }
    write_json(output / "expected.json", expected)
    return expected


def _fetch_verified_archive(
    archive_url: str,
    cache_dir: Path,
) -> tuple[Path, str, str]:
    zip_path = cache_dir / archive_url.rsplit("/", 1)[-1]
    checksum_path = cache_dir / (zip_path.name + ".CHECKSUM")
    if not zip_path.exists():
        download(archive_url, zip_path)
    if not checksum_path.exists():
        download(checksum_url(archive_url), checksum_path)
    checksum_text = checksum_path.read_text(encoding="utf-8")
    archive_sha = verify_checksum(zip_path, checksum_text)
    return zip_path, archive_sha, checksum_text.strip()


def build_real_fixture(output: Path, cache_dir: Path) -> dict:
    days = [date(2024, 12, 31), date(2025, 1, 1), date(2025, 1, 2)]
    candles: list[dict] = []
    archives: list[dict] = []

    for day in days:
        day_text = day.isoformat()
        url = daily_archive_url(day_text)
        zip_path, archive_sha, official_checksum = _fetch_verified_archive(url, cache_dir)
        unit = source_unit_for_archive_day(day)
        parsed = parse_binance_zip(
            zip_path,
            source_timestamp_unit=unit,
            dataset_version=REAL_FIXTURE_VERSION,
        )
        candles.extend(parsed)
        archives.append(
            {
                "archive_sha256": archive_sha,
                "archive_url": url,
                "official_checksum_document": official_checksum,
                "source_timestamp_unit": unit,
            }
        )

    start_us = iso_to_us("2024-12-31T00:00:00Z")
    end_us = iso_to_us("2025-01-03T00:00:00Z")
    result = validate_native_hourly(
        candles,
        expected_start_us=start_us,
        expected_end_us=end_us,
        require_contiguous=True,
    )
    if result.critical_errors:
        raise P0DataError(f"Real fixture validation failed: {result.critical_errors}")
    if len(result.candles) != 72:
        raise P0DataError(f"Expected 72 real fixture records, got {len(result.candles)}")

    derived_4h = resample_hourly(result.candles, "4h")
    derived_1d = resample_hourly(result.candles, "1d")
    if any(not c["complete"] for c in derived_4h + derived_1d):
        raise P0DataError("Real fixture produced incomplete derived candles.")

    output.mkdir(parents=True, exist_ok=True)
    hashes = {
        "derived_1d_jsonl": write_jsonl(output / "derived_1d.jsonl", derived_1d),
        "derived_4h_jsonl": write_jsonl(output / "derived_4h.jsonl", derived_4h),
        "native_jsonl": write_jsonl(output / "native.jsonl", result.candles),
    }
    manifest = {
        "archives": archives,
        "dataset_id": "ASSET-P0-REAL-GOLDEN-BTCUSDT-1H-2024-12-31_2025-01-02",
        "dataset_version": REAL_FIXTURE_VERSION,
        "derived_1d_records": len(derived_1d),
        "derived_4h_records": len(derived_4h),
        "end_us": end_us,
        "hashes": hashes,
        "native_records": len(result.candles),
        "serialization_id": SERIALIZATION_ID,
        "start_us": start_us,
    }
    write_json(output / "manifest.json", manifest)
    return manifest


def build_main_dataset(output: Path, cache_dir: Path) -> dict:
    months = ["2025-01", "2025-02", "2025-03"]
    candles: list[dict] = []
    archives: list[dict] = []

    for month in months:
        url = monthly_archive_url(month)
        zip_path, archive_sha, official_checksum = _fetch_verified_archive(url, cache_dir)
        candles.extend(
            parse_binance_zip(
                zip_path,
                source_timestamp_unit="us",
                dataset_version=MAIN_DATASET_VERSION,
            )
        )
        archives.append(
            {
                "archive_sha256": archive_sha,
                "archive_url": url,
                "official_checksum_document": official_checksum,
                "source_timestamp_unit": "us",
            }
        )

    start_us = iso_to_us("2025-01-01T00:00:00Z")
    end_us = iso_to_us("2025-04-01T00:00:00Z")
    result = validate_native_hourly(
        candles,
        expected_start_us=start_us,
        expected_end_us=end_us,
        require_contiguous=True,
    )
    if result.critical_errors:
        raise P0DataError(f"Main dataset validation failed: {result.critical_errors}")
    if len(result.candles) != 2160:
        raise P0DataError(f"Expected 2160 native records, got {len(result.candles)}")

    derived_4h = resample_hourly(result.candles, "4h")
    derived_1d = resample_hourly(result.candles, "1d")
    if len(derived_4h) != 540 or any(not c["complete"] for c in derived_4h):
        raise P0DataError("4h resampling count/completeness mismatch.")
    if len(derived_1d) != 90 or any(not c["complete"] for c in derived_1d):
        raise P0DataError("1d resampling count/completeness mismatch.")

    output.mkdir(parents=True, exist_ok=True)
    hashes = {
        "derived_1d_jsonl": write_jsonl(output / "derived_1d.jsonl", derived_1d),
        "derived_4h_jsonl": write_jsonl(output / "derived_4h.jsonl", derived_4h),
        "native_jsonl": write_jsonl(output / "native.jsonl", result.candles),
    }
    manifest = {
        "archives": archives,
        "asset": "BTC",
        "base_asset": "BTC",
        "candle_boundary_policy_id": "asset-p0-utc-boundaries-v0.1.0",
        "checksum": hashes["native_jsonl"],
        "checksum_algorithm": "SHA-256",
        "dataset_id": "ASSET-P0-001-BTCUSDT-SPOT-1H-2025Q1",
        "dataset_version": MAIN_DATASET_VERSION,
        "derived_1d_records": len(derived_1d),
        "derived_4h_records": len(derived_4h),
        "end_timestamp": "2025-04-01T00:00:00Z",
        "hashes": hashes,
        "ingestion_timestamp": datetime.now(timezone.utc).isoformat(),
        "instrument": "BTCUSDT",
        "market_type": "spot",
        "missing_data_policy_id": "asset-p0-main-contiguous-v0.1.0",
        "native_timeframe": "1h",
        "quote_asset": "USDT",
        "raw_record_count": len(candles),
        "schema_version": "asset-p0-dataset-manifest-0.1.0",
        "serialization_id": SERIALIZATION_ID,
        "source_endpoint_or_contract": "Binance Public Data monthly Spot kline archives",
        "source_provider": "Binance Public Data",
        "start_timestamp": "2025-01-01T00:00:00Z",
        "timezone_policy": "UTC",
        "validated_record_count": len(result.candles),
        "venue": "Binance Spot",
    }
    manifest_sha = write_json(output / "dataset_manifest.json", manifest)
    return {"manifest": manifest, "manifest_sha256": manifest_sha}


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    synthetic = sub.add_parser("synthetic")
    synthetic.add_argument("--output", type=Path, required=True)

    real = sub.add_parser("real-fixture")
    real.add_argument("--output", type=Path, required=True)
    real.add_argument("--cache", type=Path, required=True)

    main_ds = sub.add_parser("main-dataset")
    main_ds.add_argument("--output", type=Path, required=True)
    main_ds.add_argument("--cache", type=Path, required=True)

    args = parser.parse_args()

    if args.command == "synthetic":
        result = build_synthetic(args.output)
    elif args.command == "real-fixture":
        result = build_real_fixture(args.output, args.cache)
    else:
        result = build_main_dataset(args.output, args.cache)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
