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
   - Todos os cards são interativos
   - Se houver alerta ativo, abre o detalhe do alerta
   - Se não houver alerta ativo, abre a tela de detalhes de monitoramento da região

4. **Detalhe do Alerta**
   - Título do alerta
   - Região
   - Severidade
   - Dados de sensor
   - Ação recomendada
   - Status
   - Explicação do motivo do alerta

5. **Detalhe de Monitoramento da Região**
   - Exibido quando a região clicada não possui alerta ativo
   - Nome da região, cidade/UF, risco, score satelital e sensores
   - Status de monitoramento, ação recomendada e explicação do risco

## Dados mockados
O protótipo utiliza apenas dados locais mockados em `src/data/mockData.ts` para:
- regiões
- alertas
- métricas de dashboard

Isso mantém o app leve, previsível e ideal para demonstração em vídeo sem depender do backend online.

## Por que dados mockados são aceitáveis nesta entrega FIAP
Para o MVP acadêmico da Global Solution, dados mockados permitem:
- demonstrar claramente a proposta de valor e UX do produto
- validar o fluxo de telas e comunicação visual de risco
- reduzir complexidade técnica inicial e risco de falhas em demo

Assim, o time consegue apresentar um pitch de 3 minutos com foco em problema, solução e experiência do usuário.
