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

class BookingOut(BaseModel):
    id: uuid.UUID
    event_id:uuid.UUID
    event_name:str
    venue_name:str
    start_time:datetime
    end_time:datetime
    seats:List[str]
    total_amount:Decimal
    created_at:datetime
    model_config = {
        "arbitrary_types_allowed": True
    }

class SeatBookingRequest(BaseModel):
    event_id: uuid.UUID
    seat_ids: List[uuid.UUID]

class CancelBookingRequest(BaseModel):
    booking_id: uuid.UUID

