from sqlalchemy import Column, String, ForeignKey
from app.db.base import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
import uuid

class Event(Base):
    __tablename__ = "events"

    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    venue_id = Column(UUID, ForeignKey("venues.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    default_price = Column(Integer, nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    created_by = Column(UUID, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
