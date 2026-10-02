# Asset PRO P0 — Data Validation Specification

**Project:** Crypto Pro Suite  
**Document:** Data Validation Specification  
**Version:** 0.2.0  
**Status:** Draft  
**Owner:** Rogerio Raposo  
**Language:** English  
**Last Updated:** 2026-10-02  
**Documentation Standard:** [DOCUMENTATION_STANDARD.md](../../DOCUMENTATION_STANDARD.md)

---

## 1. Purpose

Define producer-side objective validation controls for historical OHLCV before the dataset is exposed to Asset PRO P0.

## 2. Archive Integrity

Every Binance archive used by ASSET-P0-001 SHALL be acquired together with its official `.CHECKSUM` file when available.

Before extraction:

- compute SHA-256 of the ZIP;
- compare it with the official checksum;
- reject the archive from the formal dataset if the checksum does not match.

Archive checksum verification does not replace validation of the extracted records.

## 3. OHLC Invariants

Each record shall satisfy:

- High >= Open;
- High >= Close;
- Low <= Open;
- Low <= Close;
- High >= Low;
- open_time < interval_end;
- prices >= 0;
- volume >= 0.

Records that violate required invariants shall not be silently repaired.

## 4. Quality Flags

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

## 5. Gap Policy

General methodology retains three classes:

- Non-Material;
- Material;
- Critical.

ASSET-P0-001 deliberately uses a stricter formal validation rule:

> any missing native BTCUSDT 1h interval inside the frozen main validation period is a blocking dataset-integrity failure.

This strict rule is appropriate because P0 is validating infrastructure, not tolerance of incomplete historical market data.

Gap-handling behavior itself is tested using the Synthetic Golden Fixture and therefore does not require corruption of the main validation dataset.

No silent OHLCV interpolation is allowed.

## 6. Duplicates

Duplicate identity is based on instrument, timeframe, and canonical interval start under the active candle-boundary policy.

Any unresolved duplicate in the formal ASSET-P0-001 main validation dataset is a blocking failure.

## 7. Timestamp Validation

Source timestamp units SHALL be determined from the explicit source contract, not guessed during formal execution.

Normalized timestamps SHALL conform to the canonical epoch-microsecond contract.

Intervals shall align exactly with the active UTC Candle Boundary Policy.

## 8. Expected Record Counts

For the planned ASSET-P0-001 main dataset:

- native 1h records: 2160;
- derived 4h records: 540;
- derived 1d records: 90.

A count mismatch is blocking unless a reviewed source exception is documented before execution freeze.

## 9. Outliers

Extreme price or volume observations shall be flagged, not automatically removed. Legitimate flash events must remain representable.

## 10. Final Dataset Checksum

After normalization and canonical serialization, the final dataset SHALL receive a SHA-256 checksum recorded in the canonical Dataset Manifest.

---

# Document History

| Version | Date | Description |
|---|---|---|
| 0.1.0 | 2026-10-02 | Initial P0 producer-side validation specification. |
| 0.2.0 | 2026-10-02 | Added archive checksum verification, strict ASSET-P0-001 continuity rules, timestamp validation and expected record counts. |

---

**End of Document**
