# Arquitetura final

[Mermaid](arquitetura.mmd) · [SVG](arquitetura.svg) · [PNG](arquitetura.png)

O frontend Expo usa Nginx e encaminha consultas `/api` para Spring Boot. O PostgreSQL preserva o estado operacional. A API verifica o sensor, grava a leitura e aplica o limiar de alerta. Depois tenta registrar no RAW a origem do simulador, o identificador da leitura e o UUID do caso. A resposta de criação continua independente de uma falha registrada na gravação analítica.

O ETL valida eventos, preserva a trilha em TRUSTED e agrupa por região em CURATED. O cálculo agrega os indicadores por sensor. O dashboard consome a API do mesmo ambiente, com origem e horário do score. O operador consulta a recomendação separadamente. O texto é consultivo, usa `MOCK` por padrão e está identificado. OCI permanece como caminho futuro de armazenamento. Oracle local recebe somente o snapshot analítico e não participa da geração de alertas.

O volume do Lake é compartilhado pela API e pelos jobs, com uma trava de execução do ETL. A automação executa o lote periodicamente. Os event logs preservam o vínculo entre casos e lotes. As métricas internas do Actuator exigem administração. O status agregado pode ser consultado pela interface local.

## Entradas e saídas da execução final

| Entrada real do cenário | Saída observada |
|---|---|
| Região de demonstração e sensor RAINFALL criado com IDs retornados pela API | Cadastro em PostgreSQL, visível no painel |
| 45 mm/h | Leitura aceita; alerta ativo ausente para a região antes da próxima leitura |
| 95 mm/h | Leitura aceita; alerta HIGH; score agregado 100/100; média de 70 mm/h |
| Sensor inexistente, requisição autorizada | HTTP 404 e caso rejeitado |
| Execução manual do ETL | RAW, 2 registros TRUSTED e região publicada no CURATED |
| Consulta à recomendação | Fonte CURATED e texto MOCK, sem chamada de LLM externo |

Os IDs, valores e tempos foram extraídos do [JSON da execução final](../08_Evidencias/execucao-final/demo.json).

## Público e proposta de valor

Analistas da Defesa Civil e equipes municipais são o público prioritário para interpretar leituras, alertas e tendências. Moradores em áreas de risco são beneficiários. A proposta aproxima telemetria e evidências para priorizar revisão preventiva. O MVP demonstra o processo com dados simulados e implantação local. Uma operação de emergência exigiria validação de sensores em campo, protocolo institucional, identidade individual, disponibilidade, recuperação e testes de usabilidade com pessoas.

## Limites e evolução

A trilha atual registra tentativas e falhas, com persistência e volume local. Para operação contínua, priorizar retenção e cópias de segurança, métricas persistentes, autenticação individual, atualização do Expo e correções de dependências. Validar latência e volume em uma infraestrutura representativa antes de assumir garantias de escala. O [roteiro de evolução da Fase 6](../AUDITORIA_ETAPA_1.md) continua como referência histórica.
