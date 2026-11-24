# Verificações da Etapa 1 · 24/11/2026

Base `23b139d40daab2cdfe8e2e0b5587452f6dfe7085`. O propósito foi conferir o ponto de partida para as mudanças, com as ferramentas disponíveis na máquina Windows.

| Verificação | Comando ou método | Resultado |
|---|---|---|
| Origem atualizada | `git fetch --no-tags origin main` e `git rev-parse FETCH_HEAD origin/main main` | SHA igual nos três refs. A primeira tentativa no sandbox não resolveu DNS. A repetição com acesso autorizado atualizou a referência. |
| Testes Python | `python -B -m unittest discover -s etl/tests -v` com `TMP` e `TEMP` em `work/fase7-audit-temp/` | Exit 0; 56 testes em 0,174 s nesta execução. Os testes presentes verificam código Oracle e OCI com unidades e dublês, sem conexão com serviços. |
| Backend Maven | Maven 3.9.10, `-o -B -f backend/pom.xml test`, dependências em cache, JBR 25.0.3 e `SPRING_PROFILES_ACTIVE=dev` | A primeira execução foi interrompida após ficar sem saída com o contexto iniciado. A segunda falhou com acesso negado a arquivo em `target/`. A terceira, em árvore limpa criada por `git archive` do mesmo commit, retornou exit 0 e `BUILD SUCCESS`: um teste, zero falhas e zero erros. |
| TypeScript | `mobile/node_modules/.bin/tsc.cmd --noEmit -p mobile/tsconfig.json` no worktree Fase 6; `git diff --quiet HEAD -- mobile` confirmou igualdade dos arquivos rastreados com a base comum | Exit 0 usando dependências já instaladas. Nenhum novo `npm ci` ou export Expo nesta etapa. |
| Docker | `docker --version`, `docker compose version`, `docker ps` | CLI 29.7.2 e Compose 5.5.0. `docker ps` falhou por ausência do pipe `dockerDesktopLinuxEngine`. |
| Artefatos Fase 6 | `python entrega_fiap_validacao/08_Codigo_Referencias/validar_entrega.py` no worktree original e `Get-FileHash -Algorithm SHA256` para o ZIP original | 150 links, hashes das evidências e estrutura conferidos. O hash do ZIP corresponde ao registrado na auditoria. |

Os registros locais de Python e das tentativas Maven ficam em `work/fase7-audit-*.txt`, fora dos worktrees. A senha gerada para desenvolvimento foi removida do registro Maven. O resultado válido é o da cópia limpa e cobre o perfil H2 com JBR 25; a execução com Java 21 e PostgreSQL ainda é critério da etapa integrada.

Esta auditoria não executou PostgreSQL real, containers, GitHub Actions, scanners, testes de autorização, build web novo, dispositivos nativos, testes de carga, Oracle real, LLM externo ou upload OCI. As verificações do código e dos artefatos antigos estão separadas das verificações executadas em 24/11/2026.
