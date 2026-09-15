# Crypto Pro Data Feed Changelog

**Project:** Crypto Pro Data Feed  
**Document:** Changelog  
**Version:** 1.0.0  
**Status:** Stable  
**Owner:** Rogerio Raposo  
**Language:** English  
**Last Updated:** 2026-09-15  
**Documentation Standard:** [docs/DOCUMENTATION_STANDARD.md](docs/DOCUMENTATION_STANDARD.md)

---

# Overview

This document records notable changes to the Crypto Pro Data Feed. The project follows Semantic Versioning.

# Version 1.0.0 — Initial Stable Baseline

## Added

- Binance Spot BTCUSDT Data Feed implementation.
- Retry mechanism across approved Binance public hosts.
- Semantic validation and atomic JSON publication.
- Snapshot preservation and execution status reporting.
- Public JSON contract.
- GitHub Actions workflow.
- Engineering documentation and documentation governance.
- Documentation overview and navigation model.

## Changed

- Reorganized repository into `src/`, `data/`, and `docs/`.
- Moved `datafeed.py` to `src/datafeed.py`.
- Moved public JSON artifacts to `data/snapshot.json` and `data/status.json`.
- Moved engineering documentation to `docs/` while retaining project-level files at the repository root.
- Updated `.github/workflows/update-datafeed.yml` to execute and validate the new paths.
- Standardized relative documentation links and repository navigation.
- Normalized the license filename to `LICENSE`.

## Validation

The release baseline requires validation of successful execution, failure handling, snapshot preservation, status publication, semantic JSON validation, workflow behavior, documentation links, repository paths, and consumer compatibility.

# Future Releases

Subsequent releases should record changes under Added, Changed, Fixed, Removed, and Deprecated as applicable.

---

# Document History

| Version | Date | Description |
|---------|------------|-------------|
| 1.0.0 | 2026-07-18 | Initial stable baseline documentation. |
| 1.0.0 | 2026-09-15 | Recorded repository reorganization and documentation alignment. |

---

**End of Document**
