"""Analytics CRUD functions for admin dashboard
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, desc
from app.models.bookings import Booking
from app.models.events import Event
from app.models.venues import Venue
from app.models.seats import Seat
from app.models.booking_seats import BookingSeat
from app.models.event_seats import EventSeat
from app.schemas.analytics import AdminAnalytics, PopularEvent, CapacityUtilization
from typing import List


async def get_total_confirmed_bookings(db: AsyncSession) -> int:
    """Get total number of confirmed bookings"""
    try:
        result = await db.execute(
            select(func.count(Booking.id)).where(Booking.status == 'CONFIRMED')
        )
        return result.scalar() or 0
    except SQLAlchemyError as e:
        raise Exception(f"Error fetching total confirmed bookings: {str(e)}")


async def get_most_popular_events(db: AsyncSession, limit: int = 10) -> List[PopularEvent]:
    """Get top 10 most popular events by total seats booked"""
    try:
        # Query to get events with their booked seat counts
        query = (
            select(
                Event.id,
                Event.title,
                func.count(BookingSeat.id).label('total_seats_booked'),
                Venue.name.label('venue_name')
            )
            .select_from(Event)
            .join(EventSeat, Event.id == EventSeat.event_id)
            .join(BookingSeat, EventSeat.id == BookingSeat.event_seat_id)
            .join(Booking, BookingSeat.booking_id == Booking.id)
            .join(Venue, Event.venue_id == Venue.id)
            .where(Booking.status == 'CONFIRMED', Event.is_active == True)
            .group_by(Event.id, Event.title, Venue.name)
            .order_by(desc('total_seats_booked'))
            .limit(limit)
        )
        
        result = await db.execute(query)
        rows = result.fetchall()
        
        return [
            PopularEvent(
                event_id=str(row.id),
                title=row.title,
                total_seats_booked=row.total_seats_booked,
                venue_name=row.venue_name
            )
            for row in rows
        ]
    except SQLAlchemyError as e:
        raise Exception(f"Error fetching most popular events: {str(e)}")


async def get_capacity_utilization(db: AsyncSession) -> List[CapacityUtilization]:
    """Get capacity utilization for all events"""
    try:
        # Subquery to get booked seats count per event
        booked_seats_subquery = (
            select(
                EventSeat.event_id,
                func.count(BookingSeat.id).label('booked_seats')
            )
            .select_from(EventSeat)
            .join(BookingSeat, EventSeat.id == BookingSeat.event_seat_id)
            .join(Booking, BookingSeat.booking_id == Booking.id)
            .where(Booking.status == 'CONFIRMED')
            .group_by(EventSeat.event_id)
        ).subquery()
        
        # Main query to get total seats and booked seats per event
        query = (
            select(
                Event.id,
                Event.title,
                func.count(EventSeat.id).label('total_seats'),
                func.coalesce(booked_seats_subquery.c.booked_seats, 0).label('booked_seats'),
                Venue.name.label('venue_name')
            )
            .select_from(Event)
            .join(EventSeat, Event.id == EventSeat.event_id)
            .join(Venue, Event.venue_id == Venue.id)
            .outerjoin(booked_seats_subquery, Event.id == booked_seats_subquery.c.event_id)
            .where(Event.is_active == True)
            .group_by(Event.id, Event.title, Venue.name, booked_seats_subquery.c.booked_seats)
            .order_by(desc('booked_seats'))
        )
        
        result = await db.execute(query)
        rows = result.fetchall()
        
        capacity_data = []
        for row in rows:
            total_seats = row.total_seats
            booked_seats = row.booked_seats
            utilization_percentage = (booked_seats / total_seats * 100) if total_seats > 0 else 0
            
            capacity_data.append(
                CapacityUtilization(
                    event_id=str(row.id),
                    title=row.title,
                    total_seats=total_seats,
                    booked_seats=booked_seats,
                    utilization_percentage=round(utilization_percentage, 2),
                    venue_name=row.venue_name
                )
            )
        
        return capacity_data
    except SQLAlchemyError as e:
        raise Exception(f"Error fetching capacity utilization: {str(e)}")


async def get_admin_analytics(db: AsyncSession) -> AdminAnalytics:
    """Get comprehensive admin analytics"""
    try:
        total_bookings = await get_total_confirmed_bookings(db)
        popular_events = await get_most_popular_events(db, limit=10)
        capacity_utilization = await get_capacity_utilization(db)
        
        return AdminAnalytics(
            total_confirmed_bookings=total_bookings,
            most_popular_events=popular_events,
            capacity_utilization=capacity_utilization
        )
    except Exception as e:
        raise Exception(f"Error generating admin analytics: {str(e)}")