# Mobile - Orbital Alert (Expo + React Native)

## Requisitos
- Node.js 18+
- npm 9+
- Expo Go no celular (Android/iOS) **ou** emulador

## Instalação
```bash
cd mobile
npm install
```

## Como executar com Expo
```bash
npm run start
```

Depois:
- pressione `a` para Android (emulador)
- pressione `i` para iOS (macOS)
- ou escaneie o QR Code com o app Expo Go

## Telas disponíveis
1. **Login**
   - Campo de e-mail
   - Campo de senha
   - Botão de login acadêmico (mock)
   - Texto curto explicando o Orbital Alert

2. **Dashboard**
   - Quantidade de alertas ativos
   - Quantidade de regiões monitoradas
   - Quantidade de sensores online
   - Nível geral de risco
   - Cards visuais com resumo e explicação de monitoramento satélite + IoT

3. **Regiões**
   - Lista de regiões monitoradas
   - Cidade/UF
   - Nível de risco
   - Score de risco por satélite
   - Quantidade de sensores
   - Toque no card para abrir o detalhe de alerta relacionado

4. **Detalhe do Alerta**
   - Título do alerta
   - Região
   - Severidade
   - Dados de sensor
   - Ação recomendada
   - Status
   - Explicação do motivo do alerta

## Fonte de dados: mock (padrão) ou backend real

O app funciona nos dois modos e escolhe sozinho, sem alterar código.

| | Modo mock (padrão) | Modo backend |
|---|---|---|
| Quando | `EXPO_PUBLIC_API_BASE_URL` ausente **ou** API fora do ar | variável definida e API respondendo |
| Alertas | `src/data/mockData.ts` | `GET /api/alerts` |
| Regiões e métricas | mock | mock |
| Indicador na tela | ⚪ "Alertas em modo demonstração (dados mockados)" | 🟢 "Alertas do backend real (GET /api/alerts)" |

### Como apontar para o backend real

```bash
cd mobile
cp .env.example .env      # PowerShell: Copy-Item .env.example .env
```

```env
EXPO_PUBLIC_API_BASE_URL=http://SEU_IP_LOCAL:8080
```

Reinicie o Expo depois de mudar o `.env` (`npm run start`).

> No celular com Expo Go, `localhost` aponta para o próprio aparelho. Use o IP da máquina que
> roda o backend na mesma rede Wi-Fi. Emulador Android: `http://10.0.2.2:8080`.

### Por que o fallback existe

A chamada tem timeout de 4 s e qualquer falha (variável ausente, API fora do ar, resposta
inesperada, lista vazia) mantém os dados mockados. A demonstração offline — em vídeo ou no
pitch de 3 minutos — nunca depende do backend estar no ar.

A implementação fica em `src/services/api.ts` (~80 linhas). Regiões e métricas seguem mockadas
de propósito: o `RegionDto` do backend não expõe `satelliteRiskScore` nem `sensorsCount`, e
buscar esses números exigiria mudar o contrato da API e as telas — fora do escopo mínimo
desta fase.

## Por que dados mockados são aceitáveis nesta entrega FIAP
Para o MVP acadêmico da Global Solution, dados mockados permitem:
- demonstrar claramente a proposta de valor e UX do produto
- validar o fluxo de telas e comunicação visual de risco
- reduzir complexidade técnica inicial e risco de falhas em demo

Assim, o time consegue apresentar um pitch de 3 minutos com foco em problema, solução e experiência do usuário.
