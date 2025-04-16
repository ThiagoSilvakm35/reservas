# Script para iniciar o projeto ReservasOnline no Windows

# Funções
function Write-Header {
    param ([string]$Title)
    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host $Title -ForegroundColor Cyan
    Write-Host "=====================================================" -ForegroundColor Cyan
}

function Check-EnvFile {
    if (-not (Test-Path ".env")) {
        Write-Host "Arquivo .env não encontrado. Criando a partir do exemplo..." -ForegroundColor Yellow
        if (Test-Path ".env.example") {
            Copy-Item ".env.example" ".env"
            Write-Host "Arquivo .env criado. Por favor, edite-o com suas configurações." -ForegroundColor Green
        }
        else {
            Write-Host "Arquivo .env.example não encontrado. Por favor, crie manualmente o arquivo .env." -ForegroundColor Red
            exit 1
        }
    }
}

# Verificar se o Docker está instalado
try {
    $null = Get-Command docker -ErrorAction Stop
}
catch {
    Write-Host "Docker não encontrado. Por favor, instale o Docker Desktop para Windows." -ForegroundColor Red
    exit 1
}

# Verificar se o Docker Compose está disponível
try {
    $null = docker compose version
    $composeCmd = "docker compose"
}
catch {
    try {
        $null = docker-compose --version
        $composeCmd = "docker-compose"
    }
    catch {
        Write-Host "Docker Compose não encontrado. Por favor, instale o Docker Compose." -ForegroundColor Red
        exit 1
    }
}

# Verificar e criar o arquivo .env
Check-EnvFile

# Iniciar os contêineres
Write-Header "Iniciando os contêineres Docker"
Invoke-Expression "$composeCmd up -d"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Erro ao iniciar os contêineres. Verifique o log para mais detalhes." -ForegroundColor Red
    exit 1
}

# Esperar o banco de dados iniciar
Write-Header "Aguardando o banco de dados iniciar..."
Start-Sleep -Seconds 10

# Executar migrações
Write-Header "Executando migrações"
Invoke-Expression "$composeCmd exec web python manage.py migrate"

# Verificar e criar o administrador inicial
Write-Header "Inicializando o administrador"
Invoke-Expression "$composeCmd exec web python manage.py init_admin"

# Criar diretório static se não existir
Write-Header "Configurando arquivos estáticos"
Invoke-Expression "$composeCmd exec web mkdir -p /app/staticfiles"

# Coletar arquivos estáticos
Invoke-Expression "$composeCmd exec web python manage.py collectstatic --noinput"

# Configurar dados iniciais (opcional)
$initDb = Read-Host "Deseja inicializar o banco de dados com dados de exemplo? (s/n)"
if ($initDb -eq "s") {
    Write-Header "Inicializando banco de dados com dados de exemplo"
    Invoke-Expression "$composeCmd exec web python manage.py init_db --full"
}

# Mostrar informações
Write-Header "Sistema ReservasOnline iniciado com sucesso!"
Write-Host ""
Write-Host "URLs de acesso:" -ForegroundColor Green
Write-Host "- API: http://localhost:8000/api/v1/" -ForegroundColor Green
Write-Host "- Admin: http://localhost:8000/admin/" -ForegroundColor Green
Write-Host ""
Write-Host "Para visualizar os logs do serviço web:" -ForegroundColor Yellow
Write-Host "$composeCmd logs -f web" -ForegroundColor Yellow
Write-Host ""
Write-Host "Para visualizar os logs do Celery:" -ForegroundColor Yellow
Write-Host "$composeCmd logs -f celery_worker" -ForegroundColor Yellow
Write-Host ""
Write-Host "Para parar o sistema:" -ForegroundColor Yellow
Write-Host "$composeCmd down" -ForegroundColor Yellow
Write-Host "" 