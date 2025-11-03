# Imagen base liviana
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY app ./app

# Puerto por defecto (Azure lo sobrescribirá)
ENV PORT=8000
EXPOSE 8000

# Ejecutar Gunicorn con FastAPI en el puerto dinámico de Azure
CMD ["bash", "-c", "gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT} --timeout 600"]
