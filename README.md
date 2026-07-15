Crypto Pro Data Feed

Overview

Crypto Pro Data Feed is the official market data provider for the Crypto Pro Suite.

Its purpose is to obtain reliable market data directly from Binance Spot and make it available in a standardized format for the analytical modules of the Suite.

The first consumer of this data feed is BTC PRO, which performs institutional-grade technical analysis of Bitcoin.

---

Objectives

- Obtain official market data from Binance Spot.
- Generate an auditable market snapshot.
- Provide a single, reliable source of market data.
- Ensure reproducibility of every technical analysis.
- Serve as the future Data Feed module for the Crypto Pro Suite.

---

Primary Data Source

- Exchange: Binance Spot
- Trading Pair: BTC/USDT

Contingency Policy

Binance is always used as the primary source.

Only if Binance becomes unavailable will a secondary exchange be used.

Whenever this happens, the generated snapshot must explicitly record:

- the reason why Binance could not be used;
- the substitute exchange;
- the date and time of the occurrence.

---

Current Scope (Version 1.0)

The current version is intentionally minimal and supports only the requirements of the BTC PRO module.

Generated data include:

- Market Snapshot
- Current Price
- 24h High
- 24h Low
- 24h Volume
- Weekly Candles
- Daily Candles
- 4-Hour Candles

These data are sufficient to calculate the indicators used by BTC PRO.

---

Future Evolution

Future versions of the Data Feed will support:

- ETH
- SOL
- XRP
- Additional crypto assets
- Funding Rate
- Open Interest
- BTC Dominance
- Fear & Greed Index
- Stablecoin metrics
- Other market indicators required by the Crypto Pro Suite

---

Project Principles

This project follows four principles:

1. Simplicity
2. Reliability
3. Reproducibility
4. Modularity

The goal is to keep the Data Feed as small and reliable as possible while allowing the analytical modules to evolve independently.

---

Project Status

Current Version: Draft 0.1

Status: In development.
