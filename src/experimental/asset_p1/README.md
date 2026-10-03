# Asset PRO P1 — Experimental Producer Source

**Status:** Draft / Experimental / Non-Normative

This directory is reserved for ASSET-P1-D1-001 producer-side code.

P1 code will generalize the validated P0 producer contract to multiple instruments and segment datasets.

It must not mutate or reinterpret frozen `asset_p0` code.

Planned responsibilities:

- parameterized Binance Spot monthly archive acquisition;
- checksum verification;
- generic instrument metadata;
- canonical 1h normalization;
- deterministic 4h / 1d resampling;
- per-asset/per-segment Dataset Manifest generation;
- Holdout access segregation.

No P1 implementation has been frozen.
