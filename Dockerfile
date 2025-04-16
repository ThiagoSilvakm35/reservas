FROM python:3.11-slim

WORKDIR /app

# Instalar dependências de sistema
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro para aproveitar o cache do Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante do projeto
COPY . .

# Porta exposta pelo servidor
EXPOSE 8000

# Comando para executar o serviço
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "ReservasOnline.wsgi:application"] 