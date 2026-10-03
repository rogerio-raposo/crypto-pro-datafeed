# Asset PRO P1 — Source Eligibility Plan

**Project:** Crypto Pro Suite  
**Experiment:** ASSET-P1-D1-001  
**Status:** Draft / Experimental / Non-Normative

---

## Objective

Verify before P1 Design Freeze that every required Binance Public Data monthly archive exists for every asset and selected calendar month.

## Required Matrix

Assets:

- BTCUSDT;
- ETHUSDT;
- SOLUSDT;
- XRPUSDT.

Months:

- 2021-01 through 2021-06;
- 2022-06 through 2022-11;
- 2023-01 through 2023-12;
- 2024-01 through 2024-12.

Total checks:

`4 × 36 = 144 monthly ZIP archives`.

Each ZIP must also expose the corresponding:

`.CHECKSUM`

object.

## Eligibility Result

An instrument is source-eligible only if all required ZIP and CHECKSUM objects exist.

The eligibility workflow records:

- instrument;
- year-month;
- ZIP URL;
- ZIP HTTP result;
- CHECKSUM URL;
- CHECKSUM HTTP result;
- final eligible boolean.

No price behavior is inspected during this source check.

## Governance

Source eligibility is infrastructure evidence only.

It must not be used to choose periods based on subsequent market behavior.
