# Banco de Dados - Orbital Alert

Este diretório contém os scripts PostgreSQL do MVP acadêmico **Orbital Alert**.

## Objetivo do banco
O banco armazena dados necessários para demonstrar o fluxo principal do projeto: regiões monitoradas recebem sensores IoT, sensores geram leituras, e leituras de risco ajudam a justificar alertas preventivos.

## Arquivos
- `schema.sql`: cria as tabelas, chaves primárias, chaves estrangeiras, constraints e índices básicos.
- `seed.sql`: insere dados fictícios e realistas para apresentação e testes.
- `queries.sql`: contém consultas úteis para demonstrar o sistema.

## Entidades
- `users`: usuários fictícios que representam operadores ou analistas da plataforma.
- `regions`: regiões monitoradas, com cidade, estado, coordenadas, score satelital e nível de risco.
- `sensors`: sensores IoT vinculados a uma região, como chuva, nível de água, fumaça e temperatura.
- `sensor_readings`: histórico de leituras simuladas geradas pelos sensores.
- `alerts`: alertas preventivos vinculados a regiões monitoradas.

## Relacionamentos
- Uma região possui vários sensores (`regions` -> `sensors`).
- Um sensor possui várias leituras (`sensors` -> `sensor_readings`).
- Uma região pode possuir vários alertas (`regions` -> `alerts`).

## Como executar
Pré-requisito: PostgreSQL instalado e um banco criado, por exemplo `orbital_alert`.

```bash
createdb -U postgres orbital_alert
psql -U postgres -d orbital_alert -f database/schema.sql
psql -U postgres -d orbital_alert -f database/seed.sql
psql -U postgres -d orbital_alert -f database/queries.sql
```

Se o banco já existir, execute apenas os scripts necessários:

```bash
psql -U postgres -d orbital_alert -f database/schema.sql
psql -U postgres -d orbital_alert -f database/seed.sql
```

## Como as tabelas se conectam ao projeto
- O **backend Spring Boot** usa essas entidades como base para endpoints de regiões, sensores, leituras e alertas.
- O **simulador IoT** envia leituras que representam `sensor_readings`.
- O **mobile** apresenta a ideia do monitoramento e alertas com dados mockados compatíveis com o conceito do banco.
- O **Postman** e as consultas SQL ajudam a demonstrar o comportamento do sistema durante a apresentação.

A modelagem foi mantida simples para facilitar explicação, execução local e inclusão na documentação final da FIAP Global Solution.
