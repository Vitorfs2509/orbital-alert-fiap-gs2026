# IoT Simulator - Orbital Alert

## Objetivo
Este simulador Python envia uma leitura demo para o backend do projeto **Orbital Alert** em `POST /api/readings`.

O foco é um modo acadêmico simples: enviar apenas uma leitura de demonstração para um sensor com `sensorId = 1`.

## Pré-requisitos
1. Subir o backend localmente em `http://localhost:8080`.
2. Criar uma região e um sensor no Swagger.
3. Garantir que o sensor criado tenha `id = 1`.

## Instalação de dependências
```powershell
cd iot-simulator
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Como rodar
```powershell
python sensor_simulator.py
```

## O que o script faz
- Envia a leitura demo padrão:
```json
{
  "sensorId": 1,
  "value": 87.5
}
```
- Mostra no terminal:
  - API URL
  - endpoint usado
  - payload enviado
  - status HTTP
  - resposta da API
- Se a API estiver offline, salva a leitura em `mock_readings.json`.

## Modo contínuo opcional
Para executar continuamente até Ctrl+C:
```powershell
python sensor_simulator.py --loop
```

Para mudar o intervalo entre envios em modo loop:
```powershell
python sensor_simulator.py --loop --interval 3
```

## Exemplo de saída esperada
```text
API URL: http://localhost:8080
Endpoint: http://localhost:8080/api/readings
Payload enviado: {"sensorId": 1, "value": 87.5}
Status HTTP: 201
Resposta da API: {"id": 10, "sensorId": 1, "value": 87.5, ...}
```

Se a API estiver offline:
```text
API URL: http://localhost:8080
Endpoint: http://localhost:8080/api/readings
Payload enviado: {"sensorId": 1, "value": 87.5}
Erro ao chamar a API: ...
Leitura salva em mock_readings.json para análise posterior.
```

## Verificação posterior
Após rodar o script, verifique o backend usando:
```powershell
curl http://localhost:8080/api/alerts
```

Isso demonstra o fluxo de IoT -> API -> alerta com um exemplo acadêmico simples.
