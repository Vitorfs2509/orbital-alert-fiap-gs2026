# Orbital Alert

## 1. Nome do projeto
Orbital Alert

## 2. Descrição da solução
Orbital Alert é um MVP acadêmico que combina dados satelitais simulados e sensores IoT para monitorar regiões de risco e gerar alertas preventivos de enchentes, queimadas e eventos climáticos extremos.

> **Foco desta fase acadêmica: monitoramento e prevenção de enchentes.**
> O cenário demonstrado (sensores `WATER_LEVEL` e `RAINFALL`, score de risco `FLOOD`, pitch e
> evidências) prioriza enchentes por ser o evento de maior recorrência e impacto nas regiões
> estudadas. **Isso é uma escolha de caso de uso, não uma remoção funcional:** o suporte técnico
> a incêndio/temperatura (`TEMPERATURE`, `SMOKE`, `HUMIDITY`) continua íntegro no backend, no
> simulador, nos ETLs e no modelo de risco.

## 3. Problema abordado
O sistema busca antecipar ameaças ambientais em áreas vulneráveis, oferecendo monitoramento contínuo e geração de alertas automáticos para apoiar decisões de mitigação e resposta rápida. Na fase atual, o caso de uso demonstrado é a **enchente**: nível de água e volume de chuva acima dos limiares disparam alerta automático e alimentam o score de risco por região.

## 4. Conexão com Space Economy
A solução integra informações espaciais e terrestres para promover a Space Economy, demonstrando como dados derivados de observação da Terra e IoT podem ser aplicados em proteção de populações e gestão de riscos climáticos.

## 5. Tecnologias usadas
- Backend: Java Spring Boot
- Banco de dados local: H2 (profile `dev`)
- Modelagem oficial de banco: PostgreSQL
- Mobile: React Native com Expo
- Simulador IoT: Python
- Data Lake e ETL (Fase 5): arquivos JSON/JSONL/CSV e scripts Python (biblioteca padrão)
- IA generativa (Fase 5): modo MOCK offline, com integração opcional a LLM externo
- Cloud (Fase 6): **Oracle Cloud Infrastructure — Object Storage**, via SDK oficial `oci` (opcional)
- Documentação e evidências: Markdown e imagens

## 6. Estrutura de pastas
```text
.
├── backend/
├── mobile/
├── database/
├── iot-simulator/
├── data-lake/              # Fase 5: RAW / TRUSTED / CURATED / samples
│   ├── raw/
│   ├── trusted/
│   ├── curated/
│   └── samples/
├── etl/                    # Fase 5: scripts de ETL em Python
│   ├── raw_to_trusted.py
│   ├── trusted_to_curated.py
│   ├── oci_storage.py            # Fase 6: integração OCI Object Storage
│   ├── sync_data_lake_to_oci.py  # Fase 6: sincronização do Data Lake
│   ├── requirements-oci.txt      # Fase 6: dependência opcional (SDK oci)
│   └── tests/
├── docs/
│   ├── evidencias/
│   ├── evidencias-api/
│   ├── evidencias-iot/
│   ├── oracle-integration.md
│   ├── data-lake-architecture.md
│   ├── ingestion-flow.md
│   ├── data-maintenance.md
│   ├── ai-generative-example.md
│   ├── documento-final.md
│   ├── plano-de-testes.md
│   └── roteiro-pitch.md
├── postman/
├── README.md
├── integrantes.txt
├── .env.example            # Fase 6: modelo de variáveis (sem segredos)
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

Por padrão o app roda com **dados mockados**, sem depender do backend. Para consumir os alertas
reais da API, crie `mobile/.env` a partir de [mobile/.env.example](mobile/.env.example):

```env
EXPO_PUBLIC_API_BASE_URL=http://SEU_IP_LOCAL:8080
```

Com a variável definida, o app busca `GET /api/alerts`. Se a API estiver fora do ar, ele volta
sozinho para o mock — a demonstração offline nunca quebra.

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

## 11.1. Fase 5 — Data Lake, ETL e IA generativa

A Fase 5 acrescenta uma camada analítica **em paralelo** ao sistema operacional. A API, o banco,
os alertas e o aplicativo mobile continuam funcionando exatamente como antes.

```text
Sensores IoT → Spring Boot API → banco operacional → alertas → mobile
                      ↓
                 Data Lake RAW → ETL → TRUSTED → ETL → CURATED → IA generativa → recomendação
```

### Demonstração completa (do zero)

```powershell
# 1) Backend no ar (perfil dev/H2)
cd backend
.\mvnw.cmd spring-boot:run "-Dspring-boot.run.profiles=dev"

# 2) Em outro terminal, na raiz do repositório: cadastre região e sensor pelo Swagger
#    (payloads em COMO_RODAR.md) e envie uma leitura
python iot-simulator/sensor_simulator.py --sensor-id 1 --value 91.2

# 3) O evento bruto aparece na camada RAW, particionado por data
Get-Content data-lake/raw/2026/09/08/readings-2026-09-08.jsonl

# 4) ETL: RAW → TRUSTED → CURATED
python etl/raw_to_trusted.py
python etl/trusted_to_curated.py

# 5) Recomendação da IA a partir da camada CURATED
curl http://localhost:8080/api/recommendations/regions/1
```

Para demonstrar sem depender do backend, use os dados de exemplo:

```powershell
python etl/raw_to_trusted.py --raw-dir data-lake/samples
python etl/trusted_to_curated.py
```

### Novos endpoints

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/api/recommendations/regions/{regionId}` | Recomendação de IA para uma região |
| `GET` | `/api/recommendations` | Recomendação para todas as regiões |
| `GET` | `/api/recommendations/regions/{regionId}/prompt` | Prompt exato enviado à IA (auditoria) |

Todos são somente leitura: a IA é **apoio à decisão** e nunca executa ações.

### Configuração (nenhuma chave no código)

| Propriedade | Variável de ambiente | Padrão |
|---|---|---|
| `orbital.datalake.base-path` | `DATA_LAKE_PATH` | `../data-lake` |
| `orbital.datalake.enabled` | `DATA_LAKE_ENABLED` | `true` |
| `orbital.ai.provider` | `AI_PROVIDER` | `mock` |
| `orbital.ai.api-key` | `OPENAI_API_KEY` | *(vazio)* |

O modo `mock` é o padrão, funciona offline e sem API key. A integração com LLM externo é
opcional e degrada automaticamente para o mock em caso de falha ou chave ausente.

### Documentação da Fase 5

- [docs/data-lake-architecture.md](docs/data-lake-architecture.md) — camadas e modelo de risco
- [docs/ingestion-flow.md](docs/ingestion-flow.md) — fluxo de ingestão ponta a ponta
- [docs/data-maintenance.md](docs/data-maintenance.md) — qualidade, duplicidade, rastreabilidade
- [docs/ai-generative-example.md](docs/ai-generative-example.md) — prompt e recomendação
- [etl/README.md](etl/README.md) — uso dos scripts de ETL

## 11.2. Fase 6 — Integração Oracle (OCI Object Storage)

A Fase 6 acrescenta a persistência em nuvem do Data Lake usando **Oracle Cloud Infrastructure —
Object Storage**. O funcionamento local **não muda**: o filesystem continua sendo a fonte de
desenvolvimento, teste e fallback; a Oracle recebe uma cópia das camadas.

```text
Sensores IoT → Spring Boot API → banco operacional → AlertService → alertas → mobile
                      ↓
                 RAW local → ETL → TRUSTED local → ETL → CURATED local → recomendação
                      ↓
             sincronização (etl/sync_data_lake_to_oci.py)
                      ↓
      Oracle Cloud Infrastructure (OCI) · Object Storage
             raw/…   trusted/…   curated/…
```

Os prefixes no bucket espelham o layout local, sem tradução:

```
LOCAL  data-lake/raw/2026/09/08/readings-2026-09-08.jsonl
OCI    raw/2026/09/08/readings-2026-09-08.jsonl
```

### Ver o que seria enviado (sem conta Oracle, sem internet)

```powershell
python etl/sync_data_lake_to_oci.py --dry-run
python etl/sync_data_lake_to_oci.py --layer curated --dry-run
```

### Upload real

```powershell
pip install -r etl/requirements-oci.txt   # dependência opcional
$env:OCI_BUCKET_NAME = "orbital-alert-datalake"
python etl/sync_data_lake_to_oci.py
```

### Configuração (nenhuma credencial no código nem no Git)

| Variável | Obrigatória | Padrão |
|---|---|---|
| `OCI_BUCKET_NAME` | **sim** | — |
| `OCI_NAMESPACE` | não | resolvido pelo SDK |
| `OCI_CONFIG_FILE` | não | `~/.oci/config` |
| `OCI_PROFILE` | não | `DEFAULT` |
| `OCI_REGION` | não | região do profile |

Modelo em [.env.example](.env.example). Chave privada, fingerprint e OCIDs ficam apenas em
`~/.oci/config`, fora do repositório — o `.gitignore` bloqueia `*.pem`, `*.key`, `.oci/` e afins.

> **A integração Oracle é opcional.** `mvnw test`, os ETLs, o backend em perfil dev, o simulador
> e o app mobile continuam funcionando sem internet, sem conta Oracle e sem o pacote `oci`.

### Testes da integração

```powershell
python etl/tests/test_oci_sync.py
```

### Documentação da Fase 6

- [docs/oracle-integration.md](docs/oracle-integration.md) — tecnologia, motivo da escolha,
  arquitetura, segurança, comandos e quais screenshots tirar no Console Oracle

## 12. Onde estão as evidências e plano de testes
- Evidências da API: `docs/evidencias-api/`
- Evidências do IoT: `docs/evidencias-iot/`
- Evidências do Oracle Console: `docs/evidencias-oci/` — **pendente**, capturas manuais listadas
  em [docs/oracle-integration.md](docs/oracle-integration.md#10-evidências-para-o-trabalho-acadêmico)
- Plano de testes: `docs/plano-de-testes.md`

## 13. Integrantes do grupo
- Yuri Monteiro Zacarioto - RM550952
- Vitor Futida Sternik - RM98697
- Caio Henrique Rocha da Silva - RM552308
- Vitor Reyes Souza - RM550766

## 14. Observação sobre bancos de dados
A modelagem oficial do projeto utiliza PostgreSQL. O perfil `dev` do backend roda com H2 para facilitar demonstração local e testes rápidos sem dependências externas.
