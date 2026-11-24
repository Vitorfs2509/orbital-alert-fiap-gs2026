"""Registra fatos processuais do ETL e a associação independente ao lote."""
from datetime import datetime, timezone
import json
from uuid import uuid4


def write_events(lake, stream, records):
    folder = lake / "events"
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / f"{stream}.jsonl").open("a", encoding="utf-8") as target:
        for record in records:
            target.write(json.dumps(record, ensure_ascii=False) + "\n")


def event(activity, status, batch_id, **links):
    return {
        "event_id": str(uuid4()), "activity": activity, "status": status, "batch_id": batch_id,
        "timestamp": datetime.now(timezone.utc).isoformat(), "resource": "python-etl", **links,
    }


def membership(lake, rows, batch_id, activity):
    write_events(lake, "memberships", (
        event(activity, "SUCCESS", batch_id, case_id=row["case_id"],
              sensor_id=row["sensor_id"], region_id=row["region_id"],
              reading_id=row["reading_id"], source=row["source"])
        for row in rows if row.get("case_id")
    ))
