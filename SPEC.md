# Crypto Pro Data Feed
## Technical Specification (SPEC)

**Document:** SPEC.md

**Project:** Crypto Pro Suite

**Module:** Crypto Pro Data Feed

**Document Version:** Draft 0.1

**Schema Version:** 0.1

**Status:** Under Review

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
