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

## Endpoints
- Auth: `POST /api/auth/register`, `POST /api/auth/login`
- Regions: `GET/POST /api/regions`, `GET/PUT/DELETE /api/regions/{id}`
- Sensors: `GET/POST /api/sensors`, `GET/DELETE /api/sensors/{id}`
- Readings: `POST /api/readings`, `GET /api/readings/latest`
- Alerts: `GET /api/alerts`, `GET /api/alerts/active`, `PUT /api/alerts/{id}/resolve`

## Swagger/OpenAPI
- URL: `http://localhost:8080/swagger-ui.html`

## Configuração de banco
A API usa PostgreSQL por padrão. Configuração em `src/main/resources/application.yml`.

## Práticas de segurança aplicadas
- Senhas com hash BCrypt.
- Uso de DTOs com validação (`Bean Validation`).
- `passwordHash` não é retornado nas respostas.
- Uso de Spring Data JPA (evita SQL manual no fluxo principal).
- Tratamento global de erros para respostas seguras e padronizadas.
