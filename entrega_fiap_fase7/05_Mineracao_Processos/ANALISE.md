# Mineração de processos

A execução **aa88ffa21691**, de 24/11/2026, usou uma pilha PostgreSQL nova. As entradas foram simuladas, enquanto os registros vieram da API, do banco e do ETL em execução. A automação registrou 13 verificações, incluindo o HTTP 404 do sensor inexistente.

| Variante observada | Frequência | Caminho |
|---|---:|---|
| Leitura normal | 1 de 3 | Recebida → persistida → risco avaliado → RAW → TRUSTED → CURATED |
| Leitura com alerta | 1 de 3 | Recebida → persistida → risco avaliado → alerta gerado → RAW → TRUSTED → CURATED |
| Sensor inexistente | 1 de 3 | Recebida → rejeitada |

O [event log](dados/event_log.csv) contém **15 eventos de três casos**, todos com identificador próprio, timestamp UTC, atividade, recurso e status. O [log de lotes](dados/batch_log.csv) contém **dois eventos do lote relacionado**. O UUID de `case_id` nasce na ingestão. `reading_id` liga a leitura operacional ao evento RAW. `batch_id` identifica a execução compartilhada. Os eventos de inclusão em TRUSTED e publicação em CURATED representam a associação do caso ao primeiro lote que publicou esse caso. O tempo de um lote não foi copiado como duração de seus casos.

A maior mediana de transição observada foi **RAW → TRUSTED, 534,59 ms**, em duas observações. TRUSTED → CURATED teve mediana de **101,82 ms**, nas mesmas duas leituras. Os intervalos incluem espera pela execução do lote e gravação de eventos. Este ensaio tem apenas três casos e não representa latência de produção, escalabilidade ou um gargalo recorrente. O 404 mostra a recusa controlada antes de persistir. Diagnósticos futuros devem separar espera, processamento e I/O usando uma amostra maior.

[Resultados numéricos](dados/analise.json) · [Diagrama de transições](dados/processo.mmd) · [Gráficos PNG](dados/variantes-tempos.png) · [Gráficos SVG](dados/variantes-tempos.svg)

## Reprodução

Execute a plataforma e rode `.\scripts\demonstrar.ps1 -Mineracao -Resultado .\demo.json`. Copie os três arquivos de `/lake/events` do container backend. O analisador filtra apenas a origem registrada no JSON da demonstração:

```powershell
New-Item -ItemType Directory -Force .\eventos | Out-Null
foreach ($stream in 'api','memberships','batches') {
    docker compose exec -T backend cat "/lake/events/$stream.jsonl" > ".\eventos\$stream.jsonl"
}
python scripts/analisar_processo.py .\eventos .\demo.json .\mineracao
# Para regenerar PNG/SVG: instale matplotlib em um ambiente de análise e adicione --graficos
```

As [fontes da execução](../08_Evidencias/execucao-final/) incluem os JSONL de origem, a resposta da API, os indicadores e as capturas do navegador.
