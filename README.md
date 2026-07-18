# Crypto Pro Data Feed

**Project:** Crypto Pro Data Feed  
**Document:** README  
**Version:** 1.0.0  
**Status:** Stable  
**Owner:** Rogerio Raposo  
**Language:** English  
**Last Updated:** 2026-07-18  
**Documentation Standard:** DOCUMENTATION_STANDARD.md

---

# Overview

Crypto Pro Data Feed is the official market data acquisition module of the Crypto Pro Suite.

Its mission is to collect, validate, normalize, and publish cryptocurrency market data through a stable public JSON contract.

Rather than exposing live exchange requests to analytical modules, the Data Feed publishes deterministic snapshots that serve as the single source of truth for the entire ecosystem.

---

# Objectives

- Acquire reliable market data
- Validate exchange responses
- Normalize market information
- Publish deterministic JSON snapshots
- Preserve the latest valid snapshot during failures
- Provide a stable public contract for consumer modules

---

# Key Features

- Binance Spot integration
- Automatic retry mechanism
- Semantic validation
- Atomic file publication
- Snapshot preservation
- Execution status reporting
- Standard library only
- GitHub Actions automation
- Public JSON contract
- Consumer-independent architecture

---

# Architecture Overview

```text
            Binance Spot API
                    │
                    ▼
             datafeed.py
                    │
      ┌─────────────┴─────────────┐
      ▼                           ▼
 snapshot.json               status.json
      │                           │
      └─────────────┬─────────────┘
                    ▼
           GitHub Repository
                    │
                    ▼
       Published Data Contract
                    │
                    ▼
        Crypto Pro Suite Modules
```

For architectural details, see `ARCHITECTURE.md`.

---

# Repository Structure

```text
.
├── .github/
│   └── workflows/
├── datafeed.py
├── snapshot.json
├── status.json
├── README.md
├── SPEC.md
├── ARCHITECTURE.md
├── DEVELOPMENT.md
├── DOCUMENTATION_STANDARD.md
├── CHANGELOG.md
├── ROADMAP.md
├── CONTRIBUTING.md
└── LICENSE
```

---

# Published Data Contract

The repository publishes two official JSON artifacts.

## snapshot.json

Contains the latest validated market snapshot.

This file is only replaced after a successful execution.

---

## status.json

Contains execution metadata.

Consumer modules must validate this file before consuming `snapshot.json`.

Typical fields include:

- status
- timestamp
- exchange
- symbol
- snapshot_updated
- error (when applicable)

---

# Workflow

Each execution follows the same deterministic pipeline.

```text
Acquire Data
      │
      ▼
Validate
      │
      ▼
Normalize
      │
      ▼
Create Snapshot
      │
      ▼
Create Status
      │
      ▼
Publish
```

---

# Documentation

This repository follows the documentation policy defined in:

- DOCUMENTATION_STANDARD.md

Primary technical documents:

- README.md
- SPEC.md
- ARCHITECTURE.md
- DEVELOPMENT.md
- CHANGELOG.md
- ROADMAP.md
- CONTRIBUTING.md

Each document covers a specific aspect of the project.

---

# Project Status

Current Version:

**1.0.0**

Status:

**Production Ready**

Current capabilities:

- Single exchange
- Single trading pair
- Immutable snapshots
- Public JSON contract
- Automated publication

---

# Roadmap

Planned future improvements include:

- Multiple trading pairs
- Multiple exchanges
- Stablecoin metrics
- BTC Dominance
- Funding Rates
- Open Interest
- On-chain indicators

See `ROADMAP.md` for details.

---

# Contributing

Contributions are welcome.

Please read `CONTRIBUTING.md` before submitting pull requests.

---

# License

This project is distributed under the MIT License.

See `LICENSE` for details.

---

# Guiding Principle

> Reliable analytics begin with reliable data.

The Crypto Pro Data Feed is intentionally designed to provide a deterministic, auditable, and stable market data layer for every analytical module within the Crypto Pro Suite.

---

# Document History

| Version | Date | Description |
|---------|------------|-------------|
| 1.0.0 | 2026-07-18 | First stable release. |

---

**End of Document**
