# Booking API Testing Guide

## 🚀 Starting the Application

### 1. Start the FastAPI Server
```bash
cd /home/soham/atlan_1.0/backend/BookMyEvent
source myenv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Start Redis CLI (in another terminal)
```bash
redis-cli
```

## 📋 API Endpoints

### Base URL: `http://localhost:8000`

## 🔐 Authentication
First, you need to get a JWT token. Use the existing user endpoints or create a test user.

## 🎫 Booking Flow Testing

### Step 1: Initiate Booking (Creates PENDING booking with Redis locks)
```bash
curl -X POST "http://localhost:8000/bookings/book" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "your-event-uuid",
    "seat_ids": ["seat-uuid-1", "seat-uuid-2"]
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "booking_id": "booking-uuid",
  "total_amount": "100.00",
  "status": "PENDING",
  "message": "Booking created. Please complete payment within 3 minutes.",
  "payment_url": "/payments/process/booking-uuid"
}
```

### Step 2: Check Redis Locks
In Redis CLI:
```redis
# See all lock keys
KEYS lock:*

# See specific lock details
GET lock:event-uuid:seat-uuid-1
TTL lock:event-uuid:seat-uuid-1

# Monitor Redis in real-time
MONITOR
```

### Step 3: Process Payment
```bash
curl -X POST "http://localhost:8000/payments/process/booking-uuid" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_ref": "TXN_123456"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "booking_id": "booking-uuid",
  "payment_id": "payment-uuid",
  "status": "CONFIRMED",
  "transaction_ref": "TXN_123456",
  "message": "Payment successful and booking confirmed"
}
```

### Step 4: Check Booking Status
```bash
curl -X GET "http://localhost:8000/payments/status/booking-uuid" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🔧 Debug Endpoints

### 1. Check Redis Locks
```bash
curl -X GET "http://localhost:8000/bookings/debug/redis-locks" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 2. Create Test Lock
```bash
curl -X POST "http://localhost:8000/bookings/debug/create-test-lock" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 3. Clear All Locks
```bash
curl -X DELETE "http://localhost:8000/bookings/debug/clear-all-locks" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🔍 Redis CLI Commands

### Basic Redis Commands
```redis
# Connect to Redis
redis-cli

# Check if Redis is running
PING

# See all keys
KEYS *

# See all lock keys
KEYS lock:*

# Get value of a specific key
GET lock:event-uuid:seat-uuid

# Get TTL (time to live) of a key
TTL lock:event-uuid:seat-uuid

# Delete a specific key
DEL lock:event-uuid:seat-uuid

# Delete all lock keys
DEL lock:*

# Monitor Redis commands in real-time
MONITOR

# Exit Redis CLI
EXIT
```

### Advanced Redis Commands
```redis
# Get all keys with pattern
KEYS lock:*

# Get multiple values
MGET lock:event-uuid:seat-uuid-1 lock:event-uuid:seat-uuid-2

# Check if key exists
EXISTS lock:event-uuid:seat-uuid

# Get key type
TYPE lock:event-uuid:seat-uuid

# Get all keys and their TTL
EVAL "local keys = redis.call('keys', 'lock:*') local result = {} for i=1,#keys do result[i] = {keys[i], redis.call('ttl', keys[i])} end return result" 0
```

## 🧪 Testing Scenarios

### Scenario 1: Normal Booking Flow
1. Create booking → Check Redis locks
2. Process payment → Check locks are released
3. Verify booking status is CONFIRMED

### Scenario 2: Booking Timeout
1. Create booking → Check Redis locks
2. Wait 3+ minutes → Check locks auto-expire
3. Try to process payment → Should fail

### Scenario 3: Seat Collision
1. User A creates booking for seat X
2. User B tries to book same seat X → Should fail
3. Check Redis shows lock for User A

### Scenario 4: Payment Failure
1. Create booking
2. Process payment with failure → Booking cancelled
3. Check locks are released, seats available

## 📊 Monitoring Redis

### Real-time Monitoring
```bash
# In one terminal - start Redis monitor
redis-cli MONITOR

# In another terminal - make API calls
curl -X POST "http://localhost:8000/bookings/book" ...
```

### Check Lock Expiration
```redis
# Check TTL of all locks
EVAL "local keys = redis.call('keys', 'lock:*') for i=1,#keys do local ttl = redis.call('ttl', keys[i]) print(keys[i] .. ' TTL: ' .. ttl) end" 0
```

## 🐛 Troubleshooting

### Common Issues

1. **Redis Connection Error**
   - Check if Redis is running: `redis-cli PING`
   - Check Redis configuration in `app/core/redis.py`

2. **Booking Fails with "Seat not available"**
   - Check if seat is already locked: `GET lock:event-id:seat-id`
   - Check if seat exists in database

3. **Payment Processing Fails**
   - Check booking status: `GET /payments/status/booking-id`
   - Verify booking is in PENDING status

4. **Locks Not Expiring**
   - Check TTL: `TTL lock:event-id:seat-id`
   - Manual cleanup: `DELETE /bookings/debug/clear-all-locks`

### Debug Steps
1. Check Redis connection: `GET /bookings/debug/redis-locks`
2. Check booking status: `GET /payments/status/booking-id`
3. Check database for booking records
4. Check Redis for lock keys

## 📝 Example Test Script

```bash
#!/bin/bash

# Set your JWT token
JWT_TOKEN="your-jwt-token-here"
EVENT_ID="your-event-uuid"
SEAT_IDS='["seat-uuid-1", "seat-uuid-2"]'

echo "1. Creating booking..."
BOOKING_RESPONSE=$(curl -s -X POST "http://localhost:8000/bookings/book" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"event_id\": \"$EVENT_ID\", \"seat_ids\": $SEAT_IDS}")

echo "Booking Response: $BOOKING_RESPONSE"

# Extract booking ID
BOOKING_ID=$(echo $BOOKING_RESPONSE | jq -r '.booking_id')

echo "2. Checking Redis locks..."
curl -s -X GET "http://localhost:8000/bookings/debug/redis-locks" \
  -H "Authorization: Bearer $JWT_TOKEN" | jq

echo "3. Processing payment..."
PAYMENT_RESPONSE=$(curl -s -X POST "http://localhost:8000/payments/process/$BOOKING_ID" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"transaction_ref": "TXN_TEST_123"}')

echo "Payment Response: $PAYMENT_RESPONSE"

echo "4. Checking final status..."
curl -s -X GET "http://localhost:8000/payments/status/$BOOKING_ID" \
  -H "Authorization: Bearer $JWT_TOKEN" | jq
```

## 🎯 Quick Start Commands

```bash
# 1. Start server
uvicorn app.main:app --reload --port 8000

# 2. Start Redis CLI
redis-cli

# 3. Test Redis connection
PING

# 4. Monitor Redis
MONITOR

# 5. Check locks
KEYS lock:*
```

This guide will help you test the complete booking and payment flow while monitoring Redis values in real-time!

