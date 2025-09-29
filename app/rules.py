
from datetime import datetime
from typing import Tuple

FORBIDDEN_COUNTRIES = {c.lower(): c for c in ["China","Vietnam","India","Irán","Iran"]}

def _weekday_name(d: datetime) -> str:
    names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    return names[d.weekday()]

def check_registration_restrictions(card_type: str, monthly_income: float, vise_club: bool, country: str) -> Tuple[bool, str]:
    ctype = card_type
    ctry = (country or "").strip().lower()

    if ctype == "Classic":
        return True, "Cliente apto para tarjeta Classic"

    if ctype == "Gold":
        if monthly_income < 500:
            return False, "El cliente no cumple con el ingreso mínimo de 500 USD requerido para Gold"
        return True, "Cliente apto para tarjeta Gold"

    if ctype == "Platinum":
        if monthly_income < 1000:
            return False, "El cliente no cumple con el ingreso mínimo de 1000 USD requerido para Platinum"
        if not vise_club:
            return False, "El cliente no cumple con la suscripción VISE CLUB requerida para Platinum"
        return True, "Cliente apto para tarjeta Platinum"

    if ctype == "Black" or ctype == "White":
        if monthly_income < 2000:
            return False, f"El cliente no cumple con el ingreso mínimo de 2000 USD requerido para {ctype}"
        if not vise_club:
            return False, f"El cliente no cumple con la suscripción VISE CLUB requerida para {ctype}"
        # Restricción por país de residencia
        if ctry in FORBIDDEN_COUNTRIES:
            full = FORBIDDEN_COUNTRIES[ctry]
            return False, f"No se permite registrar clientes que residan en {full} para {ctype}"
        return True, f"Cliente apto para tarjeta {ctype}"

    return False, "Tipo de tarjeta inválido"

def check_purchase_restrictions(client: dict, purchase_country: str) -> Tuple[bool, str]:
    ctype = client["cardType"]
    # Adicionalmente, para Black/White rechazamos compras realizadas DESDE países restringidos.
    pc = (purchase_country or "").strip().lower()
    if ctype in ("Black", "White") and pc in FORBIDDEN_COUNTRIES:
        full = FORBIDDEN_COUNTRIES[pc]
        return False, f"El cliente con tarjeta {ctype} no puede realizar compras desde {full}"
    return True, ""

def compute_benefit(client: dict, amount: float, purchase_dt: datetime, purchase_country: str) -> Tuple[float, str]:
    """Devuelve (porcentaje_en_decimal, descripción). Regla simple: aplica el MAYOR descuento aplicable."""
    ctype = client["cardType"]
    weekday = purchase_dt.weekday()  # 0=Mon ... 6=Sun
    dayname = _weekday_name(purchase_dt)
    is_weekend = weekday >= 5
    is_weekday = weekday <= 4
    exterior = (purchase_country or "").strip().lower() != (client["country"] or "").strip().lower()

    candidates = []

    if ctype == "Classic":
        return 0.0, "Sin beneficio"

    if ctype == "Gold":
        if weekday in (0,1,2) and amount > 100:
            candidates.append((0.15, f"{dayname} - Descuento 15%"))

    if ctype == "Platinum":
        if weekday in (0,1,2) and amount > 100:
            candidates.append((0.20, f"{dayname} - Descuento 20%"))
        if weekday == 5 and amount > 200:
            candidates.append((0.30, "Sábado - Descuento 30%"))
        if exterior:
            candidates.append((0.05, "Exterior - Descuento 5%"))

    if ctype == "Black":
        if weekday in (0,1,2) and amount > 100:
            candidates.append((0.25, f"{dayname} - Descuento 25%"))
        if weekday == 5 and amount > 200:
            candidates.append((0.35, "Sábado - Descuento 35%"))
        if exterior:
            candidates.append((0.05, "Exterior - Descuento 5%"))

    if ctype == "White":
        if is_weekday and amount > 100:
            candidates.append((0.25, f"{dayname} - Descuento 25%"))
        if is_weekend and amount > 200:
            # Sábado o Domingo
            label = "Sábado/Domingo - Descuento 35%"
            if weekday == 5:
                label = "Sábado - Descuento 35%"
            elif weekday == 6:
                label = "Domingo - Descuento 35%"
            candidates.append((0.35, label))
        if exterior:
            candidates.append((0.05, "Exterior - Descuento 5%"))

    if not candidates:
        return 0.0, "Sin beneficio"
    best = max(candidates, key=lambda x: x[0])
    return best
