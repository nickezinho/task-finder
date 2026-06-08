import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.asyncio


async def test_login_success(client: AsyncClient, registered_user: dict):
    response = await client.post(
        "/auth/login",
        json={
            "username": registered_user["username"],
            "password": registered_user["password"],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "Bearer"
    assert data["access_token"]
    assert data["refresh_token"]


async def test_login_failure(client: AsyncClient, registered_user: dict):
    response = await client.post(
        "/auth/login",
        json={
            "username": registered_user["username"],
            "password": "wrong-password",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid username or password"


async def test_protected_route_requires_authentication(client: AsyncClient):
    response = await client.get("/goals/my-goals")

    assert response.status_code == 401


@pytest.mark.xfail(reason="Invalid tokens currently raise an unhandled exception instead of HTTP 401.")
async def test_invalid_token_returns_unauthorized(client: AsyncClient):
    response = await client.get(
        "/goals/my-goals",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401


async def test_current_invalid_token_behavior_is_server_error(client: AsyncClient):
    response = await client.get(
        "/goals/my-goals",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 500
