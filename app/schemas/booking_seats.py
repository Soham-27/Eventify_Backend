from pydantic import BaseModel
import uuid

class BookingSeatBase(BaseModel):
    booking_id: uuid.UUID
    event_seat_id: uuid.UUID

class BookingSeatCreate(BookingSeatBase):
    pass

class BookingSeatOut(BookingSeatBase):
    id: uuid.UUID

    model_config = {
        "arbitrary_types_allowed": True
    }
