# Asset PRO P0 — Historical Source Specification

**Project:** Crypto Pro Suite  
**Document:** Historical Source Specification  
**Version:** 0.2.0  
**Status:** Draft  
**Owner:** Rogerio Raposo  
**Language:** English  
**Last Updated:** 2026-10-02  
**Documentation Standard:** [DOCUMENTATION_STANDARD.md](../../DOCUMENTATION_STANDARD.md)

---

## 1. Purpose

Define the source-governance requirements and planned source for historical market data used in Asset PRO P0.

## 2. Planned Source for ASSET-P0-001

The planned primary historical source is:

- provider: Binance Public Data;
- archive: `https://data.binance.vision/`;
- venue: Binance Spot;
- market type: Spot;
- instrument: BTCUSDT;
- data type: klines;
- native interval: 1h;
- acquisition mode: official monthly public-data archives;
- planned validation period: 2025-01-01 00:00 UTC through 2025-04-01 00:00 UTC exclusive.

The selected period contains 90 complete UTC days and therefore has an expected contiguous native-candle count of:

`90 × 24 = 2160` one-hour candles.

This expected count is a validation expectation, not a substitute for actual acquisition and checksum verification.

## 3. Source Record

Each acquired series shall preserve:

- provider;
- venue;
- market type;
- instrument;
- quote asset;
- archive path or acquisition contract;
- acquisition timestamp;
- requested interval;
- returned interval;
- source granularity;
- source-specific identifiers when available;
- known source limitations.

## 4. Timestamp Source Rule

Binance Spot public archive data from 2025-01-01 onward uses microsecond timestamps.

The P0 normalizer shall therefore treat 2025 archive timestamps according to the explicit source contract and normalize them to canonical epoch microseconds.

Timestamp unit shall not be guessed from floating-point magnitude during formal execution.

## 5. Source Selection Rationale

BTCUSDT Spot is selected for P0 because it:

- matches the stable Data Feed v1.0.0 market scope;
- provides a highly liquid, continuously traded instrument;
- minimizes market-specific data-quality complications while infrastructure is being validated;
- permits deterministic derivation of 4h and Daily candles from a 1h native series.

P0 source selection does not establish BTCUSDT or Binance Spot as a universal Asset PRO canonical-market rule.

## 6. Historical Corrections

If the provider changes or corrects historical data after a dataset version has been frozen:

- the original dataset version remains reproducible;
- the corrected data receives a new version;
- experiments are not silently rewritten.

## 7. Licensing and Redistribution

Historical-source use shall record any known restrictions on:

- storage;
- redistribution;
- commercial use;
- API/archive retention.

Large historical datasets should not be committed to Git merely for convenience.

---

# Document History

| Version | Date | Description |
|---|---|---|
| 0.1.0 | 2026-10-02 | Initial source specification for Asset PRO P0. |
| 0.2.0 | 2026-10-02 | Selected planned BTCUSDT Binance Spot 1h public-archive source and Q1 2025 validation period for ASSET-P0-001. |

---

**End of Document**
