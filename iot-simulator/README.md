# IoT Simulator - Orbital Alert

## O que este simulador faz
Este script simula sensores IoT do projeto **Orbital Alert**. Ele gera leituras aleatórias periodicamente e tenta enviar para o backend no endpoint `POST /api/readings`.

Se a API estiver fora do ar, as leituras são armazenadas localmente em `mock_readings.json` para não perder dados durante a demonstração.

## Sensores simulados
O simulador gera leituras para os seguintes tipos:

- **TEMPERATURE** em °C
- **WATER_LEVEL** em %
- **SMOKE** com índice de 0 a 100
- **RAINFALL** em mm

Os `sensor_id` utilizados são compatíveis com o `database/seed.sql` já criado no projeto (IDs 1, 2, 4 e 5).

## Como cada sensor afeta geração de alertas
De acordo com a regra do backend:

- `WATER_LEVEL >= 80` gera alerta de risco de enchente.
- `TEMPERATURE >= 40` gera alerta de risco de incêndio florestal.
- `SMOKE >= 70` gera alerta de fumaça/incêndio.
- `RAINFALL >= 60` gera alerta de chuva intensa.

Isso permite demonstrar o fluxo completo de IoT + API + alertas de forma simples e acadêmica.

## Instalação de dependências
```bash
cd iot-simulator
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

## Como executar
Com backend rodando em `http://localhost:8080`:
```bash
python sensor_simulator.py
```

Com URL customizada da API:
```bash
API_URL=http://localhost:8080 python sensor_simulator.py
```

Opcional: alterar intervalo (segundos) entre ciclos:
```bash
SIM_INTERVAL_SECONDS=3 python sensor_simulator.py
```

## Exemplo de saída
```text
[14:12:20] TEMPERATURE sensor=4 valor=41.35 °C -> enviado para API
[14:12:20] WATER_LEVEL sensor=2 valor=84.92 % -> enviado para API
[14:12:20] SMOKE       sensor=5 valor=72.44 índice -> enviado para API
[14:12:20] RAINFALL    sensor=1 valor=63.11 mm -> enviado para API
```

Se a API estiver indisponível:
```text
[14:12:20] TEMPERATURE sensor=4 valor=41.35 °C -> API offline, salvo em mock_readings.json (ConnectionError)
```

## Relação com a Global Solution FIAP
Este simulador atende ao requisito de **IoT da Global Solution** ao representar sensores ambientais gerando dados continuamente e alimentando a plataforma de monitoramento de risco, com foco em uma implementação simples, funcional e fácil de explicar no pitch.
