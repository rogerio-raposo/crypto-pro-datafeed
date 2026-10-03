# Asset PRO P1 — Historical Data Package

**Project:** Crypto Pro Suite  
**Experiment:** ASSET-P1-D1-001  
**Status:** Design Freeze Revision 01 / Experimental / Non-Normative  
**Branch:** `experiment/asset-p1`

---

## Purpose

Define and implement the producer-side historical data contract for P1/D1 without modifying frozen ASSET-P0-001 evidence.

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

P1 producer code lives under:

`src/experimental/asset_p1/`

P0 producer code under `src/experimental/asset_p0/` remains immutable evidence for ASSET-P0-001 and is not repurposed in place.

## Documents

- [P1_DATASET_PLAN.md](P1_DATASET_PLAN.md)
- [P1_SOURCE_ELIGIBILITY_PLAN.md](P1_SOURCE_ELIGIBILITY_PLAN.md)
- [P1_GAP_REGISTRY.md](P1_GAP_REGISTRY.md)

## Data Area

`data/experimental/asset-p1/`

Current persisted evidence includes:

- source-eligibility matrix;
- 24 asset×segment Dataset Manifests;
- canonical Dataset Index;
- registered synchronized-gap metadata.

Large historical series remain outside Git.

## Current Producer Status

- source eligibility: PASS;
- continuity diagnostic: completed;
- synchronized venue-gap registry: frozen under Revision 01;
- dataset preparation Revision 01: PASS;
- DEV/VAL/HOLDOUT artifact groups generated separately;
- PCP-01 paths remain isolated from Asset P1 work.

Producer-side implementation is still experimental until the P1 Execution Freeze.
