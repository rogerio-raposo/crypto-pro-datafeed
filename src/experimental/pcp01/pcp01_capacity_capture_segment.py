#!/usr/bin/env python3
"""Controlled segment runner for PCP-01 official Capacity capture.

Runs a bounded range of hourly capture events against the frozen activation
schedule. It does not calculate PEC, PR, Capacity states, Confidence, or
Ranking outputs.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def validate_activation(activation: dict) -> tuple[datetime, datetime]:
    if not activation.get("active"):
        raise SystemExit("Activation is not active.")

    required = ("run_id", "uft_utc", "capture_start_utc", "t0_utc", "horizon_end_utc")
    missing = [key for key in required if not activation.get(key)]
    if missing:
        raise SystemExit(f"Activation missing required fields: {missing}")

    qevs = activation.get("qevs")
    if not isinstance(qevs, list) or len(qevs) != 9:
        raise SystemExit(f"Expected 9 frozen QEVs, received {0 if not isinstance(qevs, list) else len(qevs)}.")

    capture_start = parse_iso(activation["capture_start_utc"])
    t0 = parse_iso(activation["t0_utc"])
    if t0 - capture_start != timedelta(hours=24):
        raise SystemExit("T0 must equal Capture Start + 24h.")

    return capture_start, t0


def wait_until(target: datetime, max_lateness_seconds: int) -> None:
    now = utc_now()
    lateness = (now - target).total_seconds()

    if lateness > max_lateness_seconds:
        raise SystemExit(
            f"Target missed by {lateness:.1f}s; maximum allowed lateness is "
            f"{max_lateness_seconds}s."
        )

    if now < target:
        wait_seconds = (target - now).total_seconds()
        print(json.dumps({
            "status": "WAITING",
            "target_utc": target.isoformat(),
            "wait_seconds": round(wait_seconds, 3),
        }))
        time.sleep(wait_seconds)


def run_capture(activation_path: Path, output_root: Path, expected_index: int) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).with_name("pcp01_capacity_capture.py")),
            "--activation",
            str(activation_path),
            "--output-root",
            str(output_root),
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="")
    if result.returncode != 0:
        raise SystemExit(result.returncode)

    run_id = json.loads(activation_path.read_text(encoding="utf-8"))["run_id"]
    expected_path = output_root / run_id / f"event-{expected_index:02d}.json.gz"
    if not expected_path.exists():
        raise SystemExit(
            f"Expected capture event {expected_index:02d} was not persisted: {expected_path}"
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--activation", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--start-index", type=int, required=True)
    parser.add_argument("--end-index", type=int, required=True)
    parser.add_argument("--offset-seconds", type=int, default=10)
    parser.add_argument("--max-lateness-seconds", type=int, default=3300)
    args = parser.parse_args()

    if not 0 <= args.start_index <= args.end_index <= 23:
        raise SystemExit("Event index range must satisfy 0 <= start <= end <= 23.")

    activation = json.loads(args.activation.read_text(encoding="utf-8"))
    capture_start, _ = validate_activation(activation)

    for event_index in range(args.start_index, args.end_index + 1):
        target = capture_start + timedelta(hours=event_index, seconds=args.offset_seconds)
        print(json.dumps({
            "status": "TARGET",
            "event_index": event_index,
            "target_utc": target.isoformat(),
        }))
        wait_until(target, args.max_lateness_seconds)
        run_capture(args.activation, args.output_root, event_index)

    print(json.dumps({
        "status": "SEGMENT_COMPLETE",
        "start_index": args.start_index,
        "end_index": args.end_index,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
