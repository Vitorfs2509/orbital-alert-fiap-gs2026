# Evidências de Testes e Demonstração

Esta pasta deve armazenar as evidências visuais e técnicas para a entrega final da Global Solution.

## Onde colocar os arquivos
- Salve imagens em `docs/evidencias/imagens/` (criar pasta).
- Salve logs em `docs/evidencias/logs/` (criar pasta).
- Salve exports SQL/texto em `docs/evidencias/sql/` (criar pasta).

## Evidências recomendadas

1. **Tela do Swagger**
   - Captura da URL `http://localhost:8080/swagger-ui.html`.
   - Mostrar lista de endpoints disponíveis.

2. **Requisições bem-sucedidas no Postman**
   - Capturar pelo menos:
     - login/cadastro
     - listagem de regiões
     - criação de leitura
     - listagem de alertas ativos
   - Mostrar status HTTP (200/201) e corpo de resposta.

3. **Telas do app mobile**
   - Login
   - Dashboard
   - Regiões
   - Detalhe do alerta

4. **Logs do simulador IoT**
   - Trecho com leituras enviadas com sucesso.
   - Trecho com fallback offline (quando API estiver indisponível).

5. **Resultados de consultas do banco**
   - Execução de consultas relevantes de `database/queries.sql`.
   - Pelo menos uma evidência de alerta ativo e uma de contagem por severidade.

## Dica para o PDF final
Organizar as evidências por seção (Backend, Mobile, IoT, Banco) e adicionar uma legenda curta em cada imagem para facilitar a apresentação e correção.
