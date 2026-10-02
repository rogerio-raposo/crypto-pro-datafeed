# Asset PRO P0 — Dataset Plan

**Project:** Crypto Pro Suite  
**Document:** ASSET-P0-001 Dataset Plan  
**Version:** 0.2.0  
**Status:** Draft  
**Owner:** Rogerio Raposo  
**Language:** English  
**Last Updated:** 2026-10-02  
**Documentation Standard:** [DOCUMENTATION_STANDARD.md](../../DOCUMENTATION_STANDARD.md)

---

## 1. Planned Validation Dataset

- Experiment: `ASSET-P0-001`
- Provider: Binance Public Data
- Venue: Binance Spot
- Instrument: BTCUSDT
- Market type: Spot
- Data type: klines
- Native timeframe: 1h
- Start: 2025-01-01 00:00:00 UTC inclusive
- End: 2025-04-01 00:00:00 UTC exclusive
- Expected complete native records: 2160
- Required derived timeframes: 4h and 1d
- Timezone policy: UTC
- Timestamp canonical unit: epoch microseconds
- Planned checksum: SHA-256 over canonical JSONL

## 2. Planned Archive Acquisition

Main dataset uses official Binance Public Data monthly Spot kline archives:

- January 2025;
- February 2025;
- March 2025.

For each archive:

1. acquire ZIP;
2. acquire corresponding official `.CHECKSUM`;
3. verify ZIP SHA-256 before extraction;
4. parse source records using the explicit source timestamp unit;
5. normalize to canonical epoch microseconds;
6. validate record continuity and OHLC invariants;
7. canonicalize decimal strings;
8. serialize deterministic JSONL;
9. compute final normalized dataset SHA-256.

## 3. Main Dataset Acceptance

The formal real validation dataset SHALL contain:

- exactly 2160 native 1h intervals;
- no unresolved duplicate interval;
- no missing native interval;
- monotonic interval starts;
- exact UTC 1h alignment;
- valid OHLC invariants;
- complete archive-checksum provenance;
- canonical normalized dataset checksum.

Any missing native 1h interval is blocking for ASSET-P0-001. Gap-handling behavior is tested separately in the synthetic fixture.

## 4. Derived Expectations

If the native dataset is complete:

- expected 4h candles: 540;
- expected Daily candles: 90.

Each 4h candle requires four contiguous native 1h candles.

Each Daily candle requires twenty-four contiguous native 1h candles.

## 5. Real Golden Fixture

Use official daily Spot 1h archive objects for:

- 2024-12-31;
- 2025-01-01;
- 2025-01-02.

Expected complete native slots: 72.

Purpose:

- exercise actual archive acquisition;
- validate official archive checksum handling;
- validate 4h and Daily UTC boundaries;
- test explicit normalization across the source timestamp-unit transition at 2025-01-01.

## 6. Synthetic Golden Fixture

The synthetic fixture uses 48 expected hourly slots over two UTC days and intentionally includes:

- one missing native interval;
- one extreme but OHLC-valid observation;
- deterministic expected validation flags;
- deterministic expected resampling status;
- a checkpoint/restart point.

Synthetic values SHALL be hand-authored and reviewed before fixture hashes are frozen.

## 7. Status

The design inputs are specified, but no archive has been acquired and no canonical Dataset Manifest has been generated.

---

# Document History

| Version | Date | Description |
|---|---|---|
| 0.1.0 | 2026-10-02 | Initial concrete dataset plan for ASSET-P0-001. |
| 0.2.0 | 2026-10-02 | Added official checksum workflow, concrete archive objects, real fixture acquisition plan and full normalization steps. |

---

**End of Document**
