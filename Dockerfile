
# Imagen base liviana
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY app ./app

# Exponer puerto (configurable por env PORT, por defecto 3000)
ENV PORT=3000
EXPOSE 3000

# Comando de arranque
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
