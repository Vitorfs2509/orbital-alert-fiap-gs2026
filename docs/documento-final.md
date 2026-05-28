# Orbital Alert

## 1. Capa
- **Nome do projeto:** Orbital Alert  
- **Tema:** Global Solution 2026/1 - Space Economy  
- **Curso:** Engenharia de Software - FIAP  
- **Integrantes:**
  - Yuri Monteiro Zacarioto - RM550952
  - Vitor Futida Sternik - RM98697
  - Caio Henrique Rocha da Silva - RM552308
  - Vitor Reyes Souza - RM550766

---

## 2. Visão geral do projeto
O **Orbital Alert** é um MVP acadêmico que simula o monitoramento de regiões de risco por meio da combinação de dados de satélite (simulados) e leituras de sensores IoT.

### Problema resolvido
Eventos climáticos extremos como enchentes, queimadas e chuvas intensas causam impactos sociais, ambientais e econômicos. Em muitos cenários, o alerta chega tarde ou sem integração de dados.

### Solução proposta
A solução propõe um fluxo simples e funcional para:
1. receber leituras de sensores,
2. consolidar informações por região,
3. gerar alertas preventivos,
4. exibir tudo em uma interface mobile para apoio à decisão.

---

## 3. Conexão com Space Economy
O projeto se conecta à **Space Economy** ao mostrar como dados de observação da Terra (simulados como dados satelitais) podem ser usados junto com IoT para monitoramento climático.

Essa combinação apoia:
- monitoramento de riscos ambientais,
- prevenção de desastres,
- iniciativas de cidades inteligentes,
- sustentabilidade,
- tomada de decisão mais rápida por órgãos públicos e equipes técnicas.

---

## 4. Escopo do MVP
### O que está implementado
- Backend em Spring Boot com endpoints para autenticação, regiões, sensores, leituras e alertas.
- Banco PostgreSQL com modelagem relacional e scripts SQL.
- Protótipo mobile em React Native + Expo.
- Coleção Postman para testes de API.
- Plano de testes e estrutura de evidências.

### O que está mockado
- Dados exibidos no aplicativo mobile.

### O que está simulado
- Leituras de sensores IoT via script Python.
- Uso conceitual de dados satelitais por meio de score de risco nas regiões.

### Por que isso é suficiente para um MVP acadêmico
O recorte permite demonstrar o valor da solução ponta a ponta sem complexidade excessiva, com foco em clareza técnica, viabilidade de execução e apresentação em curto tempo.

---

## 5. Entregáveis de banco de dados
O modelo ER foi pensado para representar o fluxo principal do negócio: usuários monitoram regiões, regiões possuem sensores, sensores geram leituras e leituras podem gerar alertas.

### Tabelas principais
- `users`
- `regions`
- `sensors`
- `sensor_readings`
- `alerts`

### Aspectos técnicos entregues
- Chaves primárias (PK) em todas as tabelas.
- Chaves estrangeiras (FK) para relacionamento entre entidades.
- Constraints para garantir integridade de domínio.
- `seed.sql` com dados iniciais para demonstração.
- `queries.sql` com consultas de uso acadêmico.

---

## 6. Entregáveis de API
O backend foi implementado com **Java 21 + Spring Boot + Maven**.

### Arquitetura utilizada
- **Controller:** exposição dos endpoints REST.
- **Service:** regras de negócio e fluxo de aplicação.
- **Repository:** acesso aos dados com Spring Data JPA.

### Endpoints principais
- Auth: `POST /api/auth/register`, `POST /api/auth/login`
- Regions: `GET/POST /api/regions`, `GET/PUT/DELETE /api/regions/{id}`
- Sensors: `GET/POST /api/sensors`, `GET/DELETE /api/sensors/{id}`
- Readings: `POST /api/readings`, `GET /api/readings/latest`
- Alerts: `GET /api/alerts`, `GET /api/alerts/active`, `PUT /api/alerts/{id}/resolve`

### Swagger
A documentação interativa da API pode ser acessada via Swagger em:
- `http://localhost:8080/swagger-ui.html`

---

## 7. Entregáveis de plano de testes
O arquivo `docs/plano-testes.md` descreve casos de teste funcionais do MVP.

- O plano contém **pelo menos 5 casos** (foram definidos 6).
- Cada caso inclui: ID, cenário, entrada, resultado esperado e status.
- **Pelo menos 3 testes** estão marcados como executados (`Aprovado`).
- As evidências devem ser organizadas em `docs/evidencias/`.

---

## 8. Entregáveis mobile
Foi desenvolvido um protótipo em **React Native + Expo** com foco em demonstração.

### Telas
1. Login
2. Dashboard
3. Regions
4. Alert Details

### Dados mockados
O app utiliza dados locais mockados para garantir estabilidade durante o pitch e independência de conectividade no momento da apresentação.

---

## 9. Entregáveis de segurança
- **Hash de senha com BCrypt** no cadastro/autenticação.
- **Validação de entrada** com DTOs e Bean Validation.
- **Uso de JPA Repositories** para reduzir risco de SQL Injection em relação a SQL manual concatenado.
- **Tratamento seguro de erros** via handler global e respostas padronizadas.

---

## 10. Entregáveis IoT
O simulador em Python gera leituras para:
- `TEMPERATURE`
- `WATER_LEVEL`
- `SMOKE`
- `RAINFALL`

### Regras de geração de alerta
- `WATER_LEVEL >= 80` -> alerta de enchente
- `TEMPERATURE >= 40` -> alerta de risco de incêndio
- `SMOKE >= 70` -> alerta de fumaça/incêndio
- `RAINFALL >= 60` -> alerta de chuva intensa

### Fallback offline
Se a API estiver indisponível, as leituras são salvas localmente em JSON para posterior reenvio.

---

## 11. Visão geral da arquitetura
A solução é composta por módulos integrados:
- **Database (PostgreSQL):** persiste entidades de negócio e histórico.
- **Backend (Spring Boot):** centraliza regras e endpoints REST.
- **IoT Simulator (Python):** simula sensores e envia leituras.
- **Mobile (Expo):** apresenta dados e experiência do usuário para demonstração.
- **Postman:** validação manual dos endpoints.
- **Docs:** documentação técnica, plano de testes e evidências.

Fluxo didático: **sensores simulados -> API -> banco/alertas -> visualização mobile + testes/evidências**.

---

## 12. Conclusão
O Orbital Alert é relevante por tratar prevenção de riscos climáticos com uma abordagem atual e alinhada à Space Economy. O escopo é viável para contexto acadêmico, demonstra integração entre camadas e atende aos objetivos da FIAP Global Solution com clareza, simplicidade e potencial de evolução futura.
