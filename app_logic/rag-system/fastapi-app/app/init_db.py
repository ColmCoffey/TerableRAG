import asyncio
from app.db import engine, Base
from app.models.tables import Organization, User, Document, AuditLog

async def init_tables():
    async with engine.begin() as conn:
        # Drop all tables (careful - this deletes all DATA!)
        await conn.run_sync(Base.metadata.drop_all)
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created!")

if __name__ == "__main__":
    asyncio.run(init_tables())

