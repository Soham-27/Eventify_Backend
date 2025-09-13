from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal


class PopularEvent(BaseModel):
    event_id: str
    title: str
    total_seats_booked: int
    venue_name: Optional[str] = None


class CapacityUtilization(BaseModel):
    event_id: str
    title: str
    total_seats: int
    booked_seats: int
    utilization_percentage: float
    venue_name: Optional[str] = None


class AdminAnalytics(BaseModel):
    total_confirmed_bookings: int
    most_popular_events: List[PopularEvent]
    capacity_utilization: List[CapacityUtilization]
