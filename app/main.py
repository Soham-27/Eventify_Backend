from fastapi import FastAPI
from app.api.v1.users import router as users_router  # <-- import router
from app.api.v1.events import router as events_router  # <-- import route
from app.api.v1.venues import router as venues_router  # <-- import router
from app.api.v1.event_seats import router as event_seats_router  # <-- import router
from app.api.v1.bookings import router as bookings_router 
from app.api.v1.analytics import router as analytics_router  # <-- import router
from app.api.v1.payments import router as payments_router  # <-- import router

app = FastAPI(title="Eventify Backend")

app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(venues_router, prefix="/venues", tags=["venues"])
app.include_router(events_router, prefix="/events", tags=["events"])

app.include_router(event_seats_router, prefix="/event-seats", tags=["event-seats"])
app.include_router(bookings_router, prefix="/bookings", tags=["bookings"])
app.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
app.include_router(payments_router, prefix="/payments", tags=["payments"])