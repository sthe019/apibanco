# Inicializador do Projeto (versão PowerShell)
# Execute com: powershell -ExecutionPolicy Bypass -File .\iniciar.ps1

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Host.UI.RawUI.WindowTitle = 'Inicializador do Projeto'

Set-Location -Path $PSScriptRoot

function Stop-Script {
    param([string]$Mensagem)
    Write-Host "[ERRO] $Mensagem" -ForegroundColor Red
    Read-Host 'Pressione Enter para sair' | Out-Null
    exit 1
}

Write-Host '========================================'
Write-Host '       INICIALIZADOR DO PROJETO'
Write-Host '========================================'
Write-Host ''

# 1. Verificar Python3
if (-not (Get-Command python3 -ErrorAction SilentlyContinue)) {
    Stop-Script 'Python3 nao encontrado no PATH.'
}

# 2. Criar ambiente virtual, se necessario
if (-not (Test-Path 'venv\Scripts\python3.exe')) {
    Write-Host '[INFO] Criando ambiente virtual...'
    python3 -m venv venv
    if ($LASTEXITCODE -ne 0) { Stop-Script 'Falha ao criar venv.' }
}

# 3. Ativar ambiente virtual
try {
    . '.\venv\Scripts\Activate.ps1'
} catch {
    Stop-Script 'Falha ao ativar venv.'
}

# 4. Instalar dependencias
if (-not (Test-Path 'requisitos.txt')) { Stop-Script 'requisitos.txt nao encontrado.' }

Write-Host '[INFO] Instalando dependencias...'
python3 -m pip install -r requisitos.txt
if ($LASTEXITCODE -ne 0) { Stop-Script 'Falha ao instalar dependencias.' }

# 5. Ler configuracao do banco.txt
if (-not (Test-Path 'banco.txt')) { Stop-Script 'banco.txt nao encontrado.' }

$SqlServer = $null
$DbName    = $null

foreach ($linha in Get-Content 'banco.txt') {
    $partes = $linha -split '=', 2
    if ($partes.Count -lt 2) { continue }
    switch ($partes[0].Trim().ToLower()) {
        'server'   { $SqlServer = $partes[1].Trim() }
        'database' { $DbName    = $partes[1].Trim() }
    }
}

if (-not $SqlServer) { Stop-Script 'Chave server nao encontrada em banco.txt.' }
if (-not $DbName)    { Stop-Script 'Chave database nao encontrada em banco.txt.' }

# Ajuste para a instancia SQLEXPRESS caso o arquivo
# ainda esteja configurado para localhost.
if ($SqlServer -ieq 'localhost') { $SqlServer = '.\SQLEXPRESS' }

Write-Host ''
Write-Host "[INFO] Servidor: $SqlServer"
Write-Host "[INFO] Banco: $DbName"
Write-Host '[INFO] Verificando conexao...'

if (-not (Get-Command sqlcmd -ErrorAction SilentlyContinue)) {
    Stop-Script 'sqlcmd nao encontrado no PATH.'
}

# 6. Consultar existencia do banco conectando em master
$query = "SET NOCOUNT ON; SELECT CASE WHEN DB_ID(N'$DbName') IS NOT NULL THEN 1 ELSE 0 END;"
$saida = & sqlcmd -S $SqlServer -E -C -b -d master -h -1 -W -Q $query 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host ''
    Write-Host '[ERRO] Nao foi possivel conectar ao SQL Server.' -ForegroundColor Red
    $saida | Out-String | Write-Host
    Read-Host 'Pressione Enter para sair' | Out-Null
    exit 1
}

$dbExiste = ($saida | Out-String).Trim() -eq '1'

# 7. Criar banco (se nao existir) e garantir atualizacao/geracao de dados
if (-not $dbExiste) {
    Write-Host "[INFO] Banco inexistente. Criando banco..."
} else {
    Write-Host "[INFO] Banco $DbName ja existe. Verificando estrutura..."
}

if (-not (Test-Path 'site.sql')) { Stop-Script 'site.sql nao encontrado.' }

& sqlcmd -S $SqlServer -E -C -b -d master -i 'site.sql'
if ($LASTEXITCODE -ne 0) { Stop-Script 'Falha ao executar site.sql.' }

Write-Host '[INFO] Gerando / atualizando dados iniciais...'
python3 'generate_data.py'
if ($LASTEXITCODE -ne 0) { Stop-Script 'Falha ao executar o script de geracao de dados.' }

# 8. Iniciar aplicacao
if (-not (Test-Path 'run.py')) { Stop-Script 'run.py nao encontrado.' }

Write-Host ''
Write-Host '[INFO] Iniciando aplicacao...'
Write-Host '========================================'

if (Test-Path 'INTERFACE\loja_app.exe') {
    Start-Process -FilePath '.\INTERFACE\loja_app.exe'
} else {
    Write-Host '[AVISO] INTERFACE\loja_app.exe nao encontrado; iniciando apenas a API.' -ForegroundColor Yellow
}

python3 'run.py'
if ($LASTEXITCODE -ne 0) { Stop-Script 'A aplicacao foi encerrada com erro.' }