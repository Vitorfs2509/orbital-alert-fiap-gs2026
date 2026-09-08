-- =====================================================================
-- Orbital Alert - preparacao do Oracle AI Database Free (local, Docker)
-- =====================================================================
-- Cria a tablespace, o usuario da aplicacao e concede APENAS os
-- privilegios necessarios para a carga analitica da camada CURATED.
--
-- Este script NAO cria a tabela: quem cria e valida REGION_RISK_SUMMARY e
-- o proprio `etl/sync_curated_to_oracle.py` (ver oracle_database.py).
--
-- NENHUMA SENHA E VERSIONADA AQUI. A senha e pedida na execucao.
--
-- Como rodar (PowerShell, com o container de pe):
--
--   $env:PATH = "$env:LOCALAPPDATA\Programs\DockerDesktop\resources\bin;$env:PATH"
--   Get-Content database/oracle-setup.sql | docker exec -i orbital-alert-oracle `
--     sqlplus -S "system/<SENHA_SYSTEM>@localhost:1521/FREEPDB1"
--
-- Detalhes e contexto: docs/oracle-database-integration.md
-- =====================================================================

SET LINESIZE 200
WHENEVER SQLERROR EXIT SQL.SQLCODE

-- Senha do usuario da aplicacao, informada no momento da execucao.
-- Fica apenas na sessao do SQL*Plus; nunca em arquivo versionado.
ACCEPT app_password CHAR PROMPT 'Senha para o usuario ORBITAL_ALERT: ' HIDE

-- ---------------------------------------------------------------------
-- 1. Tablespace dedicada
-- ---------------------------------------------------------------------
-- A imagem `free:latest-lite` nao traz a tablespace USERS e o default do
-- PDB e a SYSTEM. Dados de aplicacao nao devem morar na SYSTEM, entao o
-- projeto ganha a sua propria tablespace, dentro do volume persistente.
CREATE TABLESPACE ORBITAL_ALERT_DATA
  DATAFILE '/opt/oracle/oradata/FREE/FREEPDB1/orbital_alert01.dbf'
  SIZE 100M AUTOEXTEND ON NEXT 50M MAXSIZE 2G;

-- ---------------------------------------------------------------------
-- 2. Usuario da aplicacao
-- ---------------------------------------------------------------------
-- A aplicacao nunca usa SYSTEM. Este usuario e dono do proprio schema.
CREATE USER ORBITAL_ALERT IDENTIFIED BY "&app_password"
  DEFAULT TABLESPACE ORBITAL_ALERT_DATA
  QUOTA UNLIMITED ON ORBITAL_ALERT_DATA;

-- ---------------------------------------------------------------------
-- 3. Privilegios minimos
-- ---------------------------------------------------------------------
-- Login e criacao da tabela analitica. INSERT / UPDATE / SELECT nos
-- objetos do proprio schema sao implicitos para o dono - por isso nao ha
-- (nem deve haver) GRANT de DBA, RESOURCE ou ANY TABLE aqui.
GRANT CREATE SESSION TO ORBITAL_ALERT;
GRANT CREATE TABLE   TO ORBITAL_ALERT;

-- ---------------------------------------------------------------------
-- 4. Conferencia
-- ---------------------------------------------------------------------
COLUMN username           FORMAT A20
COLUMN default_tablespace FORMAT A24
SELECT username, account_status, default_tablespace
  FROM dba_users
 WHERE username = 'ORBITAL_ALERT';

SELECT privilege
  FROM dba_sys_privs
 WHERE grantee = 'ORBITAL_ALERT'
 ORDER BY privilege;

EXIT
