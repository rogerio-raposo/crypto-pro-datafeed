#!/usr/bin/env python3
"""Diagnose ASSET-P1 source continuity without mutating or interpolating data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from build_datasets import ASSETS, SEGMENTS, months_between
from p1_data import (
    fetch_verified_archive,
    iso_to_us,
    parse_binance_zip,
    validate_native_hourly,
)


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--cache",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()

    rows=[]
    for phase,segment,start,end in SEGMENTS:
        for instrument in ASSETS:
            version=f"DIAGNOSTIC-{instrument}-{segment}"
            candles=[]
            archives=[]
            for ym in months_between(start,end):
                archive,prov=fetch_verified_archive(instrument,ym,args.cache)
                candles.extend(parse_binance_zip(
                    archive,
                    instrument=instrument,
                    dataset_version=version,
                    source_timestamp_unit="ms",
                ))
                archives.append(prov)
            result=validate_native_hourly(
                candles,
                expected_start_us=iso_to_us(start),
                expected_end_us=iso_to_us(end),
            )
            rows.append({
                "phase":phase,
                "segment_id":segment,
                "instrument":instrument,
                "native_records":len(result.candles),
                "missing_count":len(result.missing_open_times_us),
                "missing_open_times_us":result.missing_open_times_us,
                "duplicate_count":len(result.duplicate_open_times_us),
                "duplicate_open_times_us":result.duplicate_open_times_us,
                "critical_errors":result.critical_errors,
                "archive_count":len(archives),
            })

    report={
        "experiment_id":"ASSET-P1-D1-001",
        "dataset_cells":len(rows),
        "cells_with_missing":sum(bool(r["missing_count"]) for r in rows),
        "cells_with_duplicates":sum(bool(r["duplicate_count"]) for r in rows),
        "rows":rows,
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "dataset_cells":report["dataset_cells"],
        "cells_with_missing":report["cells_with_missing"],
        "cells_with_duplicates":report["cells_with_duplicates"],
        "summary":[
            {
                "segment_id":r["segment_id"],
                "instrument":r["instrument"],
                "missing_count":r["missing_count"],
                "missing_open_times_us":r["missing_open_times_us"],
                "duplicate_count":r["duplicate_count"],
            }
            for r in rows if r["missing_count"] or r["duplicate_count"]
        ],
    },indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
