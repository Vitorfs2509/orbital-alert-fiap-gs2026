#!/usr/bin/env python3
"""Integracao do Data Lake do Orbital Alert com o Oracle Cloud Infrastructure Object Storage.

Este modulo contem apenas a logica reutilizavel (configuracao, mapeamento de
caminhos e upload). O ponto de entrada de linha de comando fica em
`etl/sync_data_lake_to_oci.py`.

Principios:

* nenhuma credencial no codigo - tudo vem de variaveis de ambiente e/ou do
  arquivo padrao `~/.oci/config` lido pelo SDK oficial;
* o SDK `oci` e uma dependencia OPCIONAL: o import so acontece quando um upload
  real vai ser executado, entao `--dry-run`, os ETLs locais e os testes
  automatizados rodam sem instalar nada e sem conta Oracle;
* o layout local e espelhado no bucket sem traducao:
  `data-lake/raw/2026/09/08/x.jsonl` -> `raw/2026/09/08/x.jsonl`.
"""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA_LAKE_DIR = ROOT / "data-lake"

# Camadas sincronizadas. A ordem e a de processamento do pipeline.
LAYERS = ("raw", "trusted", "curated")
LAYER_ALL = "all"
LAYER_CHOICES = (LAYER_ALL,) + LAYERS

# Valores padrao do SDK oficial quando as variaveis de ambiente nao existem.
DEFAULT_CONFIG_FILE = "~/.oci/config"
DEFAULT_PROFILE = "DEFAULT"

# Arquivos de controle do git que nao fazem parte do Data Lake.
IGNORED_FILENAMES = {".gitkeep", ".DS_Store", "Thumbs.db"}

CONTENT_TYPES = {
    ".jsonl": "application/x-ndjson",
    ".json": "application/json",
    ".csv": "text/csv",
    ".md": "text/markdown",
    ".txt": "text/plain",
}
DEFAULT_CONTENT_TYPE = "application/octet-stream"


class OciConfigError(Exception):
    """Configuracao ausente ou invalida para falar com o OCI."""


class OciSdkNotInstalledError(Exception):
    """O pacote `oci` nao esta instalado neste ambiente."""


class OciSettings:
    """Configuracao de acesso ao Object Storage, sempre vinda do ambiente."""

    def __init__(self, bucket=None, namespace=None, config_file=None, profile=None, region=None):
        self.bucket = bucket or None
        self.namespace = namespace or None
        self.config_file = config_file or DEFAULT_CONFIG_FILE
        self.profile = profile or DEFAULT_PROFILE
        self.region = region or None

    @classmethod
    def from_env(cls, env=None):
        env = os.environ if env is None else env
        return cls(
            bucket=env.get("OCI_BUCKET_NAME"),
            namespace=env.get("OCI_NAMESPACE"),
            config_file=env.get("OCI_CONFIG_FILE"),
            profile=env.get("OCI_PROFILE"),
            region=env.get("OCI_REGION"),
        )

    @property
    def config_file_path(self):
        return Path(os.path.expanduser(self.config_file))

    def problems(self):
        """Lista legivel do que impede um upload real. Vazia = pronto para subir."""
        found = []
        if not self.bucket:
            found.append(
                "OCI_BUCKET_NAME nao definido - informe o bucket de destino "
                "(variavel de ambiente ou --bucket)."
            )
        if not self.config_file_path.exists():
            found.append(
                "arquivo de configuracao do OCI nao encontrado em "
                + str(self.config_file_path)
                + " - rode `oci setup config` ou aponte OCI_CONFIG_FILE."
            )
        return found

    def describe(self):
        """Resumo sem segredos, seguro para imprimir no terminal."""
        return [
            ("bucket", self.bucket or "(nao definido)"),
            ("namespace", self.namespace or "(sera resolvido pelo SDK)"),
            ("config file", str(self.config_file_path)),
            ("profile", self.profile),
            ("region", self.region or "(a do profile)"),
        ]


def validate_for_upload(settings):
    """Falha cedo e de forma compreensivel quando o OCI nao esta configurado."""
    problems = settings.problems()
    if problems:
        raise OciConfigError(
            "configuracao do OCI incompleta:\n  - " + "\n  - ".join(problems)
        )
    return True


def resolve_layers(choice):
    """Traduz o valor de `--layer` na tupla de camadas a sincronizar."""
    if choice is None or choice == LAYER_ALL:
        return LAYERS
    if choice in LAYERS:
        return (choice,)
    raise ValueError(
        "camada invalida: {0} (use {1})".format(choice, ", ".join(LAYER_CHOICES))
    )


def normalize_prefix(prefix):
    """Prefixo raiz opcional dentro do bucket, sempre terminando em `/`."""
    if not prefix:
        return ""
    cleaned = str(prefix).replace("\\", "/").strip("/")
    return cleaned + "/" if cleaned else ""


def to_object_name(local_path, data_lake_dir, prefix=""):
    """Converte um caminho local no nome do objeto no bucket.

    `data-lake/raw/2026/09/08/readings.jsonl` -> `raw/2026/09/08/readings.jsonl`
    """
    local_path = Path(local_path)
    base = Path(data_lake_dir)
    try:
        relative = local_path.resolve().relative_to(base.resolve())
    except ValueError:
        raise ValueError(
            "arquivo fora do Data Lake: {0} nao esta dentro de {1}".format(local_path, base)
        )
    return normalize_prefix(prefix) + relative.as_posix()


def content_type_for(path):
    return CONTENT_TYPES.get(Path(path).suffix.lower(), DEFAULT_CONTENT_TYPE)


def iter_layer_files(data_lake_dir, layer):
    """Todos os arquivos de uma camada, recursivamente e em ordem estavel."""
    layer_dir = Path(data_lake_dir) / layer
    if not layer_dir.is_dir():
        return []
    files = [
        path
        for path in layer_dir.rglob("*")
        if path.is_file() and path.name not in IGNORED_FILENAMES
    ]
    return sorted(files, key=lambda p: p.as_posix())


def plan_uploads(data_lake_dir, layers, prefix=""):
    """Lista de tuplas (caminho local, nome do objeto) para as camadas pedidas."""
    plan = []
    for layer in layers:
        for path in iter_layer_files(data_lake_dir, layer):
            plan.append((path, to_object_name(path, data_lake_dir, prefix)))
    return plan


def build_client(settings):
    """Cria o ObjectStorageClient oficial. Import tardio: o SDK e opcional."""
    try:
        import oci  # noqa: PLC0415 - dependencia opcional, so no upload real
    except ImportError as exc:
        raise OciSdkNotInstalledError(
            "pacote `oci` nao instalado. Rode: pip install -r etl/requirements-oci.txt"
        ) from exc

    config = oci.config.from_file(
        file_location=str(settings.config_file_path), profile_name=settings.profile
    )
    if settings.region:
        config["region"] = settings.region
    oci.config.validate_config(config)
    return oci.object_storage.ObjectStorageClient(config)


def resolve_namespace(client, settings):
    """Usa OCI_NAMESPACE quando definido; caso contrario pergunta ao proprio SDK."""
    if settings.namespace:
        return settings.namespace
    return client.get_namespace().data


def upload_file(client, namespace, bucket, object_name, local_path):
    """Envia um arquivo com `put_object`. Os objetos do Data Lake sao pequenos."""
    with open(local_path, "rb") as handle:
        client.put_object(
            namespace_name=namespace,
            bucket_name=bucket,
            object_name=object_name,
            put_object_body=handle,
            content_type=content_type_for(local_path),
        )
    return object_name
