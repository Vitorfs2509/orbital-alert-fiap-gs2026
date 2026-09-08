#!/usr/bin/env python3
"""Testes da integracao com o OCI Object Storage.

Nenhum teste faz chamada real a Oracle nem exige o pacote `oci` instalado:
o cliente e substituido por um duble e o dry-run nao toca na rede.

Uso:
    python etl/tests/test_oci_sync.py
    python -m unittest discover -s etl/tests
"""

from __future__ import annotations

import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

ETL_DIR = Path(__file__).resolve().parents[1]
if str(ETL_DIR) not in sys.path:
    sys.path.insert(0, str(ETL_DIR))

import oci_storage  # noqa: E402
import sync_data_lake_to_oci as sync  # noqa: E402


def build_fake_data_lake(root):
    """Data Lake minimo com as tres camadas, um arquivo em cada."""
    files = {
        "raw/2026/09/08/readings-2026-09-08.jsonl": '{"eventId": "e1", "value": 91.2}\n',
        "trusted/readings.jsonl": '{"event_id": "e1", "value": 91.2}\n',
        "trusted/_quality/stats_20260908T145327Z.json": "{}",
        "curated/region_risk_latest.json": "[]",
        "raw/.gitkeep": "",
    }
    for relative, content in files.items():
        path = Path(root) / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return Path(root)


class FakeObjectStorageClient:
    """Duble do ObjectStorageClient: registra o que receberia, nao envia nada."""

    def __init__(self, namespace="fakenamespace"):
        self._namespace = namespace
        self.uploads = []

    def get_namespace(self):
        return type("Response", (), {"data": self._namespace})()

    def put_object(self, namespace_name, bucket_name, object_name, put_object_body, content_type=None):
        self.uploads.append(
            {
                "namespace": namespace_name,
                "bucket": bucket_name,
                "object_name": object_name,
                "content_type": content_type,
                "body": put_object_body.read(),
            }
        )


class ObjectNameTest(unittest.TestCase):
    """O nome do objeto no bucket espelha o caminho relativo dentro do Data Lake."""

    def test_raw_path_keeps_date_partition(self):
        with TemporaryDirectory() as tmp:
            lake = build_fake_data_lake(tmp)
            local = lake / "raw" / "2026" / "09" / "08" / "readings-2026-09-08.jsonl"
            self.assertEqual(
                oci_storage.to_object_name(local, lake),
                "raw/2026/09/08/readings-2026-09-08.jsonl",
            )

    def test_object_name_always_uses_forward_slashes(self):
        with TemporaryDirectory() as tmp:
            lake = build_fake_data_lake(tmp)
            local = lake / "trusted" / "_quality" / "stats_20260908T145327Z.json"
            object_name = oci_storage.to_object_name(local, lake)
            self.assertNotIn("\\", object_name)
            self.assertEqual(object_name, "trusted/_quality/stats_20260908T145327Z.json")

    def test_optional_prefix_is_prepended_and_normalized(self):
        with TemporaryDirectory() as tmp:
            lake = build_fake_data_lake(tmp)
            local = lake / "curated" / "region_risk_latest.json"
            self.assertEqual(
                oci_storage.to_object_name(local, lake, prefix="/orbital-alert/"),
                "orbital-alert/curated/region_risk_latest.json",
            )

    def test_file_outside_data_lake_is_rejected(self):
        with TemporaryDirectory() as tmp:
            lake = build_fake_data_lake(tmp)
            outside = Path(tmp).parent / "outro.jsonl"
            with self.assertRaises(ValueError):
                oci_storage.to_object_name(outside, lake)

    def test_content_type_per_extension(self):
        self.assertEqual(oci_storage.content_type_for("a/b.jsonl"), "application/x-ndjson")
        self.assertEqual(oci_storage.content_type_for("a/b.json"), "application/json")
        self.assertEqual(oci_storage.content_type_for("a/b.csv"), "text/csv")
        self.assertEqual(oci_storage.content_type_for("a/b.bin"), "application/octet-stream")


class LayerSelectionTest(unittest.TestCase):
    """`--layer` decide o que entra no plano de upload."""

    def test_all_is_the_default_and_covers_the_three_layers(self):
        self.assertEqual(oci_storage.resolve_layers(None), ("raw", "trusted", "curated"))
        self.assertEqual(oci_storage.resolve_layers("all"), ("raw", "trusted", "curated"))

    def test_single_layer(self):
        self.assertEqual(oci_storage.resolve_layers("curated"), ("curated",))

    def test_unknown_layer_is_rejected(self):
        with self.assertRaises(ValueError):
            oci_storage.resolve_layers("bronze")

    def test_plan_only_includes_the_selected_layer(self):
        with TemporaryDirectory() as tmp:
            lake = build_fake_data_lake(tmp)
            names = [name for _, name in oci_storage.plan_uploads(lake, ("trusted",))]
            self.assertTrue(all(name.startswith("trusted/") for name in names))
            self.assertIn("trusted/readings.jsonl", names)

    def test_plan_for_all_layers_skips_git_placeholders(self):
        with TemporaryDirectory() as tmp:
            lake = build_fake_data_lake(tmp)
            names = [name for _, name in oci_storage.plan_uploads(lake, oci_storage.LAYERS)]
            self.assertEqual(
                names,
                [
                    "raw/2026/09/08/readings-2026-09-08.jsonl",
                    "trusted/_quality/stats_20260908T145327Z.json",
                    "trusted/readings.jsonl",
                    "curated/region_risk_latest.json",
                ],
            )
            self.assertNotIn("raw/.gitkeep", names)

    def test_missing_layer_directory_yields_no_files(self):
        with TemporaryDirectory() as tmp:
            self.assertEqual(oci_storage.iter_layer_files(tmp, "curated"), [])


class SettingsValidationTest(unittest.TestCase):
    """A configuracao vem do ambiente e falha de forma compreensivel."""

    def test_reads_environment_variables(self):
        settings = oci_storage.OciSettings.from_env(
            {
                "OCI_BUCKET_NAME": "orbital-alert-datalake",
                "OCI_NAMESPACE": "grabcdefgh",
                "OCI_PROFILE": "FIAP",
                "OCI_REGION": "sa-saopaulo-1",
            }
        )
        self.assertEqual(settings.bucket, "orbital-alert-datalake")
        self.assertEqual(settings.namespace, "grabcdefgh")
        self.assertEqual(settings.profile, "FIAP")
        self.assertEqual(settings.region, "sa-saopaulo-1")

    def test_defaults_match_the_official_sdk(self):
        settings = oci_storage.OciSettings.from_env({})
        self.assertEqual(settings.profile, "DEFAULT")
        self.assertIsNone(settings.bucket)
        self.assertTrue(settings.config_file_path.match("*/.oci/config"))

    def test_missing_bucket_is_reported(self):
        with TemporaryDirectory() as tmp:
            config_file = Path(tmp) / "config"
            config_file.write_text("[DEFAULT]\n", encoding="utf-8")
            settings = oci_storage.OciSettings.from_env({"OCI_CONFIG_FILE": str(config_file)})
            problems = settings.problems()
            self.assertEqual(len(problems), 1)
            self.assertIn("OCI_BUCKET_NAME", problems[0])
            with self.assertRaises(oci_storage.OciConfigError):
                oci_storage.validate_for_upload(settings)

    def test_missing_config_file_is_reported(self):
        with TemporaryDirectory() as tmp:
            settings = oci_storage.OciSettings.from_env(
                {
                    "OCI_BUCKET_NAME": "orbital-alert-datalake",
                    "OCI_CONFIG_FILE": str(Path(tmp) / "nao-existe"),
                }
            )
            problems = settings.problems()
            self.assertEqual(len(problems), 1)
            self.assertIn("configuracao do OCI nao encontrado", problems[0])

    def test_complete_configuration_passes(self):
        with TemporaryDirectory() as tmp:
            config_file = Path(tmp) / "config"
            config_file.write_text("[DEFAULT]\n", encoding="utf-8")
            settings = oci_storage.OciSettings.from_env(
                {
                    "OCI_BUCKET_NAME": "orbital-alert-datalake",
                    "OCI_CONFIG_FILE": str(config_file),
                }
            )
            self.assertEqual(settings.problems(), [])
            self.assertTrue(oci_storage.validate_for_upload(settings))

    def test_describe_never_exposes_secrets(self):
        settings = oci_storage.OciSettings.from_env({"OCI_BUCKET_NAME": "b"})
        rendered = " ".join(value for _, value in settings.describe()).lower()
        for secret_hint in ("key", "fingerprint", "ocid1.user", "ocid1.tenancy"):
            self.assertNotIn(secret_hint, rendered)


class UploadTest(unittest.TestCase):
    """O upload usa `put_object` do SDK oficial, aqui substituido por um duble."""

    def test_upload_sends_content_and_content_type(self):
        with TemporaryDirectory() as tmp:
            lake = build_fake_data_lake(tmp)
            client = FakeObjectStorageClient()
            local = lake / "raw" / "2026" / "09" / "08" / "readings-2026-09-08.jsonl"
            oci_storage.upload_file(
                client, "ns", "bucket", "raw/2026/09/08/readings-2026-09-08.jsonl", local
            )
            self.assertEqual(len(client.uploads), 1)
            upload = client.uploads[0]
            self.assertEqual(upload["object_name"], "raw/2026/09/08/readings-2026-09-08.jsonl")
            self.assertEqual(upload["content_type"], "application/x-ndjson")
            self.assertEqual(upload["body"], local.read_bytes())

    def test_namespace_from_env_wins_over_sdk_lookup(self):
        settings = oci_storage.OciSettings.from_env({"OCI_NAMESPACE": "meunamespace"})
        self.assertEqual(
            oci_storage.resolve_namespace(FakeObjectStorageClient(), settings), "meunamespace"
        )

    def test_namespace_falls_back_to_the_sdk(self):
        settings = oci_storage.OciSettings.from_env({})
        self.assertEqual(
            oci_storage.resolve_namespace(FakeObjectStorageClient("resolvido"), settings),
            "resolvido",
        )


class DryRunTest(unittest.TestCase):
    """O dry-run lista os objetos sem construir cliente nem acessar a Oracle."""

    def run_cli(self, argv):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = sync.main(argv)
        return code, buffer.getvalue()

    def test_dry_run_never_builds_a_client(self):
        def explode(_settings):
            raise AssertionError("dry-run nao pode acessar o OCI")

        original = sync.build_client
        sync.build_client = explode
        try:
            with TemporaryDirectory() as tmp:
                lake = build_fake_data_lake(tmp)
                code, output = self.run_cli(["--dry-run", "--data-lake-dir", str(lake)])
        finally:
            sync.build_client = original

        self.assertEqual(code, sync.EXIT_OK)
        self.assertIn("raw/2026/09/08/readings-2026-09-08.jsonl -> DRY-RUN", output)
        self.assertIn("trusted/readings.jsonl -> DRY-RUN", output)
        self.assertIn("curated/region_risk_latest.json -> DRY-RUN", output)
        self.assertIn("Arquivos planejados : 4", output)

    def test_dry_run_respects_layer_filter(self):
        with TemporaryDirectory() as tmp:
            lake = build_fake_data_lake(tmp)
            code, output = self.run_cli(
                ["--dry-run", "--layer", "curated", "--data-lake-dir", str(lake)]
            )
        self.assertEqual(code, sync.EXIT_OK)
        self.assertIn("curated/region_risk_latest.json -> DRY-RUN", output)
        self.assertNotIn("raw/2026", output)
        self.assertIn("Arquivos planejados : 1", output)

    def test_dry_run_works_without_any_oci_configuration(self):
        with TemporaryDirectory() as tmp:
            lake = build_fake_data_lake(tmp)
            code, output = self.run_cli(["--dry-run", "--data-lake-dir", str(lake)])
        self.assertEqual(code, sync.EXIT_OK)
        self.assertIn("Nenhum dado saiu desta maquina", output)

    def test_real_run_without_configuration_fails_with_a_readable_message(self):
        with TemporaryDirectory() as tmp:
            lake = build_fake_data_lake(tmp)
            code, output = self.run_cli(["--data-lake-dir", str(lake), "--bucket", ""])
        self.assertEqual(code, sync.EXIT_CONFIG_ERROR)
        self.assertIn("configuracao do OCI incompleta", output)
        self.assertIn("--dry-run", output)

    def test_missing_data_lake_directory_is_reported(self):
        with TemporaryDirectory() as tmp:
            code, output = self.run_cli(["--dry-run", "--data-lake-dir", str(Path(tmp) / "vazio")])
        self.assertEqual(code, sync.EXIT_CONFIG_ERROR)
        self.assertIn("Data Lake local nao encontrado", output)


if __name__ == "__main__":
    unittest.main(verbosity=2)
