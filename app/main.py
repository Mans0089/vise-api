
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
from app.schemas import ClientIn, ClientOut, ErrorOut, PurchaseIn, PurchaseApproved, PurchaseRejected
from app.store import store
from app.rules import check_registration_restrictions, check_purchase_restrictions, compute_benefit

app = FastAPI(title="VISE API", version="0.1.0")

@app.get("/health")
def health():
    return {"status": "ok"}

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
#Cambio