#!/usr/bin/env python3
"""Simulador IoT simples para o projeto Orbital Alert."""

from __future__ import annotations

import json
import os
import random
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

API_URL = os.getenv("API_URL", "http://localhost:8080").rstrip("/")
READINGS_ENDPOINT = f"{API_URL}/api/readings"
OFFLINE_FILE = Path(__file__).with_name("mock_readings.json")
INTERVAL_SECONDS = int(os.getenv("SIM_INTERVAL_SECONDS", "5"))

# IDs compatíveis com database/seed.sql (ids 1,2,4,5)
SENSORS = [
    {"sensor_id": 4, "type": "TEMPERATURE", "unit": "°C", "min": 18.0, "max": 46.0},
    {"sensor_id": 2, "type": "WATER_LEVEL", "unit": "%", "min": 20.0, "max": 98.0},
    {"sensor_id": 5, "type": "SMOKE", "unit": "índice", "min": 0.0, "max": 100.0},
    {"sensor_id": 1, "type": "RAINFALL", "unit": "mm", "min": 0.0, "max": 90.0},
]


def generate_reading(sensor: dict) -> dict:
    value = round(random.uniform(sensor["min"], sensor["max"]), 2)
    return {
        "sensor_id": sensor["sensor_id"],
        "sensor_type": sensor["type"],
        "value": value,
        "unit": sensor["unit"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def save_offline(reading: dict) -> None:
    data = []
    if OFFLINE_FILE.exists():
        try:
            data = json.loads(OFFLINE_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = []

    data.append(reading)
    OFFLINE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def send_to_api(reading: dict) -> bool:
    payload = {"sensorId": reading["sensor_id"], "value": reading["value"]}
    response = requests.post(READINGS_ENDPOINT, json=payload, timeout=5)
    response.raise_for_status()
    return True


def flush_offline_if_possible() -> None:
    if not OFFLINE_FILE.exists():
        return

    try:
        queued = json.loads(OFFLINE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print("[WARN] Arquivo offline inválido. Limpando conteúdo.")
        OFFLINE_FILE.write_text("[]", encoding="utf-8")
        return

    if not queued:
        return

    print(f"[INFO] Tentando reenviar {len(queued)} leitura(s) salvas offline...")
    pending = []
    for item in queued:
        try:
            send_to_api(item)
            print(f"[SYNC] OK sensor={item['sensor_id']} valor={item['value']}")
        except requests.RequestException:
            pending.append(item)
            print(f"[SYNC] Falha no reenvio sensor={item['sensor_id']} (mantido offline)")

    OFFLINE_FILE.write_text(json.dumps(pending, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    print("=" * 70)
    print("Orbital Alert - Simulador IoT")
    print(f"API URL: {API_URL}")
    print(f"Endpoint: {READINGS_ENDPOINT}")
    print(f"Intervalo: {INTERVAL_SECONDS}s")
    print("Pressione Ctrl+C para encerrar.")
    print("=" * 70)

    OFFLINE_FILE.write_text(OFFLINE_FILE.read_text(encoding="utf-8") if OFFLINE_FILE.exists() else "[]", encoding="utf-8")

    while True:
        flush_offline_if_possible()

        for sensor in SENSORS:
            reading = generate_reading(sensor)
            log = (
                f"[{datetime.now().strftime('%H:%M:%S')}] "
                f"{reading['sensor_type']:<11} sensor={reading['sensor_id']} "
                f"valor={reading['value']} {reading['unit']}"
            )

            try:
                send_to_api(reading)
                print(f"{log} -> enviado para API")
            except requests.RequestException as exc:
                save_offline(reading)
                print(f"{log} -> API offline, salvo em {OFFLINE_FILE.name} ({exc.__class__.__name__})")

        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Simulador encerrado pelo usuário.")
