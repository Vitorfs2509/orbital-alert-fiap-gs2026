# Backend - Orbital Alert

API RESTful do MVP acadêmico **Orbital Alert**, desenvolvida em Java 21 com Spring Boot para simular o monitoramento de regiões de risco e geração de alertas preventivos.

## Tecnologias usadas
- Java 21
- Spring Boot
- Maven
- Spring Web
- Spring Data JPA
- PostgreSQL Driver
- Bean Validation
- Springdoc OpenAPI/Swagger
- Spring Security Crypto (BCrypt)

## Configuração do banco
A API usa PostgreSQL por padrão e espera que os scripts em `database/` sejam executados antes da aplicação.

Variáveis de ambiente opcionais:
- `DB_URL` (padrão: `jdbc:postgresql://localhost:5432/orbital_alert`)
- `DB_USER` (padrão: `postgres`)
- `DB_PASSWORD` (padrão: `postgres`)

Exemplo:
```bash
psql -U postgres -d orbital_alert -f ../database/schema.sql
psql -U postgres -d orbital_alert -f ../database/seed.sql
```

## Como rodar a API
```bash
cd backend
./mvnw spring-boot:run
```

No Windows, use:
```bat
cd backend
.\mvnw.cmd spring-boot:run
```

A API ficará disponível em:
- `http://localhost:8080`

## Maven Wrapper
O backend inclui Maven Wrapper, então não é necessário ter Maven instalado globalmente.

Linux/macOS:
```bash
cd backend
./mvnw test
./mvnw spring-boot:run
```

Windows:
```bat
cd backend
.\mvnw.cmd test
.\mvnw.cmd spring-boot:run
```

## Principais endpoints

### Autenticação
- `POST /api/auth/register`
- `POST /api/auth/login`

### Regiões
- `GET /api/regions`
- `POST /api/regions`

### Sensores
- `GET /api/sensors`
- `POST /api/sensors`
- `DELETE /api/sensors/{id}`

### Leituras
- `POST /api/readings`

### Alertas
- `GET /api/alerts`
- `GET /api/alerts/active`
- `PUT /api/alerts/{id}/resolve`

## Swagger/OpenAPI
A documentação interativa fica disponível em:
- `http://localhost:8080/swagger-ui.html`

## Regras de alerta
Ao receber uma leitura em `POST /api/readings`, a API salva a leitura e cria um alerta quando necessário:

- `WATER_LEVEL >= 80`: alerta de enchente.
- `TEMPERATURE >= 40`: alerta de temperatura elevada/risco de queimada.
- `SMOKE >= 70`: alerta de fumaça/incêndio.
- `RAINFALL >= 60`: alerta de chuva intensa.

Os alertas retornados pela API usam status acadêmico simples:
- `ACTIVE`
- `RESOLVED`

## Segurança e validação
- Senhas são armazenadas com hash BCrypt.
- `passwordHash` não é retornado nas respostas.
- DTOs usam Bean Validation (`@NotBlank`, `@Email`, `@NotNull`, `@Positive`).
- Acesso ao banco é feito por JPA Repository, evitando SQL manual concatenado.
- Erros básicos são tratados por um handler global.
