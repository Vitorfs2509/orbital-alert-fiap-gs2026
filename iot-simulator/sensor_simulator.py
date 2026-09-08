#!/usr/bin/env python3
"""Simulador IoT acadêmico para o projeto Orbital Alert."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

API_URL = os.getenv("API_URL", "http://localhost:8080").rstrip("/")
READINGS_ENDPOINT = f"{API_URL}/api/readings"
OFFLINE_FILE = Path(__file__).with_name("mock_readings.json")
# `source` identifica a origem do evento na camada RAW do Data Lake.
DEFAULT_SOURCE = "IOT_SIMULATOR"
DEFAULT_PAYLOAD = {"sensorId": 1, "value": 87.5, "source": DEFAULT_SOURCE}


def save_offline(payload: dict) -> None:
    data = []
    if OFFLINE_FILE.exists():
        try:
            data = json.loads(OFFLINE_FILE.read_text(encoding="utf-8"))
            if not isinstance(data, list):
                data = []
        except json.JSONDecodeError:
            data = []

    data.append({"payload": payload, "saved_at": datetime.now(timezone.utc).isoformat()})
    OFFLINE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def send_reading(payload: dict) -> None:
    print("API URL:", API_URL)
    print("Endpoint:", READINGS_ENDPOINT)
    print("Payload enviado:", json.dumps(payload, ensure_ascii=False))

    try:
        response = requests.post(READINGS_ENDPOINT, json=payload, timeout=5)
        print("Status HTTP:", response.status_code)

        if response.content:
            print("Resposta da API:", response.text)

        response.raise_for_status()

    except requests.HTTPError as exc:
        print("Erro HTTP:", exc)
        if hasattr(exc, "response") and exc.response is not None:
            print("Status code:", exc.response.status_code)
            print("Body da resposta:", exc.response.text)
        raise
    except requests.RequestException as exc:
        print("Erro ao chamar a API:", exc)
        save_offline(payload)
        print(f"Leitura salva em {OFFLINE_FILE.name} para análise posterior.")
        raise


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Simulador IoT acadêmico para Orbital Alert")
    parser.add_argument("--loop", action="store_true", help="Executa continuamente até Ctrl+C")
    parser.add_argument("--interval", type=float, default=5.0, help="Intervalo em segundos para enviar leituras em modo loop")
    parser.add_argument("--sensor-id", type=int, default=1, help="ID do sensor usado na leitura demo")
    parser.add_argument("--value", type=float, default=87.5, help="Valor enviado na leitura demo")
    parser.add_argument("--source", default=DEFAULT_SOURCE, help="Origem registrada na camada RAW do Data Lake")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = {"sensorId": args.sensor_id, "value": args.value, "source": args.source}

    if args.loop:
        print("Modo loop habilitado. Pressione Ctrl+C para encerrar.")
        if not OFFLINE_FILE.exists():
            OFFLINE_FILE.write_text("[]", encoding="utf-8")
        while True:
            try:
                send_reading(payload)
            except requests.RequestException:
                pass
            time.sleep(args.interval)
    else:
        if not OFFLINE_FILE.exists():
            OFFLINE_FILE.write_text("[]", encoding="utf-8")

        try:
            send_reading(payload)
        except requests.HTTPError:
            return 1
        except requests.RequestException:
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
