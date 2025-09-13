#!/usr/bin/env python3
"""
Simple script to check Redis values
Run with: python check_redis.py
"""

import asyncio
import redis.asyncio as aioredis

async def check_redis_values():
    # Connect to Redis
    redis_client = aioredis.from_url("redis://localhost:6379/0", decode_responses=True)
    
    try:
        # Get all keys
        all_keys = await redis_client.keys("*")
        print(f"Total keys in Redis: {len(all_keys)}")
        
        # Get all lock keys
        lock_keys = await redis_client.keys("lock:*")
        print(f"Lock keys: {len(lock_keys)}")
        
        for key in lock_keys:
            value = await redis_client.get(key)
            ttl = await redis_client.ttl(key)
            print(f"  {key}: {value} (TTL: {ttl}s)")
        
        # Get all keys and their values
        print("\nAll keys and values:")
        for key in all_keys:
            value = await redis_client.get(key)
            ttl = await redis_client.ttl(key)
            print(f"  {key}: {value} (TTL: {ttl}s)")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await redis_client.close()

if __name__ == "__main__":
    asyncio.run(check_redis_values())
