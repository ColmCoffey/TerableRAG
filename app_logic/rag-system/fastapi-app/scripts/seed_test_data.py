import asyncio
from app.db import async_sessionmaker
from app.models.tables import Organization

async def seed():
    async with async_sessionmaker() as session:
        org = Organization(
            id="org_123",
            name="Test Organization"
        )
        session.add(org)
        await session.commit()
        print("Test org created!")

if __name__ == "__main__":
    asyncio.run(seed())