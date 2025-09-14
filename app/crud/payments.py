from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from app.models.payments import Payment
from app.schemas.payments import PaymentCreate, PaymentUpdate
import uuid

async def create_payment(db: AsyncSession, payment: PaymentCreate):
    """Create payment in database"""
    try:
        db_payment = Payment(
            id=uuid.uuid4(),
            booking_id=payment.booking_id,
            user_id=payment.user_id,
            amount=payment.amount,
            status=payment.status,
            transaction_ref=payment.transaction_ref
        )
        db.add(db_payment)
        await db.commit()
        await db.refresh(db_payment)
        return db_payment
    except SQLAlchemyError as e:
        await db.rollback()
        raise Exception(f"Error creating payment: {str(e)}")

async def get_payment_by_id(db: AsyncSession, payment_id: str):
    """Get payment by ID from database"""
    try:
        result = await db.execute(select(Payment).where(Payment.id == payment_id))
        return result.scalars().first()
    except SQLAlchemyError as e:
        raise Exception(f"Error fetching payment: {str(e)}")

async def get_payments_by_booking(db: AsyncSession, booking_id: str):
    """Get payments by booking ID from database"""
    try:
        result = await db.execute(select(Payment).where(Payment.booking_id == booking_id))
        return result.scalars().all()
    except SQLAlchemyError as e:
        raise Exception(f"Error fetching booking payments: {str(e)}")

async def get_payments_by_user(db: AsyncSession, user_id: str):
    """Get payments by user ID from database"""
    try:
        result = await db.execute(select(Payment).where(Payment.user_id == user_id))
        return result.scalars().all()
    except SQLAlchemyError as e:
        raise Exception(f"Error fetching user payments: {str(e)}")

async def update_payment(db: AsyncSession, payment_id: str, payment_update: PaymentUpdate):
    """Update payment in database"""
    try:
        result = await db.execute(select(Payment).where(Payment.id == payment_id))
        db_payment = result.scalars().first()
        if not db_payment:
            return None
        
        for var, value in vars(payment_update).items():
            if value is not None:
                setattr(db_payment, var, value)
        
        db_payment.updated_at = datetime.utcnow()
        db.add(db_payment)
        await db.commit()
        await db.refresh(db_payment)
        return db_payment
    except SQLAlchemyError as e:
        await db.rollback()
        raise Exception(f"Error updating payment: {str(e)}")

async def delete_payment(db: AsyncSession, payment_id: str):
    """Delete payment from database"""
    try:
        result = await db.execute(select(Payment).where(Payment.id == payment_id))
        db_payment = result.scalars().first()
        if not db_payment:
            return None
        
        await db.delete(db_payment)
        await db.commit()
        return True
    except SQLAlchemyError as e:
        await db.rollback()
        raise Exception(f"Error deleting payment: {str(e)}")

