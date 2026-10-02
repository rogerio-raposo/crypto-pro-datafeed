# Asset PRO P0 — Canonical Serialization Specification

**Project:** Crypto Pro Suite  
**Document:** Canonical Serialization Specification  
**Version:** 0.1.0  
**Status:** Draft  
**Owner:** Rogerio Raposo  
**Language:** English  
**Last Updated:** 2026-10-02  
**Documentation Standard:** [DOCUMENTATION_STANDARD.md](../../DOCUMENTATION_STANDARD.md)

---

## 1. Purpose

Define deterministic serialization for P0 dataset, fixture, snapshot and replay hash comparisons.

## 2. Dataset Record Format

Canonical normalized candle datasets use UTF-8 JSON Lines.

Each line contains one JSON object.

Rules:

- UTF-8 encoding;
- LF (`\n`) line endings;
- one final LF after each record;
- keys sorted lexicographically;
- compact JSON separators with no insignificant whitespace;
- non-ASCII text emitted directly as UTF-8;
- integer timestamps expressed as epoch microseconds;
- price/volume values expressed as canonical decimal strings;
- quality-flag arrays sorted lexicographically;
- records ordered by instrument, timeframe and `open_time_us`.

## 3. Canonical Decimal Strings

Canonical decimal strings:

- use ordinary base-10 notation;
- never use exponent notation;
- remove a leading plus sign;
- remove unnecessary trailing fractional zeros;
- remove the decimal point if the fractional part becomes empty;
- normalize negative zero to `"0"`.

Examples:

- `"100.0000"` → `"100"`;
- `"0.120000"` → `"0.12"`;
- `"-0.000"` → `"0"`.

## 4. Canonical JSON Documents

Single JSON manifests and deterministic metadata objects use:

- UTF-8;
- lexicographically sorted keys;
- compact separators;
- LF as final byte;
- canonical decimal strings where numeric precision is semantically relevant.

## 5. Hash

SHA-256 is the planned P0 checksum algorithm for canonical serialized content.

Hash algorithm and serialization version SHALL be recorded in the dataset manifest.

## 6. Version Identifier

Serialization policy identifier:

`asset-p0-canonical-json-v0.1.0`

A material change to serialization rules requires a new identifier.

---

# Document History

| Version | Date | Description |
|---|---|---|
| 0.1.0 | 2026-10-02 | Initial deterministic JSON/JSONL serialization specification for ASSET-P0-001. |

---

**End of Document**
