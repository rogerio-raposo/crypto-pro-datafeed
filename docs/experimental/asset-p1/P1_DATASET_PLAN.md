# Asset PRO P1 — Dataset Plan

**Project:** Crypto Pro Suite  
**Experiment:** ASSET-P1-D1-001  
**Status:** Draft / Experimental / Non-Normative

---

## 1. Assets

| Role | Instrument |
|---|---|
| A1 | BTCUSDT |
| A2 | ETHUSDT |
| A3 | SOLUSDT |
| A4 | XRPUSDT |

Venue:

`Binance Spot`

Source:

`Binance Public Data monthly Spot kline archives`

Native timeframe:

`1h`

Derived:

- 4h;
- 1d.

## 2. Required Segments

### DEV-01
2021-01-01 through 2021-07-01 UTC exclusive.

### DEV-02
2022-06-01 through 2022-12-01 UTC exclusive.

### VAL-01
2023-01-01 through 2023-07-01 UTC exclusive.

### VAL-02
2023-07-01 through 2024-01-01 UTC exclusive.

### HOLD-01
2024-01-01 through 2024-07-01 UTC exclusive.

### HOLD-02
2024-07-01 through 2025-01-01 UTC exclusive.

All segments contain six complete calendar months.

Total required source months per instrument:

`36`

Total monthly source archives across four instruments:

`144`

## 3. Timestamp Policy

All selected source months are before 2025-01-01.

Expected Binance Public Data Spot archive source unit:

`milliseconds`

P1 nevertheless normalizes to the same canonical epoch-microsecond contract validated by P0.

## 4. Data Identity

Each asset×segment dataset will receive:

- Dataset ID;
- Data Version;
- source archive list;
- official archive checksums;
- native normalized SHA-256;
- derived 4h SHA-256;
- derived 1d SHA-256;
- record counts;
- source/processing commit identity.

## 5. Holdout Governance

Holdout data may be acquired and checksum-frozen before method tuning, but Holdout analytical outputs must remain inaccessible to tuning logic until candidate lock after VAL.

Acquiring Holdout source bytes does not constitute opening Holdout analytical results.

## 6. Continuity

Missing monthly archive or irreparable data gap in any required common segment blocks Design Freeze until:

- the segment is revised consistently for all assets; or
- the affected asset is replaced through an explicit design revision.

No per-asset silent shortening is allowed.
