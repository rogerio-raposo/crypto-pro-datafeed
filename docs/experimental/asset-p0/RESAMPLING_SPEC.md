# Asset PRO P0 — Resampling Specification

**Project:** Crypto Pro Suite  
**Document:** Resampling Specification  
**Version:** 0.2.0  
**Status:** Draft  
**Owner:** Rogerio Raposo  
**Language:** English  
**Last Updated:** 2026-10-02  
**Documentation Standard:** [DOCUMENTATION_STANDARD.md](../../DOCUMENTATION_STANDARD.md)

---

## 1. Purpose

Define deterministic OHLCV resampling rules for historical datasets used by Asset PRO P0/P1.

## 2. Native and Target Timeframes for ASSET-P0-001

Planned native timeframe:

- 1h.

Required deterministic derived timeframes:

- 4h;
- 1d.

Weekly resampling is outside ASSET-P0-001.

## 3. Aggregation

For source candles ordered inside one target interval:

- Open = first Open;
- High = maximum High;
- Low = minimum Low;
- Close = last Close;
- Volume = sum of Volume.

Optional additive source fields may be aggregated only when their semantics permit it.

All arithmetic on persisted decimal fields shall use exact decimal semantics, not binary floating-point arithmetic.

## 4. Candle Boundary Policy

ASSET-P0-001 uses the policy defined in [CANDLE_BOUNDARY_POLICY.md](CANDLE_BOUNDARY_POLICY.md).

Target boundaries:

- 1h: every UTC clock hour;
- 4h: 00:00, 04:00, 08:00, 12:00, 16:00, 20:00 UTC;
- 1d: 00:00 UTC.

Intervals use half-open semantics:

`[interval_start, interval_end)`.

## 5. Incomplete Inputs

A 4h candle requires exactly four valid contiguous 1h source intervals.

A Daily candle requires exactly twenty-four valid contiguous 1h source intervals.

If any required source interval is absent, the derived candle shall not be presented as complete. The applicable quality condition must remain explicit.

For the formal ASSET-P0-001 validation dataset, any missing native 1h interval is a blocking dataset-integrity failure.

## 6. Determinism

Identical source data, boundary policy, decimal-normalization rules, and resampling specification shall produce byte-equivalent canonical outputs after canonical serialization.

---

# Document History

| Version | Date | Description |
|---|---|---|
| 0.1.0 | 2026-10-02 | Initial deterministic resampling specification for Asset P0. |
| 0.2.0 | 2026-10-02 | Fixed P0 native 1h input, 4h/Daily targets, UTC boundaries and exact completeness requirements. |

---

**End of Document**
