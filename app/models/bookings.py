from sqlalchemy import Column, String, ForeignKey, CheckConstraint, DateTime
from sqlalchemy.dialects.postgresql import UUID, NUMERIC
from app.db.base import Base
from datetime import datetime
import uuid

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    event_id = Column(UUID, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    total_amount = Column(NUMERIC(10, 2), nullable=False)
    status = Column(String, default='CONFIRMED')
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    __table_args__ = (
        CheckConstraint("status IN ('PENDING', 'CONFIRMED', 'CANCELLED')", name='check_booking_status'),
    )
