from pydantic import BaseModel
import uuid
from decimal import Decimal
from typing import Optional

class EventSeatBase(BaseModel):
    event_id: uuid.UUID
    seat_id: uuid.UUID
    price: Decimal
    status: str = "AVAILABLE"

class EventSeatCreate(EventSeatBase):
    pass

class EventSeatUpdate(BaseModel):
    price: Optional[Decimal] = None
    status: Optional[str] = None

class EventSeatOut(EventSeatBase):
    id: uuid.UUID

    model_config = {
        "arbitrary_types_allowed": True
    }

class EventSeatWithSeatOut(EventSeatOut):
    label: str
    row_no: str
    seat_no: int

class RowPriceUpdate(BaseModel):
    row_no: str
    new_price: Decimal

class RowPriceUpdateResponse(BaseModel):
    message: str
    row: str
    new_price: Decimal
    updated_count: int
