# Catálogo de evidências

| Fonte | Conteúdo | Natureza |
|---|---|---|
| [Arquivo do cenário final](execucao-final/demo.json) | 45 e 95 mm/h, 13 verificações, IDs de leitura e alerta, score e falha controlada | HTTP, banco e processamento reais · dados de entrada simulados |
| [Dashboard](execucao-final/web-dashboard.png), [detalhe](execucao-final/web-regiao.png), [vazio](execucao-final/web-vazio.png) | Capturas do Expo web no Compose final | Execução real em navegador |
| [Estado final](execucao-final/status.json) | Contadores do processo e status do lote | Resposta real do serviço |
| [API JSONL](execucao-final/api.jsonl), [lote](execucao-final/batches.jsonl), [associações](execucao-final/memberships.jsonl) | Eventos originais da execução instrumentada | Emissão real |
| [Etapa 2](../02_Execucao_Plataforma/RESULTADOS.md) | Persistência após recriação, navegador falhando sem fallback, duas cargas Oracle | Evidências históricas da Fase 7 de um checkpoint anterior |
| [DevSecOps](../03_DevSecOps/DEVSECOPS.md) | Testes, qualidade, auditoria e Actions | Execuções local e remota identificadas |
| [Monitoramento](../04_Monitoramento/MONITORAMENTO.md) | Lote periódico, trava e falha controlada | Execução local isolada |
| [Mineração](../05_Mineracao_Processos/ANALISE.md) | Análise, event log CSV e gráficos | Transformação dos registros reais |
| [Auditoria](../AUDITORIA_ETAPA_1.md) | Inventário da Fase 6, catálogo e hash do pacote anterior | Histórico e avaliação de usabilidade com personas simuladas |

Os arquivos `web-*.json` da execução final registram respostas HTTP observadas pelo navegador. O pacote separa a execução final da documentação e das capturas anteriores.
