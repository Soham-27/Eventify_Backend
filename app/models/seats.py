from sqlalchemy import Column, String, Integer, ForeignKey, UniqueConstraint, DateTime
from app.db.base import Base
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

class Seat(Base):
    __tablename__ = "seats"

    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    venue_id = Column(UUID, ForeignKey("venues.id", ondelete="CASCADE"), nullable=False)
    label = Column(String, nullable=False)  # e.g. A1, B2
    row_no = Column(String, nullable=False)  # e.g. A, B, C
    seat_no = Column(Integer, nullable=False)  # e.g. 1, 2, 3
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('venue_id', 'label', name='unique_venue_seat_label'),
    )
