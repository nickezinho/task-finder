import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.asyncio


async def test_create_goal(client: AsyncClient, auth_headers: dict):
    response = await client.post(
        "/goals/create",
        headers=auth_headers,
        json={
            "title": "Learn FastAPI",
            "description": "Build a small async API",
            "priority": "medium",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"]
    assert data["title"] == "Learn FastAPI"
    assert data["priority"] == "medium"


async def test_list_goals(client: AsyncClient, auth_headers: dict, goal: dict):
    response = await client.get("/goals/my-goals", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == goal["id"]


async def test_get_goal_by_id(client: AsyncClient, auth_headers: dict, goal: dict):
    response = await client.get(f"/goals/{goal['id']}", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["id"] == goal["id"]


async def test_update_goal(client: AsyncClient, auth_headers: dict, goal: dict):
    response = await client.patch(
        f"/goals/{goal['id']}",
        headers=auth_headers,
        json={
            "title": "Updated goal",
            "priority": "low",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated goal"
    assert data["priority"] == "low"


async def test_delete_goal(client: AsyncClient, auth_headers: dict, goal: dict):
    delete_response = await client.delete(f"/goals/{goal['id']}", headers=auth_headers)
    get_response = await client.get(f"/goals/{goal['id']}", headers=auth_headers)

    assert delete_response.status_code == 200
    assert delete_response.json()["detail"] == "Goal deleted successfully"
    assert get_response.status_code == 404
