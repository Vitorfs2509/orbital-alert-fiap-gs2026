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

## 12. O que gravar no vídeo pitch
Mostre no vídeo:
- problema que o projeto resolve
- solução proposta pelo Orbital Alert
- protótipo mobile em ação
- Swagger/API funcionando
- criação de região e de sensor
- execuçãodo simulador IoT
- alerta gerado a partir da leitura
- conexão com Space Economy

## 13. O que ainda falta
- gravar o vídeo pitch
- colocar o link do vídeo em `integrantes.txt`
- gerar o PDF final do projeto
- gerar o ZIP final para entrega
