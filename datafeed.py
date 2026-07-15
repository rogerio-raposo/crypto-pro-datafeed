#!/usr/bin/env python3
"""
Crypto Pro Data Feed — Binance Spot

Collects public BTC/USDT market data from Binance Spot and generates
an auditable snapshot for the BTC PRO analytical module.

No API key or Binance account is required.
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo


PRIMARY_EXCHANGE = "Binance Spot"
SYMBOL = "BTCUSDT"

BINANCE_BASE_URLS = (
    "https://data-api.binance.vision",
    "https://api.binance.com",
    "https://api1.binance.com",
    "https://api2.binance.com",
    "https://api3.binance.com",
)

INTERVALS = {
    "4h": 500,
    "1d": 500,
    "1w": 260,
}

REQUEST_TIMEOUT_SECONDS = 20
MAX_RETRIES_PER_HOST = 3

PROJECT_DIR = Path(__file__).resolve().parent
SNAPSHOT_PATH = PROJECT_DIR / "snapshot.json"
FAILURE_PATH = PROJECT_DIR / "failure.json"


class DataFeedError(RuntimeError):
    """Raised when required market data cannot be obtained."""


def utc_datetime_from_milliseconds(timestamp_ms: int) -> str:
    """Convert a Unix timestamp in milliseconds to an ISO 8601 UTC string."""
    return datetime.fromtimestamp(
        timestamp_ms / 1000,
        tz=timezone.utc,
    ).isoformat()


def request_json(
    endpoint: str,
    parameters: dict[str, Any] | None = None,
) -> tuple[Any, str]:
    """
    Request JSON from Binance public endpoints.

    Returns:
        A tuple containing the decoded response and the Binance host used.

    Raises:
        DataFeedError: If all official Binance hosts fail.
    """
    parameters = parameters or {}
    query_string = urlencode(parameters)
    errors: list[str] = []

    for base_url in BINANCE_BASE_URLS:
        url = f"{base_url}{endpoint}"

        if query_string:
            url = f"{url}?{query_string}"

        for attempt in range(1, MAX_RETRIES_PER_HOST + 1):
            try:
                request = Request(
                    url,
                    headers={
                        "Accept": "application/json",
                        "User-Agent": "Crypto-Pro-DataFeed/0.1",
                    },
                )

                with urlopen(
                    request,
                    timeout=REQUEST_TIMEOUT_SECONDS,
                ) as response:
                    if response.status != 200:
                        raise DataFeedError(
                            f"Unexpected HTTP status: {response.status}"
                        )

                    payload = response.read().decode("utf-8")
                    return json.loads(payload), base_url

            except (
                HTTPError,
                URLError,
                TimeoutError,
                json.JSONDecodeError,
                DataFeedError,
            ) as error:
                errors.append(
                    f"{base_url} | attempt {attempt} | "
                    f"{type(error).__name__}: {error}"
                )
                time.sleep(min(attempt * 2, 5))

    error_summary = "\n".join(errors[-12:])

    raise DataFeedError(
        "All official Binance public endpoints failed.\n"
        f"{error_summary}"
    )


def parse_ticker(raw_ticker: dict[str, Any]) -> dict[str, Any]:
    """Normalize the Binance 24-hour ticker response."""
    return {
        "last_price": float(raw_ticker["lastPrice"]),
        "open_price": float(raw_ticker["openPrice"]),
        "high_price": float(raw_ticker["highPrice"]),
        "low_price": float(raw_ticker["lowPrice"]),
        "price_change": float(raw_ticker["priceChange"]),
        "price_change_percent": float(
            raw_ticker["priceChangePercent"]
        ),
        "weighted_average_price": float(
            raw_ticker["weightedAvgPrice"]
        ),
        "base_volume": float(raw_ticker["volume"]),
        "quote_volume": float(raw_ticker["quoteVolume"]),
        "number_of_trades": int(raw_ticker["count"]),
        "period_open_time_utc": utc_datetime_from_milliseconds(
            int(raw_ticker["openTime"])
        ),
        "period_close_time_utc": utc_datetime_from_milliseconds(
            int(raw_ticker["closeTime"])
        ),
    }


def parse_kline(raw_kline: list[Any], captured_at_ms: int) -> dict[str, Any]:
    """Normalize one Binance candlestick record."""
    close_time_ms = int(raw_kline[6])

    return {
        "open_time_ms": int(raw_kline[0]),
        "open_time_utc": utc_datetime_from_milliseconds(
            int(raw_kline[0])
        ),
        "open": float(raw_kline[1]),
        "high": float(raw_kline[2]),
        "low": float(raw_kline[3]),
        "close": float(raw_kline[4]),
        "base_volume": float(raw_kline[5]),
        "close_time_ms": close_time_ms,
        "close_time_utc": utc_datetime_from_milliseconds(
            close_time_ms
        ),
        "quote_volume": float(raw_kline[7]),
        "number_of_trades": int(raw_kline[8]),
        "taker_buy_base_volume": float(raw_kline[9]),
        "taker_buy_quote_volume": float(raw_kline[10]),
        "is_closed": close_time_ms < captured_at_ms,
    }


def collect_klines(
    interval: str,
    limit: int,
    captured_at_ms: int,
) -> tuple[dict[str, Any], str]:
    """Collect and normalize a Binance candlestick series."""
    raw_klines, host = request_json(
        "/api/v3/klines",
        {
            "symbol": SYMBOL,
            "interval": interval,
            "limit": limit,
        },
    )

    if not isinstance(raw_klines, list) or not raw_klines:
        raise DataFeedError(
            f"Binance returned no candles for interval {interval}."
        )

    candles = [
        parse_kline(raw_kline, captured_at_ms)
        for raw_kline in raw_klines
    ]

    closed_candles = [
        candle for candle in candles if candle["is_closed"]
    ]

    if not closed_candles:
        raise DataFeedError(
            f"No completed candles were returned for interval {interval}."
        )

    return (
        {
            "interval": interval,
            "requested_limit": limit,
            "received_candles": len(candles),
            "closed_candles": len(closed_candles),
            "first_open_time_utc": candles[0]["open_time_utc"],
            "last_open_time_utc": candles[-1]["open_time_utc"],
            "latest_closed_candle": closed_candles[-1],
            "candles": candles,
        },
        host,
    )


def remove_file_if_exists(path: Path) -> None:
    """Remove an obsolete output file if it exists."""
    if path.exists():
        path.unlink()


def write_json(path: Path, data: dict[str, Any]) -> None:
    """Write formatted UTF-8 JSON to disk."""
    path.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def create_snapshot() -> dict[str, Any]:
    """Collect all required Binance data and build the snapshot."""
    captured_at_utc = datetime.now(timezone.utc)
    captured_at_recife = captured_at_utc.astimezone(
        ZoneInfo("America/Recife")
    )
    captured_at_ms = int(captured_at_utc.timestamp() * 1000)

    raw_ticker, ticker_host = request_json(
        "/api/v3/ticker/24hr",
        {"symbol": SYMBOL},
    )

    market_intervals: dict[str, Any] = {}
    hosts_used: dict[str, str] = {
        "ticker_24h": ticker_host,
    }

    for interval, limit in INTERVALS.items():
        interval_data, host = collect_klines(
            interval,
            limit,
            captured_at_ms,
        )
        market_intervals[interval] = interval_data
        hosts_used[f"candles_{interval}"] = host

    return {
        "schema_version": "0.1",
        "module": "Crypto Pro Data Feed",
        "source_status": "primary",
        "exchange": PRIMARY_EXCHANGE,
        "market_type": "spot",
        "symbol": SYMBOL,
        "base_asset": "BTC",
        "quote_asset": "USDT",
        "captured_at_utc": captured_at_utc.isoformat(),
        "captured_at_america_recife": (
            captured_at_recife.isoformat()
        ),
        "data_origin": "Binance public REST API",
        "authentication_required": False,
        "hosts_used": hosts_used,
        "ticker_24h": parse_ticker(raw_ticker),
        "timeframes": market_intervals,
        "contingency": {
            "activated": False,
            "substitute_exchange": None,
            "reason": None,
        },
        "quality_control": {
            "ticker_available": True,
            "required_timeframes": list(INTERVALS.keys()),
            "all_required_timeframes_available": True,
            "contains_incomplete_current_candle": True,
            "analysis_should_prefer_closed_candles": True,
        },
        "methodology_note": (
            "Data were obtained directly from official Binance "
            "public endpoints. No substitute exchange was used. "
            "Analytical calculations should normally use completed "
            "candles and treat the current open candle separately."
        ),
    }


def record_failure(error: Exception) -> None:
    """Create an auditable failure record."""
    failed_at_utc = datetime.now(timezone.utc)
    failed_at_recife = failed_at_utc.astimezone(
        ZoneInfo("America/Recife")
    )

    failure_record = {
        "schema_version": "0.1",
        "module": "Crypto Pro Data Feed",
        "source_status": "failure",
        "exchange_attempted": PRIMARY_EXCHANGE,
        "symbol": SYMBOL,
        "failed_at_utc": failed_at_utc.isoformat(),
        "failed_at_america_recife": (
            failed_at_recife.isoformat()
        ),
        "reason": str(error),
        "contingency": {
            "activated": False,
            "substitute_exchange": None,
            "reason": (
                "The MVP does not yet implement an automatic "
                "substitute exchange."
            ),
        },
    }

    write_json(FAILURE_PATH, failure_record)


def main() -> int:
    """Run the data feed and create snapshot.json."""
    try:
        snapshot = create_snapshot()
        write_json(SNAPSHOT_PATH, snapshot)
        remove_file_if_exists(FAILURE_PATH)

        ticker = snapshot["ticker_24h"]

        print("Crypto Pro Data Feed completed successfully.")
        print(f"Exchange: {snapshot['exchange']}")
        print(f"Symbol: {snapshot['symbol']}")
        print(f"Last price: {ticker['last_price']}")
        print(f"Snapshot: {SNAPSHOT_PATH}")

        return 0

    except Exception as error:
        record_failure(error)
        remove_file_if_exists(SNAPSHOT_PATH)

        print(
            f"Data feed failed: {error}",
            file=sys.stderr,
        )
        print(
            f"Failure record: {FAILURE_PATH}",
            file=sys.stderr,
        )

        return 1


if __name__ == "__main__":
    raise SystemExit(main())
