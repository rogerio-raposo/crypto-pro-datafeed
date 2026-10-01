# Crypto Pro Data Feed — PCP-01 Ranking Capture Extension

**Project:** Crypto Pro Data Feed  
**Document:** Experimental Capture Extension for Ranking PCP-01  
**Status:** Experimental / Pre-implementation  
**Date:** 2026-09-30  
**Scope:** internal methodological pilot only  
**Stable baseline affected:** none

---

# 1. Purpose

This document specifies the minimum experimental extension required for the Crypto Pro Data Feed to supply the Ranking Institucional Simplificado PCP-01.

It does **not** modify the stable v1.0.0 public contract and does not authorize commercial use of any exchange data.

# 2. Architectural Rule

The Ranking defines required data semantics. The Data Feed remains the sole producer responsible for acquisition, normalization, validation, provenance, and publication.

No permanent exchange collector should be implemented inside the Ranking module.

# 3. Existing Baseline

The stable implementation currently:
- uses Binance Spot;
- targets BTCUSDT;
- publishes `data/snapshot.json` and `data/status.json`;
- collects ticker and candlesticks;
- does not yet provide multi-asset catalogs, multi-exchange normalization, order-book snapshots, QEV mapping, or PCP-01 capture manifests.

The PCP-01 extension must therefore remain isolated from the stable contract until validated.

# 4. Experimental Architecture

```text
Exchange Adapters
     │
     ├─ instrument catalog
     ├─ market status
     ├─ order book
     └─ turnover/history
     ↓
Normalization Layer
     ↓
Canonical Pilot Schema
     ↓
Validation / Provenance
     ↓
PCP-01 Experimental Artifacts
     ↓
Ranking PCP-01
```

# 5. Source Adapter Interface

Each adapter should expose a common internal interface equivalent to:

- `list_spot_markets()`
- `get_market_status(symbol)`
- `get_order_book(symbol, required_depth)`
- `get_turnover_history(symbol, start, end)`
- `get_source_time()` when available
- `get_network_availability(asset)` only when supported and required

Adapters must preserve raw source identifiers and native timestamps.

# 6. Candidate Adapters

Initial candidates:
- Binance;
- Bybit;
- OKX;
- Bitget;
- MEXC.

Implementation order must follow QPS approval. A technically documented exchange must not be enabled for an official pilot run while source-use rights remain unresolved.

# 7. Canonical Market Record

Minimum fields:

```text
source
venue
market_type
native_symbol
base_asset
quote_asset
trading_status
source_timestamp
observed_at_utc
raw_provenance
schema_version
```

# 8. Canonical Order Book Snapshot

Minimum fields:

```text
run_id
capture_event_id
canonical_asset_id
venue
native_symbol
base_asset
quote_asset
source_timestamp
observed_at_utc
bids: [[price, quantity], ...]
asks: [[price, quantity], ...]
best_bid
best_ask
depth_levels_received
depth_limit_flag
collection_status
source_endpoint
source_response_metadata
schema_version
```

The adapter must not fabricate missing depth.

# 9. Turnover Record

Minimum fields:

```text
canonical_asset_id
venue
native_symbol
interval_start
interval_end
base_volume
quote_volume
quote_asset
usd_equivalent_turnover
normalization_method
source_timestamp
observed_at_utc
collection_status
provenance
```

# 10. Capture Schedule

For each qualified Asset × Venue × Market:

- 24 official hourly capture events;
- UTC scheduling;
- target cross-venue alignment <= 60 seconds;
- maximum alignment for consolidated multi-venue snapshot = 180 seconds;
- retry attempts logged;
- API/source failures separated from collector failures.

Dry-run data must never be mixed into official PCP-01 capture data.

# 11. RAS Support

The producer only supplies market data. It should not assign Absorption states.

For PCP-01:
- RAS = USD 5,000,000 / 24h;
- 24 equal child orders ≈ USD 208,333 each.

The Ranking/validation layer computes PEC and PR from validated published data.

# 12. Failure Semantics

Required categories:

- `SUCCESS`
- `SOURCE_MARKET_UNAVAILABLE`
- `SOURCE_API_ERROR`
- `RATE_LIMITED`
- `TIMEOUT`
- `INVALID_PAYLOAD`
- `INSUFFICIENT_DEPTH_RETURNED`
- `COLLECTOR_ERROR`

Source transport failure must not be converted into market illiquidity.

# 13. Experimental Publication

Do not overwrite the stable `data/snapshot.json` contract.

Recommended isolated namespace:

```text
data/experimental/pcp-01/
├── status.json
├── universe/
├── capture/
└── turnover/
```

Exact filenames may be defined during implementation.

# 14. Validation

Before UFT/T0 activation, require:
- schema validation;
- timestamp validation;
- bid/ask ordering validation;
- positive price/quantity validation;
- duplicate-level handling;
- quote/base consistency;
- capture-event completeness;
- provenance presence;
- retry/error logging;
- two consecutive hourly dry-run cycles.

# 15. Source Governance

Technical API availability is not sufficient for production use.

Every adapter must carry source-governance metadata:
- documentation reference;
- terms reference;
- pilot-use approval status;
- commercial-use approval status;
- approval date;
- restrictions/notes.

Commercial source approval is external to the technical adapter and must be explicit.

# 16. Non-goals

This extension does not:
- rank assets;
- calculate E-states;
- calculate Confidence;
- infer Flow Vectors;
- calculate PEC/PR as methodology outputs;
- produce trading signals;
- replace the stable Data Feed contract;
- establish commercial data rights.

# 17. Implementation Sequence

1. finalize QPS/use-rights gate;
2. define experimental schemas;
3. implement one adapter first;
4. validate normalization;
5. add remaining approved adapters incrementally;
6. implement capture scheduler;
7. run two-cycle dry-run;
8. publish technical readiness result;
9. only then permit PCP-01 UFT/T0.

# 18. Stop Rule

Do not implement an exchange adapter for the official pilot path if:
- its required endpoints cannot meet the pilot data contract;
- the terms/use-rights status is incompatible or unresolved for the intended pilot use;
- repeated dry-runs show unacceptable reliability;
- required provenance cannot be preserved.

---

**Status:** specification only; no source adapter implementation is authorized by this document.
