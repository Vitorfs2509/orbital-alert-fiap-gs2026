# Como rodar no Windows

Abra o Docker Desktop, aguarde o engine Linux iniciar e abra o PowerShell na raiz do projeto extraído. Execute:

```powershell
.\scripts\subir.ps1
.\scripts\demonstrar.ps1 -Mineracao -Resultado .\demo.json
```

Abra **http://127.0.0.1:8080/**. Clique em **Abrir painel** e depois na região **AgroSmart · Demo …**. Se o painel já estava aberto, clique em **Atualizar dados**. O primeiro build baixa as imagens e dependências. O script cria `.env` com senhas e credenciais aleatórias locais quando necessário. Guarde o `.env` local para usar os volumes existentes.

Se a política do PowerShell impedir scripts locais e você já revisou os arquivos extraídos, execute cada script em um processo com a política limitada a ele:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\subir.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demonstrar.ps1 -Mineracao -Resultado .\demo.json
```

Para ver o status e encerrar:

```powershell
Invoke-RestMethod http://127.0.0.1:8080/api/status | ConvertTo-Json -Depth 10
.\scripts\encerrar.ps1
```

O encerramento padrão preserva os volumes. Se a porta estiver ocupada, configure `ORBITAL_WEB_PORT` no `.env` e use o endereço exibido por `subir.ps1`. Oracle é opcional e precisa de senhas próprias. Veja o [guia detalhado](02_Execucao_Plataforma/COMO_RODAR_COMPOSE.md).
