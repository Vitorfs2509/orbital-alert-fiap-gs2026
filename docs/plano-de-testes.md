# Plano de Testes Manual - Orbital Alert

Este plano de testes descreve os cenários manuais para validar os principais fluxos do sistema Orbital Alert, incluindo backend e simulador IoT.

## Caso de Teste 1: Criar região monitorada
- ID: CT-01
- Cenário: Criação de uma nova região monitorada pelo sistema.
- Objetivo: Verificar se o backend aceita o cadastro de regiões via API.
- Entrada: Requisição `POST /api/regions` com dados da região.
- Passos:
  1. Abrir o Swagger do backend em `http://localhost:8080/swagger-ui/index.html`.
  2. Navegar até a operação `POST /api/regions`.
  3. Preencher os campos obrigatórios da região.
  4. Executar a chamada da API.
- Resultado esperado:
  - Retorno HTTP 201 ou 200.
  - Corpo de resposta contendo o ID da região criada e os dados enviados.
- Status: Aprovado
- Evidência relacionada: `docs/evidencias-api/post-regions.png`

## Caso de Teste 2: Criar sensor IoT
- ID: CT-02
- Cenário: Cadastro de um sensor IoT vinculado a uma região existente.
- Objetivo: Verificar se o backend permite criar sensores para monitoramento.
- Entrada: Requisição `POST /api/sensors` com `regionId` e atributos do sensor.
- Passos:
  1. No Swagger, localizar a operação `POST /api/sensors`.
  2. Informar `regionId` válido e dados do sensor.
  3. Executar a chamada da API.
- Resultado esperado:
  - Retorno HTTP 201 ou 200.
  - Corpo da resposta contendo `sensorId`, `regionId` e tipo de sensor.
- Status: Aprovado
- Evidência relacionada: `docs/evidencias-api/post-sensors.png`

## Caso de Teste 3: Enviar leitura de sensor
- ID: CT-03
- Cenário: Envio de uma leitura manual para um sensor cadastrado.
- Objetivo: Validar o endpoint de registro de leituras do backend.
- Entrada: Requisição `POST /api/readings` com payload do sensor.
- Passos:
  1. No Swagger, abrir `POST /api/readings`.
  2. Informar `sensorId: 1` e `value` numérico.
  3. Executar a chamada.
- Resultado esperado:
  - Retorno HTTP 201 ou 200.
  - Confirmação de que a leitura foi registrada.
- Status: Aprovado
- Evidência relacionada: `docs/evidencias-api/post-readings.png`

## Caso de Teste 4: Gerar alerta automático
- ID: CT-04
- Cenário: Envio de leitura que ultrapassa limiar de risco e dispara um alerta.
- Objetivo: Verificar a geração automática de alertas a partir de leituras críticas.
- Entrada: Requisição `POST /api/readings` com valor elevado para `sensorId: 1`.
- Passos:
  1. Executar `POST /api/readings` com `sensorId: 1` e `value` acima do limite crítico.
  2. Consultar os alertas gerados via `GET /api/alerts` ou `GET /api/alerts/active`.
- Resultado esperado:
  - Um alerta novo aparece na lista de alertas.
  - O alerta indica risco associado ao sensor e valor recebido.
- Status: Aprovado
- Evidência relacionada: `docs/evidencias-api/get-alerts.png`

## Caso de Teste 5: Resolver alerta
- ID: CT-05
- Cenário: Marcar um alerta como resolvido pelo backend.
- Objetivo: Validar o endpoint de resolução de alertas.
- Entrada: Requisição `PUT /api/alerts/{id}/resolve` para um alerta existente.
- Passos:
  1. Obter o `id` de um alerta ativo via `GET /api/alerts/active`.
  2. Executar `PUT /api/alerts/{id}/resolve` com o ID do alerta.
  3. Verificar a resposta e o status do alerta.
- Resultado esperado:
  - Retorno HTTP 200.
  - O alerta não aparece mais na lista de alertas ativos.
- Status: Aprovado
- Evidência relacionada: `docs/evidencias-api/put-alert-resolv.png`

## Caso de Teste 6: Listar alertas ativos
- ID: CT-06
- Cenário: Consulta dos alertas que ainda não foram resolvidos.
- Objetivo: Confirmar que o backend retorna apenas alertas ativos no endpoint correto.
- Entrada: Requisição `GET /api/alerts/active`.
- Passos:
  1. No Swagger, acessar a operação `GET /api/alerts/active`.
  2. Executar a chamada.
- Resultado esperado:
  - Retorno HTTP 200.
  - Lista de alertas ativos, sem alertas já resolvidos.
- Status: Aprovado
- Evidência relacionada: `docs/evidencias-api/get-alerts-active.png`

## Caso de Teste 7: Rodar simulador IoT enviando leitura para API
- ID: CT-07
- Cenário: Uso do simulador de IoT para enviar uma leitura de demonstração ao backend.
- Objetivo: Validar a integração do script `sensor_simulator.py` com a API do backend.
- Entrada: Execução do comando `python sensor_simulator.py` com backend ativo.
- Passos:
  1. Certificar que o backend está rodando em `http://localhost:8080`.
  2. Executar o script `iot-simulator/sensor_simulator.py`.
  3. Observar a saída do terminal e garantir que o payload foi enviado.
  4. Verificar em `GET /api/alerts` se um alerta foi gerado conforme a leitura.
- Resultado esperado:
  - O terminal exibe URL da API, endpoint, payload enviado, status HTTP e resposta.
  - A leitura é aceita pela API e um alerta é gerado se o valor estiver em limite crítico.
- Status: Aprovado
- Evidência relacionada:
  - `docs/evidencias-iot/01-terminal-simulador-iot.png`
  - `docs/evidencias-iot/02-alerta-gerado-pelo-iot.png`
