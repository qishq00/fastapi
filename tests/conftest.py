import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from app.main import app
from app.dependencies import get_db
from .test_database import override_get_db, create_test_db

@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    await create_test_db()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def get_token(client):
    # Регистрация
    await client.post("/register", json={"username": "alice", "password": "secret"})

    # Логин
    response = await client.post("/login", data={
        "username": "alice",
        "password": "secret"
    })

    token = response.json()["access_token"]
    return token
