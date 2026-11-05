@echo off
setlocal
chcp 65001 > nul
title Inicializador do Projeto

cd /d "%~dp0"

echo ========================================
echo       INICIALIZADOR DO PROJETO
echo ========================================
echo.

:: 1. Verificar Python3
where python3 > nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python3 nao encontrado no PATH.
    pause
    exit /b 1
)

:: 2. Criar ambiente virtual, se necessario
if not exist "venv\Scripts\python3.exe" (
    echo [INFO] Criando ambiente virtual...
    python3 -m venv venv
    if errorlevel 1 (
        echo [ERRO] Falha ao criar venv.
        pause
        exit /b 1
    )
)

:: 3. Ativar ambiente virtual
call "venv\Scripts\activate.bat"
if errorlevel 1 (
    echo [ERRO] Falha ao ativar venv.
    pause
    exit /b 1
)

:: 4. Instalar dependencias
if not exist "requisitos.txt" (
    echo [ERRO] requisitos.txt nao encontrado.
    pause
    exit /b 1
)

echo [INFO] Instalando dependencias...
python3 -m pip install -r requisitos.txt
if errorlevel 1 (
    echo [ERRO] Falha ao instalar dependencias.
    pause
    exit /b 1
)

:: 5. Ler configuracao do banco.txt
if not exist "banco.txt" (
    echo [ERRO] banco.txt nao encontrado.
    pause
    exit /b 1
)

set "SQL_SERVER="
set "DB_NAME="

for /f "usebackq tokens=1,* delims==" %%A in ("banco.txt") do (
    if /i "%%A"=="server" set "SQL_SERVER=%%B"
    if /i "%%A"=="database" set "DB_NAME=%%B"
)

if not defined SQL_SERVER (
    echo [ERRO] Chave server nao encontrada em banco.txt.
    pause
    exit /b 1
)

if not defined DB_NAME (
    echo [ERRO] Chave database nao encontrada em banco.txt.
    pause
    exit /b 1
)

:: Ajuste para a instancia SQLEXPRESS caso o arquivo
:: ainda esteja configurado para localhost.
if /i "%SQL_SERVER%"=="localhost" set "SQL_SERVER=.\SQLEXPRESS"

echo.
echo [INFO] Servidor: %SQL_SERVER%
echo [INFO] Banco: %DB_NAME%
echo [INFO] Verificando conexao...

where sqlcmd > nul 2>&1
if errorlevel 1 (
    echo [ERRO] sqlcmd nao encontrado no PATH.
    pause
    exit /b 1
)

:: 6. Consultar existencia do banco conectando em master
set "DB_RESULT=%TEMP%\db_check_%RANDOM%.txt"
set "DB_ERROR=%TEMP%\db_error_%RANDOM%.txt"

sqlcmd -S "%SQL_SERVER%" -E -C -b -d master -h -1 -W ^
    -Q "SET NOCOUNT ON; SELECT CASE WHEN DB_ID(N'%DB_NAME%') IS NOT NULL THEN 1 ELSE 0 END;" ^
    -o "%DB_RESULT%" 2> "%DB_ERROR%"

if errorlevel 1 (
    echo.
    echo [ERRO] Nao foi possivel conectar ao SQL Server.
    type "%DB_ERROR%"
    del "%DB_RESULT%" "%DB_ERROR%" > nul 2>&1
    pause
    exit /b 1
)

set "DB_EXISTS="
set /p DB_EXISTS=<"%DB_RESULT%"

del "%DB_RESULT%" "%DB_ERROR%" > nul 2>&1

:: 7. Criar banco (se nao existir) e garantir atualizacao/geracao de dados
if "%DB_EXISTS%"=="0" (
    echo [INFO] Banco inexistente. Criando banco...
) else (
    echo [INFO] Banco %DB_NAME% ja existe. Verificando estrutura...
)

if not exist "site.sql" (
    echo [ERRO] site.sql nao encontrado.
    pause
    exit /b 1
)

sqlcmd -S "%SQL_SERVER%" -E -C -b -d master -i "site.sql"
if errorlevel 1 (
    echo [ERRO] Falha ao executar site.sql.
    pause
    exit /b 1
)

echo [INFO] Gerando / atualizando dados iniciais...
python3 "generate_data.py"
if errorlevel 1 (
    echo [ERRO] Falha ao executar o script de geracao de dados.
    pause
    exit /b 1
)

:: 8. Iniciar aplicacao
if not exist "run.py" (
    echo [ERRO] run.py nao encontrado.
    pause
    exit /b 1
)

echo.
echo [INFO] Iniciando aplicacao...
echo ========================================

start INTERFACE\loja_app.exe
python3 "run.py"

if errorlevel 1 (
    echo [ERRO] A aplicacao foi encerrada com erro.
    pause
    exit /b 1
)

endlocal