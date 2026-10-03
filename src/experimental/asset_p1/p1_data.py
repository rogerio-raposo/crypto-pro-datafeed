#!/usr/bin/env python3
"""ASSET-P1-D1-001 multi-asset historical-data utilities.

Experimental / non-normative. Python Standard Library only.
Frozen P0 source files are not modified.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import urllib.request
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable, Sequence

HOUR_US = 3_600_000_000
DAY_US = 86_400_000_000
BINANCE_ARCHIVE_ROOT = "https://data.binance.vision/data/spot"
SERIALIZATION_ID = "asset-p1-canonical-json-v0.1.0"
DATASET_SCHEMA_VERSION = "asset-p1-dataset-manifest-0.1.0"


class P1DataError(RuntimeError):
    pass


def canonical_decimal(value: str | int | Decimal) -> str:
    try:
        d = value if isinstance(value, Decimal) else Decimal(str(value))
    except InvalidOperation as exc:
        raise P1DataError(f"Invalid decimal value: {value!r}") from exc
    if not d.is_finite():
        raise P1DataError(f"Non-finite decimal value: {value!r}")
    if d == 0:
        return "0"
    text = format(d, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def canonical_json_bytes(obj: dict) -> bytes:
    return (
        json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def expected_sha256(text: str) -> str:
    token = text.strip().split()[0].lower()
    if len(token) != 64 or any(ch not in "0123456789abcdef" for ch in token):
        raise P1DataError("Invalid SHA-256 checksum document.")
    return token


def verify_checksum(path: Path, checksum_text: str) -> str:
    expected = expected_sha256(checksum_text)
    actual = sha256_path(path)
    if actual != expected:
        raise P1DataError(
            f"Checksum mismatch for {path.name}: expected {expected}, got {actual}"
        )
    return actual


def timestamp_to_us(raw: str | int, unit: str) -> int:
    value = int(raw)
    if unit == "ms":
        return value * 1000
    if unit == "us":
        return value
    raise P1DataError(f"Unsupported source timestamp unit: {unit}")


def instrument_asset(instrument: str) -> tuple[str, str]:
    if not instrument.endswith("USDT"):
        raise P1DataError(f"Unsupported quote convention: {instrument}")
    return instrument[:-4], "USDT"


def monthly_archive_url(instrument: str, year_month: str) -> str:
    name = f"{instrument}-1h-{year_month}.zip"
    return f"{BINANCE_ARCHIVE_ROOT}/monthly/klines/{instrument}/1h/{name}"


def checksum_url(archive_url: str) -> str:
    return archive_url + ".CHECKSUM"


def download(url: str, destination: Path, timeout: int = 45) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Crypto-Pro-DataFeed-ASSET-P1/0.1"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        destination.write_bytes(r.read())


def fetch_verified_archive(
    instrument: str,
    year_month: str,
    cache_dir: Path,
) -> tuple[Path, dict]:
    url = monthly_archive_url(instrument, year_month)
    zip_path = cache_dir / instrument / f"{instrument}-1h-{year_month}.zip"
    checksum_path = Path(str(zip_path) + ".CHECKSUM")
    if not zip_path.exists():
        download(url, zip_path)
    if not checksum_path.exists():
        download(checksum_url(url), checksum_path)
    checksum_text = checksum_path.read_text(encoding="utf-8")
    actual = verify_checksum(zip_path, checksum_text)
    return zip_path, {
        "archive_url": url,
        "archive_sha256": actual,
        "official_checksum_document": checksum_text.strip(),
        "source_timestamp_unit": "ms",
        "year_month": year_month,
    }


def _validate_price_fields(candle: dict) -> list[str]:
    flags: list[str] = []
    try:
        o = Decimal(candle["open"])
        h = Decimal(candle["high"])
        l = Decimal(candle["low"])
        c = Decimal(candle["close"])
        v = Decimal(candle["volume"])
    except (InvalidOperation, KeyError) as exc:
        raise P1DataError("Malformed canonical candle fields.") from exc
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
    instrument: str,
    dataset_version: str,
    source_timestamp_unit: str = "ms",
) -> dict:
    if len(row) < 11:
        raise P1DataError(f"Incomplete Binance kline row with {len(row)} fields.")
    base, quote = instrument_asset(instrument)
    open_us = timestamp_to_us(row[0], source_timestamp_unit)
    source_close_us = timestamp_to_us(row[6], source_timestamp_unit)
    candle = {
        "asset": base,
        "close": canonical_decimal(row[4]),
        "data_origin": "NATIVE",
        "data_quality_flags": [],
        "dataset_version": dataset_version,
        "high": canonical_decimal(row[2]),
        "instrument": instrument,
        "interval_end_us": open_us + HOUR_US,
        "low": canonical_decimal(row[3]),
        "market_type": "spot",
        "open": canonical_decimal(row[1]),
        "open_time_us": open_us,
        "quote_asset": quote,
        "quote_volume": canonical_decimal(row[7]),
        "source_close_time_us": source_close_us,
        "source_timestamp_unit": source_timestamp_unit,
        "timeframe": "1h",
        "trade_count": int(row[8]),
        "venue": "Binance Spot",
        "volume": canonical_decimal(row[5]),
    }
    candle["data_quality_flags"] = sorted(set(_validate_price_fields(candle)))
    return candle


def parse_binance_zip(
    zip_path: Path,
    *,
    instrument: str,
    dataset_version: str,
    source_timestamp_unit: str = "ms",
) -> list[dict]:
    out: list[dict] = []
    with zipfile.ZipFile(zip_path) as zf:
        csv_names = [n for n in zf.namelist() if n.lower().endswith(".csv")]
        if len(csv_names) != 1:
            raise P1DataError(
                f"Expected one CSV in {zip_path.name}, found {csv_names}"
            )
        with zf.open(csv_names[0]) as raw:
            text = io.TextIOWrapper(raw, encoding="utf-8", newline="")
            for row in csv.reader(text):
                if not row or not row[0].strip().isdigit():
                    continue
                out.append(
                    normalize_binance_kline(
                        row,
                        instrument=instrument,
                        dataset_version=dataset_version,
                        source_timestamp_unit=source_timestamp_unit,
                    )
                )
    return out


@dataclass(frozen=True)
class ValidationResult:
    candles: list[dict]
    missing_open_times_us: list[int]
    duplicate_open_times_us: list[int]
    critical_errors: list[str]


def validate_native_hourly(
    candles: Sequence[dict],
    *,
    expected_start_us: int,
    expected_end_us: int,
) -> ValidationResult:
    ordered = sorted((dict(c) for c in candles), key=lambda c: int(c["open_time_us"]))
    seen: set[int] = set()
    missing: list[int] = []
    duplicates: list[int] = []
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
        seen.add(open_us)
        if "INVALID_OHLC" in flags:
            critical.append(f"Invalid OHLC at {open_us}")

        if idx:
            prev_open = int(ordered[idx - 1]["open_time_us"])
            expected = prev_open + HOUR_US
            if open_us > expected:
                for ts in range(expected, open_us, HOUR_US):
                    missing.append(ts)
                flags.add("MISSING_INTERVAL")
            elif open_us < expected and open_us != prev_open:
                critical.append(f"Non-monotonic interval at {open_us}")
        candle["data_quality_flags"] = sorted(flags)

    if not ordered or int(ordered[0]["open_time_us"]) != expected_start_us:
        critical.append("Dataset start mismatch.")
    if not ordered or int(ordered[-1]["interval_end_us"]) != expected_end_us:
        critical.append("Dataset end mismatch.")
    if missing:
        critical.append(f"Missing {len(set(missing))} native interval(s).")
    if duplicates:
        critical.append(f"Found {len(set(duplicates))} duplicate interval(s).")

    return ValidationResult(
        candles=ordered,
        missing_open_times_us=sorted(set(missing)),
        duplicate_open_times_us=sorted(set(duplicates)),
        critical_errors=sorted(set(critical)),
    )


def resample_hourly(candles: Sequence[dict], target: str) -> list[dict]:
    if target == "4h":
        target_us, required = 4 * HOUR_US, 4
    elif target == "1d":
        target_us, required = DAY_US, 24
    else:
        raise P1DataError(f"Unsupported target timeframe: {target}")

    groups: dict[int, list[dict]] = {}
    for c in sorted(candles, key=lambda x: int(x["open_time_us"])):
        bucket = (int(c["open_time_us"]) // target_us) * target_us
        groups.setdefault(bucket, []).append(c)

    out: list[dict] = []
    for bucket in sorted(groups):
        group = groups[bucket]
        complete = (
            len(group) == required
            and int(group[0]["open_time_us"]) == bucket
            and int(group[-1]["interval_end_us"]) == bucket + target_us
            and all(
                int(group[i]["open_time_us"]) + HOUR_US
                == int(group[i + 1]["open_time_us"])
                for i in range(len(group) - 1)
            )
        )
        flags = {
            f
            for c in group
            for f in c.get("data_quality_flags", [])
            if f != "MISSING_INTERVAL"
        }
        if not complete:
            flags.add("MISSING_INTERVAL")
        derived = {
            "asset": group[0]["asset"],
            "close": group[-1]["close"],
            "complete": complete,
            "data_origin": "DERIVED",
            "data_quality_flags": sorted(flags),
            "dataset_version": group[0]["dataset_version"],
            "high": canonical_decimal(max(Decimal(c["high"]) for c in group)),
            "instrument": group[0]["instrument"],
            "interval_end_us": bucket + target_us,
            "low": canonical_decimal(min(Decimal(c["low"]) for c in group)),
            "market_type": group[0]["market_type"],
            "open": group[0]["open"],
            "open_time_us": bucket,
            "quote_asset": group[0]["quote_asset"],
            "quote_volume": canonical_decimal(
                sum(Decimal(c.get("quote_volume", "0")) for c in group)
            ),
            "source_timeframe": "1h",
            "timeframe": target,
            "trade_count": sum(int(c.get("trade_count", 0)) for c in group),
            "venue": group[0]["venue"],
            "volume": canonical_decimal(sum(Decimal(c["volume"]) for c in group)),
        }
        out.append(derived)
    return out


def serialize_jsonl(records: Iterable[dict]) -> bytes:
    return b"".join(canonical_json_bytes(r) for r in records)


def write_jsonl(path: Path, records: Iterable[dict]) -> str:
    data = serialize_jsonl(records)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return sha256_bytes(data)


def write_json(path: Path, obj: dict) -> str:
    data = canonical_json_bytes(obj)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return sha256_bytes(data)


def iso_to_us(value: str) -> int:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1_000_000)
