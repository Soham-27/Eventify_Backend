# BookMyEvent API Documentation

## Overview

The BookMyEvent API is a comprehensive event booking system built with FastAPI. It provides endpoints for user management, event management, venue management, seat booking, payment processing, and analytics.

**Base URL:** `http://localhost:8000`  
**API Version:** v1  
**Interactive Documentation:** 
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Authentication

Most endpoints require authentication using JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## User Roles

- **USER**: Regular users who can book events and manage their bookings
- **ADMIN**: Administrators who can manage events, venues, and access analytics

---

## 🔐 User APIs

### Authentication & User Management

#### Register User
```http
POST /users/
```

**Description:** Create a new user account

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "full_name": "John Doe",
  "phone": "+1234567890"
}
```

**Response:** `201 Created`
```json
{
  "user": {
    "user_id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "phone": "+1234567890",
    "role": "USER",
    "created_at": "2024-01-01T00:00:00Z"
  },
  "access_token": "jwt_token_here",
  "token_type": "bearer"
}
```

#### Login User
```http
POST /users/login
```

**Description:** Authenticate user and get access token

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:** `200 OK`
```json
{
  "user": {
    "user_id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "phone": "+1234567890",
    "role": "USER",
    "created_at": "2024-01-01T00:00:00Z"
  },
  "access_token": "jwt_token_here",
  "token_type": "bearer"
}
```

#### Get Current User
```http
GET /users/me
```

**Description:** Get current user information

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "phone": "+1234567890",
  "role": "USER",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Event Discovery

#### Get All Events
```http
GET /events/?skip=0&limit=10
```

**Description:** Get list of all events with pagination

**Query Parameters:**
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum number of records to return (default: 10)

**Response:** `200 OK`
```json
[
  {
    "event_id": "uuid",
    "title": "Concert Night",
    "description": "Amazing concert",
    "event_date": "2024-12-31T20:00:00Z",
    "venue_id": "uuid",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### Get Upcoming Events
```http
GET /events/upcoming?skip=0&limit=10
```

**Description:** Get upcoming events with capacity details

**Query Parameters:**
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum number of records to return (default: 10)

**Response:** `200 OK`
```json
[
  {
    "event_id": "uuid",
    "title": "Concert Night",
    "description": "Amazing concert",
    "event_date": "2024-12-31T20:00:00Z",
    "venue_id": "uuid",
    "is_active": true,
    "total_capacity": 100,
    "booked_seats": 50,
    "available_seats": 50
  }
]
```

#### Get Event by ID
```http
GET /events/{event_id}
```

**Description:** Get specific event details

**Path Parameters:**
- `event_id` (string): Event UUID

**Response:** `200 OK`
```json
{
  "event_id": "uuid",
  "title": "Concert Night",
  "description": "Amazing concert",
  "event_date": "2024-12-31T20:00:00Z",
  "venue_id": "uuid",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Venue Information

#### Get All Venues
```http
GET /venues/?skip=0&limit=10
```

**Description:** Get list of all venues

**Query Parameters:**
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum number of records to return (default: 10)

**Response:** `200 OK`
```json
[
  {
    "venue_id": "uuid",
    "name": "Grand Theater",
    "address": "123 Main St",
    "city": "New York",
    "capacity": 500,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### Get Venue by ID
```http
GET /venues/{venue_id}
```

**Description:** Get specific venue details

**Path Parameters:**
- `venue_id` (string): Venue UUID

**Response:** `200 OK`
```json
{
  "venue_id": "uuid",
  "name": "Grand Theater",
  "address": "123 Main St",
  "city": "New York",
  "capacity": 500,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Seat Management

#### Get Event Seats
```http
GET /event-seats/event/{event_id}
```

**Description:** Get all seats for an event with seat details

**Path Parameters:**
- `event_id` (string): Event UUID

**Response:** `200 OK`
```json
[
  {
    "event_seat_id": "uuid",
    "event_id": "uuid",
    "seat_id": "uuid",
    "price": 50.00,
    "is_available": true,
    "seat": {
      "seat_id": "uuid",
      "row_no": "A",
      "seat_no": "1",
      "venue_id": "uuid"
    }
  }
]
```

#### Get Available Event Seats
```http
GET /event-seats/event/{event_id}/available
```

**Description:** Get only available seats for an event

**Path Parameters:**
- `event_id` (string): Event UUID

**Response:** `200 OK`
```json
[
  {
    "event_seat_id": "uuid",
    "event_id": "uuid",
    "seat_id": "uuid",
    "price": 50.00,
    "is_available": true
  }
]
```

#### Get Seats by Row
```http
GET /event-seats/event/{event_id}/row/{row_no}
```

**Description:** Get all seats for a specific row in an event

**Path Parameters:**
- `event_id` (string): Event UUID
- `row_no` (string): Row number (e.g., "A", "B", "1", "2")

**Response:** `200 OK`
```json
[
  {
    "event_seat_id": "uuid",
    "event_id": "uuid",
    "seat_id": "uuid",
    "price": 50.00,
    "is_available": true
  }
]
```

### Booking Management

#### Book Seats
```http
POST /bookings/book
```

**Description:** Book seats for an event with payment flow

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "event_id": "uuid",
  "seat_ids": ["uuid1", "uuid2", "uuid3"]
}
```

**Response:** `201 Created`
```json
{
  "success": true,
  "booking_id": "uuid",
  "message": "Booking created successfully",
  "payment_required": true,
  "total_amount": 150.00,
  "seats": [
    {
      "seat_id": "uuid1",
      "row_no": "A",
      "seat_no": "1",
      "price": 50.00
    }
  ]
}
```

#### Cancel Booking
```http
POST /bookings/cancel
```

**Description:** Cancel a pending booking and release seats

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "booking_id": "uuid"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Booking cancelled successfully",
  "booking_id": "uuid"
}
```

#### Get User Bookings
```http
GET /bookings/get-bookings-by-user
```

**Description:** Get all bookings for the current user

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
[
  {
    "booking_id": "uuid",
    "user_id": "uuid",
    "event_id": "uuid",
    "status": "CONFIRMED",
    "total_amount": 150.00,
    "created_at": "2024-01-01T00:00:00Z",
    "booking_seats": [
      {
        "seat_id": "uuid",
        "row_no": "A",
        "seat_no": "1",
        "price": 50.00
      }
    ]
  }
]
```

### Payment Processing

#### Process Payment
```http
POST /payments/process/{booking_id}
```

**Description:** Process payment for a booking

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `booking_id` (string): Booking UUID

**Request Body:**
```json
{
  "payment_method": "credit_card",
  "card_number": "4111111111111111",
  "expiry_date": "12/25",
  "cvv": "123"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "payment_id": "uuid",
  "booking_id": "uuid",
  "status": "PAID",
  "amount": 150.00,
  "message": "Payment processed successfully"
}
```

#### Get Booking Status
```http
GET /payments/status/{booking_id}
```

**Description:** Get booking and payment status

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `booking_id` (string): Booking UUID

**Response:** `200 OK`
```json
{
  "success": true,
  "booking_id": "uuid",
  "status": "CONFIRMED",
  "payment_status": "PAID",
  "total_amount": 150.00,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Payment Health Check
```http
GET /payments/health
```

**Description:** Health check for payment service

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "service": "payment",
  "message": "Payment service is running"
}
```

---

## 👑 Admin APIs

### Event Management

#### Create Event
```http
POST /events/
```

**Description:** Create a new event (admin only)

**Headers:** `Authorization: Bearer <admin_token>`

**Request Body:**
```json
{
  "title": "Concert Night",
  "description": "Amazing concert",
  "event_date": "2024-12-31T20:00:00Z",
  "venue_id": "uuid"
}
```

**Response:** `201 Created`
```json
{
  "event_id": "uuid",
  "title": "Concert Night",
  "description": "Amazing concert",
  "event_date": "2024-12-31T20:00:00Z",
  "venue_id": "uuid",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Update Event
```http
PUT /events/{event_id}
```

**Description:** Update event details (admin only)

**Headers:** `Authorization: Bearer <admin_token>`

**Path Parameters:**
- `event_id` (string): Event UUID

**Request Body:**
```json
{
  "title": "Updated Concert Night",
  "description": "Updated description",
  "event_date": "2024-12-31T21:00:00Z"
}
```

**Response:** `200 OK`
```json
{
  "event_id": "uuid",
  "title": "Updated Concert Night",
  "description": "Updated description",
  "event_date": "2024-12-31T21:00:00Z",
  "venue_id": "uuid",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Update Event Status
```http
PATCH /events/{event_id}/status
```

**Description:** Update event active status (admin only)

**Headers:** `Authorization: Bearer <admin_token>`

**Path Parameters:**
- `event_id` (string): Event UUID

**Request Body:**
```json
{
  "is_active": false
}
```

**Response:** `200 OK`
```json
{
  "event_id": "uuid",
  "title": "Concert Night",
  "description": "Amazing concert",
  "event_date": "2024-12-31T20:00:00Z",
  "venue_id": "uuid",
  "is_active": false,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Delete Event
```http
DELETE /events/{event_id}
```

**Description:** Delete event (admin only)

**Headers:** `Authorization: Bearer <admin_token>`

**Path Parameters:**
- `event_id` (string): Event UUID

**Response:** `200 OK`
```json
{
  "message": "Event deleted successfully"
}
```

### Venue Management

#### Create Venue
```http
POST /venues/
```

**Description:** Create a new venue (admin only)

**Headers:** `Authorization: Bearer <admin_token>`

**Request Body:**
```json
{
  "name": "Grand Theater",
  "address": "123 Main St",
  "city": "New York",
  "capacity": 500
}
```

**Response:** `201 Created`
```json
{
  "venue_id": "uuid",
  "name": "Grand Theater",
  "address": "123 Main St",
  "city": "New York",
  "capacity": 500,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Update Venue
```http
PUT /venues/{venue_id}
```

**Description:** Update venue (admin only)

**Headers:** `Authorization: Bearer <admin_token>`

**Path Parameters:**
- `venue_id` (string): Venue UUID

**Request Body:**
```json
{
  "name": "Updated Grand Theater",
  "address": "456 New St",
  "city": "Los Angeles",
  "capacity": 600
}
```

**Response:** `200 OK`
```json
{
  "venue_id": "uuid",
  "name": "Updated Grand Theater",
  "address": "456 New St",
  "city": "Los Angeles",
  "capacity": 600,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Delete Venue
```http
DELETE /venues/{venue_id}
```

**Description:** Delete venue (admin only)

**Headers:** `Authorization: Bearer <admin_token>`

**Path Parameters:**
- `venue_id` (string): Venue UUID

**Response:** `200 OK`
```json
{
  "message": "Venue deleted successfully"
}
```

### Seat Price Management

#### Update Row Price
```http
PUT /event-seats/event/{event_id}/row/price
```

**Description:** Update price for all seats in a specific row (admin only)

**Headers:** `Authorization: Bearer <admin_token>`

**Path Parameters:**
- `event_id` (string): Event UUID

**Request Body:**
```json
{
  "row_no": "A",
  "new_price": 75.00
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Row price updated successfully",
  "event_id": "uuid",
  "row_no": "A",
  "new_price": 75.00,
  "updated_seats": 10
}
```

### Analytics & Reporting

#### Get Total Bookings
```http
GET /analytics/admin/total-bookings
```

**Description:** Get total number of confirmed bookings (admin only)

**Headers:** `Authorization: Bearer <admin_token>`

**Response:** `200 OK`
```json
{
  "total_confirmed_bookings": 150
}
```

#### Get Popular Events
```http
GET /analytics/admin/popular-events?limit=10
```

**Description:** Get most popular events by seats booked (admin only)

**Headers:** `Authorization: Bearer <admin_token>`

**Query Parameters:**
- `limit` (int, optional): Number of events to return (default: 10)

**Response:** `200 OK`
```json
[
  {
    "event_id": "uuid",
    "title": "Concert Night",
    "total_seats_booked": 450,
    "venue_capacity": 500,
    "utilization_percentage": 90.0
  }
]
```

#### Get Capacity Utilization
```http
GET /analytics/admin/capacity-utilization
```

**Description:** Get capacity utilization for all events (admin only)

**Headers:** `Authorization: Bearer <admin_token>`

**Response:** `200 OK`
```json
[
  {
    "event_id": "uuid",
    "title": "Concert Night",
    "venue_name": "Grand Theater",
    "total_capacity": 500,
    "booked_seats": 450,
    "available_seats": 50,
    "utilization_percentage": 90.0
  }
]
```

### Payment Management

#### Cleanup Expired Bookings
```http
POST /payments/cleanup-expired
```

**Description:** Clean up expired bookings (admin only)

**Headers:** `Authorization: Bearer <admin_token>`

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Expired bookings cleaned up successfully",
  "cleaned_bookings": 5,
  "released_seats": 15
}
```

---

## 🛠️ Debug & Development APIs

### Redis Debug (Development Only)

#### Debug Redis Locks
```http
GET /bookings/debug/redis-locks
```

**Description:** Debug endpoint to see all Redis lock keys

**Response:** `200 OK`
```json
{
  "redis_connection": "OK",
  "total_locks": 3,
  "lock_details": [
    {
      "key": "lock:event123:seat456",
      "value": "user789",
      "ttl": 300
    }
  ]
}
```

#### Create Test Lock
```http
POST /bookings/debug/create-test-lock
```

**Description:** Create a test lock for debugging

**Response:** `200 OK`
```json
{
  "message": "Test lock created",
  "key": "lock:test-event:test-seat",
  "value": "test-user-123",
  "ttl": 60
}
```

#### Clear All Locks
```http
DELETE /bookings/debug/clear-all-locks
```

**Description:** Clear all Redis locks (for testing)

**Response:** `200 OK`
```json
{
  "message": "Cleared 5 locks",
  "cleared_keys": ["lock:event1:seat1", "lock:event1:seat2"]
}
```

---

## Error Responses

### Common Error Codes

- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Missing or invalid authentication token
- `403 Forbidden` - Insufficient permissions (admin required)
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

### Error Response Format

```json
{
  "detail": "Error message description"
}
```

