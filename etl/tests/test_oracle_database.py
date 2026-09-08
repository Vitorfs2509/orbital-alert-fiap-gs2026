#!/usr/bin/env python3
"""Testes da integracao CURATED -> Oracle AI Database Free.

Nenhum teste abre conexao real nem exige o pacote `oracledb` instalado:
o cursor e substituido por um duble e o dry-run nao toca no banco.

Uso:
    python etl/tests/test_oracle_database.py
    python -m unittest discover -s etl/tests
"""

from __future__ import annotations

import io
import json
import sys
import unittest
from contextlib import redirect_stdout
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

ETL_DIR = Path(__file__).resolve().parents[1]
if str(ETL_DIR) not in sys.path:
    sys.path.insert(0, str(ETL_DIR))

import oracle_database as odb  # noqa: E402
import sync_curated_to_oracle as sync  # noqa: E402

# Copia fiel de um registro real de data-lake/curated/region_risk_latest.json.
CURATED_REGION = {
    "regionId": 1,
    "regionName": "Margem Rio Tiete - Norte",
    "riskScore": 100,
    "riskLevel": "HIGH",
    "riskType": "FLOOD",
    "dominantSensorType": "RAINFALL",
    "readings": 6,
    "sensors": 2,
    "windowStart": "2026-09-08T11:53:14Z",
    "windowEnd": "2026-09-08T11:53:16Z",
    "indicators": [
        {"sensorType": "RAINFALL", "subScore": 100, "trend": "RISING"},
        {"sensorType": "WATER_LEVEL", "subScore": 100, "trend": "RISING"},
    ],
    "ignoredSensorTypes": [],
    "generatedAt": "2026-09-08T17:04:11Z",
}

CURATED_CSV = (
    "region_id,region_name,risk_score,risk_level,risk_type,readings,sensors,"
    "window_start,window_end,dominant_sensor_type,generated_at\n"
    "1,Margem Rio Tiete - Norte,100,HIGH,FLOOD,6,2,"
    "2026-09-08T11:53:14Z,2026-09-08T11:53:16Z,RAINFALL,2026-09-08T17:04:11Z\n"
)


def build_curated_dir(root, regions=None, with_csv=True):
    """Camada CURATED minima, com os mesmos nomes de arquivo do projeto."""
    curated = Path(root)
    curated.mkdir(parents=True, exist_ok=True)
    payload = [CURATED_REGION] if regions is None else regions
    (curated / odb.CURATED_JSON).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    if with_csv:
        (curated / odb.CURATED_CSV).write_text(CURATED_CSV, encoding="utf-8")
    return curated


class FakeCursor:
    """Duble do cursor: registra os binds recebidos, nao fala com o banco."""

    def __init__(self, existing_table=False):
        self.executed = []
        self.merges = []
        self.rowcount = 1
        self._existing_table = existing_table

    def execute(self, sql, params=None):
        self.executed.append(sql)
        if sql.startswith("CREATE TABLE") and self._existing_table:
            raise RuntimeError("ORA-00955: name is already used by an existing object")
        if sql.startswith("MERGE"):
            self.merges.append(params)
        return self

    def fetchone(self):
        return (len(self.merges),)

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return False


class FakeConnection:
    """Duble da conexao: entrega sempre o mesmo cursor e conta commits."""

    def __init__(self, existing_table=False):
        self.cursor_obj = FakeCursor(existing_table=existing_table)
        self.commits = 0
        self.rollbacks = 0
        self.closed = False

    def cursor(self):
        return self.cursor_obj

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1

    def close(self):
        self.closed = True


class TimestampTest(unittest.TestCase):
    """O CURATED grava ISO-8601 em UTC com sufixo Z."""

    def test_z_suffix_becomes_naive_utc(self):
        self.assertEqual(
            odb.parse_timestamp("2026-09-08T17:04:11Z"),
            datetime(2026, 9, 8, 17, 4, 11),
        )

    def test_offset_is_converted_to_utc(self):
        self.assertEqual(
            odb.parse_timestamp("2026-09-08T14:04:11-03:00"),
            datetime(2026, 9, 8, 17, 4, 11),
        )

    def test_empty_values_become_none(self):
        self.assertIsNone(odb.parse_timestamp(None))
        self.assertIsNone(odb.parse_timestamp(""))


class CuratedParsingTest(unittest.TestCase):
    """Leitura dos arquivos reais da camada CURATED."""

    def test_json_is_preferred_over_csv(self):
        with TemporaryDirectory() as tmp:
            curated = build_curated_dir(tmp)
            regions, source = odb.load_curated_regions(curated)
        self.assertEqual(source.name, odb.CURATED_JSON)
        self.assertEqual(len(regions), 1)
        self.assertEqual(regions[0]["regionName"], "Margem Rio Tiete - Norte")

    def test_csv_is_used_when_json_is_absent(self):
        with TemporaryDirectory() as tmp:
            curated = build_curated_dir(tmp)
            (curated / odb.CURATED_JSON).unlink()
            regions, source = odb.load_curated_regions(curated)
        self.assertEqual(source.name, odb.CURATED_CSV)
        self.assertEqual(regions[0]["regionId"], "1")
        self.assertEqual(regions[0]["riskLevel"], "HIGH")

    def test_missing_curated_layer_is_reported(self):
        with TemporaryDirectory() as tmp:
            with self.assertRaises(odb.CuratedDataError) as ctx:
                odb.load_curated_regions(Path(tmp) / "vazio")
        self.assertIn("CURATED", str(ctx.exception))

    def test_invalid_json_is_reported(self):
        with TemporaryDirectory() as tmp:
            curated = Path(tmp)
            (curated / odb.CURATED_JSON).write_text("{nao e json", encoding="utf-8")
            with self.assertRaises(odb.CuratedDataError):
                odb.load_curated_regions(curated)


class ColumnMappingTest(unittest.TestCase):
    """Cada campo do CURATED cai na coluna certa de REGION_RISK_SUMMARY."""

    def test_json_region_maps_every_column(self):
        row = odb.to_row(CURATED_REGION, "curated/region_risk_latest.json")
        self.assertEqual(row["region_id"], 1)
        self.assertEqual(row["region_name"], "Margem Rio Tiete - Norte")
        self.assertEqual(row["risk_score"], 100)
        self.assertEqual(row["risk_level"], "HIGH")
        self.assertEqual(row["risk_type"], "FLOOD")
        self.assertEqual(row["dominant_sensor_type"], "RAINFALL")
        self.assertEqual(row["readings"], 6)
        self.assertEqual(row["sensors"], 2)
        self.assertEqual(row["indicators"], 2)
        self.assertEqual(row["window_start"], datetime(2026, 9, 8, 11, 53, 14))
        self.assertEqual(row["window_end"], datetime(2026, 9, 8, 11, 53, 16))
        self.assertEqual(row["generated_at"], datetime(2026, 9, 8, 17, 4, 11))
        self.assertEqual(row["source"], "curated/region_risk_latest.json")

    def test_binds_cover_exactly_the_merge_placeholders(self):
        row = odb.to_row(CURATED_REGION, "x.json")
        expected = {name.lower() for name in odb.COLUMNS}
        self.assertEqual(set(row) - {"source"}, expected - {"source"})

    def test_csv_strings_are_converted_to_numbers(self):
        with TemporaryDirectory() as tmp:
            curated = build_curated_dir(tmp)
            (curated / odb.CURATED_JSON).unlink()
            regions, source = odb.load_curated_regions(curated)
        row = odb.to_row(regions[0], source)
        self.assertEqual(row["region_id"], 1)
        self.assertEqual(row["risk_score"], 100)
        self.assertIsNone(row["indicators"])  # o CSV de regioes nao traz indicadores

    def test_region_without_id_is_rejected(self):
        with self.assertRaises(odb.CuratedDataError):
            odb.to_row({"riskLevel": "HIGH", "generatedAt": "2026-09-08T17:04:11Z"}, "x")

    def test_region_without_generated_at_is_rejected(self):
        """GENERATED_AT faz parte da chave do MERGE; sem ele nao ha idempotencia."""
        with self.assertRaises(odb.CuratedDataError) as ctx:
            odb.to_row({"regionId": 1, "riskLevel": "HIGH"}, "x")
        self.assertIn("generatedAt", str(ctx.exception))

    def test_log_line_is_readable(self):
        row = odb.to_row(CURATED_REGION, "x.json")
        self.assertEqual(odb.format_row(row), "Regiao 1 | HIGH | FLOOD | score=100")


class SettingsTest(unittest.TestCase):
    """Toda a conexao vem do ambiente; nenhuma senha no codigo."""

    def test_reads_environment_variables(self):
        settings = odb.OracleSettings.from_env(
            {
                "ORACLE_DB_HOST": "db.local",
                "ORACLE_DB_PORT": "1522",
                "ORACLE_DB_SERVICE": "OUTROPDB",
                "ORACLE_DB_USER": "OUTRO_USER",
                "ORACLE_DB_PASSWORD": "segredo",
            }
        )
        self.assertEqual(settings.dsn, "db.local:1522/OUTROPDB")
        self.assertEqual(settings.user, "OUTRO_USER")

    def test_defaults_match_the_docker_container(self):
        settings = odb.OracleSettings.from_env({})
        self.assertEqual(settings.dsn, "localhost:1521/FREEPDB1")
        self.assertEqual(settings.user, "ORBITAL_ALERT")

    def test_missing_password_is_reported(self):
        settings = odb.OracleSettings.from_env({})
        problems = settings.problems()
        self.assertEqual(len(problems), 1)
        self.assertIn("ORACLE_DB_PASSWORD", problems[0])

    def test_complete_configuration_passes(self):
        settings = odb.OracleSettings.from_env({"ORACLE_DB_PASSWORD": "segredo"})
        self.assertEqual(settings.problems(), [])
        self.assertTrue(odb.validate_for_connection(settings))

    def test_incomplete_configuration_raises(self):
        with self.assertRaises(odb.OracleConfigError):
            odb.validate_for_connection(odb.OracleSettings.from_env({}))

    def test_describe_never_exposes_the_password(self):
        settings = odb.OracleSettings.from_env({"ORACLE_DB_PASSWORD": "segredo"})
        rendered = str(settings.describe())
        self.assertNotIn("segredo", rendered)
        self.assertIn("(definida)", rendered)


class MergeTest(unittest.TestCase):
    """A carga e idempotente e nao depende de banco para ser verificada."""

    def test_merge_binds_the_row_as_named_parameters(self):
        cursor = FakeCursor()
        row = odb.to_row(CURATED_REGION, "x.json")
        odb.merge_row(cursor, row)
        self.assertEqual(cursor.merges, [row])
        self.assertTrue(cursor.executed[0].startswith("MERGE INTO REGION_RISK_SUMMARY"))

    def test_merge_key_is_region_plus_snapshot(self):
        self.assertIn(
            "ON (tgt.REGION_ID = src.REGION_ID AND tgt.GENERATED_AT = src.GENERATED_AT)",
            odb.MERGE_SQL,
        )

    def test_every_column_has_a_placeholder(self):
        for column in odb.COLUMNS:
            self.assertIn(":" + column.lower(), odb.MERGE_SQL)

    def test_existing_table_is_not_recreated(self):
        connection = FakeConnection(existing_table=True)
        self.assertFalse(odb.ensure_table(connection))

    def test_table_is_created_when_absent(self):
        connection = FakeConnection()
        self.assertTrue(odb.ensure_table(connection))
        self.assertIn("CREATE TABLE REGION_RISK_SUMMARY", connection.cursor_obj.executed[0])

    def test_unexpected_ddl_error_is_not_swallowed(self):
        class BrokenConnection(FakeConnection):
            def cursor(self):
                cursor = FakeCursor()
                cursor.execute = lambda sql, params=None: (_ for _ in ()).throw(
                    RuntimeError("ORA-01031: insufficient privileges")
                )
                cursor.__enter__ = lambda self=cursor: self
                cursor.__exit__ = lambda *a: False
                return cursor

        with self.assertRaises(RuntimeError):
            odb.ensure_table(BrokenConnection())


class CliTest(unittest.TestCase):
    """O CLI roda sem banco e sem o driver instalado."""

    def run_cli(self, argv):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = sync.main(argv)
        return code, buffer.getvalue()

    def test_dry_run_never_opens_a_connection(self):
        def explode(settings):
            raise AssertionError("dry-run nao pode abrir conexao")

        original = sync.connect
        sync.connect = explode
        try:
            with TemporaryDirectory() as tmp:
                curated = build_curated_dir(tmp)
                code, output = self.run_cli(["--dry-run", "--curated-dir", str(curated)])
        finally:
            sync.connect = original

        self.assertEqual(code, sync.EXIT_OK)
        self.assertIn("[ORACLE] Regiao 1 | HIGH | FLOOD | score=100 -> DRY-RUN", output)
        self.assertIn("Nenhuma conexao foi aberta", output)

    def test_dry_run_works_without_any_oracle_configuration(self):
        with TemporaryDirectory() as tmp:
            curated = build_curated_dir(tmp)
            code, output = self.run_cli(["--dry-run", "--curated-dir", str(curated)])
        self.assertEqual(code, sync.EXIT_OK)
        self.assertIn("ORACLE_DB_PASSWORD", output)

    def test_dry_run_never_prints_the_password(self):
        settings = odb.OracleSettings.from_env({"ORACLE_DB_PASSWORD": "s3nh4-secreta"})
        with TemporaryDirectory() as tmp:
            curated = build_curated_dir(tmp)
            original = odb.OracleSettings.from_env
            odb.OracleSettings.from_env = classmethod(lambda cls, env=None: settings)
            sync.OracleSettings = odb.OracleSettings
            try:
                code, output = self.run_cli(["--dry-run", "--curated-dir", str(curated)])
            finally:
                odb.OracleSettings.from_env = original
                sync.OracleSettings = odb.OracleSettings
        self.assertEqual(code, sync.EXIT_OK)
        self.assertNotIn("s3nh4-secreta", output)

    def test_empty_curated_layer_is_reported(self):
        with TemporaryDirectory() as tmp:
            curated = build_curated_dir(tmp, regions=[], with_csv=False)
            code, output = self.run_cli(["--dry-run", "--curated-dir", str(curated)])
        self.assertEqual(code, sync.EXIT_OK)
        self.assertIn("nao tem nenhuma regiao", output)

    def test_missing_curated_directory_is_reported(self):
        with TemporaryDirectory() as tmp:
            code, output = self.run_cli(["--dry-run", "--curated-dir", str(Path(tmp) / "vazio")])
        self.assertEqual(code, sync.EXIT_CONFIG_ERROR)
        self.assertIn("CURATED", output)

    def test_real_run_without_password_fails_with_a_readable_message(self):
        original = odb.OracleSettings.from_env
        odb.OracleSettings.from_env = classmethod(
            lambda cls, env=None: odb.OracleSettings(password=None)
        )
        sync.OracleSettings = odb.OracleSettings
        try:
            with TemporaryDirectory() as tmp:
                curated = build_curated_dir(tmp)
                code, output = self.run_cli(["--curated-dir", str(curated)])
        finally:
            odb.OracleSettings.from_env = original
            sync.OracleSettings = odb.OracleSettings

        self.assertEqual(code, sync.EXIT_CONFIG_ERROR)
        self.assertIn("configuracao do Oracle Database incompleta", output)
        self.assertIn("--dry-run", output)


if __name__ == "__main__":
    unittest.main(verbosity=2)
