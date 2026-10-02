# ASSET-P0 Synthetic Golden Fixture

**Status:** Experimental / Non-Normative  
**Experiment:** ASSET-P0-001  
**Fixture version:** ASSET-P0-SYNTHETIC-v0.1.0

## Purpose

Exercise producer-side validation and deterministic resampling without external data acquisition.

## Shape

- 48 expected one-hour slots across two UTC days.
- 47 native records.
- one deliberate missing interval;
- one deliberate extreme but OHLC-valid price observation;
- derived 4h and 1d outputs;
- checkpoint/restart timestamp used by the Suite replay regression.

## Frozen Expected Hashes

- `native.jsonl`: `09ca24c7bc6c7c08ec678b10e5c93817ba64d5cd3aef08e6fc122b6c9a838575`
- `derived_4h.jsonl`: `53c2e1a6166464df63ead361042399edf6bfbac956bf2b5a8cef4d4fd2370b7c`
- `derived_1d.jsonl`: `0bbb526838b76d1ab58ee17286d2067030861c3c9ff223dee6ce8570ecb54f18`

The canonical expectations are stored in `expected.json`.

## Important

This fixture is a deterministic implementation/regression artifact. Passing it does not mean P0 itself has passed.
