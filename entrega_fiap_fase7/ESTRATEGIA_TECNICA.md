# Estratégia técnica e arquivos previstos

O plano abaixo descreve alterações propostas após a auditoria. A base mantém o contrato operacional do Orbital Alert. Cada etapa terá evidências, arquivos salvos e commit local próprio.

## Próxima etapa · Plataforma integrada e Docker

1. **Validar o ambiente e a persistência.** Confirmar disponibilidade do Docker Desktop e build Java 21. Padronizar `RAINFALL`, preservar restrições e preparar ajuste explícito para dados legados. Usar volumes nomeados, schema versionado e bootstrap verificável, com teste de instância nova e reinício com volume já populado. Manter `dev` para H2 e um perfil integrado para PostgreSQL. Criar os dados da demonstração por API ou fixture explícita, sem partir de IDs fixos ou usuários com hashes ilustrativos.
2. **Orquestrar a pilha existente.** Imagens para API Java 21, Expo web e ferramentas Python. Rede interna com PostgreSQL e processos sem portas públicas. Publicar apenas o frontend em loopback por padrão e encaminhar `/api` à API por proxy. Compartilhar volume do Lake entre API e ETL; o frontend consome resultados via API. O ETL manual e o simulador serão tarefas executadas sob demanda nesta etapa. A execução periódica entra na Etapa 4. Oracle usa perfil opcional e volume próprio, sujeito à disponibilidade do software.
3. **Integrar o painel.** Usar os contratos de regiões, sensores, leituras e alertas, corrigindo a consulta das últimas leituras quando necessário. Expor leitura do Risk Score e indicadores sem disparar chamadas a IA para carregar o dashboard. Mostrar a origem, horário, estados vazio/erro e opção de atualizar. O modo demo será explícito. Preservar opção de URL configurável para o Expo nativo. Preparar contrato comum para a proteção de identidade e papéis da Etapa 3. A fase intermediária é para uso local.
4. **Demonstrar o fluxo com IDs correlacionáveis.** Adaptar o harness da Fase 6. Criar região/sensor isolados, usar leituras abaixo e acima do limiar, validar IDs recebidos, persistência e alerta, executar o ETL no Lake da mesma execução e conferir score/indicadores via API e painel. Capturar o dashboard web com dados reais da API e testar resposta vazia e indisponibilidade. Recomendação padrão identificada como mock consultivo. A sincronização Oracle só será executada com o perfil disponível. Um dry-run será registrado como tal.

### Critério de aceite da Etapa 2

- `docker compose config` e build das imagens concluem. Frontend/ API respondem e o PostgreSQL fica saudável com a modelagem real.
- Cadastro e leitura de `RAINFALL` funcionam; reiniciar preserva registros. O banco operacional fica na rede interna.
- O cenário gera evidências verificáveis: dados simulados enviados por HTTP, leitura persistida, condição normal sem novo alerta, limiar com novo alerta, RAW/TRUSTED/CURATED e Risk Score exibido no navegador com origem indicada.
- Falha ou vazio da API permanece explícita no dashboard. Scripts de subir, demonstrar e encerrar retornam códigos úteis e o encerramento padrão conserva dados. Capturas têm legenda e registro de execução.
- Oracle opcional tem resultado separado. Se o daemon permanecer indisponível, comunicar quais verificações ficaram bloqueadas e preservar as evidências obtidas até então.

## Etapas seguintes

| Etapa | Decisão técnica proposta | Evidência de aceite |
|---|---|---|
| 3 · DevSecOps | Usar proteção Spring Security com identidades controladas e papéis; separar ingestão, consulta e administração. Aplicar autorização no servidor, remover escolha pública de papel e validar sessão ou credencial por cliente. Para o web, usar mesma origem e resolver CSRF segundo o mecanismo de autenticação escolhido. CI com Maven/Java 21, JUnit, Python, TS, Expo web, qualidade/JaCoCo, scans de dependências e Trivy, build e smoke. Preservar resultados mesmo em falha. | Casos positivos e negativos; relatórios e logs locais; execução remota somente após autorização para publicar. |
| 4 · Operação | Adicionar Actuator, disponibilidade de banco e métricas com acesso definido. Diferenciar recebimento, persistência, RAW, alerta gerado e alerta ativo. Registrar tentativa e último sucesso do lote ETL em UTC. Compartilhar mecanismo de exclusão entre jobs manual e periódico e publicar status mesmo em falha. | Health por serviço, métricas antes/depois do cenário, tentativa concorrente e falha controlada observáveis. |
| 5 · Mineração | Reservar desde a integração IDs de requisição/leituras e mapear ID RAW a `readingId`. Emitir eventos de caso nas etapas operacionais. Gerar `batch_id` separado e registrar associação verificável do caso ao lote; não duplicar tempo de processamento do lote como duração individual. Consolidar `event_log.csv` emitido pelas execuções controladas e analisar variantes, tempos e falhas em Python. | Fluxos normal/alerta/erro com IDs conferidos, relatório reproduzível e gráficos com limites da amostra. |
| 6 · Documentação | Consolidar arquitetura/fluxo, uso, DevSecOps, operação e mineração. Incorporar achados pertinentes da usabilidade simulada (clareza da fonte, termos e recomendação consultiva). | Diagramas em formatos solicitados, PDF verificado e catálogo distinguindo execução atual, histórica e dados simulados. |
| 7 · Vídeos e pitch | Preparar roteiro técnico de 5–8 min, roteiro pitch de até 5 min e apresentação PowerPoint. Usar telas só após comprovar o cenário a ser mostrado. | Roteiros com falas, comandos e telas, `.pptx` revisado. Links aguardam gravação. |
| 8 · Empacotamento | Fechar pastas e checklist, selecionar fontes/configuração/dados/relatórios, validar links, ZIP e manifesto. | ZIP e checksum conferidos, sem dependências instaladas ou credenciais. |

## Arquivos que deverão mudar

| Etapa | Arquivos existentes a ajustar | Arquivos novos previstos |
|---|---|---|
| 2 | `.env.example`, `.gitignore` se necessário, `README.md`, `COMO_RODAR.md`, `database/schema.sql`, `database/seed.sql`, `backend/src/main/resources/application.yml`, `backend/.../repository/SensorReadingRepository.java`, `mobile/App.tsx`, `mobile/src/services/api.ts`, `mobile/src/types/index.ts`, `mobile/.env.example`, `iot-simulator/sensor_simulator.py`; integração pontual com serviços de risco já existentes. | `compose.yaml`, `.dockerignore`, `backend/Dockerfile`, `mobile/Dockerfile`, `mobile/nginx.conf`, `docker/python.Dockerfile`, perfil integrado do backend, endpoint/DTO de risco, ajuste SQL legado em `database/migrations/`, `scripts/subir.ps1`, `scripts/demonstrar.ps1`, `scripts/encerrar.ps1`, cenário em `scripts/demo_fase7.py`, documentação e evidências da Etapa 2. |
| 3 | `backend/pom.xml`, `SecurityConfig.java`, `AuthService.java`, `AuthDtos.java`, guias, cliente web e simulador conforme contrato, manifests/lockfiles se scanner ou ferramentas exigirem mudança testada. | `.github/workflows/ci.yml`, testes de segurança e integração, configuração de análise estática, `entrega_fiap_fase7/03_DevSecOps/`. |
| 4 | `backend/pom.xml`, `application.yml` e perfil integrado, serviços de ingestão/alerta/Lake, ETLs e `compose.yaml`. | Componentes de métricas e health, `etl/run_pipeline.py`, scheduler e `04_Monitoramento/`. |
| 5 | Serviços de ingestão/alerta e ETLs, após definir contrato de IDs. | Emissor/exportador de eventos, análise Python, dataset e gráficos em `05_Mineracao_Processos/`. |
| 6–8 | Documentos consolidados e guias em `entrega_fiap_fase7/`; referências no README. | Diagramas, PDFs, PowerPoint, roteiros, catálogo de evidências, checklist e pacote final. |

Os nomes previstos podem mudar durante a implementação se os contratos ou a validação exigirem. A integração em Docker e a segurança dos endpoints são as próximas prioridades do projeto. A Etapa 2 é o próximo checkpoint após a autorização solicitada no enunciado.
