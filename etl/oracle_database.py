#!/usr/bin/env python3
"""Persistencia analitica da camada CURATED no Oracle AI Database Free.

Este modulo contem apenas a logica reutilizavel (configuracao, leitura do
CURATED, mapeamento de colunas e SQL). O ponto de entrada de linha de comando
fica em `etl/sync_curated_to_oracle.py`.

Principios:

* o Oracle NAO substitui o banco operacional (H2 / PostgreSQL). Ele recebe
  apenas o resultado analitico da camada CURATED, em paralelo ao pipeline;
* nenhuma credencial no codigo - host, porta, service, usuario e senha vem de
  variaveis de ambiente;
* o driver `oracledb` e uma dependencia OPCIONAL: o import so acontece quando
  uma conexao real vai ser aberta, entao `--dry-run`, os ETLs locais e os
  testes automatizados rodam sem banco nenhum instalado;
* a carga e idempotente: o MERGE usa a chave (REGION_ID, GENERATED_AT), entao
  rodar o mesmo snapshot duas vezes atualiza a linha em vez de duplicar, e um
  novo `generatedAt` (nova execucao do ETL) vira um novo registro historico.
"""

from __future__ import annotations

import csv
import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CURATED_DIR = ROOT / "data-lake" / "curated"

# Tabela analitica no Oracle. Espelha o grao da camada CURATED: uma linha por
# regiao por execucao do ETL (`region_risk_latest.json`).
TABLE_NAME = "REGION_RISK_SUMMARY"

# Arquivos do CURATED lidos, em ordem de preferencia. O JSON e mais rico
# (traz os indicadores); o CSV e o fallback com os mesmos campos de regiao.
CURATED_JSON = "region_risk_latest.json"
CURATED_CSV = "region_risk_latest.csv"

# Valores padrao para desenvolvimento local com o container Docker.
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 1521
DEFAULT_SERVICE = "FREEPDB1"
DEFAULT_USER = "ORBITAL_ALERT"

# Colunas da tabela, na ordem em que sao vinculadas no MERGE.
COLUMNS = (
    "REGION_ID",
    "REGION_NAME",
    "RISK_SCORE",
    "RISK_LEVEL",
    "RISK_TYPE",
    "DOMINANT_SENSOR_TYPE",
    "READINGS",
    "SENSORS",
    "INDICATORS",
    "WINDOW_START",
    "WINDOW_END",
    "GENERATED_AT",
    "SOURCE",
)

CREATE_TABLE_SQL = """
CREATE TABLE REGION_RISK_SUMMARY (
    REGION_ID            NUMBER(10)     NOT NULL,
    REGION_NAME          VARCHAR2(200),
    RISK_SCORE           NUMBER(5)      NOT NULL,
    RISK_LEVEL           VARCHAR2(20)   NOT NULL,
    RISK_TYPE            VARCHAR2(30),
    DOMINANT_SENSOR_TYPE VARCHAR2(30),
    READINGS             NUMBER(10),
    SENSORS              NUMBER(10),
    INDICATORS           NUMBER(10),
    WINDOW_START         TIMESTAMP,
    WINDOW_END           TIMESTAMP,
    GENERATED_AT         TIMESTAMP      NOT NULL,
    SOURCE               VARCHAR2(400),
    INGESTED_AT          TIMESTAMP      DEFAULT SYSTIMESTAMP NOT NULL,
    CONSTRAINT PK_REGION_RISK_SUMMARY PRIMARY KEY (REGION_ID, GENERATED_AT)
)
""".strip()

# MERGE idempotente: a mesma regiao no mesmo snapshot e atualizada, nunca
# duplicada. Binds nomeados na ordem de COLUMNS.
MERGE_SQL = """
MERGE INTO REGION_RISK_SUMMARY tgt
USING (
    SELECT
        :region_id            AS REGION_ID,
        :region_name          AS REGION_NAME,
        :risk_score           AS RISK_SCORE,
        :risk_level           AS RISK_LEVEL,
        :risk_type            AS RISK_TYPE,
        :dominant_sensor_type AS DOMINANT_SENSOR_TYPE,
        :readings             AS READINGS,
        :sensors              AS SENSORS,
        :indicators           AS INDICATORS,
        :window_start         AS WINDOW_START,
        :window_end           AS WINDOW_END,
        :generated_at         AS GENERATED_AT,
        :source               AS SOURCE
    FROM dual
) src
ON (tgt.REGION_ID = src.REGION_ID AND tgt.GENERATED_AT = src.GENERATED_AT)
WHEN MATCHED THEN UPDATE SET
    tgt.REGION_NAME          = src.REGION_NAME,
    tgt.RISK_SCORE           = src.RISK_SCORE,
    tgt.RISK_LEVEL           = src.RISK_LEVEL,
    tgt.RISK_TYPE            = src.RISK_TYPE,
    tgt.DOMINANT_SENSOR_TYPE = src.DOMINANT_SENSOR_TYPE,
    tgt.READINGS             = src.READINGS,
    tgt.SENSORS              = src.SENSORS,
    tgt.INDICATORS           = src.INDICATORS,
    tgt.WINDOW_START         = src.WINDOW_START,
    tgt.WINDOW_END           = src.WINDOW_END,
    tgt.SOURCE               = src.SOURCE,
    tgt.INGESTED_AT          = SYSTIMESTAMP
WHEN NOT MATCHED THEN INSERT (
    REGION_ID, REGION_NAME, RISK_SCORE, RISK_LEVEL, RISK_TYPE,
    DOMINANT_SENSOR_TYPE, READINGS, SENSORS, INDICATORS,
    WINDOW_START, WINDOW_END, GENERATED_AT, SOURCE
) VALUES (
    src.REGION_ID, src.REGION_NAME, src.RISK_SCORE, src.RISK_LEVEL, src.RISK_TYPE,
    src.DOMINANT_SENSOR_TYPE, src.READINGS, src.SENSORS, src.INDICATORS,
    src.WINDOW_START, src.WINDOW_END, src.GENERATED_AT, src.SOURCE
)
""".strip()

SELECT_COUNT_SQL = "SELECT COUNT(*) FROM REGION_RISK_SUMMARY"

# ORA-00955: "name is already used by an existing object". A tabela ja existe,
# entao `ensure_table` nao tem nada a fazer.
ORA_NAME_ALREADY_USED = 955


class OracleConfigError(Exception):
    """Configuracao ausente ou invalida para falar com o Oracle Database."""


class OracleDriverNotInstalledError(Exception):
    """O pacote `oracledb` nao esta instalado neste ambiente."""


class CuratedDataError(Exception):
    """A camada CURATED nao existe ou nao pode ser interpretada."""


class OracleSettings:
    """Dados de conexao com o Oracle Database, sempre vindos do ambiente."""

    def __init__(self, host=None, port=None, service=None, user=None, password=None):
        self.host = host or DEFAULT_HOST
        self.port = int(port) if port else DEFAULT_PORT
        self.service = service or DEFAULT_SERVICE
        self.user = user or DEFAULT_USER
        self.password = password or None

    @classmethod
    def from_env(cls, env=None):
        env = os.environ if env is None else env
        return cls(
            host=env.get("ORACLE_DB_HOST"),
            port=env.get("ORACLE_DB_PORT"),
            service=env.get("ORACLE_DB_SERVICE"),
            user=env.get("ORACLE_DB_USER"),
            password=env.get("ORACLE_DB_PASSWORD"),
        )

    @property
    def dsn(self):
        """Easy Connect string aceita pelo driver: host:porta/service."""
        return "{0}:{1}/{2}".format(self.host, self.port, self.service)

    def problems(self):
        """Lista legivel do que impede uma conexao real. Vazia = pronto."""
        found = []
        if not self.password:
            found.append(
                "ORACLE_DB_PASSWORD nao definido - informe a senha do usuario "
                "da aplicacao (variavel de ambiente; nunca versionada)."
            )
        if not self.user:
            found.append("ORACLE_DB_USER nao definido - use o usuario da aplicacao.")
        if not self.service:
            found.append("ORACLE_DB_SERVICE nao definido - no container use FREEPDB1.")
        return found

    def describe(self):
        """Resumo sem segredos, seguro para imprimir no terminal."""
        return [
            ("host", self.host),
            ("port", str(self.port)),
            ("service", self.service),
            ("user", self.user),
            ("dsn", self.dsn),
            ("password", "(definida)" if self.password else "(nao definida)"),
        ]


def validate_for_connection(settings):
    """Falha cedo e de forma compreensivel quando o Oracle nao esta configurado."""
    problems = settings.problems()
    if problems:
        raise OracleConfigError(
            "configuracao do Oracle Database incompleta:\n  - " + "\n  - ".join(problems)
        )
    return True


def parse_timestamp(value):
    """Converte o ISO-8601 UTC do CURATED (`2026-09-08T17:04:11Z`) em datetime.

    Retorna um datetime *naive* em UTC, que e o que a coluna TIMESTAMP guarda.
    Todos os horarios do Data Lake ja estao em UTC.
    """
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.replace(tzinfo=None)
    text = str(value).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
    return parsed


def _to_int(value, default=None):
    if value in (None, ""):
        return default
    return int(float(value))


def curated_source_path(curated_dir):
    """Arquivo do CURATED que sera lido, preferindo o JSON completo."""
    curated_dir = Path(curated_dir)
    for filename in (CURATED_JSON, CURATED_CSV):
        candidate = curated_dir / filename
        if candidate.is_file():
            return candidate
    raise CuratedDataError(
        "nenhum arquivo da camada CURATED encontrado em {0} (esperado {1} ou {2}). "
        "Rode os ETLs antes: python etl/raw_to_trusted.py && python etl/trusted_to_curated.py".format(
            curated_dir, CURATED_JSON, CURATED_CSV
        )
    )


def load_curated_regions(curated_dir):
    """Le o CURATED e devolve (lista de regioes, caminho do arquivo lido)."""
    path = curated_source_path(curated_dir)
    if path.suffix.lower() == ".json":
        return _load_json(path), path
    return _load_csv(path), path


def _load_json(path):
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise CuratedDataError("JSON invalido em {0}: {1}".format(path, exc)) from exc
    if not isinstance(payload, list):
        raise CuratedDataError(
            "formato inesperado em {0}: esperado uma lista de regioes.".format(path)
        )
    return payload


def _load_csv(path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    # Traduz o cabecalho snake_case do CSV para as chaves camelCase do JSON,
    # de modo que `to_row` enxergue sempre a mesma estrutura.
    mapping = {
        "region_id": "regionId",
        "region_name": "regionName",
        "risk_score": "riskScore",
        "risk_level": "riskLevel",
        "risk_type": "riskType",
        "dominant_sensor_type": "dominantSensorType",
        "readings": "readings",
        "sensors": "sensors",
        "window_start": "windowStart",
        "window_end": "windowEnd",
        "generated_at": "generatedAt",
    }
    return [
        {mapping[key]: value for key, value in row.items() if key in mapping}
        for row in rows
    ]


def to_row(region, source):
    """Mapeia uma regiao do CURATED nas colunas de REGION_RISK_SUMMARY."""
    region_id = _to_int(region.get("regionId"))
    if region_id is None:
        raise CuratedDataError("registro do CURATED sem regionId: {0}".format(region))

    generated_at = parse_timestamp(region.get("generatedAt"))
    if generated_at is None:
        raise CuratedDataError(
            "registro do CURATED sem generatedAt (regiao {0}) - a chave do MERGE "
            "depende dele.".format(region_id)
        )

    indicators = region.get("indicators")
    return {
        "region_id": region_id,
        "region_name": region.get("regionName") or None,
        "risk_score": _to_int(region.get("riskScore"), 0),
        "risk_level": region.get("riskLevel") or "UNKNOWN",
        "risk_type": region.get("riskType") or None,
        "dominant_sensor_type": region.get("dominantSensorType") or None,
        "readings": _to_int(region.get("readings")),
        "sensors": _to_int(region.get("sensors")),
        "indicators": len(indicators) if isinstance(indicators, list) else None,
        "window_start": parse_timestamp(region.get("windowStart")),
        "window_end": parse_timestamp(region.get("windowEnd")),
        "generated_at": generated_at,
        "source": str(source),
    }


def build_rows(regions, source):
    """Todas as linhas prontas para o MERGE, na ordem do arquivo CURATED."""
    return [to_row(region, source) for region in regions]


def format_row(row):
    """Linha legivel de log: `Regiao 1 | HIGH | FLOOD | score=100`."""
    return "Regiao {0} | {1} | {2} | score={3}".format(
        row["region_id"],
        row["risk_level"],
        row["risk_type"] or "-",
        row["risk_score"],
    )


def connect(settings):
    """Abre a conexao com o Oracle. Import tardio: o driver e opcional."""
    try:
        import oracledb  # noqa: PLC0415 - dependencia opcional, so na conexao real
    except ImportError as exc:
        raise OracleDriverNotInstalledError(
            "pacote `oracledb` nao instalado. "
            "Rode: pip install -r etl/requirements-oracle-db.txt"
        ) from exc

    return oracledb.connect(
        user=settings.user, password=settings.password, dsn=settings.dsn
    )


def ensure_table(connection):
    """Cria REGION_RISK_SUMMARY se ainda nao existir. Devolve True se criou."""
    with connection.cursor() as cursor:
        try:
            cursor.execute(CREATE_TABLE_SQL)
        except Exception as exc:  # oracledb.DatabaseError, sem importar o driver aqui
            if _is_name_already_used(exc):
                return False
            raise
    return True


def _is_name_already_used(exc):
    """True quando o erro do Oracle e apenas 'objeto ja existe' (ORA-00955)."""
    error = getattr(exc, "args", (None,))[0]
    code = getattr(error, "code", None)
    if code == ORA_NAME_ALREADY_USED:
        return True
    return "ORA-00955" in str(exc)


def merge_row(cursor, row):
    """Executa o MERGE idempotente de uma regiao."""
    cursor.execute(MERGE_SQL, row)
    return cursor.rowcount


def count_rows(connection):
    with connection.cursor() as cursor:
        cursor.execute(SELECT_COUNT_SQL)
        return cursor.fetchone()[0]
