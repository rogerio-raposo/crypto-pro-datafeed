#!/usr/bin/env python3
"""PCP-01 multi-asset Capacity dry-run cycle for Binance Spot.

This is an operational validation collector. It does not calculate PEC, PR,
Accessibility/Absorption E-states, Capacity Gate results, or Ranking outputs.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from binance_qps_probe import (
    ProbeError,
    executable_notional,
    get_market,
    get_order_book,
    get_source_time,
    get_turnover_history,
)

SCHEMA_VERSION = "pcp01-capacity-dry-run-0.1"
STATUS_SCHEMA_VERSION = "pcp01-capacity-dry-run-status-0.1"
VENUE = "Binance"
DEPTH_LIMIT = 1000
CHILD_NOTIONAL_USD = 5_000_000 / 24

QEV_MAP = [
    ("CPS-PLUME", "PLUMEUSDT", "PLUME", "USDT"),
    ("CPS-OP", "OPUSDT", "OP", "USDT"),
    ("CPS-APT", "APTUSDT", "APT", "USDT"),
    ("CPS-SUI", "SUIUSDT", "SUI", "USDT"),
    ("CPS-LINK", "LINKUSDT", "LINK", "USDT"),
    ("CPS-RSR", "RSRUSDT", "RSR", "USDT"),
    ("CPS-INJ", "INJUSDT", "INJ", "USDT"),
    ("CPS-HYPE", "HYPEUSDT", "HYPE", "USDT"),
    ("CPS-SYRUP", "SYRUPUSDT", "SYRUP", "USDT"),
]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def hour_slot(dt: datetime) -> str:
    return dt.replace(minute=0, second=0, microsecond=0).isoformat()


def classify_error(error: Exception) -> str:
    text = str(error)
    if "All Binance public hosts failed" in text:
        return "SOURCE_API_ERROR"
    if "Only " in text and "closed daily candles" in text:
        return "INVALID_PAYLOAD"
    if isinstance(error, ProbeError):
        return "INVALID_PAYLOAD"
    return "COLLECTOR_ERROR"


def capture_asset(
    canonical_asset_id: str,
    symbol: str,
    expected_base: str,
    expected_quote: str,
) -> dict[str, Any]:
    started = utc_now()
    try:
        market = get_market(symbol)
        if market["trading_status"] != "TRADING":
            return {
                "canonical_asset_id": canonical_asset_id,
                "symbol": symbol,
                "collection_status": "SOURCE_MARKET_UNAVAILABLE",
                "started_at_utc": started.isoformat(),
                "completed_at_utc": utc_now().isoformat(),
                "market": market,
                "error": "Market is not TRADING.",
            }
        if market["base_asset"] != expected_base or market["quote_asset"] != expected_quote:
            raise ProbeError(
                f"Quote/base mismatch for {symbol}: "
                f"{market['base_asset']}/{market['quote_asset']}"
            )

        book = get_order_book(symbol, DEPTH_LIMIT)
        turnover = get_turnover_history(symbol, 7)

        bid_notional = executable_notional(book["bids"])
        ask_notional = executable_notional(book["asks"])

        return {
            "canonical_asset_id": canonical_asset_id,
            "venue": VENUE,
            "market_type": "spot",
            "symbol": symbol,
            "base_asset": expected_base,
            "quote_asset": expected_quote,
            "quote_usd_equivalent": True,
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
                "bid_levels_received": book["bid_levels_received"],
                "ask_levels_received": book["ask_levels_received"],
                "best_bid": book["best_bid"],
                "best_ask": book["best_ask"],
                "bid_notional_visible": bid_notional,
                "ask_notional_visible": ask_notional,
                "pcp01_child_notional_usd": CHILD_NOTIONAL_USD,
                "sell_child_notional_covered": bid_notional >= CHILD_NOTIONAL_USD,
                "buy_child_notional_covered": ask_notional >= CHILD_NOTIONAL_USD,
                "bids": book["bids"],
                "asks": book["asks"],
            },
            "turnover": turnover,
        }
    except Exception as error:
        return {
            "canonical_asset_id": canonical_asset_id,
            "venue": VENUE,
            "market_type": "spot",
            "symbol": symbol,
            "base_asset": expected_base,
            "quote_asset": expected_quote,
            "collection_status": classify_error(error),
            "started_at_utc": started.isoformat(),
            "completed_at_utc": utc_now().isoformat(),
            "error_type": type(error).__name__,
            "error": str(error),
        }


def summarize(asset: dict[str, Any]) -> dict[str, Any]:
    row = {
        "canonical_asset_id": asset["canonical_asset_id"],
        "symbol": asset["symbol"],
        "collection_status": asset["collection_status"],
        "completed_at_utc": asset["completed_at_utc"],
    }
    if asset["collection_status"] == "SUCCESS":
        book = asset["order_book"]
        row.update(
            {
                "bid_levels_received": book["bid_levels_received"],
                "ask_levels_received": book["ask_levels_received"],
                "bid_notional_visible": book["bid_notional_visible"],
                "ask_notional_visible": book["ask_notional_visible"],
                "sell_child_notional_covered": book["sell_child_notional_covered"],
                "buy_child_notional_covered": book["buy_child_notional_covered"],
                "turnover_days": asset["turnover"]["days"],
            }
        )
    else:
        row["error"] = asset.get("error")
    return row


def parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def update_status(path: Path, cycle: dict[str, Any]) -> dict[str, Any]:
    if path.exists():
        status = json.loads(path.read_text(encoding="utf-8"))
    else:
        status = {
            "schema_version": STATUS_SCHEMA_VERSION,
            "pilot": "PCP-01",
            "venue": VENUE,
            "two_cycle_status": "PENDING",
            "cycles": [],
        }

    summary = {
        "cycle_id": cycle["cycle_id"],
        "hour_slot_utc": cycle["hour_slot_utc"],
        "started_at_utc": cycle["started_at_utc"],
        "completed_at_utc": cycle["completed_at_utc"],
        "technical_cycle_status": cycle["technical_cycle_status"],
        "success_count": cycle["success_count"],
        "planned_count": cycle["planned_count"],
        "assets": [summarize(x) for x in cycle["assets"]],
    }

    cycles = [
        x for x in status.get("cycles", [])
        if x.get("hour_slot_utc") != summary["hour_slot_utc"]
    ]
    cycles.append(summary)
    cycles.sort(key=lambda x: x["hour_slot_utc"])
    status["cycles"] = cycles[-24:]

    last_two = status["cycles"][-2:]
    qualified = False
    if len(last_two) == 2:
        a, b = last_two
        delta = parse_iso(b["hour_slot_utc"]) - parse_iso(a["hour_slot_utc"])
        qualified = (
            delta.total_seconds() == 3600
            and a["technical_cycle_status"] == "PASS"
            and b["technical_cycle_status"] == "PASS"
        )

    status["two_cycle_status"] = "PASS" if qualified else "PENDING"
    status["updated_at_utc"] = cycle["completed_at_utc"]
    if qualified:
        status["qualified_cycle_ids"] = [x["cycle_id"] for x in last_two]
        status["qualification_note"] = (
            "Two technically successful captures in adjacent UTC hour slots. "
            "This is operational readiness only; no PEC/PR or Capacity E-state "
            "is calculated from dry-run data."
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return status


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cycle-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--status-file", type=Path, required=True)
    args = parser.parse_args()

    started = utc_now()
    source_time = get_source_time()
    assets = [capture_asset(*row) for row in QEV_MAP]
    success_count = sum(x["collection_status"] == "SUCCESS" for x in assets)

    cycle = {
        "schema_version": SCHEMA_VERSION,
        "pilot": "PCP-01",
        "probe_type": "CAPACITY_OPERATIONAL_DRY_RUN",
        "cycle_id": args.cycle_id,
        "venue": VENUE,
        "started_at_utc": started.isoformat(),
        "hour_slot_utc": hour_slot(started),
        "completed_at_utc": utc_now().isoformat(),
        "source_time": source_time,
        "planned_count": len(assets),
        "success_count": success_count,
        "technical_cycle_status": "PASS" if success_count == len(assets) else "FAIL",
        "assets": assets,
        "methodology_note": (
            "Dry-run validates acquisition/schema/provenance only. Visible depth "
            "diagnostics do not determine technical success and no PEC, PR, "
            "Accessibility, Absorption or Capacity state is calculated."
        ),
    }
    write_json(args.output, cycle)
    status = update_status(args.status_file, cycle)

    print(json.dumps({
        "cycle_id": cycle["cycle_id"],
        "hour_slot_utc": cycle["hour_slot_utc"],
        "technical_cycle_status": cycle["technical_cycle_status"],
        "success_count": cycle["success_count"],
        "planned_count": cycle["planned_count"],
        "two_cycle_status": status["two_cycle_status"],
        "assets": [summarize(x) for x in assets],
    }, ensure_ascii=False, indent=2))

    return 0 if cycle["technical_cycle_status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
