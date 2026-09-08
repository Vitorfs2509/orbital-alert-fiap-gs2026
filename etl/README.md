# ETL — Orbital Alert (Fases 5 e 6)

Scripts de processamento do Data Lake. Os ETLs usam **somente a biblioteca padrão do
Python 3** — nenhuma dependência externa é necessária para o pipeline local.

| Script | Entrada | Saída | Dependências |
|---|---|---|---|
| `raw_to_trusted.py` | `data-lake/raw/` | `data-lake/trusted/` | stdlib |
| `trusted_to_curated.py` | `data-lake/trusted/` | `data-lake/curated/` | stdlib |
| `sync_data_lake_to_oci.py` | `data-lake/{raw,trusted,curated}/` | bucket OCI Object Storage | `oci` (opcional) |
| `oci_storage.py` | — | módulo de apoio do script acima | stdlib (import do `oci` é tardio) |

Execute sempre a partir da **raiz do repositório**.

## Uso rápido

```powershell
# Demonstração com os dados de exemplo (não precisa do backend no ar)
python etl/raw_to_trusted.py --raw-dir data-lake/samples
python etl/trusted_to_curated.py

# Fluxo real, com eventos gravados pela API
python etl/raw_to_trusted.py
python etl/trusted_to_curated.py

# Fase 6 — o que subiria para a Oracle (não acessa a rede)
python etl/sync_data_lake_to_oci.py --dry-run
```

## `raw_to_trusted.py`

Lê os eventos brutos, aplica as regras de qualidade e grava a camada confiável.

| Argumento | Padrão | Descrição |
|---|---|---|
| `--raw-dir` | `data-lake/raw` | Diretório da camada RAW |
| `--trusted-dir` | `data-lake/trusted` | Diretório da camada TRUSTED |
| `--date` | todas | Processa só uma partição (`--date 2026-09-08`) |

O que faz:

1. varre recursivamente as partições `AAAA/MM/DD/`, lendo `.jsonl` e `.json`;
2. valida campos obrigatórios, tipos e faixa plausível;
3. padroniza timestamps para UTC ISO-8601 e normaliza o tipo de sensor (`RAIN` → `RAINFALL`);
4. remove duplicatas por `eventId` e por chave de negócio (`sensorId` + `measuredAt` + `value`);
5. grava `readings.jsonl` e `readings.csv`;
6. registra estatísticas em `_quality/stats_<runId>.json` e os registros barrados em
   `_quality/rejected_<runId>.jsonl`.

Arquivos iniciados por `_` e o arquivo de referência `regions.json` são ignorados na varredura.

## `trusted_to_curated.py`

Agrega por região e calcula o score de risco.

| Argumento | Padrão | Descrição |
|---|---|---|
| `--trusted-dir` | `data-lake/trusted` | Diretório da camada TRUSTED |
| `--curated-dir` | `data-lake/curated` | Diretório da camada CURATED |
| `--regions` | `data-lake/samples/regions.json` | Mapa `regionId` → nome da região |

O que faz:

1. agrupa as leituras por região;
2. calcula por tipo de sensor: `samples`, média, mínimo, máximo, último valor e tendência;
3. converte cada média em sub-score 0–100 comparando com o limiar de alerta do backend;
4. combina os sub-scores no score da região e classifica em `LOW` / `MEDIUM` / `HIGH`;
5. grava JSON (consumido pela IA) e CSV (analytics).

A fórmula está documentada em
[../docs/data-lake-architecture.md](../docs/data-lake-architecture.md#4-modelo-de-risco-curated).

> As regras de risco existem em dois lugares que precisam ficar sincronizados:
> `RISK_RULES` neste script e `RULES` em `backend/.../service/RiskScoreCalculator.java`,
> usado como fallback quando o ETL ainda não rodou.

## `sync_data_lake_to_oci.py` (Fase 6 — opcional)

Envia as camadas do Data Lake local para um bucket do **Oracle Cloud Infrastructure
Object Storage**, preservando a estrutura relativa dos arquivos:

```
LOCAL  data-lake/raw/2026/09/08/readings-2026-09-08.jsonl
OCI    raw/2026/09/08/readings-2026-09-08.jsonl
```

| Argumento | Padrão | Descrição |
|---|---|---|
| `--layer` | `all` | `raw`, `trusted`, `curated` ou `all` |
| `--dry-run` | desligado | lista o que seria enviado; **não acessa a Oracle** |
| `--data-lake-dir` | `data-lake` | raiz do Data Lake local |
| `--bucket` | `OCI_BUCKET_NAME` | sobrepõe o bucket de destino |
| `--prefix` | vazio | prefixo raiz opcional dentro do bucket |

Configuração por variáveis de ambiente (`OCI_BUCKET_NAME`, `OCI_NAMESPACE`,
`OCI_CONFIG_FILE`, `OCI_PROFILE`, `OCI_REGION`) e/ou pelo arquivo padrão
`~/.oci/config` do SDK. **Nenhuma credencial fica no código nem no repositório.**

> **A integração é opcional.** O import do pacote `oci` acontece só no upload real:
> `--dry-run`, os ETLs, o backend, o simulador e os testes rodam sem internet, sem
> conta Oracle e sem instalar nada.

Passo a passo completo (criação do bucket, credenciais, upload real e evidências)
em [../docs/oracle-integration.md](../docs/oracle-integration.md).

## Testes

```powershell
python etl/tests/test_oci_sync.py
# ou
python -m unittest discover -s etl/tests
```

25 testes com `unittest` da stdlib. Nenhuma chamada real ao OCI: o
`ObjectStorageClient` é substituído por um duble.

## Idempotência

Reexecutar sobre o mesmo RAW produz exatamente o mesmo TRUSTED: os arquivos de saída são
reescritos (não acrescidos) e a deduplicação ocorre dentro da própria execução. O RAW nunca é
modificado, o que permite reprocessar todo o histórico se uma regra de qualidade mudar.
