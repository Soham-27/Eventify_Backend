from sqlalchemy import Column, Integer, String, DateTime
from app.db.base import Base
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

class Venue(Base):
    __tablename__ = "venues"

    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    address = Column(String, nullable=True)
    total_rows = Column(Integer, nullable=False)
    seats_per_row = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
