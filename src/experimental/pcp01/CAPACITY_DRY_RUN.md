# PCP-01 Capacity dry-run

Experimental operational validation for the nine Run A assets that survived
(or provisionally survived) the Relationship Materiality Gate.

Mapped Binance Spot markets:

- PLUMEUSDT
- OPUSDT
- APTUSDT
- SUIUSDT
- LINKUSDT
- RSRUSDT
- INJUSDT
- HYPEUSDT
- SYRUPUSDT

The collector validates acquisition, market identity/status, order-book schema,
turnover availability, timestamps and provenance.

It intentionally does **not** calculate PEC, PR, Accessibility, Absorption,
Capacity Gate results or Ranking outputs.

Two-cycle readiness means two PASS cycles in adjacent UTC hour slots. After
that status is reached, scheduled executions short-circuit without further
market-data capture.

Full cycle payloads are GitHub Actions artifacts. The repository persists only
the lightweight status history.
