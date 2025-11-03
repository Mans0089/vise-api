# Imagen base liviana
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY app ./app

# Exponer puerto 80 (Azure usará este)
ENV PORT=80
EXPOSE 80

# Usar gunicorn con el worker de uvicorn (mejor para producción)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]