#!/usr/bin/env python3
"""Build a provisional Binance-supported market universe for PCP-01.

This script produces a market-derived discovery universe only. It does not
perform semantic asset canonicalization, Flow Vector admission, or ranking.
"""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

BASE_URL = "https://data-api.binance.vision"
ENDPOINT = "/api/v3/exchangeInfo"
SCHEMA_VERSION = "pcp01-smu-binance-0.1"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def fetch_exchange_info() -> tuple[dict[str, Any], str]:
    url = BASE_URL + ENDPOINT
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "Crypto-Pro-DataFeed-PCP01/0.1",
        },
    )
    with urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("symbols"), list):
        raise RuntimeError("Invalid Binance exchangeInfo payload.")
    return payload, url


def build_universe(payload: dict[str, Any], source_url: str) -> dict[str, Any]:
    observed_at = utc_now()
    markets: list[dict[str, Any]] = []
    by_base: dict[str, list[dict[str, str]]] = defaultdict(list)

    for raw in payload["symbols"]:
        if raw.get("status") != "TRADING":
            continue
        if raw.get("isSpotTradingAllowed") is False:
            continue

        symbol = str(raw.get("symbol") or "")
        base = str(raw.get("baseAsset") or "")
        quote = str(raw.get("quoteAsset") or "")
        if not symbol or not base or not quote:
            continue

        market = {
            "native_symbol": symbol,
            "base_asset": base,
            "quote_asset": quote,
            "trading_status": raw.get("status"),
        }
        markets.append(market)
        by_base[base].append(
            {
                "native_symbol": symbol,
                "quote_asset": quote,
            }
        )

    assets: list[dict[str, Any]] = []
    for base in sorted(by_base):
        base_markets = sorted(by_base[base], key=lambda x: (x["quote_asset"], x["native_symbol"]))
        assets.append(
            {
                "provisional_asset_key": f"BINANCE:{base}",
                "base_asset": base,
                "market_count": len(base_markets),
                "quote_assets": sorted({x["quote_asset"] for x in base_markets}),
                "markets": base_markets,
                "canonicalization_status": "PROVISIONAL_SYMBOL_IDENTITY",
            }
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "SUPPORTED_MARKET_UNIVERSE_PROVISIONAL",
        "venue": "Binance",
        "market_type": "spot",
        "observed_at_utc": observed_at,
        "source_endpoint": source_url,
        "active_spot_market_count": len(markets),
        "provisional_base_asset_count": len(assets),
        "identity_warning": (
            "Ticker/baseAsset is not a final canonical identity. Full identity resolution "
            "is required before Current Admission for selected discovery candidates."
        ),
        "assets": assets,
    }


def main() -> int:
    payload, source_url = fetch_exchange_info()
    universe = build_universe(payload, source_url)

    output = Path("data/experimental/pcp-01/universe/binance-supported-market-universe.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(universe, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": "SUCCESS",
        "output": str(output),
        "active_spot_market_count": universe["active_spot_market_count"],
        "provisional_base_asset_count": universe["provisional_base_asset_count"],
        "observed_at_utc": universe["observed_at_utc"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
