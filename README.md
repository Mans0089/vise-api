
# VISE API (FastAPI - versión simple)

API mínima para registrar clientes y procesar compras con reglas de **restricciones** y **beneficios** por tipo de tarjeta.

## Ejecutar en local

```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
export PORT=3000  # En Windows: set PORT=3000
uvicorn app.main:app --reload --port ${PORT}
```

Abrir: http://127.0.0.1:${PORT}/docs

## Docker

```bash
docker build -t vise-api:latest .
docker run -d -p 3000:3000 --name vise-api -e PORT=3000 vise-api:latest
```

## Rutas

- `GET /health`
- `POST /client` → registra cliente si cumple restricciones
- `POST /purchase` → procesa compra y aplica el **mayor** descuento aplicable (regla simple)

> Nota: almacenamiento **en memoria** (se pierde al reiniciar). Suficiente para pruebas de la actividad.

## Supuestos de negocio

- Para compras con múltiples beneficios posibles, se aplica **el mayor porcentaje** (no acumulamos).
- Para tarjetas **Black** y **White**:
  - No se registra cliente cuya **residencia** esté en: China, Vietnam, India, Irán.
  - Además, se **rechaza la compra** si el `purchaseCountry` es uno de esos países (para alinear con el ejemplo de la consigna).
- Descuento por **exterior**: si `purchaseCountry != country` del cliente (comparación case-insensitive).

## Pruebas con Hurl

Usa el archivo `tests/session.hurl` o en el root `session.hurl` y corre:

```bash
hurl --variable host=http://localhost:3000 --error-format long --test session.hurl
```
