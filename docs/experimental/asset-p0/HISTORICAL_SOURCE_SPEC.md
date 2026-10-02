# Asset PRO P0 — Historical Source Specification

**Project:** Crypto Pro Suite  
**Document:** Historical Source Specification  
**Version:** 0.1.0  
**Status:** Draft  
**Owner:** Rogerio Raposo  
**Language:** English  
**Last Updated:** 2026-10-02  
**Documentation Standard:** [DOCUMENTATION_STANDARD.md](../../DOCUMENTATION_STANDARD.md)

---

## 1. Purpose

Define the minimum source-governance requirements for historical market data used in Asset PRO P0.

## 2. Source Record

Each acquired series shall preserve:

- provider;
- venue;
- market type;
- instrument;
- quote asset;
- endpoint or acquisition contract;
- acquisition timestamp;
- requested interval;
- returned interval;
- source granularity;
- source-specific identifiers when available;
- known source limitations.

## 3. Source Selection

P0 shall use one coherent Canonical Market series per test instrument unless an anomaly investigation explicitly requires a Validation Venue.

Source selection shall not be based solely on exchange preference. It shall be compatible with the Asset PRO Canonical Market Policy maintained in the CRYPTO-PRO-SUITE repository.

## 4. Historical Corrections

If the provider changes or corrects historical data after a dataset version has been frozen:

- the original dataset version remains reproducible;
- the corrected data receives a new version;
- experiments are not silently rewritten.

## 5. Licensing and Redistribution

Historical-source use shall record any known restrictions on:

- storage;
- redistribution;
- commercial use;
- API retention.

Large historical datasets should not be committed to Git merely for convenience.

## 6. Initial P0 Status

The final source provider, instruments, and periods are intentionally **TBD until the P0 Experiment Manifest is frozen**.

---

# Document History

| Version | Date | Description |
|---|---|---|
| 0.1.0 | 2026-10-02 | Initial source specification for Asset PRO P0. |

---

**End of Document**
