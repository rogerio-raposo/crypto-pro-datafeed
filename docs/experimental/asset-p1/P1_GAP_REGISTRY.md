# Asset PRO P1 — Synchronized Venue Gap Registry

**Project:** Crypto Pro Suite  
**Experiment:** ASSET-P1-D1-001  
**Status:** Design Freeze Revision 01 / Experimental / Non-Normative

---

## 1. Rule

P1 does not interpolate missing candles.

A missing native 1h interval is accepted only when it is listed in this registry and is reproduced identically across BTCUSDT, ETHUSDT, SOLUSDT and XRPUSDT.

Any additional, missing-from-registry, or asset-specific gap blocks Execution Freeze.

## 2. Frozen Registry

### DEV-01

| UTC open time | Epoch microseconds |
|---|---:|
| 2021-02-11 04:00 | 1613016000000000 |
| 2021-03-06 02:00 | 1614996000000000 |
| 2021-04-20 02:00 | 1618884000000000 |
| 2021-04-20 03:00 | 1618887600000000 |
| 2021-04-25 05:00 | 1619326800000000 |
| 2021-04-25 06:00 | 1619330400000000 |
| 2021-04-25 07:00 | 1619334000000000 |

### VAL-01

| UTC open time | Epoch microseconds |
|---|---:|
| 2023-03-24 13:00 | 1679662800000000 |

Other frozen segments:

- DEV-02: no registered gap;
- VAL-02: no registered gap;
- HOLD-01: no registered gap;
- HOLD-02: no registered gap.

## 3. Provenance

Continuity diagnostic:

- workflow run: `37096651289`;
- artifact ID: `11264686520`;
- artifact digest: `sha256:bc6d5305382340ff9cf7c8a93e967eaf8ef5eeae0481bd1264cfee90bf9bbd5c`.

The diagnostic found:

- 24 asset×segment source cells;
- 0 duplicate intervals;
- identical gap timestamps across all four assets in each affected segment.

## 4. Venue Evidence

Binance published system-maintenance/interruption notices covering the registered gaps:

- 2021-02-11 temporary maintenance;
- 2021-03-06 scheduled Spot system upgrade;
- 2021-04-20 scheduled Spot system upgrade;
- 2021-04-25 scheduled Spot system upgrade;
- 2023-03-24 temporary Spot matching-engine interruption.

## 5. Analytical Consequence

For each affected analytical timeframe:

- any derived candle containing a registered gap is incomplete;
- incomplete derived candles are retained only for audit;
- incomplete candles are excluded from analytical input;
- complete candles are divided into contiguous Analysis Islands;
- D1 state must reset at island boundaries.

No structural or metric calculation may bridge two islands.
