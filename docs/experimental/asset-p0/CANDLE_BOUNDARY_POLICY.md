# Asset PRO P0 — Candle Boundary Policy

**Project:** Crypto Pro Suite  
**Document:** Candle Boundary Policy  
**Version:** 0.1.0  
**Status:** Draft  
**Owner:** Rogerio Raposo  
**Language:** English  
**Last Updated:** 2026-10-02  
**Documentation Standard:** [DOCUMENTATION_STANDARD.md](../../DOCUMENTATION_STANDARD.md)

---

## 1. Purpose

Define the temporal boundary rules used by ASSET-P0-001 for native and derived candles.

## 2. Reference Timezone

All canonical interval boundaries use **UTC**.

No local timezone or daylight-saving rule participates in candle construction.

## 3. Interval Semantics

All canonical candles use half-open intervals:

`[interval_start, interval_end)`.

Canonical replay availability occurs at `interval_end_us`, not at an exchange-specific last-trade timestamp.

## 4. Boundaries

### 1h
Starts at each UTC clock hour.

### 4h
Starts at:

- 00:00 UTC;
- 04:00 UTC;
- 08:00 UTC;
- 12:00 UTC;
- 16:00 UTC;
- 20:00 UTC.

### 1d
Starts at 00:00 UTC.

## 5. Provider Close Timestamp

Provider close timestamps may represent the final microsecond or millisecond before the exclusive interval boundary.

They may be preserved as source metadata, but canonical replay visibility is governed by `interval_end_us`.

## 6. Incomplete Candles

A candle whose exclusive end boundary has not yet occurred is incomplete and SHALL NOT be exposed as a finalized candle.

---

# Document History

| Version | Date | Description |
|---|---|---|
| 0.1.0 | 2026-10-02 | Initial UTC candle-boundary policy for ASSET-P0-001. |

---

**End of Document**
