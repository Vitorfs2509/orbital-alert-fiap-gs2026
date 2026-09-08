# Orbital Alert

## 1. Capa
- **Nome do projeto:** Orbital Alert
- **Tema:** Global Solution 2026/1 - Space Economy
- **Curso:** Engenharia de Software - FIAP
- **Entrega:** MVP acadêmico de monitoramento ambiental

---

## 2. Integrantes
- Yuri Monteiro Zacarioto - RM550952
- Vitor Futida Sternik - RM98697
- Caio Henrique Rocha da Silva - RM552308
- Vitor Reyes Souza - RM550766

---

## 3. Visão geral da solução
Orbital Alert é um MVP acadêmico que une dados satelitais simulados e sensores IoT para monitorar regiões de risco e gerar alertas preventivos relacionados a enchentes, queimadas e eventos climáticos extremos.

A solução demonstra um fluxo de dados integrado entre sensores, backend, banco de dados e interface de apresentação.

> **Foco desta fase acadêmica: monitoramento e prevenção de enchentes.**
> O cenário priorizado na demonstração usa os sensores `WATER_LEVEL` e `RAINFALL`, o tipo de
> risco `FLOOD` no score do Data Lake e as evidências correspondentes. Trata-se de uma escolha
> de caso de uso: o suporte técnico a incêndio/temperatura (`TEMPERATURE`, `SMOKE`, `HUMIDITY`)
> permanece implementado e testado no backend, no simulador e nos ETLs.

---

## 4. Problema abordado
O projeto aborda a dificuldade de identificar rapidamente riscos ambientais em áreas vulneráveis, onde a falta de integração entre fontes de dados torna a resposta mais lenta.

A proposta é fornecer alertas automáticos e apoio à tomada de decisão antes que eventos críticos causem danos maiores.

---

## 5. Conexão com Space Economy
Orbital Alert está alinhado à Space Economy ao explorar o uso de dados de observação da Terra e análise geoespacial, mesmo em formato simulado.

O conceito evidencia como informações espaciais e IoT podem gerar valor em aplicações de monitoramento ambiental e gestão de risco.

---

## 6. Arquitetura geral
A arquitetura do projeto é composta por módulos integrados:
- **Backend Spring Boot:** expõe API REST para regiões, sensores, leituras e alertas.
- **Banco de dados PostgreSQL:** modelagem oficial para persistência de dados.
- **Mobile React Native/Expo:** protótipo para visualização de alertas.
- **Simulador IoT Python:** gera leituras de sensores e envia para a API.
- **Data Lake e ETL (Fase 5):** camadas RAW/TRUSTED/CURATED em arquivos, com score de risco por região.
- **Oracle AI Database Free (Fase 6):** banco Oracle real, executado localmente em Docker pela imagem oficial `container-registry.oracle.com/database/free:latest-lite`, recebendo os dados analíticos da camada CURATED na tabela `REGION_RISK_SUMMARY` (carga idempotente via `MERGE`). O Oracle **não substitui** H2/PostgreSQL, que continuam sendo o banco operacional da API, do `AlertService` e do mobile. Detalhes em [oracle-database-integration.md](oracle-database-integration.md).
- **Oracle Cloud Infrastructure — Object Storage (Fase 6, opcional/futuro):** persistência em nuvem das três camadas do Data Lake, preservando os prefixes `raw/`, `trusted/` e `curated/`. Implementada em código e **validada por dry-run**; não houve upload real, porque a criação da conta Oracle Cloud não pôde ser concluída (erro no cadastro). O filesystem local segue como ambiente de desenvolvimento, teste e fallback. Detalhes em [oracle-integration.md](oracle-integration.md).
- **Postman e documentação:** apoio aos testes manuais e evidências.

O fluxo principal consiste em:
1. cadastro de região e sensor;
2. envio de leituras;
3. processamento de dados;
4. geração de alertas;
5. apresentação e validação.

---

## 7. Banco de Dados
A modelagem oficial está disponível na pasta `database/`.

### Scripts de banco
- `database/schema.sql`
- `database/seed.sql`
- `database/queries.sql`

### Componentes do modelo
- `users`
- `regions`
- `sensors`
- `sensor_readings`
- `alerts`

A estrutura inclui chaves primárias, estrangeiras e constraints para manter a integridade dos dados.

---

## 8. API / Backend
O backend foi implementado com **Java 21 + Spring Boot + Maven**.

### Principais camadas
- **Controller:** expõe os endpoints REST.
- **Service:** gerencia regras de negócio.
- **Repository:** interage com o banco de dados via Spring Data JPA.

### Endpoints relevantes
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/regions`
- `POST /api/regions`
- `GET /api/sensors`
- `POST /api/sensors`
- `POST /api/readings`
- `GET /api/alerts`
- `GET /api/alerts/active`
- `PUT /api/alerts/{id}/resolve`

### Swagger
A API pode ser acessada em:
- `http://localhost:8080/swagger-ui/index.html`

---

## 9. Plano de Testes
O plano de testes está documentado em `docs/plano-testes.md`.

O documento cobre casos de teste para:
- criação de região monitorada;
- cadastro de sensor IoT;
- envio de leitura de sensor;
- geração de alerta automático;
- resolução de alerta;
- listagem de alertas ativos;
- execução do simulador IoT.

As evidências relacionadas estão organizadas nas pastas de imagens.

---

## 10. Mobile
O protótipo mobile foi construído em **React Native com Expo**.

### Características
- interface de demonstração para alertas e regiões;
- uso de dados mockados para garantir estabilidade na apresentação;
- foco em comunicação clara do valor do MVP.

---

## 11. Segurança
O projeto considera aspectos básicos de segurança:
- uso de **BCrypt** para hash de senha;
- validação de entrada com DTOs;
- Spring Data JPA para reduzir riscos de SQL Injection;
- tratamento de erros controlado no backend.

---

## 12. IoT
O simulador Python produz leituras para sensores de:
- `TEMPERATURE`
- `WATER_LEVEL`
- `SMOKE`
- `RAINFALL`

### Regras de alerta
- `WATER_LEVEL >= 80` => alerta de enchente
- `TEMPERATURE >= 40` => alerta de incêndio
- `SMOKE >= 70` => alerta de fumaça
- `RAINFALL >= 60` => alerta de chuva intensa

### Fallback offline
Se o backend estiver indisponível, as leituras são gravadas em `mock_readings.json`.

---

## 13. Evidências
As evidências do projeto estão disponíveis em:
- `docs/evidencias-api/`
- `docs/evidencias-iot/`

Elas suportam a validação dos testes realizados e demonstram o funcionamento dos fluxos principais.

---

## 14. Conclusão
Orbital Alert apresenta um MVP acadêmico consistente para monitoramento de riscos ambientais com suporte à Space Economy.

A entrega demonstra a integração entre sensores simulados, backend, banco de dados e mobile, entregando um caso de uso válido para prevenção de desastres e tomada de decisão.
