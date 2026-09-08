#!/usr/bin/env python3
"""ETL da camada TRUSTED (Silver) para a camada CURATED (Gold) do Orbital Alert.

Agrupa as leituras confiaveis por regiao, calcula indicadores por tipo de sensor
e produz um score de risco deterministico de 0 a 100 com nivel LOW/MEDIUM/HIGH.
O resultado alimenta analytics e o endpoint de IA generativa
`GET /api/recommendations/regions/{regionId}`.

Uso:
    python etl/trusted_to_curated.py
    python etl/trusted_to_curated.py --regions data-lake/samples/regions.json
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TRUSTED_DIR = ROOT / "data-lake" / "trusted"
DEFAULT_CURATED_DIR = ROOT / "data-lake" / "curated"
DEFAULT_REGIONS_FILE = ROOT / "data-lake" / "samples" / "regions.json"

# Regras de risco por tipo de sensor.
# `limit`    : limiar de alerta - reproduz os mesmos valores do AlertService do
#              backend, para que o Data Lake e o motor operacional de alertas
#              contem a mesma historia. Atingir o limiar equivale a sub-score 100.
# `baseline` : valor considerado normal para a regiao. Equivale a sub-score 0.
# `direction`: "above" = risco cresce acima do limite (baseline < limit);
#              "below" = risco cresce abaixo do limite (baseline > limit).
RISK_RULES = {
    "WATER_LEVEL": {"baseline": 20.0, "limit": 80.0, "direction": "above", "risk_type": "FLOOD"},
    "RAINFALL": {"baseline": 0.0, "limit": 60.0, "direction": "above", "risk_type": "FLOOD"},
    "TEMPERATURE": {"baseline": 25.0, "limit": 40.0, "direction": "above", "risk_type": "FIRE"},
    "SMOKE": {"baseline": 10.0, "limit": 70.0, "direction": "above", "risk_type": "FIRE"},
    "HUMIDITY": {"baseline": 60.0, "limit": 30.0, "direction": "below", "risk_type": "FIRE"},
}

# Faixas de classificacao do score final.
LEVEL_HIGH = 70
LEVEL_MEDIUM = 40

# Peso do indicador dominante vs. media dos indicadores.
WEIGHT_MAX = 0.7
WEIGHT_MEAN = 0.3

# Bonus aplicado quando o indicador dominante esta em tendencia de alta.
TREND_BONUS = 10

REGION_CSV_COLUMNS = [
    "region_id",
    "region_name",
    "risk_score",
    "risk_level",
    "risk_type",
    "readings",
    "sensors",
    "window_start",
    "window_end",
    "dominant_sensor_type",
    "generated_at",
]

INDICATOR_CSV_COLUMNS = [
    "region_id",
    "region_name",
    "sensor_type",
    "unit",
    "samples",
    "avg_value",
    "min_value",
    "max_value",
    "last_value",
    "baseline",
    "threshold",
    "direction",
    "sub_score",
    "trend",
]


def iso_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def clamp(value, low, high):
    return max(low, min(high, value))


def load_trusted(trusted_dir):
    """Le a camada TRUSTED (prioriza JSONL; cai para CSV se necessario)."""
    jsonl_path = trusted_dir / "readings.jsonl"
    if jsonl_path.exists():
        events = []
        for line in jsonl_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                events.append(json.loads(line))
        return events, jsonl_path

    csv_path = trusted_dir / "readings.csv"
    if csv_path.exists():
        events = []
        with csv_path.open("r", encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                row["value"] = float(row["value"])
                row["sensor_id"] = int(row["sensor_id"])
                row["region_id"] = int(row["region_id"]) if row.get("region_id") else None
                events.append(row)
        return events, csv_path

    return [], None


def load_region_names(regions_file):
    if regions_file is None or not Path(regions_file).exists():
        return {}
    data = json.loads(Path(regions_file).read_text(encoding="utf-8"))
    return {str(key): str(value) for key, value in data.items()}


def compute_sub_score(sensor_type, avg_value):
    """Converte a media de um sensor em um sub-score 0..100.

    Regra deterministica, sem modelo estatistico nem machine learning:
    interpolacao linear entre o valor normal (baseline = 0) e o limiar de
    alerta do backend (limit = 100), com corte nas pontas.

        sub_score = 100 * (media - baseline) / (limit - baseline)
    """
    rule = RISK_RULES[sensor_type]
    span = rule["limit"] - rule["baseline"]
    if span == 0:
        return 0
    ratio = (avg_value - rule["baseline"]) / span
    return int(clamp(round(ratio * 100), 0, 100))


def compute_trend(values):
    """Compara a media da segunda metade com a da primeira metade da serie."""
    if len(values) < 2:
        return "INSUFFICIENT_DATA"
    half = len(values) // 2
    first = sum(values[:half]) / half if half else values[0]
    second = sum(values[half:]) / (len(values) - half)
    if first == 0:
        return "RISING" if second > 0 else "STABLE"
    change = (second - first) / abs(first)
    if change > 0.05:
        return "RISING"
    if change < -0.05:
        return "FALLING"
    return "STABLE"


def build_indicator(sensor_type, events):
    events = sorted(events, key=lambda e: e["measured_at"])
    values = [float(e["value"]) for e in events]
    avg_value = sum(values) / len(values)
    rule = RISK_RULES[sensor_type]

    # Umidade e um risco invertido: a tendencia relevante e a queda.
    raw_trend = compute_trend(values)
    if rule["direction"] == "below":
        if raw_trend == "RISING":
            trend = "FALLING"
        elif raw_trend == "FALLING":
            trend = "RISING"
        else:
            trend = raw_trend
    else:
        trend = raw_trend

    return {
        "sensorType": sensor_type,
        "unit": events[-1].get("unit") or "N/A",
        "samples": len(values),
        "avgValue": round(avg_value, 2),
        "minValue": round(min(values), 2),
        "maxValue": round(max(values), 2),
        "lastValue": round(values[-1], 2),
        "baseline": rule["baseline"],
        "threshold": rule["limit"],
        "direction": rule["direction"],
        "riskType": rule["risk_type"],
        "subScore": compute_sub_score(sensor_type, avg_value),
        # "RISING" aqui significa sempre "o risco esta aumentando".
        "trend": trend,
    }


def classify(score):
    if score >= LEVEL_HIGH:
        return "HIGH"
    if score >= LEVEL_MEDIUM:
        return "MEDIUM"
    return "LOW"


def build_region_risk(region_id, region_name, events, generated_at):
    by_type = {}
    for event in events:
        by_type.setdefault(event["sensor_type"], []).append(event)

    indicators = [
        build_indicator(sensor_type, type_events)
        for sensor_type, type_events in sorted(by_type.items())
        if sensor_type in RISK_RULES
    ]
    # Tipos sem regra de risco (ex.: PRESSURE) permanecem no TRUSTED, mas nao
    # entram no score - ficam registrados para rastreabilidade.
    ignored_types = sorted(t for t in by_type if t not in RISK_RULES)

    timestamps = sorted(e["measured_at"] for e in events)

    if not indicators:
        return {
            "regionId": region_id,
            "regionName": region_name,
            "riskScore": 0,
            "riskLevel": "LOW",
            "riskType": "NONE",
            "dominantSensorType": None,
            "readings": len(events),
            "sensors": len({e["sensor_id"] for e in events}),
            "windowStart": timestamps[0],
            "windowEnd": timestamps[-1],
            "indicators": [],
            "ignoredSensorTypes": ignored_types,
            "generatedAt": generated_at,
        }

    indicators.sort(key=lambda i: i["subScore"], reverse=True)
    dominant = indicators[0]
    sub_scores = [i["subScore"] for i in indicators]

    base = WEIGHT_MAX * max(sub_scores) + WEIGHT_MEAN * (sum(sub_scores) / len(sub_scores))
    bonus = TREND_BONUS if dominant["trend"] == "RISING" else 0
    score = int(clamp(round(base + bonus), 0, 100))
    level = classify(score)
    risk_type = dominant["riskType"] if level != "LOW" else "NONE"

    return {
        "regionId": region_id,
        "regionName": region_name,
        "riskScore": score,
        "riskLevel": level,
        "riskType": risk_type,
        "dominantSensorType": dominant["sensorType"],
        "readings": len(events),
        "sensors": len({e["sensor_id"] for e in events}),
        "windowStart": timestamps[0],
        "windowEnd": timestamps[-1],
        "indicators": indicators,
        "ignoredSensorTypes": ignored_types,
        "generatedAt": generated_at,
    }


def write_outputs(curated_dir, regions, stats):
    curated_dir.mkdir(parents=True, exist_ok=True)
    snapshot_day = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    payload = json.dumps(regions, ensure_ascii=False, indent=2)
    (curated_dir / "region_risk_latest.json").write_text(payload, encoding="utf-8")
    (curated_dir / ("region_risk_" + snapshot_day + ".json")).write_text(payload, encoding="utf-8")

    with (curated_dir / "region_risk_latest.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REGION_CSV_COLUMNS)
        writer.writeheader()
        for region in regions:
            writer.writerow(
                {
                    "region_id": region["regionId"],
                    "region_name": region["regionName"],
                    "risk_score": region["riskScore"],
                    "risk_level": region["riskLevel"],
                    "risk_type": region["riskType"],
                    "readings": region["readings"],
                    "sensors": region["sensors"],
                    "window_start": region["windowStart"],
                    "window_end": region["windowEnd"],
                    "dominant_sensor_type": region["dominantSensorType"],
                    "generated_at": region["generatedAt"],
                }
            )

    with (curated_dir / "indicators_latest.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=INDICATOR_CSV_COLUMNS)
        writer.writeheader()
        for region in regions:
            for indicator in region["indicators"]:
                writer.writerow(
                    {
                        "region_id": region["regionId"],
                        "region_name": region["regionName"],
                        "sensor_type": indicator["sensorType"],
                        "unit": indicator["unit"],
                        "samples": indicator["samples"],
                        "avg_value": indicator["avgValue"],
                        "min_value": indicator["minValue"],
                        "max_value": indicator["maxValue"],
                        "last_value": indicator["lastValue"],
                        "baseline": indicator["baseline"],
                        "threshold": indicator["threshold"],
                        "direction": indicator["direction"],
                        "sub_score": indicator["subScore"],
                        "trend": indicator["trend"],
                    }
                )

    (curated_dir / "_stats_latest.json").write_text(
        json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def parse_args():
    parser = argparse.ArgumentParser(description="ETL TRUSTED -> CURATED do Orbital Alert")
    parser.add_argument("--trusted-dir", default=str(DEFAULT_TRUSTED_DIR), help="Diretorio da camada TRUSTED")
    parser.add_argument("--curated-dir", default=str(DEFAULT_CURATED_DIR), help="Diretorio da camada CURATED")
    parser.add_argument("--regions", default=str(DEFAULT_REGIONS_FILE), help="JSON com regionId -> nome da regiao")
    return parser.parse_args()


def main():
    args = parse_args()
    trusted_dir = Path(args.trusted_dir).resolve()
    curated_dir = Path(args.curated_dir).resolve()

    print("=" * 62)
    print("Orbital Alert | ETL TRUSTED -> CURATED")
    print("=" * 62)
    print("TRUSTED: " + str(trusted_dir))
    print("CURATED: " + str(curated_dir))

    events, source_path = load_trusted(trusted_dir)
    if not events:
        print("\nAVISO: camada TRUSTED vazia ou inexistente.")
        print("Rode antes: python etl/raw_to_trusted.py --raw-dir data-lake/samples")
        return 0

    print("Origem : " + str(source_path))

    region_names = load_region_names(args.regions)
    generated_at = iso_now()

    grouped = {}
    without_region = 0
    for event in events:
        region_id = event.get("region_id")
        if region_id is None:
            without_region += 1
            continue
        grouped.setdefault(int(region_id), []).append(event)

    regions = []
    for region_id in sorted(grouped):
        name = region_names.get(str(region_id), "Regiao " + str(region_id))
        regions.append(build_region_risk(region_id, name, grouped[region_id], generated_at))

    regions.sort(key=lambda r: r["riskScore"], reverse=True)

    stats = {
        "layer": "CURATED",
        "generated_at": generated_at,
        "source": source_path.as_posix() if source_path else None,
        "events_read": len(events),
        "events_without_region": without_region,
        "regions_processed": len(regions),
        "regions_by_level": {},
        "scoring_rules": {
            "thresholds": RISK_RULES,
            "weight_max": WEIGHT_MAX,
            "weight_mean": WEIGHT_MEAN,
            "trend_bonus": TREND_BONUS,
            "level_high_min": LEVEL_HIGH,
            "level_medium_min": LEVEL_MEDIUM,
        },
    }
    for region in regions:
        level = region["riskLevel"]
        stats["regions_by_level"][level] = stats["regions_by_level"].get(level, 0) + 1

    write_outputs(curated_dir, regions, stats)

    print("\n--- Risco por regiao ---")
    print("{0:<4} {1:<30} {2:>6} {3:<8} {4:<8}".format("ID", "REGIAO", "SCORE", "NIVEL", "TIPO"))
    for region in regions:
        print(
            "{0:<4} {1:<30} {2:>6} {3:<8} {4:<8}".format(
                region["regionId"],
                region["regionName"][:30],
                region["riskScore"],
                region["riskLevel"],
                region["riskType"],
            )
        )

    print("\nEventos lidos            : {0}".format(len(events)))
    print("Eventos sem regionId     : {0}".format(without_region))
    print("Regioes processadas      : {0}".format(len(regions)))
    print("\nOK: camada CURATED atualizada.")
    print("Proximo passo: GET /api/recommendations/regions/{regionId}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
