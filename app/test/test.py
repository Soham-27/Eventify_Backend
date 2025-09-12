import asyncio
import httpx

async def book(token):
    async with httpx.AsyncClient() as client:
        r = await client.post(
            "http://localhost:8000/bookings/book",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json={"event_id": "04a425ed-63ab-4ce5-9122-75abc75ba5c2", "seat_ids": ["9ccb6d75-d243-45fc-ac35-f4796e0285df","30346926-8447-4d37-87b7-0b1f63458593"]}
        )
        print(token, r.status_code, r.json())

async def main():
    await asyncio.gather(
        book("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZGU1YzQ5NTctYjA4Ny00MmQ3LTgxNTMtNWY1OTM4YzY4MWYyIiwicm9sZSI6IlVTRVIiLCJleHAiOjE3NTc3NjM5NTF9.Zch8M20FtWbWvc6eZIOhwr-82suzFxPcs-1cHYT9lj0"),
        book("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMjIwNjg2N2UtMDEwNy00OTY2LWFjNDQtZTBkNmVjY2Y0OTFjIiwicm9sZSI6IlVTRVIiLCJleHAiOjE3NTc3NjM5OTB9.JkRfaX8uds75qIfQcWcq737c0IsvRd0Buucs1MjbNMw")
    )

asyncio.run(main())
