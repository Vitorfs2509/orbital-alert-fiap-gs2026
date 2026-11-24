# Monitoramento e automação

A plataforma sobe com um agendador Python. `ETL_INTERVAL_SECONDS` define o intervalo em segundos (padrão 300). O agendador e o job manual usam a mesma trava do volume `lake`. Uma tentativa periódica concorrente registra `SKIPPED_LOCKED`, sem sobrescrever o estado do lote em andamento. O job manual aguarda a trava por até 60 segundos. O processamento registra início, fim, duração e resultado em UTC. O estado compartilhado é publicado por troca atômica e mantém separados o último sucesso e a tentativa mais recente.

```powershell
docker compose ps -a
Invoke-RestMethod http://127.0.0.1:8080/api/health
Invoke-RestMethod http://127.0.0.1:8080/api/status | ConvertTo-Json -Depth 10
docker compose logs --tail 30 backend scheduler
docker compose run --rm -T etl
```

| Campo | Semântica |
|---|---|
| `readingsReceived` | Chamadas autorizadas com payload válido que chegam ao serviço de leituras. |
| `readingsProcessed` | Leituras que completaram persistência e avaliação operacional. |
| `readingFailures` | Falhas do serviço, incluindo sensor ausente. Requisições rejeitadas antes do serviço ficam fora. |
| `rawFailures` | Tentativas de gravação RAW com falha enquanto o Lake está ativo. |
| `alertsGenerated` | Alertas criados pela ingestão desde a inicialização do processo. |
| `alertsActive` | Total atual no PostgreSQL dos estados OPEN e MONITORING. |
| `etl.lastAttempt` e `etl.lastSuccess` | Estado do agendamento e estatísticas reais do processamento. |

O Actuator expõe health e métricas na rede interna. A autenticação de administração continua necessária:

```powershell
docker compose exec backend sh -c 'curl -fsS -H "Authorization: Bearer $ORBITAL_ADMIN_TOKEN" http://localhost:8080/actuator/metrics/orbital.readings.processed'
```

Os contadores Micrometer reiniciam junto com o processo Java. O Lake armazena o estado do último ETL no volume persistente. Os logs de ingestão JSON identificam operações e IDs técnicos sem registrar credenciais. O estado `FAILED` conserva o último sucesso para diagnóstico. O painel integrado continua lendo o último snapshot disponível.

A validação está em [evidências](evidencias/). O health verifica disponibilidade, não comprova atualidade de todo o histórico. Validação de recuperação, retenção de longa duração e séries históricas de métricas ficam como evolução.
