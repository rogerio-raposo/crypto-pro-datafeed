# Asset PRO P0 — Provenance Specification

**Project:** Crypto Pro Suite  
**Document:** Provenance Specification  
**Version:** 0.2.0  
**Status:** Draft  
**Owner:** Rogerio Raposo  
**Language:** English  
**Last Updated:** 2026-10-02  
**Documentation Standard:** [DOCUMENTATION_STANDARD.md](../../DOCUMENTATION_STANDARD.md)

---

## 1. Purpose

Define the provenance chain required to reproduce and audit historical datasets supplied to Asset PRO P0.

## 2. Provenance Chain

The dataset record shall permit reconstruction of:

`provider → archive object → official archive checksum → venue → instrument → acquisition → raw records → validation → normalization → resampling, if any → dataset version → canonical dataset checksum`.

## 3. Required References

A frozen dataset manifest shall record:

- Data Feed repository commit SHA;
- source specification version;
- dataset-contract version;
- validation specification version;
- resampling specification version;
- candle-boundary policy version;
- canonical-serialization version;
- code version or commit used for dataset preparation;
- acquisition timestamp;
- each source archive path;
- each official archive checksum;
- dataset checksum.

## 4. ASSET-P0-001 Archive Plan

Main validation dataset:

- `BTCUSDT-1h-2025-01.zip`;
- `BTCUSDT-1h-2025-02.zip`;
- `BTCUSDT-1h-2025-03.zip`;

from the official Binance Spot monthly kline archive hierarchy, each paired with its corresponding `.CHECKSUM` object.

Real Golden Fixture:

- daily BTCUSDT Spot 1h archive objects for 2024-12-31;
- 2025-01-01;
- 2025-01-02;

each paired with its corresponding official checksum object when available.

The fixture intentionally crosses the source timestamp-unit transition and must preserve source-unit metadata before canonical normalization.

## 5. Cross-Repository Use

The CRYPTO-PRO-SUITE P0 Experiment Manifest shall reference the canonical Data Feed dataset manifest rather than duplicating it.

Formal Execution Freeze shall use an immutable Data Feed commit SHA, not a moving branch or `main` reference.

## 6. Corrections

A material change anywhere in the provenance chain creates a new dataset version and must not silently change a frozen experiment.

---

# Document History

| Version | Date | Description |
|---|---|---|
| 0.1.0 | 2026-10-02 | Initial P0 provenance specification. |
| 0.2.0 | 2026-10-02 | Added source-archive checksum chain and concrete ASSET-P0-001 archive plan. |

---

**End of Document**
