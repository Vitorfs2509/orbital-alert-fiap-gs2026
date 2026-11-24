# DevSecOps · qualidade e segurança

## Política aplicada

Leituras públicas foram limitadas aos endpoints do painel e à verificação de saúde. Cadastro e alterações de regiões/sensores, resolução de alertas, cadastro de usuários e diagnóstico de recomendações exigem a credencial de administração. A ingestão exige a credencial separada do sensor. Identidade ausente ou inválida recebe HTTP 401. Identidade válida sem o papel exigido recebe 403. O filtro usa Bearer explícito, sessões desativadas e comparação de segredo sem delegar credenciais ao frontend. O login legado verifica BCrypt e retorna perfil. Ele não emite as credenciais operacionais. Login completo por pessoa, rotação gerenciada e TLS ficam para uma implantação fora deste MVP local.

O script `scripts/configurar.ps1` cria valores aleatórios se os campos estiverem vazios e grava apenas no `.env` local, ignorado pelo Git. O Compose restringe bancos e backend à rede interna e publica o frontend em loopback. O banco usa um único papel nesse ambiente acadêmico. Produção requer papel de migração separado, identidade individual e limitação de chamadas. O cliente de LLM fica opcional e desativado por padrão.

## Pipeline

[Workflow no GitHub](https://github.com/Vitorfs2509/orbital-alert-fiap-gs2026/actions) publica relatórios separados de Java, Python, web e containers. O job Java executa Maven, JUnit, JaCoCo e SpotBugs com Java 21. Python executa testes, Ruff e pip-audit. Web executa TypeScript, exportação Expo e npm audit. O job integrado faz build, sobe a pilha, executa a PoC e usa Trivy para dependências no JAR e vulnerabilidades das imagens. As verificações de segurança mantêm os resultados e o código de saída. O scanner de imagens passa pelos alvos restantes quando um alvo falha.

## Aplicações e riscos residuais

- A auditoria npm original registrou 44 alertas (2 críticos, 19 altos); a atualização compatível de lockfile reduziu para 33 (1 crítico, 10 altos). Alertas que exigem migração principal do Expo foram deixados visíveis. Valide o cliente nativo em uma migração separada.
- O backend passou para Spring Boot 3.5.16 e Springdoc 2.8.17, ainda em Java 21. Requests foi atualizado para 2.34.2. Os relatórios de dependências ficam separados da observação por inspeção do código.
- Um status de scanner indica o que a base e a configuração daquela execução encontraram. A falta de relatório ou erro de acesso à base de vulnerabilidades não equivale a aprovação.

Resultados e relatórios locais ficam em [evidências](evidencias/). O relatório final registra o resultado remoto observado e os achados ainda abertos.
