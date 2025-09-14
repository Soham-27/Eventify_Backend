from pydantic import BaseModel
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

class PaymentBase(BaseModel):
    booking_id: uuid.UUID
    user_id: uuid.UUID
    amount: Decimal
    status: str = "PENDING"
    transaction_ref: Optional[str] = None

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(BaseModel):
    status: Optional[str] = None
    transaction_ref: Optional[str] = None

class PaymentOut(BaseModel):
    id: uuid.UUID
    booking_id: uuid.UUID
    user_id: uuid.UUID
    amount: Decimal
    status: str
    transaction_ref: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = {
        "arbitrary_types_allowed": True
    }

class PaymentStatusUpdate(BaseModel):
    status: str
    transaction_ref: Optional[str] = None