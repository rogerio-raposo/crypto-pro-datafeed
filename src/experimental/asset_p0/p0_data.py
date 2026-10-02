#!/usr/bin/env python3
"""ASSET-P0-001 producer-side historical data utilities.

Experimental / non-normative. Python Standard Library only.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import urllib.request
import zipfile
from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable, Sequence

HOUR_US = 3_600_000_000
DAY_US = 86_400_000_000
SOURCE_MICROSECOND_CUTOFF = date(2025, 1, 1)
EXTREME_PRICE_RATIO = Decimal("0.50")
SERIALIZATION_ID = "asset-p0-canonical-json-v0.1.0"
BINANCE_ARCHIVE_ROOT = "https://data.binance.vision/data/spot"


class P0DataError(RuntimeError):
    """Raised when producer-side P0 data validation fails."""


def canonical_decimal(value: str | int | Decimal) -> str:
    try:
        d = value if isinstance(value, Decimal) else Decimal(str(value))
    except InvalidOperation as exc:
        raise P0DataError(f"Invalid decimal value: {value!r}") from exc
    if not d.is_finite():
        raise P0DataError(f"Non-finite decimal value: {value!r}")
    if d == 0:
        return "0"
    text = format(d, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def canonical_json_line(obj: dict) -> bytes:
    return (
        json.dumps(
            obj,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def canonical_json_document(obj: dict) -> bytes:
    return canonical_json_line(obj)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def expected_sha256(checksum_text: str) -> str:
    token = checksum_text.strip().split()[0].lower()
    if len(token) != 64 or any(ch not in "0123456789abcdef" for ch in token):
        raise P0DataError("Invalid SHA-256 checksum document.")
    return token


def verify_checksum(path: Path, checksum_text: str) -> str:
    expected = expected_sha256(checksum_text)
    actual = sha256_path(path)
    if actual != expected:
        raise P0DataError(
            f"Archive checksum mismatch for {path.name}: "
            f"expected {expected}, got {actual}"
        )
    return actual


def source_unit_for_archive_day(archive_day: date) -> str:
    return "us" if archive_day >= SOURCE_MICROSECOND_CUTOFF else "ms"


def timestamp_to_us(raw: str | int, source_unit: str) -> int:
    value = int(raw)
    if source_unit == "us":
        return value
    if source_unit == "ms":
        return value * 1000
    raise P0DataError(f"Unsupported timestamp unit: {source_unit}")


def _validate_price_fields(candle: dict) -> list[str]:
    flags: list[str] = []
    try:
        o = Decimal(candle["open"])
        h = Decimal(candle["high"])
        l = Decimal(candle["low"])
        c = Decimal(candle["close"])
        v = Decimal(candle["volume"])
    except (InvalidOperation, KeyError) as exc:
        raise P0DataError("Malformed canonical candle decimal fields.") from exc

    if min(o, h, l, c, v) < 0:
        flags.append("INVALID_OHLC")
    if h < o or h < c or l > o or l > c or h < l:
        flags.append("INVALID_OHLC")
    if v == 0:
        flags.append("ZERO_VOLUME")
    return flags


def normalize_binance_kline(
    row: Sequence[str],
    *,
    source_timestamp_unit: str,
    dataset_version: str,
    instrument: str = "BTCUSDT",
    venue: str = "Binance Spot",
    market_type: str = "spot",
    timeframe: str = "1h",
) -> dict:
    if len(row) < 11:
        raise P0DataError(f"Incomplete Binance kline row with {len(row)} fields.")

    open_time_us = timestamp_to_us(row[0], source_timestamp_unit)
    source_close_time_us = timestamp_to_us(row[6], source_timestamp_unit)
    interval_end_us = open_time_us + HOUR_US

    candle = {
        "asset": "BTC",
        "data_origin": "NATIVE",
        "data_quality_flags": [],
        "dataset_version": dataset_version,
        "high": canonical_decimal(row[2]),
        "instrument": instrument,
        "interval_end_us": interval_end_us,
        "low": canonical_decimal(row[3]),
        "market_type": market_type,
        "open": canonical_decimal(row[1]),
        "open_time_us": open_time_us,
        "quote_asset": "USDT",
        "quote_volume": canonical_decimal(row[7]),
        "source_close_time_us": source_close_time_us,
        "source_timestamp_unit": source_timestamp_unit,
        "timeframe": timeframe,
        "trade_count": int(row[8]),
        "venue": venue,
        "volume": canonical_decimal(row[5]),
        "close": canonical_decimal(row[4]),
    }
    candle["data_quality_flags"] = sorted(set(_validate_price_fields(candle)))
    return candle


def parse_binance_zip(
    zip_path: Path,
    *,
    source_timestamp_unit: str,
    dataset_version: str,
) -> list[dict]:
    rows: list[dict] = []
    with zipfile.ZipFile(zip_path) as archive:
        csv_names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
        if len(csv_names) != 1:
            raise P0DataError(
                f"Expected exactly one CSV in {zip_path.name}, found {csv_names}"
            )
        with archive.open(csv_names[0]) as raw:
            text = io.TextIOWrapper(raw, encoding="utf-8", newline="")
            reader = csv.reader(text)
            for row in reader:
                if not row:
                    continue
                if not row[0].strip().isdigit():
                    continue
                rows.append(
                    normalize_binance_kline(
                        row,
                        source_timestamp_unit=source_timestamp_unit,
                        dataset_version=dataset_version,
                    )
                )
    return rows


@dataclass(frozen=True)
class ValidationResult:
    candles: list[dict]
    missing_open_times_us: list[int]
    duplicate_open_times_us: list[int]
    critical_errors: list[str]


def validate_native_hourly(
    candles: Sequence[dict],
    *,
    expected_start_us: int | None = None,
    expected_end_us: int | None = None,
    require_contiguous: bool,
) -> ValidationResult:
    ordered = sorted((dict(c) for c in candles), key=lambda c: int(c["open_time_us"]))
    seen: set[int] = set()
    duplicates: list[int] = []
    missing: list[int] = []
    critical: list[str] = []

    for idx, candle in enumerate(ordered):
        open_us = int(candle["open_time_us"])
        end_us = int(candle["interval_end_us"])
        flags = set(candle.get("data_quality_flags", []))

        if open_us % HOUR_US != 0 or end_us != open_us + HOUR_US:
            flags.add("TIMESTAMP_IRREGULARITY")
            critical.append(f"Timestamp irregularity at {open_us}")

        if open_us in seen:
            flags.add("DUPLICATE_CANDLE")
            duplicates.append(open_us)
            critical.append(f"Duplicate candle at {open_us}")
        seen.add(open_us)

        if "INVALID_OHLC" in flags:
            critical.append(f"Invalid OHLC at {open_us}")

        if idx:
            prev = ordered[idx - 1]
            prev_open = int(prev["open_time_us"])
            expected = prev_open + HOUR_US
            if open_us > expected:
                for missing_us in range(expected, open_us, HOUR_US):
                    missing.append(missing_us)
                flags.add("MISSING_INTERVAL")
            elif open_us < expected and open_us != prev_open:
                critical.append(f"Non-monotonic interval at {open_us}")

            prev_close = Decimal(prev["close"])
            if prev_close > 0:
                high = Decimal(candle["high"])
                low = Decimal(candle["low"])
                move = max(abs(high - prev_close), abs(low - prev_close)) / prev_close
                if move >= EXTREME_PRICE_RATIO:
                    flags.add("EXTREME_PRICE_MOVE")

        candle["data_quality_flags"] = sorted(flags)

    if expected_start_us is not None:
        if not ordered or int(ordered[0]["open_time_us"]) != expected_start_us:
            critical.append("Dataset does not start at the expected interval.")

    if expected_end_us is not None:
        if not ordered or int(ordered[-1]["interval_end_us"]) != expected_end_us:
            critical.append("Dataset does not end at the expected interval.")

    if require_contiguous and missing:
        critical.append(f"Missing {len(missing)} required native interval(s).")
    if duplicates:
        critical.append(f"Found {len(duplicates)} duplicate native interval(s).")

    return ValidationResult(
        candles=ordered,
        missing_open_times_us=sorted(set(missing)),
        duplicate_open_times_us=sorted(set(duplicates)),
        critical_errors=sorted(set(critical)),
    )


def resample_hourly(candles: Sequence[dict], target: str) -> list[dict]:
    if target == "4h":
        target_us = 4 * HOUR_US
        expected_count = 4
    elif target == "1d":
        target_us = DAY_US
        expected_count = 24
    else:
        raise P0DataError(f"Unsupported target timeframe: {target}")

    groups: dict[int, list[dict]] = {}
    for candle in sorted(candles, key=lambda c: int(c["open_time_us"])):
        open_us = int(candle["open_time_us"])
        bucket = (open_us // target_us) * target_us
        groups.setdefault(bucket, []).append(candle)

    result: list[dict] = []
    for bucket in sorted(groups):
        group = groups[bucket]
        flags = set()
        for candle in group:
            flags.update(
                flag
                for flag in candle.get("data_quality_flags", [])
                if flag != "MISSING_INTERVAL"
            )
        complete = (
            len(group) == expected_count
            and int(group[0]["open_time_us"]) == bucket
            and int(group[-1]["interval_end_us"]) == bucket + target_us
            and all(
                int(group[i]["open_time_us"]) + HOUR_US
                == int(group[i + 1]["open_time_us"])
                for i in range(len(group) - 1)
            )
        )
        if not complete:
            flags.add("MISSING_INTERVAL")

        high = max(Decimal(c["high"]) for c in group)
        low = min(Decimal(c["low"]) for c in group)
        volume = sum(Decimal(c["volume"]) for c in group)
        quote_volume = sum(Decimal(c.get("quote_volume", "0")) for c in group)
        trade_count = sum(int(c.get("trade_count", 0)) for c in group)

        derived = {
            "asset": group[0]["asset"],
            "close": group[-1]["close"],
            "complete": complete,
            "data_origin": "DERIVED",
            "data_quality_flags": sorted(flags),
            "dataset_version": group[0]["dataset_version"],
            "high": canonical_decimal(high),
            "instrument": group[0]["instrument"],
            "interval_end_us": bucket + target_us,
            "low": canonical_decimal(low),
            "market_type": group[0]["market_type"],
            "open": group[0]["open"],
            "open_time_us": bucket,
            "quote_asset": group[0]["quote_asset"],
            "quote_volume": canonical_decimal(quote_volume),
            "source_timeframe": "1h",
            "timeframe": target,
            "trade_count": trade_count,
            "venue": group[0]["venue"],
            "volume": canonical_decimal(volume),
        }
        result.append(derived)
    return result


def serialize_jsonl(records: Iterable[dict]) -> bytes:
    return b"".join(canonical_json_line(record) for record in records)


def write_jsonl(path: Path, records: Iterable[dict]) -> str:
    data = serialize_jsonl(records)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return sha256_bytes(data)


def write_json(path: Path, obj: dict) -> str:
    data = canonical_json_document(obj)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return sha256_bytes(data)


def download(url: str, destination: Path, *, timeout: int = 30) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Crypto-Pro-DataFeed-ASSET-P0/0.1"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        destination.write_bytes(response.read())


def monthly_archive_url(year_month: str) -> str:
    name = f"BTCUSDT-1h-{year_month}.zip"
    return f"{BINANCE_ARCHIVE_ROOT}/monthly/klines/BTCUSDT/1h/{name}"


def daily_archive_url(day: str) -> str:
    name = f"BTCUSDT-1h-{day}.zip"
    return f"{BINANCE_ARCHIVE_ROOT}/daily/klines/BTCUSDT/1h/{name}"


def checksum_url(archive_url: str) -> str:
    return archive_url + ".CHECKSUM"


def iso_to_us(value: str) -> int:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1_000_000)
