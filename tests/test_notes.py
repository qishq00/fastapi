import pytest

# Проверка 401 без токена
@pytest.mark.asyncio
async def test_users_me_unauthorized(client):
    response = await client.get("/users/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_users_me_authorized(client, get_token):
    token = get_token
    response = await client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "alice"

@pytest.mark.asyncio
async def test_create_and_get_own_notes(client, get_token):
    token = get_token

    # Создание заметки
    create_resp = await client.post(
        "/notes",
        json={"title": "Test Note", "content": "Test Content"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create_resp.status_code == 200
    note_id = create_resp.json()["id"]

    # Получение списка
    list_resp = await client.get(
        "/notes",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert list_resp.status_code == 200
    notes = list_resp.json()
    assert any(n["id"] == note_id for n in notes)

@pytest.mark.asyncio
async def test_cannot_access_others_notes(client):
    # Пользователь 1
    await client.post("/register", json={"username": "alice2", "password": "pw"})
    login1 = await client.post("/login", data={"username": "alice2", "password": "pw"})
    token1 = login1.json()["access_token"]

    # Создание заметки
    create_resp = await client.post(
        "/notes",
        json={"title": "Private Note", "content": "Secret"},
        headers={"Authorization": f"Bearer {token1}"}
    )
    note_id = create_resp.json()["id"]

    # Пользователь 2
    await client.post("/register", json={"username": "bob", "password": "pw"})
    login2 = await client.post("/login", data={"username": "bob", "password": "pw"})
    token2 = login2.json()["access_token"]

    # Попытка доступа к чужой заметке
    get_resp = await client.get(
        f"/notes/{note_id}",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert get_resp.status_code == 404
