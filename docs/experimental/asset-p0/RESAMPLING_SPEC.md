# Asset PRO P0 — Resampling Specification

**Project:** Crypto Pro Suite  
**Document:** Resampling Specification  
**Version:** 0.1.0  
**Status:** Draft  
**Owner:** Rogerio Raposo  
**Language:** English  
**Last Updated:** 2026-10-02  
**Documentation Standard:** [DOCUMENTATION_STANDARD.md](../../DOCUMENTATION_STANDARD.md)

---

## 1. Purpose

Define deterministic OHLCV resampling rules for historical datasets used by Asset PRO P0/P1.

## 2. Aggregation

For source candles ordered inside one target interval:

- Open = first Open;
- High = maximum High;
- Low = minimum Low;
- Close = last Close;
- Volume = sum of Volume.

Optional additive source fields may be aggregated only when their semantics permit it.

## 3. Candle Boundary Policy

Each dataset shall reference a versioned Candle Boundary Policy defining:

- timezone;
- target interval alignment;
- Daily boundaries;
- 4h boundaries;
- Weekly boundaries when used;
- interval inclusion convention;
- incomplete-candle treatment.

UTC is the preferred reference unless a different policy is explicitly required and versioned.

## 4. Incomplete Inputs

If required source intervals are missing inside an aggregated candle, the derived candle shall carry the applicable quality flag. Missing intervals shall not be hidden by aggregation.

## 5. Determinism

Identical source data, boundary policy, and resampling specification shall produce byte-equivalent canonical outputs after canonical serialization.

---

# Document History

| Version | Date | Description |
|---|---|---|
| 0.1.0 | 2026-10-02 | Initial deterministic resampling specification for Asset P0. |

---

**End of Document**
