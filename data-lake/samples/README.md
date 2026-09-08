# data-lake/samples

Dados de exemplo usados para demonstrar o pipeline RAW -> TRUSTED -> CURATED
sem depender do backend estar em execucao.

## Arquivos

| Arquivo | Descricao |
|---|---|
| `raw_sample.jsonl` | 28 eventos brutos no mesmo formato gravado pelo backend na camada RAW |
| `regions.json` | Mapa `regionId -> nome da regiao` (espelha `database/seed.sql`), usado para enriquecer a camada CURATED |

## Problemas de qualidade propositais em `raw_sample.jsonl`

O arquivo foi montado para exercitar todas as regras do ETL:

| Linha (eventId final) | Problema | Tratamento esperado |
|---|---|---|
| `...000003` (repetido) | Duplicata exata (mesmo `eventId`) | Descartada por deduplicacao tecnica |
| `...000099` | Duplicata logica (mesmo sensor/instante/valor, `eventId` diferente) | Descartada por deduplicacao de negocio |
| `...000101` | `value` nulo | Rejeitado: `missing_value` |
| `...000102` | `measuredAt` invalido | Rejeitado: `invalid_measured_at` |
| `...000103` | `sensorId` nulo | Rejeitado: `missing_sensor_id` |
| `...000104` | `value` = 99999 (fora da faixa fisica) | Rejeitado: `value_out_of_range` |
| `...000105` | `sensorType` = `PRESSURE` (sem regra de risco) | Aceito no TRUSTED, ignorado no calculo de risco do CURATED |

## Como executar

```powershell
python etl/raw_to_trusted.py --raw-dir data-lake/samples
python etl/trusted_to_curated.py
```
