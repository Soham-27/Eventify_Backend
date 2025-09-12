from pydantic import BaseModel
import uuid
from datetime import datetime
from typing import Optional

class SeatBase(BaseModel):
    venue_id: uuid.UUID
    label: str
    row_no: str
    seat_no: int

class SeatCreate(SeatBase):
    pass

class SeatUpdate(BaseModel):
    label: Optional[str] = None
    row_no: Optional[str] = None
    seat_no: Optional[int] = None

class SeatOut(SeatBase):
    id: uuid.UUID
    created_at: datetime

    model_config = {
        "arbitrary_types_allowed": True
    }
