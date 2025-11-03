# Imagen base liviana
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY app ./app

# Exponer puerto 80 (Azure usará este)
ENV PORT=8000
EXPOSE 8000

# Gunicorn con Uvicorn
CMD ["gunicorn", "app.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:${PORT}", "--timeout", "600"]