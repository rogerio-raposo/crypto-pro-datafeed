# PCP-01 Experimental Data Feed

This directory contains experimental code used to validate the Ranking Institucional Simplificado PCP-01 data contract.

## Boundary

- does not replace `src/datafeed.py`;
- does not modify the stable v1.0.0 JSON contract;
- does not rank assets;
- does not calculate PEC, PR, E-states, Confidence, or Ranking Classes;
- must preserve provenance and distinguish source/API failures from economic market conditions.

## Technical probe

`binance_qps_probe.py` validates Binance Spot public market-data acquisition.

## Capacity dry-run

`pcp01_capacity_dry_run.py` qualifies the technical collection path. The controlled two-cycle workflow uses one run with an internal one-hour separation so GitHub scheduler latency cannot redefine the pre-registered adjacent-hour criterion.

## Official Capacity capture

Official PCP-01 capture remains inactive until a formal activation file is written after the UFT human gate.

The controlled official workflow is manually dispatched on the isolated PCP-01 branch and uses bounded sequential segments:

- events 00–04;
- events 05–09;
- events 10–14;
- events 15–19;
- events 20–23;
- exact seven-day turnover at T0.

`pcp01_capacity_capture_segment.py` waits for the frozen hourly targets inside each bounded job and rejects an event if the intended hour has been missed beyond the allowed lateness window. This avoids dependence on recurring GitHub cron timing for the official 24-hour capture window.

Raw capture remains producer-only evidence. Ranking methodology calculations remain downstream.
