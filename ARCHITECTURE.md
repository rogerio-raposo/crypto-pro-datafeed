# Crypto Pro Data Feed Architecture

**Project:** Crypto Pro Data Feed  
**Document:** Architecture  
**Version:** 1.0.0  
**Status:** Stable  
**Owner:** Rogerio Raposo  
**Language:** English  
**Last Updated:** 2026-07-18  
**Documentation Standard:** DOCUMENTATION_STANDARD.md

---

# 1. Purpose

The Crypto Pro Data Feed is responsible for acquiring, validating, standardizing, and publishing cryptocurrency market data for the Crypto Pro Suite.

It is the only component authorized to communicate directly with external market data providers.

All downstream modules consume standardized market data exclusively through the published JSON contract, ensuring loose coupling between data acquisition and analytical components.

---

# 2. Design Philosophy

The architecture is guided by the following engineering principles:

- Single Responsibility
- Reliability over Completeness
- Deterministic Outputs
- Simplicity First
- Loose Coupling
- Public Data Contract
- Auditability
- Reproducibility
- Extensibility

The primary objective is to provide a stable and trustworthy data foundation for every module within the Crypto Pro Suite.

---

# 3. High-Level Architecture

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

The Data Feed acts exclusively as a producer.

Consumer modules never communicate directly with external exchanges.

Instead, they rely solely on the published data contract.

---

# 4. Architecture Decision Records (ADR)

## AD-001 — Single Data Source

The initial implementation uses Binance Spot as the sole market data provider.

This minimizes operational complexity while establishing a robust acquisition layer.

Future releases may introduce additional exchanges without changing the public interface consumed by downstream modules.

---

## AD-002 — Immutable Snapshot Publication

Instead of exposing live requests, the Data Feed periodically publishes immutable market snapshots.

This approach guarantees deterministic analyses, reproducibility, and simplified auditing.

---

## AD-003 — Public JSON Contract

Market data is distributed through versioned JSON files.

These files constitute the official public contract between the Data Feed and every consumer module.

Internal implementation details must never alter this contract without an explicit schema revision.

---

## AD-004 — Producer–Consumer Separation

Data acquisition and market analysis are intentionally separated.

The Data Feed is responsible only for collecting, validating, normalizing, and publishing market information.

Analytical interpretation belongs exclusively to downstream modules.

---

## AD-005 — Snapshot Preservation

A successfully published snapshot is considered immutable.

Failed executions must never overwrite the latest valid snapshot.

This guarantees continuous availability of trusted market data even during temporary operational failures.

---

## AD-006 — Status-Based Execution Validation

Every execution produces a `status.json` file.

Consumer modules must validate the execution status before reading `snapshot.json`.

This architectural decision replaced the previous `failure.json` proposal and significantly improved publication reliability.

---

# 5. Data Flow

Every execution follows the same deterministic workflow.

1. Acquire market data.
2. Validate external responses.
3. Normalize market information.
4. Build the market snapshot.
5. Build the execution status.
6. Publish artifacts.
7. Make the published contract available to consumer modules.

Every execution produces predictable and reproducible outputs.

---

# 6. Failure Strategy

The Data Feed follows four mandatory rules.

- A failed execution never overwrites `snapshot.json`.
- Every execution updates `status.json`.
- Failure reasons are always explicitly recorded.
- Consumer modules must validate `status.json` before consuming `snapshot.json`.

This strategy guarantees operational resilience while preserving the integrity of the published data.

---

# 7. Extensibility

The architecture was intentionally designed for incremental evolution.

Planned future extensions include:

- Multiple trading pairs
- Multiple exchanges
- Stablecoin market metrics
- BTC Dominance
- Market breadth indicators
- Funding Rates
- Open Interest
- On-chain metrics

These capabilities should extend the architecture without breaking the existing public contract.

---

# 8. Repository Boundaries

This repository is intentionally limited to market data acquisition.

It does not perform:

- Technical analysis
- Trading signals
- Market interpretation
- Institutional rankings
- Portfolio management
- Investment recommendations

Those responsibilities belong to higher-level modules within the Crypto Pro Suite.

---

# 9. Relationship with the Crypto Pro Suite

```text
Crypto Pro Data Feed
          │
          ▼
        BTC PRO
          │
          ▼
Capital Rotation Pro
          │
          ▼
Institutional Ranking
          │
          ▼
Reports & Decision Support
```

The Data Feed provides the standardized market layer upon which every analytical component of the Crypto Pro Suite is built.

---

# 10. Architecture Stability

This architecture is intended to remain stable across future releases.

Whenever possible, new capabilities should be introduced by extending existing components rather than modifying the established public data contract.

Maintaining contract stability is considered a fundamental architectural principle of the Crypto Pro Suite.

---

# 11. Guiding Principle

> A stable architecture enables stable analytics.

The quality of every analytical module depends directly on the reliability, consistency, and predictability of the Data Feed.

For this reason, architectural simplicity and deterministic behavior always take precedence over feature quantity.

---

# Document History

| Version | Date | Description |
|---------|------------|-------------|
| 1.0.0 | 2026-07-18 | First stable release. |

---

**End of Document**
