# Asset PRO P0 — Provenance Specification

**Project:** Crypto Pro Suite  
**Document:** Provenance Specification  
**Version:** 0.1.0  
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

`provider → venue → instrument → acquisition request → raw records → validation → normalization → resampling, if any → dataset version → checksum`.

## 3. Required References

A frozen dataset manifest shall record:

- Data Feed repository commit SHA;
- source specification version;
- validation specification version;
- resampling specification version when applicable;
- code version or commit used for dataset preparation;
- acquisition timestamp;
- dataset checksum.

## 4. Cross-Repository Use

The CRYPTO-PRO-SUITE P0 Experiment Manifest shall reference the canonical Data Feed dataset manifest rather than duplicating it.

Formal experiment freeze shall use an immutable Data Feed commit SHA, not a moving `main` reference.

## 5. Corrections

A material change anywhere in the provenance chain creates a new dataset version and must not silently change a frozen experiment.

---

# Document History

| Version | Date | Description |
|---|---|---|
| 0.1.0 | 2026-10-02 | Initial P0 provenance specification. |

---

**End of Document**
