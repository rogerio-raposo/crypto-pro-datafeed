# Asset PRO P0 — Historical Data Experimental Package

**Project:** Crypto Pro Suite  
**Document:** Asset PRO P0 Historical Data Experimental Package  
**Version:** 0.2.0  
**Status:** Draft  
**Owner:** Rogerio Raposo  
**Language:** English  
**Last Updated:** 2026-10-02  
**Documentation Standard:** [DOCUMENTATION_STANDARD.md](../../DOCUMENTATION_STANDARD.md)

---

## 1. Purpose

This package defines the producer-side experimental data contract required by Asset PRO Pilot P0.

P0 validates historical-data integrity, provenance, deterministic resampling, and reproducibility before the CRYPTO-PRO-SUITE repository is allowed to execute the Asset PRO causal replay and subsequent P1/D1 validation.

This package is **experimental and non-normative**. It does not modify the stable Data Feed v1.0.0 public contract.

## 2. Ownership Boundary

The Data Feed owns:

- historical source acquisition;
- source and instrument provenance;
- objective data validation;
- producer-side normalization;
- deterministic resampling;
- dataset technical manifests;
- fixture production.

The CRYPTO-PRO-SUITE Asset PRO experimental harness owns:

- causal replay;
- analytical state;
- D1–D5 methodology;
- P0/P1 experiment manifests and decision records.

Guiding rule:

> The Data Feed defines what happened. The Asset PRO experimental harness controls what could be known at each replay timestamp.

## 3. ASSET-P0-001 Design Baseline

Planned validation dataset:

- Binance Public Data;
- Binance Spot;
- BTCUSDT;
- 1h native klines;
- 2025-01-01 00:00 UTC inclusive through 2025-04-01 00:00 UTC exclusive;
- derived 4h and 1d series;
- UTC candle boundaries;
- canonical epoch-microsecond timestamps;
- SHA-256 integrity.

The main historical validation dataset will be acquired from official monthly archives. The small real golden fixture will use official daily archives around the 2025-01-01 timestamp-unit transition.

## 4. Documents

- [DATASET_CONTRACT.md](DATASET_CONTRACT.md)
- [HISTORICAL_SOURCE_SPEC.md](HISTORICAL_SOURCE_SPEC.md)
- [DATA_VALIDATION_SPEC.md](DATA_VALIDATION_SPEC.md)
- [RESAMPLING_SPEC.md](RESAMPLING_SPEC.md)
- [PROVENANCE_SPEC.md](PROVENANCE_SPEC.md)
- [CANDLE_BOUNDARY_POLICY.md](CANDLE_BOUNDARY_POLICY.md)
- [CANONICAL_SERIALIZATION_SPEC.md](CANONICAL_SERIALIZATION_SPEC.md)
- [P0_DATASET_PLAN.md](P0_DATASET_PLAN.md)

## 5. Experimental Paths

- source placeholder: `src/experimental/asset_p0/`
- fixture/data placeholder: `data/experimental/asset-p0/`

Large historical datasets are not intended to be committed to Git. Reproducibility must rely on immutable identity, provenance, version, checksum, and reconstruction instructions.

## 6. Branch Isolation

Active Asset P0 producer-side work is isolated on branch:

`experiment/asset-p0`

This branch must be freshness-checked against `main` before integration. It must not overwrite parallel PCP-01 experimental work.

---

# Document History

| Version | Date | Description |
|---|---|---|
| 0.1.0 | 2026-10-02 | Initial experimental package for Asset PRO P0. |
| 0.2.0 | 2026-10-02 | Added ASSET-P0-001 design baseline, branch-isolation rule, and expanded document index. |

---

**End of Document**
