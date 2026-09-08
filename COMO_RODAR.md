# COMO RODAR

## 1. Contexto rápido do projeto
Orbital Alert é um MVP acadêmico que simula o uso de dados satelitais e sensores IoT para monitorar regiões de risco e gerar alertas preventivos de enchentes, queimadas e eventos climáticos extremos.

O projeto inclui:
- Backend Spring Boot com Swagger e profile `dev/H2`
- Mobile React Native/Expo com dados mockados
- Simulador IoT em Python
- Banco modelado na pasta `database`
- Documentação e evidências em `docs`

## 2. Pré-requisitos básicos
Antes de começar, instale:
- Java 21
- Node.js
- Python 3
- Git
- VS Code

## 3. Como clonar o repositório
No terminal, execute:
```powershell
git clone <URL do repositório>
cd orbital-alert-fiap-gs2026
```

## 4. Como rodar o backend
No terminal:
```powershell
cd backend
.\mvnw.cmd spring-boot:run "-Dspring-boot.run.profiles=dev"
```

## 5. Link do Swagger
Acesse o Swagger quando o backend estiver rodando:

- `http://localhost:8080/swagger-ui/index.html`

## 6. Passo a passo no Swagger
1. Criar região usando `POST /api/regions`.
2. Criar sensor usando `POST /api/sensors`.
3. Verificar sensor usando `GET /api/sensors` ou `GET /api/sensors/{id}`.
4. Depois de confirmar o sensor, rodar o simulador IoT.

## 7. JSON para criar região
Use o seguinte payload para criar uma região de demonstração:
```json
{
  "name": "Santos - Zona Portuária",
  "city": "Santos",
  "state": "SP",
  "latitude": -23.9608,
  "longitude": -46.3336,
  "satelliteRiskScore": 85,
  "riskLevel": "HIGH"
}
```

## 8. JSON para criar sensor
Use o payload abaixo para criar um sensor ativo:
```json
{
  "regionId": 1,
  "type": "WATER_LEVEL",
  "status": "ACTIVE",
  "unit": "%"
}
```

## 9. Como rodar o simulador IoT
No terminal:
```powershell
cd iot-simulator
pip install -r requirements.txt
python sensor_simulator.py
```

## 10. Como verificar alerta
Após rodar o simulador, verifique os alertas no Swagger ou usando:
- `GET /api/alerts`
- `GET /api/alerts/active`

## 11. Como rodar o mobile
No terminal:
```powershell
cd mobile
npm install
npx expo start
```

## 12. Como rodar o Oracle AI Database Free (Fase 6)
Opcional — o projeto roda inteiro sem ele. Serve para demonstrar a integração Oracle real.

Pré-requisito: Docker Desktop aberto. Se `docker` não estiver no PATH:
```powershell
$env:PATH = "$env:LOCALAPPDATA\Programs\DockerDesktop\resources\bin;$env:PATH"
```

Primeira vez (baixa a imagem e cria o banco — leva alguns minutos):
```powershell
docker pull container-registry.oracle.com/database/free:latest-lite
docker volume create orbital-alert-oracle-data
docker run -d --name orbital-alert-oracle -p 1521:1521 `
  -e ORACLE_PWD="<senha do SYSTEM>" `
  -v orbital-alert-oracle-data:/opt/oracle/oradata `
  container-registry.oracle.com/database/free:latest-lite

docker logs -f orbital-alert-oracle   # espere "DATABASE IS READY TO USE!"
```

Criar o usuário da aplicação (uma única vez):
```powershell
Get-Content database/oracle-setup.sql | docker exec -i orbital-alert-oracle `
  sqlplus -S "system/<senha do SYSTEM>@localhost:1521/FREEPDB1"
```

Sincronizar a camada CURATED e conferir:
```powershell
pip install -r etl/requirements-oracle-db.txt
$env:ORACLE_DB_PASSWORD = "<senha do ORBITAL_ALERT>"
python etl/sync_curated_to_oracle.py

docker exec -it orbital-alert-oracle sqlplus "ORBITAL_ALERT/<senha>@localhost:1521/FREEPDB1"
-- SELECT * FROM REGION_RISK_SUMMARY;
```

Nas próximas vezes basta `docker start orbital-alert-oracle`.
Guia completo: [docs/oracle-database-integration.md](docs/oracle-database-integration.md).

## 13. O que gravar no vídeo pitch
Mostre no vídeo:
- problema que o projeto resolve
- solução proposta pelo Orbital Alert
- protótipo mobile em ação
- Swagger/API funcionando
- criação de região e de sensor
- execuçãodo simulador IoT
- alerta gerado a partir da leitura
- conexão com Space Economy
- integração Oracle real: contêiner de pé e `SELECT * FROM REGION_RISK_SUMMARY`

## 14. O que ainda falta
- gravar o vídeo pitch
- colocar o link do vídeo em `integrantes.txt`
- gerar o PDF final do projeto
- gerar o ZIP final para entrega
