from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime

from app.schemas import ClientIn, ErrorOut, PurchaseIn, PurchaseRejected
from app.store import store
from app.rules import check_registration_restrictions, check_purchase_restrictions, compute_benefit

# --- Añadidos para OpenTelemetry ---
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware
import exporter  # importamos el exporter configurado antes

app = FastAPI(title="VISE API", version="0.1.0")

# Instrumentar automáticamente FastAPI (trazas + métricas)
FastAPIInstrumentor.instrument_app(app)
app.add_middleware(OpenTelemetryMiddleware)

# Puedes usar el tracer o el meter de tu exporter
tracer = exporter.service_tracer
meter = exporter.service_meter

# Ejemplo de métrica personalizada
request_counter = meter.create_counter(
    name="viseapi_requests_total",
    description="Número total de solicitudes procesadas",
)

@app.middleware("http")
async def add_metrics(request, call_next):
    response = await call_next(request)
    request_counter.add(1, {"path": request.url.path, "method": request.method})
    return response

# ---- ENDPOINTS ----

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/client", responses={400: {"model": ErrorOut}}, response_model_exclude_none=True)
def register_client(payload: ClientIn):
    with tracer.start_as_current_span("register_client"):
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

@app.post("/purchase", responses={400: {"model": PurchaseRejected}}, response_model_exclude_none=True)
def purchase(payload: PurchaseIn):
    with tracer.start_as_current_span("purchase"):
        client = store.get_client(payload.clientId)
        if not client:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        ok, err = check_purchase_restrictions(client, payload.purchaseCountry)
        if not ok:
            return JSONResponse(status_code=400, content={"status": "Rejected", "error": err})

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
