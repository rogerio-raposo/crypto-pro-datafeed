# Asset PRO P0 — Data Validation Specification

**Project:** Crypto Pro Suite  
**Document:** Data Validation Specification  
**Version:** 0.1.0  
**Status:** Draft  
**Owner:** Rogerio Raposo  
**Language:** English  
**Last Updated:** 2026-10-02  
**Documentation Standard:** [DOCUMENTATION_STANDARD.md](../../DOCUMENTATION_STANDARD.md)

---

## 1. Purpose

Define producer-side objective validation controls for historical OHLCV before the dataset is exposed to Asset PRO P0.

## 2. OHLC Invariants

Each record shall satisfy:

- High >= Open;
- High >= Close;
- Low <= Open;
- Low <= Close;
- High >= Low;
- open_time < close_time;
- prices >= 0;
- volume >= 0.

Records that violate required invariants shall not be silently repaired.

## 3. Quality Flags

Initial controlled vocabulary:

- `INVALID_OHLC`;
- `DUPLICATE_CANDLE`;
- `MISSING_INTERVAL`;
- `ZERO_VOLUME`;
- `EXTREME_PRICE_MOVE`;
- `EXTREME_VOLUME`;
- `TIMESTAMP_IRREGULARITY`;
- `SOURCE_DISCONTINUITY`;
- `INSTRUMENT_CHANGE`;
- `SUSPENSION`;
- `CROSS_VENUE_ANOMALY`.

A flag is evidence about data quality, not automatically evidence that the market observation is erroneous.

## 4. Gaps

Gaps shall be detectable and classifiable as:

- Non-Material;
- Material;
- Critical.

Numerical thresholds remain TBD and shall be frozen before formal execution.

No silent OHLCV interpolation is allowed.

## 5. Duplicates

Duplicate identity is based on instrument, timeframe, and timestamp under the active candle-boundary policy.

Unresolved duplicates affecting the formal dataset are a critical validation failure.

## 6. Outliers

Extreme price or volume observations shall be flagged, not automatically removed. Legitimate flash events must remain representable.

---

# Document History

| Version | Date | Description |
|---|---|---|
| 0.1.0 | 2026-10-02 | Initial P0 producer-side validation specification. |

---

**End of Document**
