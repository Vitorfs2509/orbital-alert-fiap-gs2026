# Plano de Testes - Orbital Alert

Este plano contém testes funcionais básicos para validação do MVP acadêmico.

## Casos de teste

| ID | Cenário | Entrada | Resultado esperado | Status |
|---|---|---|---|---|
| CT-01 | Cadastro de usuário válido | `POST /api/auth/register` com nome, e-mail único, senha e role válidos | API retorna sucesso e dados do usuário sem `passwordHash` | **Aprovado** |
| CT-02 | Login com credenciais válidas | `POST /api/auth/login` com e-mail/senha cadastrados | API retorna sucesso e perfil do usuário | **Aprovado** |
| CT-03 | Consulta de regiões monitoradas | `GET /api/regions` | API retorna lista de regiões (HTTP 200) | **Aprovado** |
| CT-04 | Geração de alerta por leitura crítica | `POST /api/readings` com `sensorId` de WATER_LEVEL e `value >= 80` | Leitura salva e novo alerta aparece em `GET /api/alerts/active` | Pendente |
| CT-05 | Resolução de alerta | `PUT /api/alerts/{id}/resolve` para alerta aberto | Status do alerta alterado para `RESOLVED` e `resolvedAt` preenchido | Pendente |
| CT-06 | Validação de payload inválido em região | `POST /api/regions` com `state` inválido (ex.: `SaoPaulo`) | API retorna erro de validação (HTTP 400) com mensagem clara | Pendente |

## Observações
- Os testes aprovados consideram execução local com backend ativo em `http://localhost:8080` e banco PostgreSQL configurado.
- Os testes pendentes devem ser executados e capturados em evidências para anexar no PDF final.
