#!/usr/bin/env python3
"""PCP-01 experimental Binance QPS technical probe.

This module is isolated from the stable Crypto Pro Data Feed v1.0.0 contract.
It verifies the market-data capabilities needed before an official PCP-01 run.
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


SCHEMA_VERSION = "pcp01-probe-0.1"
VENUE = "Binance"
MARKET_TYPE = "spot"
DEFAULT_SYMBOL = "BTCUSDT"
DEFAULT_DEPTH_LIMIT = 1000
DEFAULT_CHILD_NOTIONAL_USD = 5_000_000 / 24

BINANCE_BASE_URLS = (
    "https://data-api.binance.vision",
    "https://api.binance.com",
    "https://api1.binance.com",
    "https://api2.binance.com",
    "https://api3.binance.com",
)

REQUEST_TIMEOUT_SECONDS = 20
MAX_RETRIES_PER_HOST = 2


class ProbeError(RuntimeError):
    """Raised when the technical probe cannot acquire or validate required data."""


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_from_ms(timestamp_ms: int) -> str:
    return datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc).isoformat()


def request_json(
    endpoint: str,
    parameters: dict[str, Any] | None = None,
) -> tuple[Any, str, str]:
    parameters = parameters or {}
    query = urlencode(parameters)
    errors: list[str] = []

    for base_url in BINANCE_BASE_URLS:
        url = f"{base_url}{endpoint}"
        if query:
            url = f"{url}?{query}"

        for attempt in range(1, MAX_RETRIES_PER_HOST + 1):
            try:
                request = Request(
                    url,
                    headers={
                        "Accept": "application/json",
                        "User-Agent": "Crypto-Pro-DataFeed-PCP01/0.1",
                    },
                )
                with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
                    if response.status != 200:
                        raise ProbeError(f"Unexpected HTTP status {response.status}")
                    return json.loads(response.read().decode("utf-8")), base_url, url
            except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, ProbeError) as error:
                errors.append(
                    f"{base_url} attempt={attempt} {type(error).__name__}: {error}"
                )
                time.sleep(min(attempt, 2))

    raise ProbeError("All Binance public hosts failed: " + " | ".join(errors[-8:]))


def get_source_time() -> dict[str, Any]:
    observed_at = utc_now()
    payload, host, url = request_json("/api/v3/time")
    if not isinstance(payload, dict) or "serverTime" not in payload:
        raise ProbeError("Invalid /api/v3/time payload.")

    server_time_ms = int(payload["serverTime"])
    return {
        "server_time_ms": server_time_ms,
        "server_time_utc": iso_from_ms(server_time_ms),
        "observed_at_utc": observed_at.isoformat(),
        "host": host,
        "endpoint": url,
    }


def get_market(symbol: str) -> dict[str, Any]:
    observed_at = utc_now()
    payload, host, url = request_json("/api/v3/exchangeInfo", {"symbol": symbol})

    if not isinstance(payload, dict):
        raise ProbeError("Invalid exchangeInfo payload.")

    symbols = payload.get("symbols")
    if not isinstance(symbols, list) or len(symbols) != 1:
        raise ProbeError(f"Expected one symbol record for {symbol}.")

    raw = symbols[0]
    return {
        "source": VENUE,
        "venue": VENUE,
        "market_type": MARKET_TYPE,
        "native_symbol": raw.get("symbol"),
        "base_asset": raw.get("baseAsset"),
        "quote_asset": raw.get("quoteAsset"),
        "trading_status": raw.get("status"),
        "is_spot_trading_allowed": raw.get("isSpotTradingAllowed"),
        "observed_at_utc": observed_at.isoformat(),
        "source_endpoint": url,
        "source_host": host,
    }


def list_spot_markets() -> dict[str, Any]:
    observed_at = utc_now()
    payload, host, url = request_json("/api/v3/exchangeInfo")
    symbols = payload.get("symbols") if isinstance(payload, dict) else None
    if not isinstance(symbols, list):
        raise ProbeError("Invalid exchangeInfo catalog payload.")

    records = []
    for raw in symbols:
        if raw.get("isSpotTradingAllowed") is False:
            continue
        records.append(
            {
                "native_symbol": raw.get("symbol"),
                "base_asset": raw.get("baseAsset"),
                "quote_asset": raw.get("quoteAsset"),
                "trading_status": raw.get("status"),
            }
        )

    return {
        "count": len(records),
        "observed_at_utc": observed_at.isoformat(),
        "source_host": host,
        "source_endpoint": url,
        "sample": records[:10],
    }


def _normalize_levels(raw_levels: Any, side: str) -> list[list[float]]:
    if not isinstance(raw_levels, list):
        raise ProbeError(f"Order-book {side} is not a list.")

    levels: list[list[float]] = []
    for raw in raw_levels:
        if not isinstance(raw, list) or len(raw) < 2:
            raise ProbeError(f"Malformed {side} level.")
        price = float(raw[0])
        quantity = float(raw[1])
        if price <= 0 or quantity < 0:
            raise ProbeError(f"Invalid {side} price/quantity.")
        levels.append([price, quantity])

    return levels


def get_order_book(symbol: str, limit: int) -> dict[str, Any]:
    observed_at = utc_now()
    payload, host, url = request_json(
        "/api/v3/depth",
        {"symbol": symbol, "limit": limit},
    )
    if not isinstance(payload, dict):
        raise ProbeError("Invalid depth payload.")

    bids = _normalize_levels(payload.get("bids"), "bids")
    asks = _normalize_levels(payload.get("asks"), "asks")
    if not bids or not asks:
        raise ProbeError("Depth payload has empty bid or ask side.")

    if bids[0][0] >= asks[0][0]:
        raise ProbeError("Invalid crossed or locked top of book.")

    return {
        "last_update_id": payload.get("lastUpdateId"),
        "observed_at_utc": observed_at.isoformat(),
        "source_host": host,
        "source_endpoint": url,
        "requested_limit": limit,
        "bid_levels_received": len(bids),
        "ask_levels_received": len(asks),
        "best_bid": bids[0][0],
        "best_ask": asks[0][0],
        "bids": bids,
        "asks": asks,
    }


def get_turnover_history(symbol: str, days: int = 7) -> dict[str, Any]:
    observed_at = utc_now()
    captured_ms = int(observed_at.timestamp() * 1000)
    payload, host, url = request_json(
        "/api/v3/klines",
        {"symbol": symbol, "interval": "1d", "limit": days + 2},
    )
    if not isinstance(payload, list):
        raise ProbeError("Invalid kline payload.")

    closed: list[dict[str, Any]] = []
    for raw in payload:
        if not isinstance(raw, list) or len(raw) < 8:
            raise ProbeError("Malformed kline record.")
        close_time_ms = int(raw[6])
        if close_time_ms >= captured_ms:
            continue
        closed.append(
            {
                "open_time_utc": iso_from_ms(int(raw[0])),
                "close_time_utc": iso_from_ms(close_time_ms),
                "base_volume": float(raw[5]),
                "quote_volume": float(raw[7]),
            }
        )

    closed = closed[-days:]
    if len(closed) < days:
        raise ProbeError(f"Only {len(closed)} closed daily candles available; {days} required.")

    return {
        "days": days,
        "records": closed,
        "observed_at_utc": observed_at.isoformat(),
        "source_host": host,
        "source_endpoint": url,
    }


def executable_notional(levels: list[list[float]]) -> float:
    return sum(price * quantity for price, quantity in levels)


def build_probe(
    symbol: str,
    depth_limit: int,
    child_notional_usd: float,
) -> dict[str, Any]:
    started = utc_now()
    source_time = get_source_time()
    market = get_market(symbol)
    catalog = list_spot_markets()
    book = get_order_book(symbol, depth_limit)
    turnover = get_turnover_history(symbol, 7)

    bid_notional = executable_notional(book["bids"])
    ask_notional = executable_notional(book["asks"])
    active = market["trading_status"] == "TRADING"
    spot_allowed = market["is_spot_trading_allowed"] is not False
    buy_depth_ok = ask_notional >= child_notional_usd
    sell_depth_ok = bid_notional >= child_notional_usd

    limitations: list[str] = []
    if not buy_depth_ok:
        limitations.append("ask depth below PCP-01 child notional at requested limit")
    if not sell_depth_ok:
        limitations.append("bid depth below PCP-01 child notional at requested limit")
    if not active:
        limitations.append("market is not TRADING")
    if not spot_allowed:
        limitations.append("spot trading not allowed")

    if active and spot_allowed and buy_depth_ok and sell_depth_ok:
        status = "PASS"
    elif active and spot_allowed:
        status = "PASS_WITH_LIMITATIONS"
    else:
        status = "FAIL"

    return {
        "schema_version": SCHEMA_VERSION,
        "probe_type": "QPS_TECHNICAL_DRY_RUN",
        "venue": VENUE,
        "symbol": symbol,
        "started_at_utc": started.isoformat(),
        "completed_at_utc": utc_now().isoformat(),
        "technical_probe_status": status,
        "limitations": limitations,
        "source_time": source_time,
        "market": market,
        "catalog": {
            "spot_market_count": catalog["count"],
            "observed_at_utc": catalog["observed_at_utc"],
            "source_host": catalog["source_host"],
            "source_endpoint": catalog["source_endpoint"],
        },
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
            "pcp01_child_notional_usd": child_notional_usd,
            "sell_depth_sufficient": sell_depth_ok,
            "buy_depth_sufficient": buy_depth_ok,
        },
        "turnover": turnover,
        "commercial_source_approval": "DEFERRED_NOT_EVALUATED_BY_PROBE",
        "methodology_note": (
            "Technical probe only. PASS does not activate PCP-01 UFT/T0 and "
            "does not constitute commercial source approval."
        ),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default=DEFAULT_SYMBOL)
    parser.add_argument("--depth-limit", type=int, default=DEFAULT_DEPTH_LIMIT)
    parser.add_argument(
        "--child-notional-usd",
        type=float,
        default=DEFAULT_CHILD_NOTIONAL_USD,
    )
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = build_probe(
        symbol=args.symbol.upper(),
        depth_limit=args.depth_limit,
        child_notional_usd=args.child_notional_usd,
    )

    if args.output:
        write_json(args.output, result)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["technical_probe_status"] != "FAIL" else 2


if __name__ == "__main__":
    raise SystemExit(main())
