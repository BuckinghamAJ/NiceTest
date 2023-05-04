"""
Generate a postgresql database with for the following tables:
- Tests
- Steps
- Requirements
"""
import os
from nice_test.backend.models.base import Docs, Steps, Requirements
from sqlmodel import create_engine, Session, SQLModel
from dotenv import load_dotenv
import asyncio


load_dotenv()  # take environment variables from .env.

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, echo=True, future=True)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


# TODO: Make Nice Test User for application
# grant select,insert,update,delete ON requirements,steps,tests TO nice_test_user;


def make_db():
    asyncio.run(init_db())


async def get_session() -> AsyncSession:
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
