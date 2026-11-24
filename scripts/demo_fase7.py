#!/usr/bin/env python3
"""Executa a PoC integrada com uma região nova e leituras IoT simuladas."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from uuid import uuid4

import requests


ROOT = Path(__file__).resolve().parents[1]


def api(base, path, payload=None):
    url = f"{base.rstrip('/')}/api/{path}"
    response = (requests.get(url, timeout=15) if payload is None
                else requests.post(url, json=payload, timeout=15, headers={
                    "Authorization": "Bearer " + os.environ.get("ORBITAL_ADMIN_TOKEN", ""),
                }))
    response.raise_for_status()
    return response.json()


def require(condition, description):
    if not condition:
        raise RuntimeError(description)


def python(*args, env=None):
    result = subprocess.run(
        [sys.executable, *map(str, args)], cwd=ROOT,
        env={**(env if env is not None else os.environ), "PYTHONIOENCODING": "utf-8"},
        text=True, encoding="utf-8", capture_output=True, check=False,
    )
    if result.stdout:
        print(result.stdout.rstrip(), file=sys.stderr)
    if result.stderr:
        print(result.stderr.rstrip(), file=sys.stderr)
    result.check_returncode()
    return result.stdout


def simulator(base, sensor_id, value, source):
    output = python(
        "iot-simulator/sensor_simulator.py", "--sensor-id", sensor_id, "--value", value, "--source", source,
        env={**os.environ, "API_URL": base},
    )
    prefix = "Resposta da API: "
    return next(json.loads(line[len(prefix):]) for line in output.splitlines() if line.startswith(prefix))


def etl(base, lake):
    with TemporaryDirectory(prefix="orbital-catalogo-") as tmp:
        names = Path(tmp) / "regions.json"
        regions = {str(region["id"]): region["name"] for region in api(base, "regions")}
        names.write_text(json.dumps(regions, ensure_ascii=False), encoding="utf-8")
        python("etl/raw_to_trusted.py", "--raw-dir", lake / "raw", "--trusted-dir", lake / "trusted")
        python("etl/trusted_to_curated.py", "--trusted-dir", lake / "trusted",
               "--curated-dir", lake / "curated", "--regions", names)


def json_lines(path):
    with path.open(encoding="utf-8") as records:
        for line in records:
            if line.strip():
                yield json.loads(line)


def scenario(base, browser_base, lake, skip_recommendation):
    run_id = uuid4().hex[:12]
    checks = []

    def check(condition, description):
        require(condition, description)
        checks.append(description)

    check(api(browser_base, "health")["status"] == "UP", "Health da API pelo endereço público do painel")
    name = f"AgroSmart · Demo {run_id}"
    region = api(base, "regions", {
        "name": name, "city": "São Paulo", "state": "SP", "latitude": -23.50,
        "longitude": -46.62, "satelliteRiskScore": 0, "riskLevel": "LOW",
    })
    region_id = region["id"]
    sensor = api(base, "sensors", {
        "regionId": region_id, "type": "RAINFALL", "status": "ACTIVE", "unit": "mm/h",
    })
    check(sensor["regionId"] == region_id and sensor["type"] == "RAINFALL", "Sensor RAINFALL cadastrado na região")

    def active_alerts():
        return [alert for alert in api(base, "alerts/active") if alert["regionId"] == region_id]

    def latest_reading():
        readings = [reading for reading in api(base, "readings/latest") if reading["sensorId"] == sensor["id"]]
        require(len(readings) == 1, "Leituras mais recentes devem retornar uma linha por sensor")
        return readings[0]

    source = f"IOT_SIMULATOR:{run_id}"
    normal = simulator(base, sensor["id"], 45, source)
    check(latest_reading()["id"] == normal["id"], "Leitura normal retornou pela consulta ao banco operacional")
    check(not active_alerts(), "Leitura abaixo de 60 não criou alerta ativo")
    critical = simulator(base, sensor["id"], 95, source)
    check(latest_reading()["id"] == critical["id"], "Nova leitura substituiu a anterior como mais recente")
    alerts = active_alerts()
    check(len(alerts) == 1 and alerts[0]["severity"] == "HIGH", "Limiar de chuva criou um alerta HIGH na região")

    raw = [event for path in (lake / "raw").rglob("*.jsonl")
           for event in json_lines(path) if event.get("source") == source]
    check({event["readingId"] for event in raw} == {normal["id"], critical["id"]}
          and len(raw) == 2
          and all(event["sensorId"] == sensor["id"] and event["regionId"] == region_id for event in raw),
          "Duas leituras operacionais encontradas no RAW por origem, leitura, sensor e região")

    etl(base, lake)
    raw_ids = {event["eventId"] for event in raw}
    trusted = [row for row in json_lines(lake / "trusted" / "readings.jsonl") if row["event_id"] in raw_ids]
    check(len(trusted) == 2 and {row["event_id"] for row in trusted} == raw_ids,
          "TRUSTED preservou os dois eventos RAW")
    snapshots = json.loads((lake / "curated" / "region_risk_latest.json").read_text(encoding="utf-8"))
    snapshot = next(record for record in snapshots if record["regionId"] == region_id)
    check(snapshot["regionName"] == name and snapshot["readings"] == 2
          and snapshot["riskType"] == "FLOOD" and 0 <= snapshot["riskScore"] <= 100
          and snapshot["indicators"][0]["sensorType"] == "RAINFALL", "CURATED calculou score e indicador de chuva para os dois eventos")

    dash_regions = api(browser_base, "regions")
    dash_sensors = api(browser_base, "sensors")
    dash_alerts = api(browser_base, "alerts/active")
    dash_readings = api(browser_base, "readings/latest")
    risk = next(item for item in api(browser_base, "risk") if item["context"]["regionId"] == region_id)
    check(any(item["id"] == region_id for item in dash_regions)
          and any(item["id"] == sensor["id"] for item in dash_sensors)
          and any(item["id"] == alerts[0]["id"] for item in dash_alerts)
          and any(item["id"] == critical["id"] for item in dash_readings),
          "Os endpoints consumidos pelo painel retornaram região, sensor, alerta e leitura")
    check(risk["dataSource"] == "CURATED_LAYER" and risk["context"]["riskScore"] == snapshot["riskScore"]
          and risk["context"]["indicators"] == snapshot["indicators"], "API do painel expôs score e indicadores do mesmo CURATED")

    recommendation = None
    if not skip_recommendation:
        recommendation = api(browser_base, f"recommendations/regions/{region_id}")
        check(recommendation["dataSource"] == "CURATED_LAYER" and bool(recommendation["aiMode"])
              and bool(recommendation["recommendation"]), "API retornou recomendação consultiva com origem e provedor")

    return {
        "runId": run_id, "finishedUtc": datetime.now(timezone.utc).isoformat(),
        "inputs": "leituras IoT simuladas enviadas pelo simulador por HTTP",
        "region": region, "sensor": sensor, "readings": [normal, critical], "alert": alerts[0],
        "raw": raw, "trusted": trusted, "risk": risk, "recommendation": recommendation, "checks": checks,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--etl-only", action="store_true", help="Reprocessar as camadas sem inserir dados simulados")
    parser.add_argument("--skip-recommendation", action="store_true", help="Não chamar o provedor de recomendações")
    args = parser.parse_args()
    base = os.environ.get("API_URL", "http://localhost:8080")
    browser_base = os.environ.get("BROWSER_API_URL", base)
    lake = Path(os.environ.get("DATA_LAKE_PATH", ROOT / "data-lake")).resolve()
    if args.etl_only:
        etl(base, lake)
    else:
        result = scenario(base, browser_base, lake, args.skip_recommendation)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (requests.RequestException, OSError, ValueError, RuntimeError,
            StopIteration, KeyError, subprocess.CalledProcessError) as error:
        print(f"Falha no cenário: {error or type(error).__name__}", file=sys.stderr)
        sys.exit(1)
