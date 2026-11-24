# Código e configuração

| Componente | Arquivos na raiz do pacote |
|---|---|
| Orquestração e exemplos | [compose.yaml](../../compose.yaml), [.env.example](../../.env.example), [.dockerignore](../../.dockerignore) |
| Backend Java | [Código](../../backend/src/main/java/com/orbitalalert/backend/), [Dockerfile](../../backend/Dockerfile), [testes](../../backend/src/test/java/com/orbitalalert/backend/) |
| Frontend Expo | [App.tsx](../../mobile/App.tsx), [cliente da API](../../mobile/src/services/api.ts), [Nginx](../../mobile/nginx.conf) |
| PostgreSQL e Oracle | [Schema](../../database/schema.sql), [migração](../../database/migrations/001_rainfall.sql), [DDL Oracle](../../database/oracle-setup.sql) |
| IoT e ETLs | [Simulador](../../iot-simulator/sensor_simulator.py), [orquestrador Python](../../etl/pipeline.py), [scripts ETL](../../etl/) |
| Operação e análise | [Scripts PowerShell, smoke e análise](../../scripts/) |
| DevSecOps | [Workflow](../../.github/workflows/ci.yml), [análise de imagens](../../scripts/escanear_imagens.sh) |

O pacote inclui o código rastreado do checkpoint da Fase 7. Dependências instaladas, caches, dados de volumes e `.env` reais ficam fora do ZIP. Os datasets em `data-lake/` são exemplos históricos. A execução nova em Compose usa o volume nomeado `lake`.
