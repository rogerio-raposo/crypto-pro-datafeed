# Crypto Pro Data Feed — Technical Specification

**Document version:** Draft 0.1  
**Schema version:** 0.1  
**Status:** Under review

---

## 1. Purpose

This document defines the technical contract of the Crypto Pro Data Feed MVP.

The Data Feed collects public market data from Binance Spot and produces an auditable JSON snapshot for the BTC PRO analytical module.

The implementation must conform to this specification.

---

## 2. Scope

The MVP supports only:

- Exchange: Binance Spot
- Symbol: BTCUSDT
- Market type: Spot
- Timeframes:
  - 4 hours
  - 1 day
  - 1 week

The MVP does not support:

- other crypto assets;
- derivatives data;
- funding rates;
- open interest;
- automatic fallback exchanges;
- databases;
- authenticated API endpoints.

---

## 3. Architecture

The MVP follows this flow:

```text
Binance public REST API
        ↓
    datafeed.py
        ↓
   snapshot.json
        ↓
 GitHub repository
        ↓
      BTC PRO
