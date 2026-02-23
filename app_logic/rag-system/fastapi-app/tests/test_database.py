import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.db import Base
import pytest_asyncio
from app.models.tables import Organization, User
import uuid

# Use a test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/ragdb_test" 

@pytest_asyncio.fixture
async def test_db():
    # Create test engine
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Add test org
        test_org = Organization(
            id="test_org_123",
            name="Test Organization"
        )
        session.add(test_org)
        await session.commit()

        yield session
    
    #Cleanup - drop tables after test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
async def test_org_exists(test_db: AsyncSession):
    from sqlalchemy import select
    result = await test_db.execute(
        select(Organization).where(Organization.id == "test_org_123")
    )
    org = result.scalar_one_or_none()
    assert org is not None
    assert org.name == "Test Organization"
    
    