@echo off
setlocal
rem Simple Maven Wrapper for Orbital Alert backend.
rem Uses a local Maven distribution when available, falls back to system mvn,
rem and can download Maven into .mvn\wrapper when Maven is not installed globally.

set "BASE_DIR=%~dp0"
set "WRAPPER_DIR=%BASE_DIR%.mvn\wrapper"
set "PROPERTIES_FILE=%WRAPPER_DIR%\maven-wrapper.properties"
set "MAVEN_VERSION=3.9.10"

if exist "%PROPERTIES_FILE%" (
  for /f "tokens=1,* delims==" %%A in ('findstr /b "maven.version=" "%PROPERTIES_FILE%"') do set "MAVEN_VERSION=%%B"
)

set "MAVEN_HOME=%WRAPPER_DIR%\apache-maven-%MAVEN_VERSION%"
set "MAVEN_CMD=%MAVEN_HOME%\bin\mvn.cmd"

if exist "%MAVEN_CMD%" (
  call "%MAVEN_CMD%" %*
  exit /b %ERRORLEVEL%
)

where mvn >nul 2>nul
if %ERRORLEVEL%==0 (
  call mvn %*
  exit /b %ERRORLEVEL%
)

if not exist "%WRAPPER_DIR%" mkdir "%WRAPPER_DIR%"
set "MAVEN_ZIP=%WRAPPER_DIR%\apache-maven-%MAVEN_VERSION%-bin.zip"
set "MAVEN_URL=https://archive.apache.org/dist/maven/maven-3/%MAVEN_VERSION%/binaries/apache-maven-%MAVEN_VERSION%-bin.zip"

echo Maven %MAVEN_VERSION% was not found locally. Downloading from: %MAVEN_URL%
powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%MAVEN_URL%' -OutFile '%MAVEN_ZIP%'; Expand-Archive -Path '%MAVEN_ZIP%' -DestinationPath '%WRAPPER_DIR%' -Force"
if %ERRORLEVEL% neq 0 exit /b %ERRORLEVEL%

call "%MAVEN_CMD%" %*
exit /b %ERRORLEVEL%
