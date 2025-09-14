from sqlalchemy import Column, String, ForeignKey, CheckConstraint, DateTime
from sqlalchemy.dialects.postgresql import UUID, NUMERIC
from app.db.base import Base
from datetime import datetime
import uuid

class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    booking_id = Column(UUID, ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount = Column(NUMERIC(10, 2), nullable=False)
    status = Column(String(20), nullable=False)
    transaction_ref = Column(String(100), nullable=True)  # mock transaction id
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        CheckConstraint("status IN ('PENDING', 'SUCCESS', 'FAILED')", name='check_payment_status'),
    )