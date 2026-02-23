from sqlalchemy.ext.asyncio import create_async_engine,  AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os

#Get database URL from environment variable, with default for local dev
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://postgres:postgres@127.0.0.1:5433/ragdb"
)

#Create engine and sessionmaker
engine = create_async_engine(DATABASE_URL, echo=True)

#Create session factory
async_sessionmaker = sessionmaker(
    engine, class_ = AsyncSession, expire_on_commit=False
)

#Create base class for declarative models
Base = declarative_base()

#Dependency to get database session
async def get_db():
    async with async_sessionmaker() as session:
        yield session
