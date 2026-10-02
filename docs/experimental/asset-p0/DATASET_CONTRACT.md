# Asset PRO P0 — Historical Dataset Contract

**Project:** Crypto Pro Suite  
**Document:** Historical Dataset Contract  
**Version:** 0.2.0  
**Status:** Draft  
**Owner:** Rogerio Raposo  
**Language:** English  
**Last Updated:** 2026-10-02  
**Documentation Standard:** [DOCUMENTATION_STANDARD.md](../../DOCUMENTATION_STANDARD.md)

---

## 1. Purpose

Define the minimum immutable historical dataset contract supplied by the Data Feed to Asset PRO Pilot P0.

## 2. Dataset Manifest

Each dataset version shall identify at least:

- `dataset_id`;
- `data_version`;
- `asset`;
- `venue`;
- `market_type`;
- `instrument`;
- `base_asset`;
- `quote_asset`;
- `source_provider`;
- `source_endpoint_or_contract`;
- `native_timeframe`;
- `start_timestamp`;
- `end_timestamp`;
- `timezone_policy`;
- `candle_boundary_policy_id`;
- `missing_data_policy_id`;
- `raw_record_count`;
- `validated_record_count`;
- `ingestion_timestamp`;
- `checksum`;
- `schema_version`;
- optional `notes`.

A dataset used by a frozen experiment shall be immutable. Corrections create a new `data_version`.

## 3. Canonical Candle Schema

Required normalized fields:

- `instrument`;
- `venue`;
- `market_type`;
- `timeframe`;
- `open_time_us`;
- `interval_end_us`;
- `open`;
- `high`;
- `low`;
- `close`;
- `volume`;
- `data_quality_flags`;
- `dataset_version`.

Optional source-dependent fields may include:

- `source_close_time_us`;
- `quote_volume`;
- `trade_count`;
- `source_record_id`;
- `source_timestamp_unit`.

### 3.1 Timestamp normalization

The canonical normalized timestamp unit for P0 is **Unix epoch microseconds**.

`interval_end_us` is the exclusive end boundary of the candle interval and is the authoritative availability boundary for causal replay.

Provider-specific close timestamps may be retained separately as `source_close_time_us`, but they shall not replace the canonical interval boundary.

### 3.2 Decimal representation

Price and volume values shall be represented as canonical decimal strings in persisted experiment datasets.

Canonical decimal strings shall:

- use base-10 notation;
- use no exponent;
- remove unnecessary leading plus signs;
- remove unnecessary trailing fractional zeros;
- represent zero as `"0"`.

This avoids binary floating-point ambiguity in deterministic serialization and hashing.

## 4. Origin

Each candle shall identify:

- `NATIVE`; or
- `DERIVED`.

Derived candles shall record the source timeframe and applicable resampling specification.

## 5. Integrity

The dataset package shall provide a deterministic checksum over the canonical serialized dataset or canonical manifest-defined representation.

Dataset identity is not equivalent to storing all historical bytes in Git.

---

# Document History

| Version | Date | Description |
|---|---|---|
| 0.1.0 | 2026-10-02 | Initial P0 historical dataset contract. |
| 0.2.0 | 2026-10-02 | Fixed canonical P0 timestamps to epoch microseconds and defined deterministic decimal persistence. |

---

**End of Document**
