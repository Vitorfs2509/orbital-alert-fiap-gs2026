# Orbital Alert · AgroSmart Fase 7

MVP acadêmico integrado e validado localmente em 24/11/2026. A demonstração executa sensores simulados, API Spring Boot, PostgreSQL, Data Lake e dashboard Expo web. O pacote inclui evidências reais do cenário e da execução do GitHub Actions, com os achados de auditoria explícitos.

- [Como rodar no Windows em dois comandos](COMO_RODAR.md)
- [Relatório técnico final em PDF](RELATORIO_TECNICO_FASE7.pdf)
- [Checklist para submissão](CHECKLIST_FINAL.md)
- [Progresso e checkpoints](../PROGRESSO.md)

| Pasta | Conteúdo principal |
|---|---|
| [01 Arquitetura](01_Arquitetura/ARQUITETURA.md) | Componentes, dados, diagrama Mermaid, SVG e PNG |
| [02 Execução](02_Execucao_Plataforma/COMO_RODAR_COMPOSE.md) | Compose, PoC, volumes e Oracle opcional |
| [03 DevSecOps](03_DevSecOps/DEVSECOPS.md) | Proteção da API, cobertura, qualidade, auditoria das dependências e pipeline |
| [04 Monitoramento](04_Monitoramento/MONITORAMENTO.md) | Actuator, status agregado, logs e ETL periódico |
| [05 Mineração](05_Mineracao_Processos/ANALISE.md) | Event log, variantes, gráfico, tempos e limites |
| [06 Pitch](06_Pitch/APRESENTACAO.md) | PowerPoint de sete slides com capturas do MVP |
| [07 Vídeos](07_Videos/LINKS_DOS_VIDEOS.md) | [Roteiro técnico](07_Videos/VIDEO_TECNICO.md), [roteiro pitch](07_Videos/VIDEO_PITCH.md) e campos para URLs |
| [08 Evidências](08_Evidencias/INDICE.md) | Catálogo, capturas e execução final |
| [09 Código](09_Codigo/REFERENCIAS.md) | Referências na árvore do projeto e scripts |

O [inventário da Fase 6](AUDITORIA_ETAPA_1.md), a [matriz original](MATRIZ_REQUISITOS.md), o [planejamento](ESTRATEGIA_TECNICA.md) e o [baseline](BASELINE_ETAPA_1.md) registram a auditoria. A [execução final aa88ffa21691](08_Evidencias/execucao-final/demo.json) passou 13 verificações. O Actions rodou e publicou evidências. A falha global por verificações de segurança está detalhada em DevSecOps.

O arquivo `MANIFESTO_FASE7.json`, na raiz do ZIP, lista o commit e os hashes SHA‑256. A reconstrução do pacote a partir de um clone está em [empacotamento](09_Codigo/EMPACOTAMENTO.md).
