#!/usr/bin/env python3
"""
Crypto Pro Data Feed — Binance Spot

Collects public BTC/USDT market data from Binance Spot and generates:

- snapshot.json: latest successfully validated market snapshot;
- status.json: result of the latest collection attempt.

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


SCHEMA_VERSION = "0.1"
MODULE_NAME = "Crypto Pro Data Feed"

PRIMARY_EXCHANGE = "Binance Spot"
MARKET_TYPE = "spot"

SYMBOL = "BTCUSDT"
BASE_ASSET = "BTC"
QUOTE_ASSET = "USDT"

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

PROJECT_DIRECTORY = Path(__file__).resolve().parent
SNAPSHOT_PATH = PROJECT_DIRECTORY / "snapshot.json"
STATUS_PATH = PROJECT_DIRECTORY / "status.json"


class DataFeedError(RuntimeError):
    """Raised when required market data cannot be acquired or validated."""


def current_times() -> tuple[datetime, datetime]:
    """Return the current time in UTC and America/Recife."""
    utc_time = datetime.now(timezone.utc)
    recife_time = utc_time.astimezone(ZoneInfo("America/Recife"))
    return utc_time, recife_time


def utc_datetime_from_milliseconds(timestamp_ms: int) -> str:
    """Convert a Unix timestamp in milliseconds to ISO 8601 UTC."""
    return datetime.fromtimestamp(
        timestamp_ms / 1000,
        tz=timezone.utc,
    ).isoformat()


def write_json_atomically(path: Path, data: dict[str, Any]) -> None:
    """
    Write formatted JSON using a temporary file.

    The final file is replaced only after the complete JSON document
    has been written successfully.
    """
    temporary_path = path.with_suffix(f"{path.suffix}.tmp")

    temporary_path.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    temporary_path.replace(path)


def request_json(
    endpoint: str,
    parameters: dict[str, Any] | None = None,
) -> tuple[Any, str]:
    """
    Request JSON from official Binance public hosts.

    Returns:
        Tuple containing the decoded response and the host used.

    Raises:
        DataFeedError: When every approved Binance host fails.
    """
    parameters = parameters or {}
    query_string = urlencode(parameters)
    collected_errors: list[str] = []

    for base_url in BINANCE_BASE_URLS:
        request_url = f"{base_url}{endpoint}"

        if query_string:
            request_url = f"{request_url}?{query_string}"

        for attempt in range(1, MAX_RETRIES_PER_HOST + 1):
            try:
                request = Request(
                    request_url,
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
                            f"Unexpected HTTP status {response.status}"
                        )

                    payload = response.read().decode("utf-8")
                    decoded_response = json.loads(payload)

                    print(
                        f"Collected {endpoint} from {base_url}",
                        flush=True,
                    )

                    return decoded_response, base_url

            except (
                HTTPError,
                URLError,
                TimeoutError,
                json.JSONDecodeError,
                DataFeedError,
            ) as error:
                error_message = (
                    f"{base_url} | attempt {attempt} | "
                    f"{type(error).__name__}: {error}"
                )
                collected_errors.append(error_message)

                print(
                    f"Request failed: {error_message}",
                    file=sys.stderr,
                    flush=True,
                )

                time.sleep(min(attempt * 2, 5))

    error_summary = "\n".join(collected_errors[-12:])

    raise DataFeedError(
        "All approved Binance public hosts failed.\n"
        f"{error_summary}"
    )


def parse_ticker(raw_ticker: dict[str, Any]) -> dict[str, Any]:
    """Normalize the Binance 24-hour ticker response."""
    required_fields = (
        "lastPrice",
        "openPrice",
        "highPrice",
        "lowPrice",
        "priceChange",
        "priceChangePercent",
        "weightedAvgPrice",
        "volume",
        "quoteVolume",
        "count",
        "openTime",
        "closeTime",
    )

    missing_fields = [
        field for field in required_fields if field not in raw_ticker
    ]

    if missing_fields:
        raise DataFeedError(
            "Ticker response is missing fields: "
            + ", ".join(missing_fields)
        )

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


def parse_candle(
    raw_candle: list[Any],
    captured_at_ms: int,
) -> dict[str, Any]:
    """Normalize one Binance candlestick record."""
    if len(raw_candle) < 11:
        raise DataFeedError(
            "Binance returned an incomplete candlestick record."
        )

    open_time_ms = int(raw_candle[0])
    close_time_ms = int(raw_candle[6])

    return {
        "open_time_ms": open_time_ms,
        "open_time_utc": utc_datetime_from_milliseconds(
            open_time_ms
        ),
        "open": float(raw_candle[1]),
        "high": float(raw_candle[2]),
        "low": float(raw_candle[3]),
        "close": float(raw_candle[4]),
        "base_volume": float(raw_candle[5]),
        "close_time_ms": close_time_ms,
        "close_time_utc": utc_datetime_from_milliseconds(
            close_time_ms
        ),
        "quote_volume": float(raw_candle[7]),
        "number_of_trades": int(raw_candle[8]),
        "taker_buy_base_volume": float(raw_candle[9]),
        "taker_buy_quote_volume": float(raw_candle[10]),
        "is_closed": close_time_ms < captured_at_ms,
    }


def collect_timeframe(
    interval: str,
    requested_limit: int,
    captured_at_ms: int,
) -> tuple[dict[str, Any], str]:
    """Collect, normalize and validate one candlestick timeframe."""
    raw_candles, host = request_json(
        "/api/v3/klines",
        {
            "symbol": SYMBOL,
            "interval": interval,
            "limit": requested_limit,
        },
    )

    if not isinstance(raw_candles, list):
        raise DataFeedError(
            f"Unexpected candle response for interval {interval}."
        )

    if len(raw_candles) < requested_limit:
        raise DataFeedError(
            f"Interval {interval} returned {len(raw_candles)} candles; "
            f"{requested_limit} were required."
        )

    candles = [
        parse_candle(raw_candle, captured_at_ms)
        for raw_candle in raw_candles
    ]

    closed_candles = [
        candle for candle in candles if candle["is_closed"]
    ]

    if not closed_candles:
        raise DataFeedError(
            f"Interval {interval} contains no completed candles."
        )

    return (
        {
            "interval": interval,
            "requested_limit": requested_limit,
            "received_candles": len(candles),
            "closed_candles": len(closed_candles),
            "first_open_time_utc": candles[0][
                "open_time_utc"
            ],
            "last_open_time_utc": candles[-1][
                "open_time_utc"
            ],
            "latest_closed_candle": closed_candles[-1],
            "candles": candles,
        },
        host,
    )


def validate_snapshot(snapshot: dict[str, Any]) -> None:
    """Perform semantic validation of the complete snapshot."""
    mandatory_root_fields = (
        "schema_version",
        "module",
        "source_status",
        "exchange",
        "market_type",
        "symbol",
        "base_asset",
        "quote_asset",
        "captured_at_utc",
        "captured_at_america_recife",
        "data_origin",
        "authentication_required",
        "hosts_used",
        "ticker_24h",
        "timeframes",
        "quality_control",
        "methodology_note",
    )

    missing_root_fields = [
        field
        for field in mandatory_root_fields
        if field not in snapshot
    ]

    if missing_root_fields:
        raise DataFeedError(
            "Snapshot is missing mandatory fields: "
            + ", ".join(missing_root_fields)
        )

    if snapshot["schema_version"] != SCHEMA_VERSION:
        raise DataFeedError("Unexpected snapshot schema version.")

    if snapshot["source_status"] != "primary":
        raise DataFeedError("Unexpected snapshot source status.")

    if snapshot["exchange"] != PRIMARY_EXCHANGE:
        raise DataFeedError("Unexpected snapshot exchange.")

    if snapshot["symbol"] != SYMBOL:
        raise DataFeedError("Unexpected snapshot symbol.")

    ticker = snapshot["ticker_24h"]

    if not isinstance(ticker, dict) or not ticker:
        raise DataFeedError("Ticker data are missing.")

    timeframes = snapshot["timeframes"]

    for interval, minimum_candles in INTERVALS.items():
        if interval not in timeframes:
            raise DataFeedError(
                f"Required timeframe {interval} is missing."
            )

        timeframe_data = timeframes[interval]

        if timeframe_data["received_candles"] < minimum_candles:
            raise DataFeedError(
                f"Timeframe {interval} contains too few candles."
            )

        if timeframe_data["closed_candles"] < 1:
            raise DataFeedError(
                f"Timeframe {interval} has no completed candles."
            )

        if not timeframe_data["latest_closed_candle"]:
            raise DataFeedError(
                f"Timeframe {interval} has no latest closed candle."
            )

    quality_control = snapshot["quality_control"]

    if quality_control["ticker_available"] is not True:
        raise DataFeedError("Ticker quality control failed.")

    if (
        quality_control[
            "all_required_timeframes_available"
        ]
        is not True
    ):
        raise DataFeedError(
            "Required timeframe quality control failed."
        )


def build_success_status(
    attempt_at_utc: datetime,
    attempt_at_recife: datetime,
) -> dict[str, Any]:
    """Build status.json for a successful collection."""
    return {
        "schema_version": SCHEMA_VERSION,
        "module": MODULE_NAME,
        "status": "success",
        "last_attempt_at_utc": attempt_at_utc.isoformat(),
        "last_attempt_at_america_recife": (
            attempt_at_recife.isoformat()
        ),
        "snapshot_updated": True,
        "exchange": PRIMARY_EXCHANGE,
        "symbol": SYMBOL,
        "reason": None,
    }


def build_failure_status(
    error: Exception,
    attempt_at_utc: datetime,
    attempt_at_recife: datetime,
) -> dict[str, Any]:
    """Build status.json for a failed collection."""
    return {
        "schema_version": SCHEMA_VERSION,
        "module": MODULE_NAME,
        "status": "failure",
        "last_attempt_at_utc": attempt_at_utc.isoformat(),
        "last_attempt_at_america_recife": (
            attempt_at_recife.isoformat()
        ),
        "snapshot_updated": False,
        "exchange": PRIMARY_EXCHANGE,
        "symbol": SYMBOL,
        "reason": str(error),
    }


def create_snapshot(
    captured_at_utc: datetime,
    captured_at_recife: datetime,
) -> dict[str, Any]:
    """Acquire all required data and build the market snapshot."""
    captured_at_ms = int(captured_at_utc.timestamp() * 1000)

    print("Starting Crypto Pro Data Feed.", flush=True)
    print(f"Exchange: {PRIMARY_EXCHANGE}", flush=True)
    print(f"Symbol: {SYMBOL}", flush=True)

    raw_ticker, ticker_host = request_json(
        "/api/v3/ticker/24hr",
        {"symbol": SYMBOL},
    )

    timeframe_data: dict[str, Any] = {}
    hosts_used: dict[str, str] = {
        "ticker_24h": ticker_host,
    }

    for interval, requested_limit in INTERVALS.items():
        collected_data, host = collect_timeframe(
            interval,
            requested_limit,
            captured_at_ms,
        )

        timeframe_data[interval] = collected_data
        hosts_used[f"candles_{interval}"] = host

    contains_incomplete_candle = any(
        any(
            not candle["is_closed"]
            for candle in timeframe["candles"]
        )
        for timeframe in timeframe_data.values()
    )

    snapshot = {
        "schema_version": SCHEMA_VERSION,
        "module": MODULE_NAME,
        "source_status": "primary",
        "exchange": PRIMARY_EXCHANGE,
        "market_type": MARKET_TYPE,
        "symbol": SYMBOL,
        "base_asset": BASE_ASSET,
        "quote_asset": QUOTE_ASSET,
        "captured_at_utc": captured_at_utc.isoformat(),
        "captured_at_america_recife": (
            captured_at_recife.isoformat()
        ),
        "data_origin": "Binance Public REST API",
        "authentication_required": False,
        "hosts_used": hosts_used,
        "ticker_24h": parse_ticker(raw_ticker),
        "timeframes": timeframe_data,
        "quality_control": {
            "ticker_available": True,
            "required_timeframes": list(INTERVALS.keys()),
            "all_required_timeframes_available": True,
            "contains_incomplete_current_candle": (
                contains_incomplete_candle
            ),
            "analysis_should_prefer_closed_candles": True,
        },
        "methodology_note": (
            "Data were obtained directly from approved Binance "
            "public endpoints. No substitute exchange was used. "
            "Analytical modules should normally use completed "
            "candles and treat the current open candle separately."
        ),
    }

    validate_snapshot(snapshot)

    return snapshot


def main() -> int:
    """
    Execute the Data Feed.

    A valid snapshot is replaced only after successful acquisition and
    validation. On failure, the previous valid snapshot is preserved.
    """
    attempt_at_utc, attempt_at_recife = current_times()

    try:
        snapshot = create_snapshot(
            attempt_at_utc,
            attempt_at_recife,
        )

        success_status = build_success_status(
            attempt_at_utc,
            attempt_at_recife,
        )

        write_json_atomically(SNAPSHOT_PATH, snapshot)
        write_json_atomically(STATUS_PATH, success_status)

        print("Data Feed completed successfully.", flush=True)
        print(f"Snapshot written to: {SNAPSHOT_PATH}", flush=True)
        print(f"Status written to: {STATUS_PATH}", flush=True)
        print(
            f"Last price: "
            f"{snapshot['ticker_24h']['last_price']}",
            flush=True,
        )

        return 0

    except Exception as error:
        failure_status = build_failure_status(
            error,
            attempt_at_utc,
            attempt_at_recife,
        )

        write_json_atomically(STATUS_PATH, failure_status)

        print(
            f"Data Feed failed: {error}",
            file=sys.stderr,
            flush=True,
        )
        print(
            "The latest valid snapshot was preserved.",
            file=sys.stderr,
            flush=True,
        )
        print(
            f"Failure status written to: {STATUS_PATH}",
            file=sys.stderr,
            flush=True,
        )

        return 1


if __name__ == "__main__":
    raise SystemExit(main())
