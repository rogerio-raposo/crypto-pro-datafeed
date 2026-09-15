# Crypto Pro Data Feed Architecture

**Project:** Crypto Pro Data Feed  
**Document:** Architecture  
**Version:** 1.0.0  
**Status:** Stable  
**Owner:** Rogerio Raposo  
**Language:** English  
**Last Updated:** 2026-09-15  
**Documentation Standard:** [DOCUMENTATION_STANDARD.md](DOCUMENTATION_STANDARD.md)

---

# 1. Purpose

The Crypto Pro Data Feed acquires, validates, standardizes, and publishes cryptocurrency market data for the Crypto Pro Suite. Downstream modules consume the published JSON contract rather than communicating directly with exchanges.

# 2. Design Philosophy

The architecture prioritizes single responsibility, reliability over completeness, deterministic outputs, simplicity, loose coupling, auditability, reproducibility, and public-contract stability.

# 3. High-Level Architecture

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

`.github/workflows/update-datafeed.yml` orchestrates repository execution, validates generated artifacts, and publishes changes. Version 1.0.0 exposes manual workflow execution through `workflow_dispatch`.

# 4. Repository Boundaries

```text
.github/workflows/update-datafeed.yml  Workflow orchestration and publication
src/datafeed.py                        Acquisition, normalization, validation
 data/snapshot.json                    Latest validated market snapshot
 data/status.json                      Latest execution status
docs/                                  Engineering documentation
```

The repository does not perform technical analysis, trading signals, market interpretation, institutional ranking, portfolio management, or investment recommendations.

# 5. Architecture Decisions

## AD-001 — Single Data Source

Version 1.0.0 uses Binance Spot as the sole market data provider to minimize operational complexity.

## AD-002 — Snapshot Publication

The Data Feed publishes a latest validated snapshot instead of exposing live exchange requests to consumers. A failed execution must not replace the latest valid snapshot.

## AD-003 — Public JSON Contract

`data/snapshot.json` and `data/status.json` form the versioned public interface. Internal implementation changes must not break this contract without an explicit schema revision.

## AD-004 — Producer–Consumer Separation

The Data Feed produces standardized market data; analytical interpretation belongs to downstream modules.

## AD-005 — Status-Based Execution Validation

Every execution updates `data/status.json`. Consumers should validate execution status before using `data/snapshot.json`.

## AD-006 — Source, Data, and Documentation Separation

Executable source code is isolated under `src/`, published artifacts under `data/`, and engineering documentation under `docs/`. This separation makes repository responsibilities explicit without introducing unnecessary directories.

# 6. Failure Strategy

On failure, the latest valid snapshot is preserved, status is updated with the failure reason, and the workflow can publish the failure status without corrupting the public snapshot.

# 7. Extensibility

Future capabilities may include multiple trading pairs, multiple exchanges, exchange failover, stablecoin metrics, BTC dominance, market breadth, funding rates, open interest, and on-chain metrics. Extensions should preserve the established public interface whenever possible.

# 8. Architecture Stability

New capabilities should extend established components rather than replace stable interfaces. Contract stability and deterministic behavior take precedence over feature quantity.

# Guiding Principle

> A stable architecture enables stable analytics.

---

# Document History

| Version | Date | Description |
|---------|------------|-------------|
| 1.0.0 | 2026-07-18 | First stable baseline. |
| 1.0.0 | 2026-09-15 | Aligned architecture and repository boundaries with the reorganized structure. |

---

**End of Document**
