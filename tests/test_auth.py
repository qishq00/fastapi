import pytest

@pytest.mark.asyncio
async def test_register_and_login(client):
    register_data = {"username": "testuser", "password": "testpass"}
    response = await client.post("/register", json=register_data)
    assert response.status_code == 200

    response = await client.post("/login", data=register_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
