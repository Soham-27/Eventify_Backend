"""Payment API endpoints

This module handles payment-specific operations:
- Process payments for existing bookings
- Check payment/booking status
- Admin cleanup operations

For booking operations (create/cancel), use /bookings endpoints instead.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.deps import get_db
from app.processor.payment_processor import PaymentProcessor
from app.schemas.payments import PaymentStatusUpdate
from app.middleware.authenticated import get_current_user
from typing import Dict, Any
import uuid

router = APIRouter()

# @router.post("/initiate-booking")
# async def initiate_booking_with_payment(
#     event_id: str,
#     seat_ids: list[str],
#     db: AsyncSession = Depends(get_db),
#     current_user: dict = Depends(get_current_user)
# ):
#     """Initiate booking process with seat locks - DUPLICATE: Use /bookings/book instead"""
#     try:
#         result = await PaymentProcessor.initiate_booking_with_payment(
#             db, event_id, current_user["id"], seat_ids
#         )
#         
#         if not result["success"]:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=result["error"]
#             )
#         
#         return result
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=str(e)
#         )

@router.post("/process/{booking_id}")
async def process_payment(
    booking_id: str,
    payment_data: Dict[str, Any] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Process payment for a booking"""
    try:
        # Validate booking_id format
        try:
            uuid.UUID(booking_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid booking ID format"
            )
        
        result = await PaymentProcessor.process_payment(db, booking_id, payment_data)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# @router.post("/cancel/{booking_id}")
# async def cancel_booking(
#     booking_id: str,
#     db: AsyncSession = Depends(get_db),
#     current_user: dict = Depends(get_current_user)
# ):
#     """Cancel a pending booking - DUPLICATE: Use /bookings/cancel instead"""
#     try:
#         # Validate booking_id format
#         try:
#             uuid.UUID(booking_id)
#         except ValueError:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Invalid booking ID format"
#             )
#         
#         result = await PaymentProcessor.cancel_booking(db, booking_id)
#         
#         if not result["success"]:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=result["error"]
#             )
#         
#         return result
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=str(e)
#         )

@router.get("/status/{booking_id}")
async def get_booking_status(
    booking_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get booking and payment status"""
    try:
        # Validate booking_id format
        try:
            uuid.UUID(booking_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid booking ID format"
            )
        
        result = await PaymentProcessor.get_booking_status(db, booking_id)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["error"]
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/cleanup-expired")
async def cleanup_expired_bookings(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Clean up expired bookings (admin only)"""
    try:
        # Check if user is admin
        if current_user.get("role") != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        result = await PaymentProcessor.cleanup_expired_bookings(db)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/health")
async def payment_health_check():
    """Health check for payment service"""
    return {
        "status": "healthy",
        "service": "payment",
        "message": "Payment service is running"
    }
