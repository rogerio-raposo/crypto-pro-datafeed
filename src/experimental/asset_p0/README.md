# Asset PRO P0 — Experimental Producer Source

**Status:** Experimental / Non-Normative  
**Experiment:** ASSET-P0-001  
**Branch:** `experiment/asset-p0`

This directory contains the producer-side implementation used to prepare ASSET-P0-001 for Execution Freeze.

## Files

- `p0_data.py` — canonical decimal/timestamp normalization, Binance archive parsing, SHA-256 verification, native-data validation, deterministic resampling and canonical serialization.
- `build_artifacts.py` — builds the Synthetic Golden Fixture, Real Golden Fixture, and main Q1-2025 validation dataset.

## Responsibility Boundary

This code may:

- acquire historical archives;
- verify official archive checksums;
- parse and normalize data;
- identify objective data-quality conditions;
- resample 1h to 4h / 1d;
- emit canonical datasets/manifests.

This code SHALL NOT:

- perform technical analysis;
- classify D1–D5;
- generate setup states;
- run the Asset PRO causal replay.

Causal replay belongs to the CRYPTO-PRO-SUITE Asset P0 experimental harness.

## Implementation-Validation Commands

From this directory:

```bash
python build_artifacts.py synthetic --output <fixture-output>
python build_artifacts.py real-fixture --output <fixture-output> --cache <archive-cache>
python build_artifacts.py main-dataset --output <dataset-output> --cache <archive-cache>
```

These commands prepare or regression-test implementation artifacts. They do **not** constitute formal P0 execution.

## Current State

- Synthetic Golden Fixture: generated and committed.
- Real Golden Fixture: implementation ready; source acquisition still pending.
- Main validation dataset: implementation ready; source acquisition still pending.
- Execution Freeze: pending.
