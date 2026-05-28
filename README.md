# Orbital Alert

## 1. Nome do projeto
Orbital Alert

## 2. Descrição da solução
Orbital Alert é um MVP acadêmico que combina dados satelitais simulados e sensores IoT para monitorar regiões de risco e gerar alertas preventivos de enchentes, queimadas e eventos climáticos extremos.

## 3. Problema abordado
O sistema busca antecipar ameaças ambientais em áreas vulneráveis, oferecendo monitoramento contínuo e geração de alertas automáticos para apoiar decisões de mitigação e resposta rápida.

## 4. Conexão com Space Economy
A solução integra informações espaciais e terrestres para promover a Space Economy, demonstrando como dados derivados de observação da Terra e IoT podem ser aplicados em proteção de populações e gestão de riscos climáticos.

## 5. Tecnologias usadas
- Backend: Java Spring Boot
- Banco de dados local: H2 (profile `dev`)
- Modelagem oficial de banco: PostgreSQL
- Mobile: React Native com Expo
- Simulador IoT: Python
- Documentação e evidências: Markdown e imagens

## 6. Estrutura de pastas
```text
.
├── backend/
├── mobile/
├── database/
├── iot-simulator/
├── docs/
│   ├── evidencias/
│   ├── evidencias-api/
│   ├── evidencias-iot/
│   ├── documento-final.md
│   ├── plano-de-testes.md
│   └── roteiro-pitch.md
├── postman/
├── README.md
├── integrantes.txt
└── .gitignore
```

## 7. Como rodar o backend em modo dev/H2
No terminal, execute:
```powershell
cd backend
.\mvnw.cmd spring-boot:run "-Dspring-boot.run.profiles=dev"
```

Este comando inicia o backend usando o perfil `dev`, que utiliza o banco em memória H2 para demonstração local.

## 8. Como acessar Swagger
Com o backend em execução, acesse:

- `http://localhost:8080/swagger-ui/index.html`

## 9. Como rodar o mobile
No terminal, execute:
```powershell
cd mobile
npm install
npm run start
```

Abra o app no Expo Go ou emulador conforme instruções do terminal.

## 10. Como rodar o simulador IoT
No terminal, execute:
```powershell
cd iot-simulator
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python sensor_simulator.py
```

O simulador envia uma leitura demo para o backend e pode ser usado para gerar alertas através da API.

## 11. Onde estão os scripts de banco
Os scripts de banco estão na pasta `database/`:
- `schema.sql`
- `seed.sql`
- `queries.sql`

## 12. Onde estão as evidências e plano de testes
- Evidências da API: `docs/evidencias-api/`
- Evidências do IoT: `docs/evidencias-iot/`
- Plano de testes: `docs/plano-de-testes.md`

## 13. Integrantes do grupo
- Yuri Monteiro Zacarioto - RM550952
- Vitor Futida Sternik - RM98697
- Caio Henrique Rocha da Silva - RM552308
- Vitor Reyes Souza - RM550766

## 14. Observação sobre bancos de dados
A modelagem oficial do projeto utiliza PostgreSQL. O perfil `dev` do backend roda com H2 para facilitar demonstração local e testes rápidos sem dependências externas.
