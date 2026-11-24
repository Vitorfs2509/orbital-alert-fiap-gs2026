# Banco de Dados - Orbital Alert

Este diretório contém os scripts SQL iniciais do projeto **Orbital Alert**, usando **PostgreSQL**.

## Arquivos

- `schema.sql`: cria a estrutura do banco com tabelas, chaves primárias, chaves estrangeiras, índices e constraints.
- `seed.sql`: popula o banco com dados de exemplo para demonstração acadêmica.
- `queries.sql`: consultas úteis para simular o uso do sistema no dia a dia.
- `migrations/001_rainfall.sql`: alinha o tipo de sensor legado `RAIN` ao enum `RAINFALL`. Execute em transação. O Compose executa a migração após aplicar o schema.

O [guia do Compose](../entrega_fiap_fase7/02_Execucao_Plataforma/COMO_RODAR_COMPOSE.md) é o caminho recomendado. O cenário cria suas próprias regiões e sensores. O `seed.sql` é opcional, foi pensado para um banco vazio e contém dados ilustrativos, inclusive hashes inadequados para autenticação.

## Como executar os scripts

> Pré-requisito: PostgreSQL instalado e um banco criado (exemplo: `orbital_alert`).

1. Executar o schema:
   ```bash
   psql -U postgres -d orbital_alert -f database/schema.sql
   ```
2. Executar a carga inicial:
   ```bash
   psql -U postgres -d orbital_alert -f database/seed.sql
   ```
3. Testar consultas:
   ```bash
   psql -U postgres -d orbital_alert -f database/queries.sql
   ```

## Como este banco atende à Global Solution

O modelo foi desenhado para ser **simples, funcional e fácil de explicar** em contexto acadêmico:

- `users`: representa quem acompanha e opera a plataforma.
- `regions`: guarda as áreas monitoradas e um score de risco vindo da simulação de satélite.
- `sensors`: registra sensores IoT por região (chuva, temperatura, fumaça, etc.).
- `sensor_readings`: armazena as leituras coletadas ao longo do tempo.
- `alerts`: concentra os alertas gerados para prevenção de eventos como enchentes e queimadas.

Com isso, o grupo consegue demonstrar o fluxo completo: **monitorar regiões -> receber leituras -> identificar risco -> gerar e resolver alertas**.
