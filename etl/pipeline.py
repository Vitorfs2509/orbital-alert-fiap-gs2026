#!/usr/bin/env python3
"""Orquestra os ETLs sob uma trava compartilhada entre jobs Compose."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import NamedTemporaryFile, TemporaryDirectory
import time
from urllib.request import urlopen
from uuid import uuid4
from process_events import event, membership, write_events

BASE = Path(__file__).resolve().parent


def utc():
    return datetime.now(timezone.utc).isoformat()


def log(record):
    print(json.dumps(record, ensure_ascii=False), flush=True)


def atomic_json(path, record):
    with NamedTemporaryFile(dir=path.parent, mode="w", encoding="utf-8", delete=False) as temp:
        json.dump(record, temp, ensure_ascii=False)
    try:
        Path(temp.name).replace(path)
    finally:
        Path(temp.name).unlink(missing_ok=True)


def acquire(lock, wait_seconds):
    import fcntl

    deadline = time.monotonic() + wait_seconds
    while True:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except BlockingIOError:
            if time.monotonic() >= deadline:
                return False
            time.sleep(0.2)


def catalog(api, directory):
    with urlopen(api.rstrip("/") + "/api/regions", timeout=15) as response:
        regions = json.load(response)
    path = directory / "regions.json"
    path.write_text(json.dumps({str(r["id"]): r["name"] for r in regions}, ensure_ascii=False), encoding="utf-8")
    return path


def execute(script, *arguments):
    outcome = subprocess.run([sys.executable, str(BASE / script), *map(str, arguments)], check=False,
                             timeout=120, capture_output=True, text=True, encoding="utf-8",
                             env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    if outcome.returncode:
        raise RuntimeError(f"{script} exit {outcome.returncode}: {outcome.stderr[-300:].strip()}")


def run_locked(lake, api, raw, lock_wait):
    control = lake / "control"
    control.mkdir(parents=True, exist_ok=True)
    with (control / "etl.lock").open("a") as lock:
        if not acquire(lock, lock_wait):
            log({"activity": "etl_lock", "status": "SKIPPED_LOCKED", "timestamp": utc()})
            return 2
        return run_batch(lake, api, raw, control / "etl-status.json")


def run_batch(lake, api, raw, status_path):
    previous = json.loads(status_path.read_text(encoding="utf-8")) if status_path.is_file() else {}
    attempt = {"batchId": str(uuid4()), "startedAt": utc(), "status": "RUNNING"}
    started = time.monotonic()
    atomic_json(status_path, {"status": "RUNNING", "lastAttempt": attempt, "lastSuccess": previous.get("lastSuccess")})
    log({"activity": "etl_batch_start", **attempt})
    write_events(lake, "batches", [event("BATCH_STARTED", "RUNNING", attempt["batchId"])])
    try:
        if not raw.is_dir():
            raise FileNotFoundError("Diretório RAW ausente")
        if not any(raw.rglob("*.jsonl")):
            attempt["status"] = "NO_INPUT"
        else:
            with TemporaryDirectory(prefix="orbital-catalog-") as tmp:
                names = catalog(api, Path(tmp))
                execute("raw_to_trusted.py", "--raw-dir", raw, "--trusted-dir", lake / "trusted")
                with (lake / "trusted/readings.jsonl").open(encoding="utf-8") as trusted:
                    rows = [json.loads(line) for line in trusted if line.strip()]
                membership(lake, rows, attempt["batchId"], "TRUSTED_INCLUDED")
                execute("trusted_to_curated.py", "--trusted-dir", lake / "trusted",
                        "--curated-dir", lake / "curated", "--regions", names)
            quality = json.loads((lake / "trusted/_stats_latest.json").read_text(encoding="utf-8"))
            snapshot = json.loads((lake / "curated/region_risk_latest.json").read_text(encoding="utf-8"))
            published = {region["regionId"] for region in snapshot}
            membership(lake, (row for row in rows if row["region_id"] in published),
                       attempt["batchId"], "CURATED_PUBLISHED")
            attempt.update(status="SUCCESS", quality=quality, regions=len(snapshot))
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
        attempt.update(status="FAILED", error=str(error))
    attempt.update(finishedAt=utc(), durationMs=round((time.monotonic() - started) * 1000, 3))
    last_success = attempt if attempt["status"] == "SUCCESS" else previous.get("lastSuccess")
    atomic_json(status_path, {"status": attempt["status"], "lastAttempt": attempt, "lastSuccess": last_success})
    write_events(lake, "batches", [event("BATCH_FINISHED", attempt["status"], attempt["batchId"],
                                         duration_ms=attempt["durationMs"])])
    log({"activity": "etl_batch_end", **attempt})
    return 1 if attempt["status"] == "FAILED" else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--periodic", action="store_true")
    parser.add_argument("--healthcheck", action="store_true")
    parser.add_argument("--raw-dir", type=Path)
    parser.add_argument("--lock-wait", type=float, default=60)
    args = parser.parse_args()
    lake = Path(os.getenv("DATA_LAKE_PATH", str(BASE.parent / "data-lake"))).resolve()
    api = os.getenv("API_URL", "http://localhost:8080")
    raw = args.raw_dir or lake / "raw"
    interval = int(os.getenv("ETL_INTERVAL_SECONDS", "300"))
    if interval < 1:
        parser.error("ETL_INTERVAL_SECONDS deve ser positivo")
    heartbeat = lake / "control/scheduler.heartbeat"
    if args.healthcheck:
        return 0 if heartbeat.is_file() and time.time() - heartbeat.stat().st_mtime <= interval * 2 + 250 else 1
    if not args.periodic:
        return run_locked(lake, api, raw, args.lock_wait)
    heartbeat.parent.mkdir(parents=True, exist_ok=True)
    log({"activity": "etl_scheduler_start", "intervalSeconds": interval, "timestamp": utc()})
    while True:
        heartbeat.touch()
        time.sleep(interval)
        if raw.exists():
            run_locked(lake, api, raw, 0)


if __name__ == "__main__":
    sys.exit(main())
