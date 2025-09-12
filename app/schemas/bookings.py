from pydantic import BaseModel
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, List

class BookingBase(BaseModel):
    event_id: uuid.UUID
    user_id: uuid.UUID
    total_amount: Decimal
    status: str = "CONFIRMED"

class BookingCreate(BookingBase):
    pass

class BookingUpdate(BaseModel):
    status: Optional[str] = None

class BookingOut(BookingBase):
    id: uuid.UUID
    created_at: datetime

    model_config = {
        "arbitrary_types_allowed": True
    }

class SeatBookingRequest(BaseModel):
    event_id: uuid.UUID
    seat_ids: List[uuid.UUID]

class CancelBookingRequest(BaseModel):
    booking_id: uuid.UUID

