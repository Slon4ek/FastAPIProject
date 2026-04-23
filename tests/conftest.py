# ruff: noqa: E402
import json
import pytest
import httpx
from unittest import mock

mock.patch("fastapi_cache.decorator.cache", lambda *args, **kwargs: lambda f: f).start()

from src.config import settings
from src.database import BaseModel, engine_null_pool, async_session_maker
from src.main import app
from src.models import * # noqa
from src.schemas.hotels import HotelAdd
from src.schemas.rooms import RoomAdd
from src.schemas.users import UserRequestAdd, UserLogin
from src.utils.db_manager import DBManager


@pytest.fixture(scope="session", autouse=True)
def check_mode() -> None:
    assert settings.MODE == "TEST"


@pytest.fixture(scope="session")
async def db():
    async with DBManager(session_factory=async_session_maker) as db:
        yield db


# async def get_db_null_pool():
#     async with DBManager(session_factory=async_session_maker_null_pool) as db:
#         yield db
#
# app.dependency_overrides[get_db_manager] = get_db_null_pool


@pytest.fixture(scope="session")
async def ac():
    async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture(scope="session", autouse=True)
async def setup_db(check_mode) -> None:
    with open("tests/mock_hotels.json", "r") as f:
        mock_hotels = json.load(f)
    with open("tests/mock_rooms.json", "r") as f:
        mock_rooms = json.load(f)


    hotels_schemas = [HotelAdd.model_validate(hotel) for hotel in mock_hotels]
    rooms_schemas = [RoomAdd.model_validate(room) for room in mock_rooms]

    async with engine_null_pool.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)
        await conn.run_sync(BaseModel.metadata.create_all)

    async with DBManager(session_factory=async_session_maker) as db_:
        await db_.hotels.add_bulk(hotels_schemas)
        await db_.rooms.add_bulk(rooms_schemas)
        await db_.commit()


@pytest.fixture(scope="session", autouse=True)
async def register_user(setup_db, ac) -> None:
    test_user = UserRequestAdd(
        username="test",
        email="test@test.com",
        password="test12345",
        first_name="test",
        last_name="test"
    )
    response = await ac.post(
        "/auth/register",
        json=test_user.model_dump()
    )
    assert response.status_code == 200


@pytest.fixture(scope="session")
async def auth_ac(register_user, ac):
    user_data = UserLogin(
        email="test@test.com",
        password="test12345",
    )
    await ac.post(
        "/auth/login",
        json=user_data.model_dump(),
    )
    assert ac.cookies["access_token"]
    yield ac