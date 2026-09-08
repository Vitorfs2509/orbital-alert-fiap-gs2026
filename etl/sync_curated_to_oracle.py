#!/usr/bin/env python3
"""Sincroniza a camada CURATED do Orbital Alert com o Oracle AI Database Free.

Le `data-lake/curated/region_risk_latest.json` (ou o CSV equivalente) e grava
cada regiao na tabela analitica `REGION_RISK_SUMMARY`:

    LOCAL   data-lake/curated/region_risk_latest.json
    ORACLE  REGION_RISK_SUMMARY (REGION_ID, GENERATED_AT)

O Oracle NAO substitui o banco operacional (H2 / PostgreSQL): ele e uma
persistencia analitica adicional, alimentada pela ponta do Data Lake.

A carga e idempotente - rodar duas vezes o mesmo snapshot atualiza a linha em
vez de duplicar. Sem banco disponivel, use `--dry-run` para conferir exatamente
o que seria gravado.

Uso:
    python etl/sync_curated_to_oracle.py --dry-run
    python etl/sync_curated_to_oracle.py                 # carga real
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_ETL_DIR = Path(__file__).resolve().parent
if str(_ETL_DIR) not in sys.path:
    sys.path.insert(0, str(_ETL_DIR))

from oracle_database import (  # noqa: E402 - depois do ajuste de sys.path
    DEFAULT_CURATED_DIR,
    TABLE_NAME,
    CuratedDataError,
    OracleConfigError,
    OracleDriverNotInstalledError,
    OracleSettings,
    build_rows,
    connect,
    count_rows,
    ensure_table,
    format_row,
    load_curated_regions,
    merge_row,
    validate_for_connection,
)

EXIT_OK = 0
EXIT_CONFIG_ERROR = 1
EXIT_LOAD_ERROR = 2


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Sincroniza a camada CURATED com o Oracle AI Database Free."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="apenas lista o que seria gravado; nao acessa o banco",
    )
    parser.add_argument(
        "--curated-dir",
        default=str(DEFAULT_CURATED_DIR),
        help="diretorio da camada CURATED (padrao: data-lake/curated)",
    )
    return parser.parse_args(argv)


def print_settings(settings):
    print("\n--- Conexao Oracle ---")
    for label, value in settings.describe():
        print("  {0:<10}: {1}".format(label, value))


def main(argv=None):
    args = parse_args(argv)
    curated_dir = Path(args.curated_dir)

    print("=" * 62)
    print("Orbital Alert - sync CURATED -> Oracle AI Database Free")
    print("=" * 62)
    print("CURATED local   : " + str(curated_dir))
    print("Tabela destino  : " + TABLE_NAME)
    print("Modo            : " + ("DRY-RUN (nenhum acesso ao banco)" if args.dry_run else "CARGA REAL"))

    try:
        regions, source = load_curated_regions(curated_dir)
        rows = build_rows(regions, source)
    except CuratedDataError as exc:
        print("\nERRO: " + str(exc))
        return EXIT_CONFIG_ERROR

    print("Arquivo lido    : " + str(source))

    settings = OracleSettings.from_env()
    print_settings(settings)

    if not rows:
        print("\nAVISO: a camada CURATED nao tem nenhuma regiao.")
        print("Rode os ETLs antes: python etl/raw_to_trusted.py && python etl/trusted_to_curated.py")
        return EXIT_OK

    if args.dry_run:
        print("\n--- Registros que seriam gravados ---")
        for row in rows:
            print("[ORACLE] {0} -> DRY-RUN".format(format_row(row)))
        print("\nRegistros planejados : {0}".format(len(rows)))
        pending = settings.problems()
        if pending:
            print("\nNota: em modo real esta configuracao ainda precisaria de:")
            for problem in pending:
                print("  - " + problem)
        print("\nOK: dry-run concluido. Nenhuma conexao foi aberta.")
        return EXIT_OK

    try:
        validate_for_connection(settings)
        connection = connect(settings)
    except (OracleConfigError, OracleDriverNotInstalledError) as exc:
        print("\nERRO: " + str(exc))
        print("\nPara conferir os registros sem banco:")
        print("  python etl/sync_curated_to_oracle.py --dry-run")
        print("Configuracao documentada em docs/oracle-database-integration.md")
        return EXIT_CONFIG_ERROR
    except Exception as exc:  # falha de rede / credencial: o driver levanta varios tipos
        print("\nERRO ao conectar em {0}: {1}".format(settings.dsn, exc))
        print("\nO container esta de pe? docker ps --filter name=orbital-alert-oracle")
        return EXIT_CONFIG_ERROR

    print("\n--- Carga ---")
    merged = 0
    failed = []
    try:
        created = ensure_table(connection)
        print("Tabela {0} : {1}".format(TABLE_NAME, "criada" if created else "ja existia"))

        with connection.cursor() as cursor:
            for row in rows:
                try:
                    merge_row(cursor, row)
                except Exception as exc:
                    failed.append((format_row(row), str(exc)))
                    print("[ORACLE] {0} -> FALHOU".format(format_row(row)))
                    continue
                merged += 1
                print("[ORACLE] {0} -> OK".format(format_row(row)))

        if failed:
            connection.rollback()
        else:
            connection.commit()

        total = count_rows(connection)
    finally:
        connection.close()

    print("\n--- Resumo ---")
    print("Banco               : {0}".format(settings.dsn))
    print("Registros gravados  : {0}/{1}".format(merged, len(rows)))
    print("Linhas na tabela    : {0}".format(total))

    if failed:
        print("Registros com falha : {0} (transacao revertida)".format(len(failed)))
        for label, message in failed:
            print("  - {0}: {1}".format(label, message))
        return EXIT_LOAD_ERROR

    print("\nOK: camada CURATED sincronizada com o Oracle AI Database Free.")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
