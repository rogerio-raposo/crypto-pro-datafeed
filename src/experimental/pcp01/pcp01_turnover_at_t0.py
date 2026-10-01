#!/usr/bin/env python3
"""Capture exact 7x24h turnover window ending at PCP-01 T0."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from binance_qps_probe import ProbeError, request_json

SCHEMA_VERSION = "pcp01-turnover-at-t0-0.1"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def iso_from_ms(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).isoformat()


def capture_symbol(qev: dict[str, Any], t0: datetime) -> dict[str, Any]:
    start = t0 - timedelta(days=7)
    start_ms = int(start.timestamp() * 1000)
    end_ms = int(t0.timestamp() * 1000) - 1

    payload, host, url = request_json(
        "/api/v3/klines",
        {
            "symbol": qev["symbol"],
            "interval": "1h",
            "startTime": start_ms,
            "endTime": end_ms,
            "limit": 1000,
        },
    )
    if not isinstance(payload, list):
        raise ProbeError("Invalid 1h kline payload.")

    rows = []
    for raw in payload:
        if not isinstance(raw, list) or len(raw) < 8:
            raise ProbeError("Malformed 1h kline record.")
        open_ms = int(raw[0])
        close_ms = int(raw[6])
        if open_ms < start_ms or open_ms >= int(t0.timestamp() * 1000):
            continue
        rows.append({
            "open_time_utc": iso_from_ms(open_ms),
            "close_time_utc": iso_from_ms(close_ms),
            "base_volume": float(raw[5]),
            "quote_volume": float(raw[7]),
        })

    rows.sort(key=lambda x: x["open_time_utc"])
    if len(rows) != 168:
        raise ProbeError(f"Expected 168 hourly records, received {len(rows)}.")

    daily_bins = []
    for day in range(7):
        chunk = rows[day * 24:(day + 1) * 24]
        daily_bins.append({
            "bin_index": day,
            "start_utc": chunk[0]["open_time_utc"],
            "end_utc": chunk[-1]["close_time_utc"],
            "base_volume": sum(x["base_volume"] for x in chunk),
            "quote_volume": sum(x["quote_volume"] for x in chunk),
        })

    return {
        "canonical_asset_id": qev["canonical_asset_id"],
        "venue": qev["venue"],
        "symbol": qev["symbol"],
        "quote_asset": qev["quote_asset"],
        "normalization_method": "USDT_PARITY_PROXY",
        "collection_status": "SUCCESS",
        "source_host": host,
        "source_endpoint": url,
        "window_start_utc": start.isoformat(),
        "window_end_utc": t0.isoformat(),
        "hourly_records": rows,
        "daily_24h_bins": daily_bins,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--activation", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()

    activation = json.loads(args.activation.read_text(encoding="utf-8"))
    if not activation.get("active"):
        print(json.dumps({"status": "INACTIVE"}))
        return 0

    now = utc_now()
    t0 = parse_iso(activation["t0_utc"])
    if now < t0:
        print(json.dumps({"status": "WAITING_FOR_T0"}))
        return 0

    run_dir = args.output_root / activation["run_id"]
    output = run_dir / "turnover-7d-at-t0.json"
    if output.exists():
        print(json.dumps({"status": "ALREADY_CAPTURED", "path": str(output)}))
        return 0

    records = []
    failures = []
    for qev in activation["qevs"]:
        try:
            records.append(capture_symbol(qev, t0))
        except Exception as error:
            failures.append({
                "canonical_asset_id": qev["canonical_asset_id"],
                "symbol": qev["symbol"],
                "error_type": type(error).__name__,
                "error": str(error),
            })

    result = {
        "schema_version": SCHEMA_VERSION,
        "run_id": activation["run_id"],
        "captured_at_utc": utc_now().isoformat(),
        "t0_utc": t0.isoformat(),
        "planned_count": len(activation["qevs"]),
        "success_count": len(records),
        "records": records,
        "failures": failures,
        "methodology_note": (
            "Raw/normalized turnover evidence only. PR and Absorption states "
            "are calculated downstream by the Ranking validation layer."
        ),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "CAPTURED" if not failures else "PARTIAL",
        "success_count": len(records),
        "planned_count": len(activation["qevs"]),
        "path": str(output),
    }, indent=2))
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
