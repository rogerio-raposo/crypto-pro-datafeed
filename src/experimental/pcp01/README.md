# PCP-01 Experimental Data Feed

This directory contains experimental code used to validate the Ranking Institucional Simplificado PCP-01 data contract.

## Boundary

- does not replace `src/datafeed.py`;
- does not modify the stable v1.0.0 JSON contract;
- does not rank assets;
- does not calculate PEC, PR, E-states, Confidence, or Ranking Classes;
- must preserve provenance and distinguish source/API failures from economic market conditions.

## First probe

`binance_qps_probe.py` validates the first adapter path using Binance Spot public market data.

Example:

```bash
python src/experimental/pcp01/binance_qps_probe.py \
  --symbol BTCUSDT \
  --depth-limit 1000 \
  --output data/experimental/pcp-01/dry-run/binance-btcusdt.json
```

This is a technical probe only. A successful result does not activate UFT/T0.
