# Plataforma integrada · execução no Windows

Pré-requisitos: Docker Desktop com engine Linux em execução, Docker Compose v2 ou posterior, PowerShell e acesso aos registries/dependências para o primeiro build. Os containers fornecem Java 21, Node, Python e PostgreSQL. Rode os comandos na raiz do repositório da Fase 7.

```powershell
.\scripts\subir.ps1
.\scripts\demonstrar.ps1 -Mineracao -Resultado .\demo-fase7.json
```

Abra **http://127.0.0.1:8080/** (ou a porta mostrada pelo script) e clique em **Abrir painel**. Antes da demonstração, um volume novo apresenta listas vazias. Depois, use **Atualizar dados**, abra a região **AgroSmart · Demo …** e verifique alerta, última leitura, Risk Score IoT, indicadores e recomendação consultiva. O botão de recomendação faz uma chamada separada. Com `AI_PROVIDER=mock`, o texto é determinístico e o painel exibe `MOCK`.

```powershell
docker compose ps -a
docker compose logs --tail 100 schema backend frontend
Invoke-RestMethod http://127.0.0.1:8080/api/health
Invoke-RestMethod http://127.0.0.1:8080/api/risk
.\scripts\encerrar.ps1
```

O primeiro comando cria `.env` local e gera as credenciais. O encerramento preserva os volumes. Ao subir novamente, banco, alertas e Lake continuam disponíveis. `ORBITAL_WEB_PORT` altera a porta local. É possível passar `-EnvFile` aos três scripts para usar um arquivo de configuração local separado. Para isolar ensaios, use um `COMPOSE_PROJECT_NAME` próprio no arquivo, além de uma porta livre. O banco e o backend ficam na rede interna do projeto. O único endereço publicado pelo Compose padrão é o frontend em loopback. As escritas exigem credenciais de serviço distintas; as consultas do painel permanecem locais e públicas.

## O que o cenário comprova

O job Python usa IDs devolvidos pela API e cria uma região por rodada. O simulador envia `45` e `95` mm/h para um sensor `RAINFALL`. A leitura de 45 fica abaixo do limiar de alerta (60). A segunda gera um alerta `HIGH`. O teste confirma leitura persistida, alerta, os dois IDs operacionais no RAW, os UUIDs dos eventos no TRUSTED e o score do CURATED exposto pela API do painel. Cada rodada acrescenta dados ao volume. Use uma pilha recém-criada para reproduzir o estado vazio.

| Componente | Entradas e saídas |
|---|---|
| `postgres` / `schema` | `pgdata`; job aplica o schema e a migração `001_rainfall.sql` em transação. O backend aguarda a conclusão e valida mapeamentos JPA. |
| `backend` | `POST /api/readings`, PostgreSQL operacional, regras de limiar e registro RAW. `GET /api/health` consulta o banco e é usado pelo Compose. |
| `etl` | Job sob demanda no perfil `jobs`. Lê o RAW, gera TRUSTED e CURATED no mesmo volume `lake`, usa nomes atuais de regiões retornados pela API. |
| `frontend` | Expo estático servido por Nginx, que encaminha `/api` internamente. Consome regiões, sensores, alertas ativos, últimas leituras, score e indicadores. |
| `oracle` / `oracle-sync` | Perfil opcional. O job lê CURATED e faz `MERGE` no Oracle local. O PostgreSQL segue responsável pelo fluxo operacional. |

Os dados do simulador são artificiais. As chamadas HTTP, gravações, processamento e capturas do painel são verificações reais quando executadas. O valor cadastral `satelliteRiskScore` é distinto do Risk Score IoT exibido no painel. Com CURATED disponível, o painel mostra a origem e o horário do snapshot. Antes do ETL para uma região, usa o risco calculado sobre o banco operacional e mostra essa origem. O score pode ficar defasado em relação às últimas leituras até o próximo ETL.

## Executar jobs individualmente

```powershell
docker compose build etl
docker compose run --rm -T etl
docker compose build simulator
docker compose run --rm -T simulator python iot-simulator/sensor_simulator.py --sensor-id <ID_EXISTENTE> --value 95
```

O comando padrão de `etl` reprocessa sem inserir leituras. O agendador e os jobs manuais compartilham a [trava de execução](../04_Monitoramento/MONITORAMENTO.md). O fallback offline do simulador usa `IOT_OFFLINE_FILE` no caminho temporário do container. Uma falha retorna código diferente de zero e o arquivo temporário não é uma fila de reenvio.

## Oracle opcional

Preencha `ORACLE_ADMIN_PASSWORD` e `ORACLE_DB_PASSWORD` no mesmo `.env` local. Opcionalmente defina `ORACLE_DB_USER` (padrão `ORBITAL_ALERT`). As senhas de inicialização são aplicadas na criação do volume Oracle. Mudanças posteriores devem ser feitas na instância conforme a administração do banco.

```powershell
.\scripts\demonstrar.ps1 -Oracle -Resultado .\demo-fase7.json
# Para sincronizar de novo, sem gerar novas leituras:
docker compose --profile oracle run --build --rm -T oracle-sync
# Dry-run do mesmo CURATED a partir do job Python. Sem conexão Oracle:
docker compose run --rm -T etl python etl/sync_curated_to_oracle.py --dry-run --curated-dir /lake/curated
```

O Oracle leva mais tempo para inicializar e pode exigir mais recursos do Docker Desktop. O job usa o driver Python em modo thin. Nenhuma porta Oracle é publicada. OCI Object Storage continua separado do cenário.

## Verificação de navegador

O smoke visual opcional usa [Playwright](https://playwright.dev/docs/api/class-browsertype) em pasta separada e Chromium/Edge instalado. Com as variáveis configuradas, rode `empty` em pilha nova, `populated` após o cenário e `unavailable` após parar apenas o backend da pilha de teste. O smoke usa os IDs e o score do JSON do cenário.

```powershell
$verificador = Join-Path $env:TEMP 'orbital-browser-check'
npm.cmd install --prefix $verificador --no-audit --no-fund playwright-core@1.65.1
$env:NODE_PATH = Join-Path $verificador 'node_modules'
$env:CHROMIUM_EXECUTABLE = 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
$env:ORBITAL_WEB_URL = 'http://127.0.0.1:8080/'
node scripts/validar_web.cjs populated .\capturas .\demo-fase7.json
```

O [guia do Expo](../../mobile/README.md) explica o modo local de demonstração e a configuração nativa. A validação desta etapa cobre a versão web.
