"""Analytics business logic processor"""

from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.analytics import AdminAnalytics, PopularEvent, CapacityUtilization
from app.service.analytics_service import AnalyticsService
from typing import List


class AnalyticsProcessor:
    """Processor class for analytics business logic"""
    
    @staticmethod
    def validate_limit(limit: int) -> bool:
        """Validate limit parameter"""
        return 1 <= limit <= 100  # Limit between 1 and 100

    @staticmethod
    async def get_total_confirmed_bookings(db: AsyncSession) -> int:
        """Process getting total confirmed bookings with business logic"""
        # Business logic: No specific validation needed for this operation
        # Could add caching logic, rate limiting, or other business rules here
        
        # Call service layer
        return await AnalyticsService.get_total_confirmed_bookings(db)

    @staticmethod
    async def get_most_popular_events(db: AsyncSession, limit: int = 10) -> List[PopularEvent]:
        """Process getting most popular events with business logic"""
        # Business logic: Validate limit parameter
        if not AnalyticsProcessor.validate_limit(limit):
            raise ValueError("Limit must be between 1 and 100")
        
        # Additional business logic can be added here
        # For example: caching, data filtering, access control, etc.
        
        # Call service layer
        return await AnalyticsService.get_most_popular_events(db, limit)

    @staticmethod
    async def get_capacity_utilization(db: AsyncSession) -> List[CapacityUtilization]:
        """Process getting capacity utilization with business logic"""
        # Business logic: No specific validation needed for this operation
        # Could add business rules like:
        # - Only show events with minimum booking threshold
        # - Filter by date ranges
        # - Apply access controls based on user permissions
        
        # Call service layer
        return await AnalyticsService.get_capacity_utilization(db)

    @staticmethod
    async def get_admin_analytics(db: AsyncSession) -> AdminAnalytics:
        """Process getting comprehensive admin analytics with business logic"""
        # Business logic: This is a comprehensive analytics call
        # Could add:
        # - Performance optimization (parallel execution)
        # - Caching strategies
        # - Data aggregation rules
        # - Access control validation
        
        # Call service layer
        return await AnalyticsService.get_admin_analytics(db)
