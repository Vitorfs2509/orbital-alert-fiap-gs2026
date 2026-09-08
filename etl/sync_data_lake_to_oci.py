#!/usr/bin/env python3
"""Sincroniza o Data Lake local do Orbital Alert com o OCI Object Storage.

Envia recursivamente `data-lake/raw/**`, `data-lake/trusted/**` e
`data-lake/curated/**` para um bucket do Oracle Cloud Infrastructure,
preservando a estrutura relativa dos arquivos:

    LOCAL  data-lake/raw/2026/09/08/readings-2026-09-08.jsonl
    OCI    raw/2026/09/08/readings-2026-09-08.jsonl

A integracao e OPCIONAL: nada no projeto depende dela para rodar localmente.
Sem credenciais, use `--dry-run` para conferir exatamente o que seria enviado.

Uso:
    python etl/sync_data_lake_to_oci.py --dry-run
    python etl/sync_data_lake_to_oci.py --layer curated --dry-run
    python etl/sync_data_lake_to_oci.py                      # upload real
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_ETL_DIR = Path(__file__).resolve().parent
if str(_ETL_DIR) not in sys.path:
    sys.path.insert(0, str(_ETL_DIR))

from oci_storage import (  # noqa: E402 - depois do ajuste de sys.path
    DEFAULT_DATA_LAKE_DIR,
    LAYER_ALL,
    LAYER_CHOICES,
    OciConfigError,
    OciSdkNotInstalledError,
    OciSettings,
    build_client,
    plan_uploads,
    resolve_layers,
    resolve_namespace,
    upload_file,
    validate_for_upload,
)

EXIT_OK = 0
EXIT_CONFIG_ERROR = 1
EXIT_UPLOAD_ERROR = 2


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Sincroniza as camadas do Data Lake com o OCI Object Storage."
    )
    parser.add_argument(
        "--layer",
        choices=list(LAYER_CHOICES),
        default=LAYER_ALL,
        help="camada a sincronizar (padrao: all)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="apenas lista o que seria enviado; nao acessa a Oracle",
    )
    parser.add_argument(
        "--data-lake-dir",
        default=str(DEFAULT_DATA_LAKE_DIR),
        help="raiz do Data Lake local (padrao: data-lake)",
    )
    parser.add_argument(
        "--bucket",
        default=None,
        help="bucket de destino (sobrepoe OCI_BUCKET_NAME)",
    )
    parser.add_argument(
        "--prefix",
        default="",
        help="prefixo raiz opcional dentro do bucket (ex.: orbital-alert)",
    )
    return parser.parse_args(argv)


def human_size(num_bytes):
    if num_bytes < 1024:
        return "{0} B".format(num_bytes)
    if num_bytes < 1024 * 1024:
        return "{0:.1f} KB".format(num_bytes / 1024)
    return "{0:.1f} MB".format(num_bytes / (1024 * 1024))


def print_settings(settings):
    print("\n--- Configuracao OCI ---")
    for label, value in settings.describe():
        print("  {0:<12}: {1}".format(label, value))


def main(argv=None):
    args = parse_args(argv)

    data_lake_dir = Path(args.data_lake_dir)
    layers = resolve_layers(args.layer)

    print("=" * 62)
    print("Orbital Alert - sync Data Lake -> OCI Object Storage")
    print("=" * 62)
    print("Data Lake local : " + str(data_lake_dir))
    print("Camadas         : " + ", ".join(layers))
    print("Modo            : " + ("DRY-RUN (nenhum acesso a Oracle)" if args.dry_run else "UPLOAD REAL"))

    if not data_lake_dir.is_dir():
        print("\nERRO: Data Lake local nao encontrado em " + str(data_lake_dir))
        return EXIT_CONFIG_ERROR

    settings = OciSettings.from_env()
    if args.bucket:
        settings.bucket = args.bucket
    print_settings(settings)

    plan = plan_uploads(data_lake_dir, layers, args.prefix)
    if not plan:
        print("\nAVISO: nenhum arquivo encontrado nas camadas selecionadas.")
        print("Rode os ETLs antes: python etl/raw_to_trusted.py && python etl/trusted_to_curated.py")
        return EXIT_OK

    total_bytes = sum(path.stat().st_size for path, _ in plan)

    if args.dry_run:
        print("\n--- Arquivos que seriam enviados ---")
        for path, object_name in plan:
            print("[OCI] {0} -> DRY-RUN ({1})".format(object_name, human_size(path.stat().st_size)))
        print("\nArquivos planejados : {0}".format(len(plan)))
        print("Volume total        : {0}".format(human_size(total_bytes)))
        pending = settings.problems()
        if pending:
            print("\nNota: em modo real esta configuracao ainda precisaria de:")
            for problem in pending:
                print("  - " + problem)
        print("\nOK: dry-run concluido. Nenhum dado saiu desta maquina.")
        return EXIT_OK

    try:
        validate_for_upload(settings)
        client = build_client(settings)
        namespace = resolve_namespace(client, settings)
    except (OciConfigError, OciSdkNotInstalledError) as exc:
        print("\nERRO: " + str(exc))
        print("\nA integracao OCI e opcional. Para conferir os caminhos sem credenciais:")
        print("  python etl/sync_data_lake_to_oci.py --dry-run")
        print("Configuracao documentada em docs/oracle-integration.md")
        return EXIT_CONFIG_ERROR

    print("  {0:<12}: {1}".format("namespace", namespace))
    print("\n--- Upload ---")

    sent = 0
    failed = []
    for path, object_name in plan:
        try:
            upload_file(client, namespace, settings.bucket, object_name, path)
        except Exception as exc:  # o SDK levanta varios tipos; nao ha o que retentar aqui
            failed.append((object_name, str(exc)))
            print("[OCI] {0} -> FALHOU".format(object_name))
            continue
        sent += 1
        print("[OCI] {0} -> OK".format(object_name))

    print("\n--- Resumo ---")
    print("Bucket              : {0}".format(settings.bucket))
    print("Arquivos enviados   : {0}/{1}".format(sent, len(plan)))
    print("Volume total        : {0}".format(human_size(total_bytes)))

    if failed:
        print("Arquivos com falha  : {0}".format(len(failed)))
        for object_name, message in failed:
            print("  - {0}: {1}".format(object_name, message))
        return EXIT_UPLOAD_ERROR

    print("\nOK: Data Lake sincronizado com o OCI Object Storage.")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
