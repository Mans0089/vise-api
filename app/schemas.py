
from pydantic import BaseModel, Field
from typing import Optional, Literal

CardType = Literal["Classic", "Gold", "Platinum", "Black", "White"]

class ClientIn(BaseModel):
    name: str
    country: str
    monthlyIncome: float = Field(ge=0)
    viseClub: bool
    cardType: CardType

class ClientOut(BaseModel):
    clientId: int
    name: str
    cardType: CardType
    status: Literal["Registered"]
    message: str

class ErrorOut(BaseModel):
    status: Literal["Rejected"]
    error: str

class PurchaseIn(BaseModel):
    clientId: int
    amount: float = Field(gt=0)
    currency: str
    purchaseDate: str  # ISO 8601 string
    purchaseCountry: str

class PurchaseDetail(BaseModel):
    clientId: int
    originalAmount: float
    discountApplied: float
    finalAmount: float
    benefit: str

class PurchaseApproved(BaseModel):
    status: Literal["Approved"]
    purchase: PurchaseDetail

class PurchaseRejected(BaseModel):
    status: Literal["Rejected"]
    error: str
