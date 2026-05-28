# Backend - Orbital Alert

## Requisitos
- Java 21
- Maven 3.9+
- PostgreSQL 14+

## Como executar
1. Configure banco PostgreSQL e rode os scripts em `database/`.
2. Configure variáveis de ambiente (opcional):
   - `DB_URL` (padrão: `jdbc:postgresql://localhost:5432/orbital_alert`)
   - `DB_USER` (padrão: `postgres`)
   - `DB_PASSWORD` (padrão: `postgres`)
3. Execute:
   ```bash
   cd backend
   mvn spring-boot:run
   ```

## Modo de desenvolvimento local com H2
Para executar o backend localmente sem PostgreSQL, use o perfil `dev` e o banco em memória H2:

```powershell
cd backend
.\mvnw.cmd spring-boot:run -Dspring-boot.run.profiles=dev
```

- O console H2 ficará disponível em `http://localhost:8080/h2-console`
- A UI do Swagger continua disponível em `http://localhost:8080/swagger-ui.html`

## Endpoints
- Auth: `POST /api/auth/register`, `POST /api/auth/login`
- Regions: `GET/POST /api/regions`, `GET/PUT/DELETE /api/regions/{id}`
- Sensors: `GET/POST /api/sensors`, `GET/DELETE /api/sensors/{id}`
- Readings: `POST /api/readings`, `GET /api/readings/latest`
- Alerts: `GET /api/alerts`, `GET /api/alerts/active`, `PUT /api/alerts/{id}/resolve`

## Swagger/OpenAPI
- URL: `http://localhost:8080/swagger-ui.html`

## Configuração de banco
A API usa PostgreSQL por padrão. A configuração padrão está em `src/main/resources/application.yml`.
Para desenvolvimento local, há um perfil `dev` que usa H2 em memória (`src/main/resources/application-dev.properties`).

## Práticas de segurança aplicadas
- Senhas com hash BCrypt.
- Uso de DTOs com validação (`Bean Validation`).
- `passwordHash` não é retornado nas respostas.
- Uso de Spring Data JPA (evita SQL manual no fluxo principal).
- Tratamento global de erros para respostas seguras e padronizadas.
