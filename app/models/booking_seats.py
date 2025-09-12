from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import uuid

class BookingSeat(Base):
    __tablename__ = "booking_seats"

    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    booking_id = Column(UUID, ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False)
    event_seat_id = Column(UUID, ForeignKey("event_seats.id", ondelete="CASCADE"), nullable=False)
    
    __table_args__ = (
        UniqueConstraint('booking_id', 'event_seat_id', name='unique_booking_seat'),
    )
