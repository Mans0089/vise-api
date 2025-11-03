import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from datetime import datetime

from app.schemas import ClientIn, ErrorOut, PurchaseIn, PurchaseRejected
from app.store import store
from app.rules import check_registration_restrictions, check_purchase_restrictions, compute_benefit

from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from app.telemetry import configure_app
from app.otel_setup import setup_tracer

# 🔹 Configura el tracer (con el nombre del servicio)
tracer = setup_tracer("vise-api")

# 🔹 Inicializa FastAPI e instrumenta OpenTelemetry
app = FastAPI(title="VISE API", version="0.1.0")

FastAPIInstrumentor.instrument_app(app)
RequestsInstrumentor().instrument()

# 🔹 Middleware para crear spans manuales por cada request
@app.middleware("http")
async def add_tracing(request: Request, call_next):
    with tracer.start_as_current_span(f"{request.method} {request.url.path}") as span:
        span.set_attribute("http.method", request.method)
        span.set_attribute("http.url", str(request.url))

        response = await call_next(request)
        span.set_attribute("http.status_code", response.status_code)
        return response
    
configure_app(app)


# 🔹 Endpoint de health check
@app.get("/health")
def health():
    return {"status": "ok"}


# 🔹 Endpoint para registrar un cliente
@app.post("/client", responses={400: {"model": ErrorOut}}, response_model_exclude_none=True)
def register_client(payload: ClientIn):
    ok, msg = check_registration_restrictions(payload.cardType, payload.monthlyIncome, payload.viseClub, payload.country)
    if not ok:
        return JSONResponse(status_code=400, content={"status": "Rejected", "error": msg})

    client_id = store.add_client(payload.model_dump())
    out = {
        "clientId": client_id,
        "name": payload.name,
        "cardType": payload.cardType,
        "status": "Registered",
        "message": f"Cliente apto para tarjeta {payload.cardType}"
    }
    return out


# 🔹 Endpoint para compras
@app.post("/purchase", responses={400: {"model": PurchaseRejected}}, response_model_exclude_none=True)
def purchase(payload: PurchaseIn):
    client = store.get_client(payload.clientId)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    # Restricciones de compra
    ok, err = check_purchase_restrictions(client, payload.purchaseCountry)
    if not ok:
        return JSONResponse(status_code=400, content={"status": "Rejected", "error": err})

    # Parse de fecha
    try:
        dt = datetime.fromisoformat(payload.purchaseDate.replace("Z", "+00:00"))
    except Exception:
        raise HTTPException(status_code=400, detail="purchaseDate inválido (usar ISO 8601)")

    pct, label = compute_benefit(client, payload.amount, dt, payload.purchaseCountry)
    discount = round(payload.amount * pct, 2)
    final = round(payload.amount - discount, 2)

    return {
        "status": "Approved",
        "purchase": {
            "clientId": payload.clientId,
            "originalAmount": payload.amount,
            "discountApplied": discount,
            "finalAmount": final,
            "benefit": label
        }
    }
