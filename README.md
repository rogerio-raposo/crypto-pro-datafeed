# Crypto Pro Data Feed

**Project:** Crypto Pro Data Feed  
**Document:** README  
**Version:** 1.0.0  
**Status:** Stable  
**Owner:** Rogerio Raposo  
**Language:** English  
**Last Updated:** 2026-09-15  
**Documentation Standard:** [docs/DOCUMENTATION_STANDARD.md](docs/DOCUMENTATION_STANDARD.md)

---

# Overview

Crypto Pro Data Feed is the official market data acquisition module of the Crypto Pro Suite. It collects, validates, normalizes, and publishes cryptocurrency market data through a stable public JSON contract.

Rather than exposing live exchange requests to analytical modules, the Data Feed publishes deterministic artifacts that act as the trusted market-data interface for downstream consumers.

# Key Features

- Binance Spot integration for BTCUSDT.
- Automatic retry across approved Binance public hosts.
- Semantic validation and atomic JSON publication.
- Preservation of the latest valid snapshot after failures.
- Execution status reporting.
- Python Standard Library only.
- GitHub Actions execution and publication workflow.

# Architecture Overview

```text
Binance Spot API
       │
       ▼
src/datafeed.py
       │
       ├──► data/snapshot.json
       └──► data/status.json
                    │
                    ▼
          Public Data Contract
                    │
                    ▼
        Crypto Pro Suite Modules
```

For architectural details, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

# Repository Structure

```text
crypto-pro-datafeed/
├── .github/
│   └── workflows/
│       └── update-datafeed.yml
├── src/
│   └── datafeed.py
├── data/
│   ├── snapshot.json
│   └── status.json
├── docs/
│   ├── DOCUMENTATION_OVERVIEW.md
│   ├── DOCUMENTATION_STANDARD.md
│   ├── SPEC.md
│   ├── ARCHITECTURE.md
│   ├── DEVELOPMENT.md
│   └── ROADMAP.md
├── .gitignore
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

# Published Data Contract

The official public artifacts are `data/snapshot.json` and `data/status.json`. A successful execution may replace both artifacts. A failed execution must preserve the latest valid snapshot while updating `data/status.json` with the failure result.

Consumer modules should validate `data/status.json` before using `data/snapshot.json`.

# Workflow

`.github/workflows/update-datafeed.yml` executes `src/datafeed.py`, validates the generated artifacts, stages the appropriate files, and publishes repository updates when changes exist. Version 1.0.0 retains manual execution through `workflow_dispatch`; periodic scheduling is outside the current release scope.

# Documentation

Start with [docs/DOCUMENTATION_OVERVIEW.md](docs/DOCUMENTATION_OVERVIEW.md), which provides the documentation map and recommended reading order.

The repository documentation is governed by [docs/DOCUMENTATION_STANDARD.md](docs/DOCUMENTATION_STANDARD.md).

# Project Status

Version **1.0.0** is the initial stable baseline. Current scope is one exchange, one trading pair, a versioned public JSON contract, failure-safe snapshot publication, and GitHub Actions execution.

# Contributing and License

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines and [LICENSE](LICENSE) for the MIT License.

# Guiding Principle

> Publish trustworthy market data through simple, deterministic and maintainable engineering.

---

# Document History

| Version | Date | Description |
|---------|------------|-------------|
| 1.0.0 | 2026-07-18 | First stable baseline. |
| 1.0.0 | 2026-09-15 | Aligned documentation with the reorganized repository structure. |

---

**End of Document**
