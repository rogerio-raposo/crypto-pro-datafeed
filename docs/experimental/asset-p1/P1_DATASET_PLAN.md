# Asset PRO P1 — Dataset Plan

**Project:** Crypto Pro Suite  
**Experiment:** ASSET-P1-D1-001  
**Status:** Design Freeze Revision 01 / Experimental / Non-Normative

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

P1 normalizes to the canonical epoch-microsecond contract validated by P0.

## 4. Data Identity

Each asset×segment dataset receives:

- Dataset ID;
- Data Version;
- source archive list;
- official archive checksums;
- native normalized SHA-256;
- derived 4h audit SHA-256;
- derived 1d audit SHA-256;
- analytical 4h SHA-256;
- analytical 1d SHA-256;
- record counts;
- registered-gap count;
- Analysis-Island counts;
- source/processing commit identity.

Current dataset generation uses version `v0.2.0` after Design Freeze Revision 01.

## 5. Holdout Governance

Holdout data may be acquired and checksum-frozen before method tuning, but Holdout analytical outputs must remain inaccessible to tuning logic until candidate lock after VAL.

Acquiring Holdout source bytes does not constitute opening Holdout analytical results.

Holdout manifests remain available for provenance/integrity audit; analytical access remains controlled by the Suite phase gate.

## 6. Continuity and Synchronized Venue Gaps

P1 never interpolates missing market candles.

A missing native 1h interval is admissible only when all of the following hold:

- the timestamp is listed in `P1_GAP_REGISTRY.md`;
- the same timestamp is missing across all four pilot instruments;
- official source archives/checksums are valid;
- the gap has venue-level evidence consistent with a common trading interruption.

For a registered synchronized venue gap:

- no synthetic candle is inserted;
- any derived 4h/Daily candle containing the gap is marked incomplete;
- incomplete derived candles remain audit-only;
- incomplete candles are excluded from analytical input;
- complete analytical candles are partitioned into contiguous Analysis Islands;
- D1 state resets at every island boundary;
- no swing, regime, Protected Swing, event, duration or match may bridge two islands.

Any additional gap, any asset-specific gap, duplicate interval, or unregistered discontinuity blocks Execution Freeze pending explicit adjudication.

Canonical registry:

`docs/experimental/asset-p1/P1_GAP_REGISTRY.md`

## 7. Current Materialization

Revision 01 dataset-preparation workflow:

- run: `37097201212`;
- conclusion: `success`;
- generated dataset manifests: 24 asset×segment cells.

Artifact groups:

- DEV: `asset-p1-dev-datasets-rev01`;
- VAL: `asset-p1-val-datasets-rev01`;
- HOLDOUT: `asset-p1-holdout-datasets-rev01`.

Git stores manifests and hashes; large normalized datasets remain workflow artifacts.
