#!/bin/bash

# Script para iniciar o projeto ReservasOnline

# Verifica se o Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "Docker não encontrado. Por favor, instale o Docker."
    exit 1
fi

# Verifica se o Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose não encontrado. Por favor, instale o Docker Compose."
    exit 1
fi

# Funções
function print_header() {
    echo "====================================================="
    echo "$1"
    echo "====================================================="
}

function check_env_file() {
    if [ ! -f ".env" ]; then
        echo "Arquivo .env não encontrado. Criando a partir do exemplo..."
        if [ -f ".env.example" ]; then
            cp .env.example .env
            echo "Arquivo .env criado. Por favor, edite-o com suas configurações."
        else
            echo "Arquivo .env.example não encontrado. Por favor, crie manualmente o arquivo .env."
            exit 1
        fi
    fi
}

# Verificar e criar o arquivo .env
check_env_file

# Iniciar os contêineres
print_header "Iniciando os contêineres Docker"
docker-compose up -d

# Verificar se os contêineres iniciaram corretamente
if [ $? -ne 0 ]; then
    echo "Erro ao iniciar os contêineres. Verifique o log para mais detalhes."
    exit 1
fi

# Esperar o banco de dados iniciar
print_header "Aguardando o banco de dados iniciar..."
sleep 10

# Executar migrações
print_header "Executando migrações"
docker-compose exec web python manage.py migrate

# Verificar e criar o administrador inicial
print_header "Inicializando o administrador"
docker-compose exec web python manage.py init_admin

# Criar diretório static se não existir
print_header "Configurando arquivos estáticos"
docker-compose exec web mkdir -p /app/staticfiles

# Coletar arquivos estáticos
docker-compose exec web python manage.py collectstatic --noinput

# Configurar dados iniciais (opcional)
read -p "Deseja inicializar o banco de dados com dados de exemplo? (s/n): " init_db
if [[ $init_db == "s" ]]; then
    print_header "Inicializando banco de dados com dados de exemplo"
    docker-compose exec web python manage.py init_db --full
fi

# Mostrar informações
print_header "Sistema ReservasOnline iniciado com sucesso!"
echo ""
echo "URLs de acesso:"
echo "- API: http://localhost:8000/api/v1/"
echo "- Admin: http://localhost:8000/admin/"
echo ""
echo "Para visualizar os logs do serviço web:"
echo "docker-compose logs -f web"
echo ""
echo "Para visualizar os logs do Celery:"
echo "docker-compose logs -f celery_worker"
echo ""
echo "Para parar o sistema:"
echo "docker-compose down"
echo "" 