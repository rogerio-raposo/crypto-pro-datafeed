# Crypto Pro Data Feed
## Technical Specification (SPEC)

**Document:** SPEC.md

**Project:** Crypto Pro Suite

**Module:** Crypto Pro Data Feed

**Document Version:** Draft 0.1

**Schema Version:** 0.1

**Status:** Under Review

**Last Update:** 2026/07/16 - Rogerio Raposo

**Compatibility:** Crypto Pro Suite v1.x

---

# 1. Purpose

This document defines the official technical specification of the Crypto Pro Data Feed.

The Data Feed is responsible exclusively for acquiring, validating, normalizing and publishing market data required by the analytical modules of the Crypto Pro Suite.

The Data Feed performs no market analysis.

Its only responsibility is to provide a reliable, reproducible and auditable market snapshot.

This specification is the contractual definition between the Data Feed and every consumer module.

Any implementation must conform to this document.

---

# 2. Scope

The MVP supports only:

• Exchange: Binance Spot

• Trading pair: BTCUSDT

• Market: Spot

• Timeframes:

- 4 Hours
- 1 Day
- 1 Week

The MVP intentionally does not support:

- additional crypto assets

- perpetual futures

- funding rates

- open interest

- derivatives

- order book

- authenticated Binance endpoints

- user accounts

- API keys

- databases

- streaming

- automatic fallback exchanges

These capabilities belong to future versions.

---

# 3. Design Principles

The Data Feed follows the principles defined in DEVELOPMENT.md.

Additionally, every implementation shall preserve the following characteristics.

## 3.1 Simplicity

The implementation should remain as small as possible.

Complexity shall only be introduced when clearly justified.

---

## 3.2 Reliability

Every published snapshot must be reproducible.

The same input shall always generate the same output.

---

## 3.3 Auditability

Every execution must identify:

- exchange

- symbol

- acquisition time

- data origin

- schema version

- collection status

---

## 3.4 Single Source of Truth

The Data Feed is the only component responsible for market data acquisition.

Analytical modules must never query exchanges directly.

---

## 3.5 Separation of Responsibilities

The Data Feed:

✔ acquires data

✔ validates data

✔ normalizes data

✔ publishes data

The Data Feed never:

✖ calculates indicators

✖ performs technical analysis

✖ generates recommendations

✖ produces reports

Those responsibilities belong to BTC PRO and future analytical modules.

---

# 4. Architecture

The MVP architecture is intentionally minimal.

```
                Binance Spot REST API
                        │
                        ▼
                  datafeed.py
                        │
                        ▼
                 snapshot.json
                 status.json
                        │
                        ▼
               GitHub Repository
                        │
                        ▼
                  BTC PRO Module
```

The Data Feed shall remain independent from every analytical module.

---

# 5. Primary Data Source

Primary exchange:

Binance Spot

Trading Pair:

BTCUSDT

Market:

Spot

Data source:

Official Binance Public REST API

Authentication:

Not required.

Only official public endpoints shall be used.

---

## 5.1 Approved Binance Hosts

The implementation may try one or more official Binance public hosts.

Examples:

- data-api.binance.vision

- api.binance.com

- api1.binance.com

- api2.binance.com

- api3.binance.com

No unofficial mirrors shall be used.

---

# 6. Contingency Policy

The MVP does not implement automatic exchange substitution.

If Binance cannot provide the required data:

- acquisition must stop

- status.json must record the failure

- the latest valid snapshot shall be preserved

- no substitute exchange shall be silently used

Future versions may support the following contingency order:

1. Binance

2. Bybit

3. Bitget

4. OKX

5. MEXC

Every contingency activation shall be explicitly identified in both the snapshot metadata and analytical reports.

---

# 7. Workflow

Every execution shall follow exactly the sequence below.

1. Acquire market data.

2. Validate data.

3. Normalize data.

4. Build snapshot.

5. Build execution status.

6. Validate generated JSON files.

7. Publish updated files.

No step may be skipped.

---

# 8. Output Files

The Data Feed maintains two public operational files.

## snapshot.json

Contains the latest successfully validated market snapshot.

A failed execution shall never overwrite a valid snapshot.

---

## status.json

Records the result of the latest execution.

The BTC PRO module must verify this file before using snapshot.json.

The Data Feed shall never publish partial or invalid market data.

# 9. Snapshot Structure

The Data Feed shall generate a single JSON document named:

```text
snapshot.json
```

The root object shall contain the following mandatory fields.

```json
{
  "schema_version": "0.1",
  "module": "Crypto Pro Data Feed",
  "source_status": "primary",
  "exchange": "Binance Spot",
  "market_type": "spot",
  "symbol": "BTCUSDT",
  "base_asset": "BTC",
  "quote_asset": "USDT",
  "captured_at_utc": "",
  "captured_at_america_recife": "",
  "data_origin": "Binance Public REST API",
  "authentication_required": false,
  "hosts_used": {},
  "ticker_24h": {},
  "timeframes": {},
  "quality_control": {},
  "methodology_note": ""
}
```

No mandatory field may be removed without increasing the schema version.

---

# 10. Timestamp Rules

Every timestamp shall:

- use ISO-8601 format;
- contain timezone information;
- preserve UTC time;
- preserve the snapshot acquisition time in America/Recife.

Example:

```
2026-07-16T14:30:00+00:00
```

Historical candle timestamps shall always be stored in UTC.

---

# 11. Ticker Structure

The object:

```text
ticker_24h
```

shall contain:

```json
{
  "last_price": 0.0,
  "open_price": 0.0,
  "high_price": 0.0,
  "low_price": 0.0,
  "price_change": 0.0,
  "price_change_percent": 0.0,
  "weighted_average_price": 0.0,
  "base_volume": 0.0,
  "quote_volume": 0.0,
  "number_of_trades": 0,
  "period_open_time_utc": "",
  "period_close_time_utc": ""
}
```

Numeric market values shall be stored as JSON numbers.

String representations of numbers are not allowed.

---

# 12. Timeframe Structure

The object:

```text
timeframes
```

shall contain:

```json
{
    "4h": {},
    "1d": {},
    "1w": {}
}
```

Each timeframe object shall contain:

```json
{
  "interval": "",
  "requested_limit": 0,
  "received_candles": 0,
  "closed_candles": 0,
  "first_open_time_utc": "",
  "last_open_time_utc": "",
  "latest_closed_candle": {},
  "candles": []
}
```

The values above represent the required schema.

---

# 13. Candle Structure

Every candle inside the array:

```text
candles
```

shall contain:

```json
{
  "open_time_ms": 0,
  "open_time_utc": "",
  "open": 0.0,
  "high": 0.0,
  "low": 0.0,
  "close": 0.0,
  "base_volume": 0.0,
  "close_time_ms": 0,
  "close_time_utc": "",
  "quote_volume": 0.0,
  "number_of_trades": 0,
  "taker_buy_base_volume": 0.0,
  "taker_buy_quote_volume": 0.0,
  "is_closed": true
}
```

No additional processing shall modify Binance market values.

The Data Feed is responsible only for normalization.

---

# 14. Open and Closed Candles

The Binance API may return the currently open candle.

The Data Feed shall preserve this candle.

The field:

```text
is_closed
```

must identify whether the candle has already closed.

Example:

```json
{
    "is_closed": false
}
```

The latest completed candle shall also be separately identified as:

```text
latest_closed_candle
```

Analytical modules shall normally use completed candles for confirmed indicators.

Open candles may be used only for intraperiod interpretation.

---

# 15. Quality Control

A snapshot shall be considered valid only if:

- ticker is available;

- 4-hour candles are available;

- daily candles are available;

- weekly candles are available;

- every timeframe contains at least one completed candle;

- every mandatory field is present;

- JSON syntax is valid.

The object:

```text
quality_control
```

shall contain:

```json
{
  "ticker_available": true,
  "required_timeframes": [
    "4h",
    "1d",
    "1w"
  ],
  "all_required_timeframes_available": true,
  "contains_incomplete_current_candle": true,
  "analysis_should_prefer_closed_candles": true
}
```

Future versions may include additional validation fields.

---

# 16. Status File

The Data Feed shall update:

```text
status.json
```

on every execution.

Successful execution:

```json
{
  "schema_version": "0.1",
  "module": "Crypto Pro Data Feed",
  "status": "success

# 17. Workflow Requirements

The GitHub Actions workflow shall execute the following sequence.

1. Checkout the repository.

2. Configure Python.

3. Execute datafeed.py.

4. Generate or update status.json.

5. Capture the collector exit code without interrupting the workflow before status.json has been validated and published.

6. Validate snapshot.json.

7. Validate status.json.

8. Perform semantic validation.

9. Commit updated files.

10. Publish the new snapshot.

The workflow shall never publish partial or invalid market data.
The workflow shall finish with a failed status after publishing a valid
failure status.json whenever the collector returns a non-zero exit code.

---

# 18. Semantic Validation

JSON syntax validation alone is insufficient.

The workflow shall verify:

- schema_version exists;

- exchange exists;

- symbol exists;

- ticker_24h exists;

- timeframes exist;

- 4h candles exist;

- 1d candles exist;

- 1w candles exist;

- every timeframe contains completed candles;

- snapshot capture time exists;

- status.json indicates success.

Any failed validation shall interrupt publication.

---

# 19. Snapshot Freshness

Every analytical module shall verify snapshot freshness before using market data.

The verification shall include:

- status == success;

- snapshot_updated == true;

- snapshot timestamp within the accepted freshness window;

- supported schema version.

A preserved snapshot from a previous successful execution shall never be presented as current when the latest collection failed.

The acceptable freshness window will be defined by the workflow execution schedule.

---

# 20. Schema Evolution

The field:

```text
schema_version
```

defines the Data Feed contract.

Rules:

- optional fields may be added during Draft versions;

- mandatory fields shall not be removed;

- incompatible changes require a new schema version;

- analytical modules shall explicitly declare supported schema versions.

Backward compatibility shall always be preferred.

---

# 21. Security

The Data Feed shall never:

- use authenticated Binance endpoints;

- store Binance credentials;

- store API keys;

- store passwords;

- expose GitHub secrets;

- expose user information.

Only public market data may be collected.

GitHub Secrets shall be used whenever authentication becomes necessary in future versions.

---

# 22. Logging

The collector should produce human-readable execution logs.

At minimum:

- execution start;

- selected Binance host;

- collected endpoints;

- generated files;

- execution result.

Logs should facilitate troubleshooting without exposing sensitive information.

---

# 23. Performance

The implementation should minimize:

- execution time;

- memory consumption;

- network requests.

Only the minimum amount of market data required by the specification shall be downloaded.

---

# 24. Acceptance Criteria

The MVP shall be considered complete only when all the following conditions are satisfied.

Functional requirements:

- Binance public API responds successfully.

- BTCUSDT ticker is collected.

- 4-hour candles are collected.

- Daily candles are collected.

- Weekly candles are collected.

- snapshot.json is generated.

- status.json is generated.

Technical requirements:

- JSON validation succeeds.

- Semantic validation succeeds.

- Required fields exist.

- Workflow finishes successfully.

Publication requirements:

- Updated files are committed automatically.

- Files become publicly accessible.

Operational requirements:

- BTC PRO successfully consumes the snapshot.

- Snapshot date and time are reported.

- Exchange and trading pair are identified.

- The latest execution status is verified before analysis.

---

# 25. Known Limitations

Current MVP limitations:

- BTC only.

- Spot market only.

- Binance only.

- No technical indicators.

- No derivatives.

- No funding rate.

- No open interest.

- No order book.

- No streaming.

- No automatic fallback exchange.

- No scheduling policy yet.

These limitations are intentional and may be removed in future versions.

---

# 26. Future Evolution

Future versions may include:

- ETH

- SOL

- XRP

- SUI

- Additional crypto assets

- Funding Rate

- Open Interest

- BTC Dominance

- Stablecoin metrics

- Fear & Greed Index

- Market breadth

- Multi-exchange validation

- Automatic contingency

- Streaming market data

- Historical database

- Additional analytical feeds

The Data Feed shall remain independent from analytical modules.

---

# 27. Compliance

Every implementation of the Crypto Pro Data Feed shall comply with:

- README.md

- DEVELOPMENT.md

- SPEC.md

Any conflict between implementation and specification shall be resolved in favor of the specification.

---

# 28. Development Rule

Before implementing any new capability:

1. Update the specification.

2. Review the specification.

3. Approve the specification.

4. Implement the code.

5. Review the implementation.

6. Execute the workflow.

7. Validate the published output.

The implementation shall never become the primary source of truth.

The specification is the official contract of the module.
