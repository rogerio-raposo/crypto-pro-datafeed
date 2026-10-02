# Asset PRO P0 — Dataset Plan

**Project:** Crypto Pro Suite  
**Document:** ASSET-P0-001 Dataset Plan  
**Version:** 0.1.0  
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

Use official Binance Public Data monthly Spot kline archives for:

- January 2025;
- February 2025;
- March 2025.

Acquisition tooling SHALL verify the downloaded archive and normalized output rather than assume record completeness from archive presence.

## 3. Dataset Acceptance for P0

The formal real validation dataset SHALL contain:

- exactly 2160 native 1h intervals;
- no unresolved duplicate interval;
- no missing native interval;
- monotonic interval starts;
- valid OHLC invariants;
- complete provenance;
- canonical dataset checksum.

Any missing native 1h interval is blocking for ASSET-P0-001. Gap-handling behavior itself is tested separately in the synthetic fixture.

## 4. Derived Expectations

If the native dataset is complete:

- expected 4h candles: 540;
- expected Daily candles: 90.

Counts are acceptance expectations and shall be verified during execution.

## 5. Status

No archive has been acquired and no canonical Dataset Manifest has been frozen yet.

---

# Document History

| Version | Date | Description |
|---|---|---|
| 0.1.0 | 2026-10-02 | Initial concrete dataset plan for ASSET-P0-001. |

---

**End of Document**
