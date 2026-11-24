FROM node:22-bookworm-slim AS build
WORKDIR /app
COPY mobile/package*.json ./
RUN npm ci --no-audit --no-fund
COPY mobile/ ./
ENV EXPO_PUBLIC_DATA_MODE=api EXPO_NO_TELEMETRY=1 EXPO_OFFLINE=1
RUN npm run typecheck && npm run build:web

FROM nginx:1.28-alpine
COPY mobile/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 8080
