# backend/Dockerfile

FROM python:3.11-slim

# Define diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && \
    apt-get install -y build-essential curl && \
    apt-get clean

# Copia arquivos de dependências e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

# Comando padrão (pode ser sobrescrito pelo docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
