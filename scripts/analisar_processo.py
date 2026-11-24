#!/usr/bin/env python3
"""Exporta eventos reais de uma rodada e calcula variantes e tempos."""
import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime
import json
from pathlib import Path
from statistics import median

FIELDS = ("case_id", "event_id", "activity", "timestamp", "resource", "status",
          "reading_id", "sensor_id", "region_id", "batch_id", "alert_id", "source", "duration_ms")


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def time(event):
    timestamp = datetime.fromisoformat(event["timestamp"])
    if timestamp.utcoffset() is None or timestamp.utcoffset().total_seconds():
        raise ValueError("Todos os eventos devem estar em UTC")
    return timestamp


def csv_file(path, records):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)


def validate(records):
    ids = {record["event_id"] for record in records}
    if len(ids) != len(records):
        raise ValueError("event_id duplicado")
    for record in records:
        if not all(record.get(key) for key in ("event_id", "activity", "timestamp", "resource", "status")):
            raise ValueError("Evento sem campos obrigatórios")
        time(record)


def analyze(events_path, run, output):
    source = f"IOT_SIMULATOR:{run['runId']}"
    cases = defaultdict(list)
    for record in read_jsonl(events_path / "api.jsonl"):
        if record["source"] in {source, run["controlledError"]["source"]}:
            cases[record["case_id"]].append(record)
    links = [row for row in read_jsonl(events_path / "memberships.jsonl") if row["case_id"] in cases]
    batches_by_case = defaultdict(list)
    for row in sorted(links, key=time):
        if row["activity"] == "CURATED_PUBLISHED":
            batches_by_case[row["case_id"]].append(row["batch_id"])
    relevant_batches = set()
    for case, candidates in batches_by_case.items():
        selected = candidates[0]
        relevant_batches.add(selected)
        cases[case].extend(row for row in links if row["batch_id"] == selected and row["case_id"] == case)
    batches = [row for row in read_jsonl(events_path / "batches.jsonl") if row["batch_id"] in relevant_batches]

    variants = Counter()
    transitions = defaultdict(list)
    case_rows = []
    events = []
    for case_id, records in cases.items():
        records.sort(key=time)
        activities = tuple(record["activity"] for record in records)
        variants[activities] += 1
        events.extend(records)
        for left, right in zip(records, records[1:]):
            transitions[(left["activity"], right["activity"])].append((time(right) - time(left)).total_seconds() * 1000)
        case_rows.append({"caseId": case_id, "activities": activities, "endStatus": records[-1]["status"],
                          "elapsedMs": round((time(records[-1]) - time(records[0])).total_seconds() * 1000, 3)})

    validate(events + batches)
    tails = Counter(records[-1]["activity"] for records in cases.values())
    if len(cases) != 3 or tails != {"CURATED_PUBLISHED": 2, "READING_REJECTED": 1}:
        raise ValueError(f"Esperados dois casos concluídos e um rejeitado: {tails}")
    required_readings = {reading["id"] for reading in run["readings"]}
    if {row["reading_id"] for row in events if row["activity"] == "CURATED_PUBLISHED"} != required_readings:
        raise ValueError("Leituras publicadas não correspondem à execução")
    if [row["alert_id"] for row in events if row["activity"] == "ALERT_GENERATED"] != [run["alert"]["id"]]:
        raise ValueError("Alerta event log não corresponde à execução")

    summary = {
        "runId": run["runId"], "caseCount": len(cases), "eventCount": len(events), "batchEventCount": len(batches),
        "cases": case_rows, "variants": [{"path": list(path), "frequency": count} for path, count in variants.items()],
        "transitions": [{"from": left, "to": right, "observations": len(values),
                         "medianMs": round(median(values), 3), "observedMs": [round(value, 3) for value in values]}
                        for (left, right), values in transitions.items()],
        "methods": "Primeiro lote com CURATED por caso; tempos UTC de parede; eventos de lote separados.",
    }

    output.mkdir(parents=True, exist_ok=True)
    csv_file(output / "event_log.csv", sorted(events, key=time))
    csv_file(output / "batch_log.csv", sorted(batches, key=time))
    (output / "analise.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    nodes = sorted({node for edge in transitions for node in edge})
    names = {node: f"N{index}" for index, node in enumerate(nodes)}
    lines = ["flowchart LR", *(f'  {names[node]}["{node}"]' for node in nodes),
             *(f"  {names[left]} -->|{len(values)}| {names[right]}" for (left, right), values in transitions.items())]
    (output / "processo.mmd").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return summary


def plot(summary, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, (variants, delays) = plt.subplots(1, 2, figsize=(12.4, 4.5), width_ratios=[1, 2])
    names = ["Normal", "Com alerta", "Erro controlado"]
    counts = {}
    for variant in summary["variants"]:
        activities = variant["path"]
        name = "Erro controlado" if "READING_REJECTED" in activities else "Com alerta" if "ALERT_GENERATED" in activities else "Normal"
        counts[name] = variant["frequency"]
    bars = variants.barh(names, [counts.get(name, 0) for name in names], color=["#037f78", "#1156b8", "#bd6338"])
    variants.bar_label(bars)
    variants.set_xlim(0, 1.35)
    variants.set_xticks([0, 1])
    variants.set_title("Frequência por variante", loc="left")
    order = sorted(summary["transitions"], key=lambda row: row["medianMs"], reverse=True)
    positions = range(len(order))
    labels = [f"{row['from']}  →  {row['to']}" for row in order]
    bars = delays.barh(positions, [row["medianMs"] for row in order], color="#1156b8")
    delays.set_yticks(positions, labels, fontsize=7)
    delays.invert_yaxis()
    delays.bar_label(bars, fmt="%.2f", padding=3, fontsize=7)
    delays.margins(x=0.17)
    delays.set_xlabel("Mediana observada (ms)")
    delays.set_title("Tempo entre eventos", loc="left")
    fig.suptitle(f"Orbital Alert · Amostra controlada de {summary['caseCount']} casos", x=0.06, ha="left", weight="bold")
    for axes in (variants, delays):
        axes.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(rect=(0.04, 0.04, 0.97, 0.94), w_pad=3)
    for extension in ("png", "svg"):
        artifact = output / f"variantes-tempos.{extension}"
        fig.savefig(artifact, dpi=170)
        if extension == "svg":
            artifact.write_text("\n".join(line.rstrip() for line in artifact.read_text(encoding="utf-8").splitlines())
                                + "\n", encoding="utf-8")
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("eventos", type=Path)
    parser.add_argument("demo", type=Path)
    parser.add_argument("saida", type=Path)
    parser.add_argument("--graficos", action="store_true")
    args = parser.parse_args()
    run = json.loads(args.demo.read_text(encoding="utf-8-sig"))
    result = analyze(args.eventos, run, args.saida)
    if args.graficos:
        plot(result, args.saida)
    print(json.dumps({key: result[key] for key in ("runId", "caseCount", "eventCount", "batchEventCount")}))
