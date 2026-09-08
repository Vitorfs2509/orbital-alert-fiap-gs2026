#!/usr/bin/env python3
"""ETL da camada RAW (Bronze) para a camada TRUSTED (Silver) do Orbital Alert.

Le os eventos brutos gravados pela API Spring Boot, aplica regras simples de
qualidade de dados (validacao, deduplicacao, padronizacao de timestamps) e
grava um conjunto confiavel em `data-lake/trusted/`.

Uso:
    python etl/raw_to_trusted.py
    python etl/raw_to_trusted.py --raw-dir data-lake/samples
    python etl/raw_to_trusted.py --date 2026-09-08
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RAW_DIR = ROOT / "data-lake" / "raw"
DEFAULT_TRUSTED_DIR = ROOT / "data-lake" / "trusted"

# Campos obrigatorios para um evento ser considerado confiavel.
REQUIRED_FIELDS = ("sensorId", "value", "measuredAt")

# Nomes alternativos aceitos para o mesmo tipo de sensor.
# O schema do banco usa RAIN e o enum Java usa RAINFALL: padronizamos em RAINFALL.
SENSOR_TYPE_ALIASES = {
    "RAIN": "RAINFALL",
    "RAINFALL": "RAINFALL",
    "WATER_LEVEL": "WATER_LEVEL",
    "WATERLEVEL": "WATER_LEVEL",
    "TEMPERATURE": "TEMPERATURE",
    "TEMP": "TEMPERATURE",
    "SMOKE": "SMOKE",
    "HUMIDITY": "HUMIDITY",
}

# Unidade padrao quando o evento bruto chega sem `unit`.
DEFAULT_UNITS = {
    "RAINFALL": "mm/h",
    "WATER_LEVEL": "cm",
    "TEMPERATURE": "C",
    "SMOKE": "ppm",
    "HUMIDITY": "%",
}

# Faixa fisica plausivel para qualquer leitura ambiental do MVP.
VALUE_MIN = -100.0
VALUE_MAX = 10000.0

# Arquivos de apoio que convivem com os eventos no Data Lake mas nao sao leituras.
# Tambem sao ignorados todos os arquivos iniciados por "_" (metadados/qualidade).
REFERENCE_FILENAMES = {"regions.json"}

CSV_COLUMNS = [
    "event_id",
    "sensor_id",
    "region_id",
    "sensor_type",
    "value",
    "unit",
    "measured_at",
    "received_at",
    "source",
    "source_file",
    "ingested_at",
]


def iso_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def to_snake(name):
    out = []
    for char in name:
        if char.isupper():
            out.append("_")
            out.append(char.lower())
        else:
            out.append(char)
    return "".join(out)


def bump(counter, key):
    counter[key] = counter.get(key, 0) + 1


def normalize_timestamp(raw_value):
    """Padroniza um timestamp para ISO-8601 UTC (YYYY-MM-DDTHH:MM:SSZ).

    O backend grava LocalDateTime (sem fuso). Timestamps sem fuso sao
    interpretados como UTC - regra unica, documentada em docs/data-maintenance.md.
    """
    if raw_value is None:
        return None
    text = str(raw_value).strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def iter_raw_files(raw_dir, date_filter):
    """Percorre o particionamento raw/YYYY/MM/DD/ e devolve os arquivos."""
    if not raw_dir.exists():
        return []
    files = sorted(
        p
        for p in raw_dir.rglob("*")
        if p.is_file()
        and p.suffix.lower() in (".jsonl", ".json")
        and not p.name.startswith("_")
        and p.name not in REFERENCE_FILENAMES
    )
    if date_filter:
        partition = date_filter.replace("-", "/")
        files = [p for p in files if partition in p.as_posix() or date_filter in p.name]
    return files


def iter_raw_records(path):
    """Le tanto JSON Lines (formato da API) quanto array JSON (arquivos de apoio)."""
    text = path.read_text(encoding="utf-8-sig").strip()
    if not text:
        return
    if text.startswith("["):
        try:
            for item in json.loads(text):
                yield item, None
        except json.JSONDecodeError as exc:
            yield None, "json_array_invalido: " + str(exc)
        return
    for line_no, line in enumerate(text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            yield json.loads(line), None
        except json.JSONDecodeError as exc:
            yield None, "linha {0}: json_invalido: {1}".format(line_no, exc)


def validate(record):
    """Valida e padroniza um evento bruto.

    Devolve (evento_limpo, None) em caso de sucesso ou (None, motivo).
    """
    for field in REQUIRED_FIELDS:
        if record.get(field) is None:
            return None, "missing_" + to_snake(field)

    try:
        sensor_id = int(record["sensorId"])
    except (TypeError, ValueError):
        return None, "invalid_sensor_id"

    try:
        value = float(record["value"])
    except (TypeError, ValueError):
        return None, "invalid_value"

    if value != value:  # NaN
        return None, "invalid_value"

    if not (VALUE_MIN <= value <= VALUE_MAX):
        return None, "value_out_of_range"

    measured_at = normalize_timestamp(record.get("measuredAt"))
    if measured_at is None:
        return None, "invalid_measured_at"

    region_id = record.get("regionId")
    if region_id is not None:
        try:
            region_id = int(region_id)
        except (TypeError, ValueError):
            return None, "invalid_region_id"

    raw_type = str(record.get("sensorType") or "").strip().upper()
    sensor_type = SENSOR_TYPE_ALIASES.get(raw_type, raw_type or "UNKNOWN")

    unit = record.get("unit") or DEFAULT_UNITS.get(sensor_type) or "N/A"
    received_at = normalize_timestamp(record.get("receivedAt")) or measured_at

    clean = {
        "event_id": record.get("eventId"),
        "sensor_id": sensor_id,
        "region_id": region_id,
        "sensor_type": sensor_type,
        "value": round(value, 4),
        "unit": str(unit),
        "measured_at": measured_at,
        "received_at": received_at,
        "source": record.get("source") or "UNKNOWN",
    }
    return clean, None


def technical_key(event):
    """Chave tecnica: o eventId gerado pela API, quando presente."""
    if event.get("event_id"):
        return ("event_id", event["event_id"])
    return None


def business_key(event):
    """Chave de negocio: mesmo sensor, mesmo instante, mesmo valor."""
    return (event["sensor_id"], event["measured_at"], event["value"])


def process(raw_dir, trusted_dir, date_filter):
    started_at = iso_now()
    files = iter_raw_files(raw_dir, date_filter)

    accepted = []
    rejected = []
    seen_technical = set()
    seen_business = set()

    stats = {
        "files_read": len(files),
        "records_read": 0,
        "records_valid": 0,
        "records_rejected": 0,
        "duplicates_technical": 0,
        "duplicates_business": 0,
        "rejected_by_reason": {},
        "records_by_sensor_type": {},
        "records_by_region": {},
    }

    for path in files:
        try:
            rel_path = path.relative_to(ROOT).as_posix()
        except ValueError:
            rel_path = path.as_posix()

        for record, parse_error in iter_raw_records(path):
            stats["records_read"] += 1

            if parse_error is not None:
                bump(stats["rejected_by_reason"], "unparseable_line")
                rejected.append({"source_file": rel_path, "reason": "unparseable_line", "detail": parse_error})
                continue

            if not isinstance(record, dict):
                bump(stats["rejected_by_reason"], "not_an_object")
                rejected.append({"source_file": rel_path, "reason": "not_an_object", "raw": str(record)[:200]})
                continue

            event, reason = validate(record)
            if reason is not None:
                bump(stats["rejected_by_reason"], reason)
                rejected.append({"source_file": rel_path, "reason": reason, "raw": record})
                continue

            tech_key = technical_key(event)
            if tech_key is not None and tech_key in seen_technical:
                stats["duplicates_technical"] += 1
                bump(stats["rejected_by_reason"], "duplicate_event_id")
                rejected.append({"source_file": rel_path, "reason": "duplicate_event_id", "raw": record})
                continue

            biz_key = business_key(event)
            if biz_key in seen_business:
                stats["duplicates_business"] += 1
                bump(stats["rejected_by_reason"], "duplicate_business_key")
                rejected.append({"source_file": rel_path, "reason": "duplicate_business_key", "raw": record})
                continue

            if tech_key is not None:
                seen_technical.add(tech_key)
            seen_business.add(biz_key)

            event["source_file"] = rel_path
            event["ingested_at"] = started_at
            accepted.append(event)

            bump(stats["records_by_sensor_type"], event["sensor_type"])
            bump(stats["records_by_region"], str(event["region_id"]))

    accepted.sort(key=lambda e: (e["measured_at"], e["sensor_id"]))
    stats["records_valid"] = len(accepted)
    stats["records_rejected"] = len(rejected)

    write_outputs(trusted_dir, accepted, rejected, stats, started_at)
    return stats


def write_outputs(trusted_dir, accepted, rejected, stats, started_at):
    quality_dir = trusted_dir / "_quality"
    trusted_dir.mkdir(parents=True, exist_ok=True)
    quality_dir.mkdir(parents=True, exist_ok=True)

    run_id = started_at.replace(":", "").replace("-", "")

    jsonl_path = trusted_dir / "readings.jsonl"
    with jsonl_path.open("w", encoding="utf-8", newline="\n") as handle:
        for event in accepted:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")

    csv_path = trusted_dir / "readings.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for event in accepted:
            writer.writerow({column: event.get(column) for column in CSV_COLUMNS})

    rejected_path = quality_dir / ("rejected_" + run_id + ".jsonl")
    with rejected_path.open("w", encoding="utf-8", newline="\n") as handle:
        for item in rejected:
            handle.write(json.dumps(item, ensure_ascii=False, default=str) + "\n")

    stats_payload = {"layer": "TRUSTED", "run_id": run_id, "started_at": started_at}
    stats_payload.update(stats)
    stats_payload["finished_at"] = iso_now()
    stats_payload["acceptance_rate_pct"] = (
        round(100.0 * stats["records_valid"] / stats["records_read"], 2) if stats["records_read"] else 0.0
    )
    stats_payload["outputs"] = {
        "readings_jsonl": jsonl_path.as_posix(),
        "readings_csv": csv_path.as_posix(),
        "rejected_jsonl": rejected_path.as_posix(),
    }

    payload_text = json.dumps(stats_payload, ensure_ascii=False, indent=2)
    (quality_dir / ("stats_" + run_id + ".json")).write_text(payload_text, encoding="utf-8")
    (trusted_dir / "_stats_latest.json").write_text(payload_text, encoding="utf-8")


def parse_args():
    parser = argparse.ArgumentParser(description="ETL RAW -> TRUSTED do Orbital Alert")
    parser.add_argument("--raw-dir", default=str(DEFAULT_RAW_DIR), help="Diretorio da camada RAW")
    parser.add_argument("--trusted-dir", default=str(DEFAULT_TRUSTED_DIR), help="Diretorio da camada TRUSTED")
    parser.add_argument("--date", default=None, help="Filtra uma particao especifica (YYYY-MM-DD)")
    return parser.parse_args()


def main():
    args = parse_args()
    raw_dir = Path(args.raw_dir).resolve()
    trusted_dir = Path(args.trusted_dir).resolve()

    print("=" * 62)
    print("Orbital Alert | ETL RAW -> TRUSTED")
    print("=" * 62)
    print("RAW    : " + str(raw_dir))
    print("TRUSTED: " + str(trusted_dir))

    if not raw_dir.exists():
        print("\nERRO: diretorio RAW nao encontrado: " + str(raw_dir))
        return 1

    stats = process(raw_dir, trusted_dir, args.date)

    if stats["records_read"] == 0:
        print("\nAVISO: nenhum evento encontrado na camada RAW.")
        print("Rode o simulador IoT com a API no ar ou use --raw-dir data-lake/samples")
        return 0

    print("\n--- Estatisticas de processamento ---")
    print("Arquivos lidos          : {0}".format(stats["files_read"]))
    print("Eventos lidos           : {0}".format(stats["records_read"]))
    print("Eventos validos         : {0}".format(stats["records_valid"]))
    print("Eventos rejeitados      : {0}".format(stats["records_rejected"]))
    print("  duplicatas tecnicas   : {0}".format(stats["duplicates_technical"]))
    print("  duplicatas de negocio : {0}".format(stats["duplicates_business"]))

    if stats["rejected_by_reason"]:
        print("\nRejeicoes por motivo:")
        for reason, count in sorted(stats["rejected_by_reason"].items()):
            print("  - {0}: {1}".format(reason, count))

    if stats["records_by_sensor_type"]:
        print("\nEventos validos por tipo de sensor:")
        for sensor_type, count in sorted(stats["records_by_sensor_type"].items()):
            print("  - {0}: {1}".format(sensor_type, count))

    print("\nOK: camada TRUSTED atualizada.")
    print("Proximo passo: python etl/trusted_to_curated.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
