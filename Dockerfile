# Dockerfile
FROM python:3.11-slim

# Evitar buffers em logs
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# instalar dependências (primeiro copia requirements para cache de build)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# copiar o código
COPY . .

# porta exposta
EXPOSE 3000

# comando padrão: uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "3000"]
