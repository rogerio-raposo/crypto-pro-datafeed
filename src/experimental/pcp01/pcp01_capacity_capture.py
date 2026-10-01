#!/usr/bin/env python3
"""PCP-01 official raw Capacity capture for an activated pilot run.

This producer captures raw market evidence only. It never assigns Capacity,
Accessibility or Absorption states and never computes Ranking outputs.
"""

from __future__ import annotations

import argparse
import gzip
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from binance_qps_probe import (
    ProbeError,
    executable_notional,
    get_market,
    get_order_book,
    get_source_time,
)

SCHEMA_VERSION = "pcp01-capacity-capture-0.1"
CHILD_NOTIONAL_USD = 5_000_000 / 24
STANDARD_DEPTH = 1000
ESCALATED_DEPTH = 5000


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def classify_error(error: Exception) -> str:
    text = str(error)
    if "All Binance public hosts failed" in text:
        return "SOURCE_API_ERROR"
    if isinstance(error, ProbeError):
        return "INVALID_PAYLOAD"
    return "COLLECTOR_ERROR"


def capture_qev(qev: dict[str, Any]) -> dict[str, Any]:
    started = utc_now()
    symbol = qev["symbol"]
    try:
        market = get_market(symbol)
        if market["trading_status"] != "TRADING":
            return {
                "canonical_asset_id": qev["canonical_asset_id"],
                "venue": qev["venue"],
                "symbol": symbol,
                "collection_status": "SOURCE_MARKET_UNAVAILABLE",
                "started_at_utc": started.isoformat(),
                "completed_at_utc": utc_now().isoformat(),
                "market": market,
            }

        if (
            market["base_asset"] != qev["base_asset"]
            or market["quote_asset"] != qev["quote_asset"]
        ):
            raise ProbeError("QEV identity mismatch.")

        book = get_order_book(symbol, STANDARD_DEPTH)
        bid_notional = executable_notional(book["bids"])
        ask_notional = executable_notional(book["asks"])
        escalated = False

        if bid_notional < CHILD_NOTIONAL_USD or ask_notional < CHILD_NOTIONAL_USD:
            book = get_order_book(symbol, ESCALATED_DEPTH)
            bid_notional = executable_notional(book["bids"])
            ask_notional = executable_notional(book["asks"])
            escalated = True

        return {
            "canonical_asset_id": qev["canonical_asset_id"],
            "venue": qev["venue"],
            "market_type": "spot",
            "symbol": symbol,
            "base_asset": qev["base_asset"],
            "quote_asset": qev["quote_asset"],
            "quote_usd_equivalent": True,
            "normalization_method": "USDT_PARITY_PROXY",
            "collection_status": "SUCCESS",
            "started_at_utc": started.isoformat(),
            "completed_at_utc": utc_now().isoformat(),
            "market": market,
            "order_book": {
                "last_update_id": book["last_update_id"],
                "observed_at_utc": book["observed_at_utc"],
                "source_host": book["source_host"],
                "source_endpoint": book["source_endpoint"],
                "requested_limit": book["requested_limit"],
                "depth_escalated": escalated,
                "bid_levels_received": book["bid_levels_received"],
                "ask_levels_received": book["ask_levels_received"],
                "best_bid": book["best_bid"],
                "best_ask": book["best_ask"],
                "bid_notional_visible": bid_notional,
                "ask_notional_visible": ask_notional,
                "child_notional_usd": CHILD_NOTIONAL_USD,
                "sell_child_notional_covered": bid_notional >= CHILD_NOTIONAL_USD,
                "buy_child_notional_covered": ask_notional >= CHILD_NOTIONAL_USD,
                "bids": book["bids"],
                "asks": book["asks"],
            },
        }
    except Exception as error:
        return {
            "canonical_asset_id": qev["canonical_asset_id"],
            "venue": qev["venue"],
            "symbol": symbol,
            "base_asset": qev["base_asset"],
            "quote_asset": qev["quote_asset"],
            "collection_status": classify_error(error),
            "started_at_utc": started.isoformat(),
            "completed_at_utc": utc_now().isoformat(),
            "error_type": type(error).__name__,
            "error": str(error),
        }


def write_gzip_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, separators=(",", ":"))


def update_manifest(path: Path, event: dict[str, Any]) -> None:
    if path.exists():
        manifest = json.loads(path.read_text(encoding="utf-8"))
    else:
        manifest = {
            "schema_version": "pcp01-capture-manifest-0.1",
            "run_id": event["run_id"],
            "venue": "Binance",
            "events": [],
        }

    summary = {
        "capture_event_id": event["capture_event_id"],
        "event_index": event["event_index"],
        "target_time_utc": event["target_time_utc"],
        "started_at_utc": event["started_at_utc"],
        "completed_at_utc": event["completed_at_utc"],
        "technical_event_status": event["technical_event_status"],
        "success_count": event["success_count"],
        "planned_count": event["planned_count"],
        "asset_status": [
            {
                "canonical_asset_id": x["canonical_asset_id"],
                "symbol": x["symbol"],
                "collection_status": x["collection_status"],
                "observed_at_utc": x.get("order_book", {}).get("observed_at_utc"),
                "depth_limit": x.get("order_book", {}).get("requested_limit"),
                "depth_escalated": x.get("order_book", {}).get("depth_escalated"),
                "sell_child_notional_covered": x.get("order_book", {}).get("sell_child_notional_covered"),
                "buy_child_notional_covered": x.get("order_book", {}).get("buy_child_notional_covered"),
            }
            for x in event["assets"]
        ],
    }

    events = [
        x for x in manifest.get("events", [])
        if x.get("event_index") != summary["event_index"]
    ]
    events.append(summary)
    events.sort(key=lambda x: x["event_index"])
    manifest["events"] = events
    manifest["updated_at_utc"] = event["completed_at_utc"]
    manifest["successful_events"] = sum(x["technical_event_status"] == "PASS" for x in events)
    manifest["captured_events"] = len(events)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
    capture_start = parse_iso(activation["capture_start_utc"])
    t0 = parse_iso(activation["t0_utc"])

    if now < capture_start:
        print(json.dumps({"status": "WAITING_FOR_CAPTURE_START"}))
        return 0
    if now >= t0:
        print(json.dumps({"status": "CAPTURE_WINDOW_CLOSED"}))
        return 0

    event_index = int((now - capture_start).total_seconds() // 3600)
    if event_index < 0 or event_index >= 24:
        print(json.dumps({"status": "OUTSIDE_EVENT_RANGE", "event_index": event_index}))
        return 0

    target = capture_start + timedelta(hours=event_index)
    run_dir = args.output_root / activation["run_id"]
    event_path = run_dir / f"event-{event_index:02d}.json.gz"
    manifest_path = run_dir / "capture-manifest.json"

    if event_path.exists():
        print(json.dumps({
            "status": "DUPLICATE_EVENT_SKIPPED",
            "event_index": event_index,
            "path": str(event_path),
        }))
        return 0

    started = utc_now()
    source_time = get_source_time()
    assets = [capture_qev(qev) for qev in activation["qevs"]]
    success_count = sum(x["collection_status"] == "SUCCESS" for x in assets)

    event = {
        "schema_version": SCHEMA_VERSION,
        "run_id": activation["run_id"],
        "capture_event_id": f"{activation['run_id']}-E{event_index:02d}",
        "event_index": event_index,
        "target_time_utc": target.isoformat(),
        "started_at_utc": started.isoformat(),
        "completed_at_utc": utc_now().isoformat(),
        "source_time": source_time,
        "planned_count": len(assets),
        "success_count": success_count,
        "technical_event_status": "PASS" if success_count == len(assets) else "PARTIAL",
        "assets": assets,
        "methodology_note": (
            "Raw official capture only. No PEC, PR, Accessibility, Absorption "
            "or Capacity E-state is assigned by the Data Feed."
        ),
    }

    write_gzip_json(event_path, event)
    update_manifest(manifest_path, event)
    print(json.dumps({
        "status": "CAPTURED",
        "event_index": event_index,
        "technical_event_status": event["technical_event_status"],
        "success_count": success_count,
        "planned_count": len(assets),
        "event_path": str(event_path),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
