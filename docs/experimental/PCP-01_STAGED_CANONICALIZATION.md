# PCP-01 — Staged Canonicalization Note

For Pilot 01, full cryptographic/economic identity resolution is not performed for every Binance base symbol before discovery.

The operational sequence is:

1. build a **provisional market universe** from venue-native base symbols;
2. perform Flow Vector discovery against that universe;
3. for assets that become discovery candidates, resolve full canonical identity before Current Admission;
4. unresolved identity produces CA-IND / Eligibility IND rather than silent symbol matching.

This does not relax the rule that ticker alone is insufficient for formal assessment. It only avoids performing expensive full canonicalization for thousands of market symbols that never become candidates.
