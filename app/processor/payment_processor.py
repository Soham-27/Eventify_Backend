"""Payment processor for handling payment operations"""

from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.service.payment_service import PaymentService
from app.schemas.payments import PaymentCreate, PaymentStatusUpdate
from app.core.redis import redis
import asyncio
import uuid

class PaymentProcessor:
    """Processor class for payment operations"""
    
    @staticmethod
    async def initiate_booking_with_payment(db: AsyncSession, event_id: str, user_id: str, seat_ids: list[str]) -> dict:
        """Initiate booking process with seat locks"""
        try:
            # Create pending booking with locks
            result = await PaymentService.create_pending_booking_with_locks(
                db, event_id, user_id, seat_ids
            )
            
            # Schedule auto-cleanup after 3 minutes
            asyncio.create_task(
                PaymentProcessor._schedule_cleanup(db, result["booking_id"], 180)
            )
            
            return {
                "success": True,
                "booking_id": result["booking_id"],
                "total_amount": result["total_amount"],
                "status": "PENDING",
                "message": "Booking created. Please complete payment within 3 minutes.",
                "payment_url": f"/payments/process/{result['booking_id']}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    async def process_payment(db: AsyncSession, booking_id: str, payment_data: dict = None) -> dict:
        """Process payment for a booking"""
        try:
            # Mock payment processing - in real app, integrate with payment gateway
            payment_success = await PaymentProcessor._mock_payment_gateway(payment_data)
            
            if payment_success:
                # Confirm payment and booking
                result = await PaymentService.confirm_payment_and_booking(
                    db, booking_id, payment_data.get("transaction_ref") if payment_data else None
                )
                return {
                    "success": True,
                    "booking_id": result["booking_id"],
                    "payment_id": result["payment_id"],
                    "status": "CONFIRMED",
                    "transaction_ref": result["transaction_ref"],
                    "message": "Payment successful and booking confirmed"
                }
            else:
                # Fail payment and cancel booking
                result = await PaymentService.fail_payment_and_cancel_booking(
                    db, booking_id, payment_data.get("transaction_ref") if payment_data else None
                )
                return {
                    "success": False,
                    "booking_id": result["booking_id"],
                    "payment_id": result["payment_id"],
                    "status": "CANCELLED",
                    "transaction_ref": result["transaction_ref"],
                    "message": "Payment failed and booking cancelled"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    async def cancel_booking(db: AsyncSession, booking_id: str) -> dict:
        """Cancel a pending booking"""
        try:
            result = await PaymentService.fail_payment_and_cancel_booking(
                db, booking_id, "USER_CANCELLED"
            )
            return {
                "success": True,
                "booking_id": result["booking_id"],
                "status": "CANCELLED",
                "message": "Booking cancelled successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    async def get_booking_status(db: AsyncSession, booking_id: str) -> dict:
        """Get booking and payment status"""
        try:
            result = await PaymentService.get_booking_status(db, booking_id)
            if not result:
                return {
                    "success": False,
                    "error": "Booking not found"
                }
            
            return {
                "success": True,
                "booking": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    async def _mock_payment_gateway(payment_data: dict = None) -> bool:
        """Mock payment gateway - returns True for successful payments"""
        # Simulate payment processing delay
        await asyncio.sleep(1)
        
        # Mock logic - 90% success rate
        import random
        return random.random() < 0.9

    @staticmethod
    async def _schedule_cleanup(db: AsyncSession, booking_id: str, delay_seconds: int):
        """Schedule cleanup for expired booking"""
        await asyncio.sleep(delay_seconds)
        
        try:
            # Check if booking is still pending
            result = await PaymentService.get_booking_status(db, booking_id)
            if result and result["status"] == "PENDING":
                # Auto-cancel expired booking
                await PaymentService.fail_payment_and_cancel_booking(
                    db, booking_id, "AUTO_EXPIRED"
                )
                print(f"Auto-cancelled expired booking: {booking_id}")
        except Exception as e:
            print(f"Error in scheduled cleanup for booking {booking_id}: {e}")

    @staticmethod
    async def cleanup_expired_bookings(db: AsyncSession) -> dict:
        """Clean up all expired bookings"""
        try:
            result = await PaymentService.cleanup_expired_locks(db)
            return {
                "success": True,
                "expired_bookings": result["expired_bookings"],
                "message": f"Cleaned up {result['expired_bookings']} expired bookings"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
