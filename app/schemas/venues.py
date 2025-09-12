from pydantic import BaseModel, Field
import uuid
from datetime import datetime
from typing import Optional

class VenueBase(BaseModel):
    name: str
    address: Optional[str] = None
    total_rows: int
    seats_per_row: int

class VenueCreate(VenueBase):
    pass

class VenueUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    total_rows: Optional[int] = None
    seats_per_row: Optional[int] = None

class VenueOut(VenueBase):
    id: uuid.UUID
    name:str
    address:Optional[str] = None
    total_rows:int
    seats_per_row:int
    created_at:datetime

    model_config = {
        "arbitrary_types_allowed": True
    }
