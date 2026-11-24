# Aplicativo Orbital Alert · Expo

Na plataforma integrada, abra a URL informada por `scripts/subir.ps1`. O Nginx serve o bundle Expo e encaminha `/api` pela mesma origem. O botão **Abrir painel** dá acesso à demonstração acadêmica local. O aplicativo não solicita credenciais nesta etapa.

| Modo | Configuração | Comportamento |
|---|---|---|
| API (padrão) | `EXPO_PUBLIC_DATA_MODE=api`. No Compose web, deixe `EXPO_PUBLIC_API_BASE_URL` vazio. | Regiões, sensores, últimas leituras, alertas ativos, Risk Score, indicadores e recomendação vêm da API. A interface distingue carregamento, vazio, falha e sucesso. |
| Demonstração | `EXPO_PUBLIC_DATA_MODE=demo` em `mobile/.env`. | Usa fixtures dentro do app. A origem simulada aparece no painel e nos detalhes. |

O **Risk Score IoT** mostra a fonte CURATED ou o cálculo sobre o banco operacional e o horário da avaliação. A recomendação consultiva tem um botão próprio e identifica o provedor usado. Para atualizar o painel de modo API, clique em **Atualizar dados**.

## Expo local e dispositivos

```powershell
cd mobile
npm ci
Copy-Item .env.example .env  # somente se .env ainda não existir
npm run start
```

Para o modo API nativo, configure em `mobile/.env` uma `EXPO_PUBLIC_API_BASE_URL` alcançável pelo dispositivo. No emulador Android, tente `http://10.0.2.2:8080` para o host local. Em dispositivos físicos, use um endereço acessível na rede e uma configuração local explícita de encaminhamento. O Compose padrão publica em loopback. No web, prefira o Compose, pois a execução do Expo dev server e da API em origens diferentes depende da política CORS do servidor. Reinicie o Expo após editar o arquivo.

```powershell
npm run typecheck
npm run build:web
```

A prova de integração desta etapa foi executada no navegador. Confira o [guia do Compose](../entrega_fiap_fase7/02_Execucao_Plataforma/COMO_RODAR_COMPOSE.md) para executar o cenário.
