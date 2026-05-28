# Orbital Alert

## Descrição
O **Orbital Alert** é um projeto acadêmico da FIAP (Global Solution 2026/1) que simula monitoramento de regiões de risco com dados satelitais simulados e sensores IoT.

## Tema e contexto
- **Tema:** Space Economy
- **Foco:** prevenção de enchentes, queimadas, chuvas intensas e eventos climáticos extremos.

## Nota acadêmica
- O **mobile** utiliza **dados mockados** para garantir estabilidade no pitch e facilitar demonstração.
- O módulo **IoT** utiliza **dados simulados** para representar sensores reais em ambiente acadêmico.

## Estrutura do repositório
```text
.
├── backend/
├── mobile/
├── database/
├── iot-simulator/
├── docs/
├── postman/
├── README.md
├── integrantes.txt
└── .gitignore
```

## Integrantes
- Yuri Monteiro Zacarioto - RM550952
- Vitor Futida Sternik - RM98697
- Caio Henrique Rocha da Silva - RM552308
- Vitor Reyes Souza - RM550766

## Link do vídeo pitch
- **A definir**

## Como executar o projeto

### 1) Banco de dados (PostgreSQL)
```bash
psql -U postgres -d orbital_alert -f database/schema.sql
psql -U postgres -d orbital_alert -f database/seed.sql
```

### 2) Backend (Spring Boot)
```bash
cd backend
mvn spring-boot:run
```

Variáveis opcionais:
- `DB_URL` (padrão: `jdbc:postgresql://localhost:5432/orbital_alert`)
- `DB_USER` (padrão: `postgres`)
- `DB_PASSWORD` (padrão: `postgres`)

Swagger:
- `http://localhost:8080/swagger-ui.html`

### 3) IoT Simulator (Python)
```bash
cd iot-simulator
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
python sensor_simulator.py
```

Opcional:
```bash
API_URL=http://localhost:8080 SIM_INTERVAL_SECONDS=3 python sensor_simulator.py
```

### 4) Mobile (Expo + React Native)
```bash
cd mobile
npm install
npm run start
```

Depois, abra no Expo Go (QR Code) ou emulador.

### 5) Postman
1. Abra o Postman.
2. Importe `postman/OrbitalAlert.postman_collection.json`.
3. Execute as rotas com backend ativo em `http://localhost:8080`.

## Checklist de entrega
- [x] Estrutura inicial do repositório
- [x] Scripts SQL (`schema.sql`, `seed.sql`, `queries.sql`)
- [x] Backend Spring Boot com endpoints principais
- [x] Simulador IoT com fallback offline
- [x] Protótipo mobile com 4 telas
- [x] Coleção Postman
- [x] Plano de testes (`docs/plano-testes.md`)
- [x] Guia de evidências (`docs/evidencias/README.md`)
- [x] Documento final rascunho (`docs/documento-final.md`)
- [x] Roteiro de pitch (`docs/roteiro-pitch.md`)
