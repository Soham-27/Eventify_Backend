from sqlalchemy import Column, String, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, NUMERIC
from app.db.base import Base
import uuid

class EventSeat(Base):
    __tablename__ = "event_seats"

    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    event_id = Column(UUID, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    seat_id = Column(UUID, ForeignKey("seats.id", ondelete="CASCADE"), nullable=False)
    price = Column(NUMERIC(10, 2), nullable=False)
    status = Column(String, default='AVAILABLE')
    
    __table_args__ = (
        UniqueConstraint('event_id', 'seat_id', name='unique_event_seat'),
        CheckConstraint("status IN ('AVAILABLE', 'BOOKED', 'LOCKED')", name='check_seat_status'),
    )
