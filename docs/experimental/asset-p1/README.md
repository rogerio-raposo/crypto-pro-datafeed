# Asset PRO P1 — Historical Data Package

**Project:** Crypto Pro Suite  
**Experiment:** ASSET-P1-D1-001  
**Status:** Draft / Experimental / Non-Normative  
**Branch:** `experiment/asset-p1`

---

## Purpose

Define the producer-side historical data plan for P1/D1 without modifying the frozen ASSET-P0-001 implementation.

## Universe

- BTCUSDT
- ETHUSDT
- SOLUSDT
- XRPUSDT

Market:

- Binance Spot

Native timeframe:

- 1h

Derived analytical timeframes:

- 4h
- 1d

## Design Rule

P1 producer code will live under:

`src/experimental/asset_p1/`

P0 producer code under `src/experimental/asset_p0/` remains immutable evidence for ASSET-P0-001 and must not be repurposed in place.

## Documents

- [P1_DATASET_PLAN.md](P1_DATASET_PLAN.md)
- [P1_SOURCE_ELIGIBILITY_PLAN.md](P1_SOURCE_ELIGIBILITY_PLAN.md)

## Data Area

`data/experimental/asset-p1/`

Large historical datasets remain outside Git. Git stores manifests, source-eligibility evidence, checksums and small audit artifacts.
