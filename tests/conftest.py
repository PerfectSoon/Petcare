import asyncio
import pytest
from alembic import command
from alembic.config import Config
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.main import app
from app.database.models import Base
from app.core.settings import settings


engine_test = create_async_engine(
    settings.test_database_url,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine_test, class_=AsyncSession, expire_on_commit=False, autoflush=False
)


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", settings.test_database_url)
    command.upgrade(alembic_cfg, "head")

    sync_engine = create_engine(settings.test_database_url.replace("+asyncpg", ""))
    with sync_engine.connect() as connection:
        alembic_cfg.attributes['connection'] = connection
        command.upgrade(alembic_cfg, "head")

    async_engine = create_async_engine(settings.test_database_url)
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await async_engine.dispose()

@pytest.fixture
async def db_session():
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()

import app.database.connection as conn_mod

@pytest.fixture(autouse=True)
def override_get_db(monkeypatch, db_session):
    async def _get_db():
        try:
            yield db_session
        finally:
            await db_session.close()
    monkeypatch.setattr(conn_mod, "get_db", _get_db)


@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://testserver") as c:
        yield c
