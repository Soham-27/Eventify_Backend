from pydantic import BaseModel, Field
import uuid
from datetime import datetime
from typing import Optional
from decimal import Decimal

class EventBase(BaseModel):
    venue_id: uuid.UUID
    title: str
    description: Optional[str] = None
    default_price: Decimal
    start_time: datetime
    end_time: datetime

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    venue_id: Optional[uuid.UUID] = None
    title: Optional[str] = None
    description: Optional[str] = None
    default_price: Optional[Decimal] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
class EventOut(EventBase):
    id: uuid.UUID
    venue_id: uuid.UUID
    title: str
    description: Optional[str] = None
    default_price: Decimal
    start_time: datetime
    end_time: datetime
    created_by: uuid.UUID
    created_at: datetime

    model_config = {
        "arbitrary_types_allowed": True
    }