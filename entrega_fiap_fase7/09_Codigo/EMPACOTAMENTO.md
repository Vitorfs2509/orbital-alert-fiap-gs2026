# Gerar e revisar o ZIP

A partir do worktree Git da Fase 7, confirme que os documentos revisados foram incluídos no commit local. Na raiz do repositório:

```powershell
python scripts/empacotar_fase7.py ..\Orbital_Alert_FIAP_Fase7.zip
```

O script empacota o snapshot Git com o código, os documentos e as evidências. Ele valida estrutura, links locais, hashes e integridade. Credenciais, arquivos reais de ambiente, dependências instaladas, caches e volumes ficam fora. Se editar os links dos vídeos no clone, registre a edição em um commit local antes de empacotar de novo. Preserve o nome `entrega_fiap_fase7` dentro do projeto.

Para revisar no Windows, extraia o ZIP e abra `entrega_fiap_fase7/README_ENTREGA.md`. O manifesto na raiz identifica todos os arquivos e a revisão. A Fase 6 permanece separada.
