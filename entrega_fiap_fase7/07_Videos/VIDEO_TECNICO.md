# Roteiro técnico · 6 min 50 s

**Preparação, fora da gravação.** Abra Docker Desktop e espere o engine Linux. Abra o PowerShell na raiz do projeto, o navegador em `http://127.0.0.1:8080/`, o [diagrama PNG](../01_Arquitetura/arquitetura.png), o relatório de [DevSecOps](../03_DevSecOps/DEVSECOPS.md) e o [gráfico de mineração](../05_Mineracao_Processos/dados/variantes-tempos.png). Execute `.\scripts\subir.ps1` antes se precisar baixar imagens. Feche abas particulares e mantenha `.env` e telas com credenciais fora da captura. Use o mesmo ambiente ao filmar os terminais e o navegador.

## 00:00–00:35 · Visão geral

**Tela.** Abra o PDF na capa e depois mostre a página inicial do aplicativo. **Fala.** “Este é o Orbital Alert, o MVP acadêmico da Fase 7. Ele ajuda uma equipe municipal a acompanhar leituras e alertas de enchente. Vou mostrar a execução desde o simulador até o dashboard e, depois, como a plataforma registra o que aconteceu. O sensor e as leituras são simulados. As chamadas, os bancos, a execução dos ETLs e a interface são reais neste ambiente local.”

## 00:35–01:25 · Arquitetura

**Tela.** Abra o diagrama arquitetural. Aponte primeiro para API e PostgreSQL, depois para RAW, TRUSTED, CURATED e dashboard. **Fala.** “O simulador chama a API Spring Boot. A leitura é gravada no PostgreSQL e a regra de limiar pode gerar um alerta na mesma operação. A API também vincula a leitura a um evento RAW. O job Python valida os eventos, produz TRUSTED e agrega o risco por região em CURATED. O dashboard consulta esse score com a origem e o horário. O Oracle local é uma cópia analítica opcional. A recomendação é consultiva e aparece identificada como MOCK nesta demo.”

## 01:25–02:10 · Serviços no ar e entrada

**Tela.** No PowerShell, mostre estes comandos e os estados saudáveis. Aguarde ou use um corte anunciado se o primeiro build levar tempo.

```powershell
.\scripts\subir.ps1
docker compose ps -a
Invoke-RestMethod http://127.0.0.1:8080/api/health
```

**Fala.** “O script cria a configuração local e sobe a pilha. O PostgreSQL operacional, o backend e o job ficam na rede do Compose. Apenas o frontend é publicado em loopback. O serviço schema termina com sucesso depois de aplicar a estrutura. O health da API confirma que ela consegue consultar o banco.”

## 02:10–03:35 · Cenário, prova e painel

**Tela.** Execute:

```powershell
.\scripts\demonstrar.ps1 -Mineracao -Resultado .\demo.json
$demo = Get-Content .\demo.json -Raw | ConvertFrom-Json
$demo.checks
$demo.region.name
```

Mostre o ID e o nome da nova região. No navegador, clique **Abrir painel** ou **Atualizar dados**, selecione essa região e aponte para o alerta, leitura mais recente, Risk Score/indicadores e fonte. Clique **Consultar recomendação** e aguarde o texto. **Fala.** “Criamos uma região e um sensor de chuva com IDs fornecidos pela API. A leitura de 45 mm/h foi gravada sem alerta. A leitura de 95 superou o limiar de 60 e abriu um alerta alto. O script também enviou uma leitura para um sensor inexistente e confirmou a rejeição HTTP 404. No dashboard, esta é a mesma região do terminal. A média da rodada foi 70 mm/h. O score é 100 na regra acadêmica e veio do CURATED. Esse número pertence ao cenário. A recomendação aparece como MOCK e depende da avaliação de quem opera.”

## 03:35–04:30 · CI e segurança

**Tela.** Abra [Actions 45422251550](https://github.com/Vitorfs2509/orbital-alert-fiap-gs2026/actions/runs/45422251550) ou o [registro dos jobs](../03_DevSecOps/evidencias/github-actions.json). Mostre os jobs Java, Python, web e Compose. **Fala.** “Java, Python, compilação web e smoke integrado passaram na execução publicada. O job web falhou no npm audit e o job Compose falhou na verificação de imagens com Trivy. O pipeline preservou os relatórios e deixou as falhas visíveis. Na API, a ingestão exige a credencial de sensor, e mudanças administrativas usam outro papel. A chamada sem credencial recebeu 401 e um papel incorreto recebeu 403 nos testes.”

## 04:30–05:25 · Observabilidade

**Tela.** Execute:

```powershell
Invoke-RestMethod http://127.0.0.1:8080/api/status | ConvertTo-Json -Depth 10
docker compose logs --tail 12 scheduler
```

Abra, se necessário, a [evidência de falha e concorrência](../04_Monitoramento/evidencias/indicadores.json). **Fala.** “O status expõe contadores reais desde a inicialização e os alertas ativos no banco. O mesmo JSON identifica o último lote e o último sucesso. O agendador reutiliza a trava do job manual. No ensaio separado, observamos um novo lote periódico, uma tentativa bloqueada por concorrência e uma falha controlada que conservou o último sucesso. O Actuator mantém as métricas detalhadas acessíveis apenas na rede interna com credencial administrativa.”

## 05:25–06:35 · Mineração de processos

**Tela.** Abra o [CSV](../05_Mineracao_Processos/dados/event_log.csv), o [log de lote](../05_Mineracao_Processos/dados/batch_log.csv) e o [gráfico](../05_Mineracao_Processos/dados/variantes-tempos.png). Destaque `case_id`, `event_id`, `timestamp`, `batch_id` e o 404 na trilha. **Fala.** “O estudo capturou três casos e 15 eventos. O lote tem seu log separado com dois eventos. No caminho normal, a leitura chega ao CURATED. No caminho com alerta, aparece uma atividade adicional. O sensor inexistente encerra o caso como rejeitado. Neste ensaio, RAW para TRUSTED teve a maior mediana entre eventos, cerca de 535 milissegundos em duas observações. A medida inclui espera pela publicação em lote e não caracteriza latência nem gargalo de produção.”

## 06:35–06:50 · Encerramento

**Tela.** Volte ao painel e mostre a página inicial do relatório. **Fala.** “A entrega inclui código, instruções de reprodução e evidências para conferir o mesmo fluxo. O próximo passo é validar sensores em campo e testar o uso com uma equipe municipal em condições controladas.”

**Após gravar.** Revise o áudio, as janelas e a duração. Insira o URL real no [arquivo de links](LINKS_DOS_VIDEOS.md).
