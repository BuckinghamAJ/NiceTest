"""
Postgres class model for test_storage database
"""
import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from contextlib import asynccontextmanager


load_dotenv()  # take environment variables from .env.


class Postgres:
    """Handles Postgres database connections & sessions"""

    def __init__(self) -> None:
        self.engine = self._create_engine()

    @property
    def url(self) -> str:
        return os.environ.get("DATABASE_URL") or None

    def _create_engine(self) -> AsyncEngine:
        return create_async_engine(self.url, echo=True, future=True)

    @asynccontextmanager
    async def get_session(self) -> AsyncSession:
        async_session = sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)
        async with async_session() as session:
            yield session

    async def close_session(self) -> None:
        await self.engine.dispose()
