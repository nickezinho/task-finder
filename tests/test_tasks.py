import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.asyncio


async def test_create_task(client: AsyncClient, auth_headers: dict, goal: dict):
    response = await client.post(
        "/tasks/create/",
        headers=auth_headers,
        json={
            "goal_id": goal["id"],
            "title": "Create task tests",
            "description": "Exercise the POST /tasks/create endpoint",
            "estimated_minutes": 45,
            "difficulty": "medium",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"]
    assert data["goal_id"] == goal["id"]
    assert data["title"] == "Create task tests"
    assert data["status"] == "pending"


async def test_list_tasks(client: AsyncClient, auth_headers: dict, goal: dict, task: dict):
    response = await client.get(f"/tasks/from-goal/{goal['id']}", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == task["id"]


async def test_get_task_by_id(client: AsyncClient, auth_headers: dict, task: dict):
    response = await client.get(f"/tasks/{task['id']}", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["id"] == task["id"]


async def test_update_task(client: AsyncClient, auth_headers: dict, task: dict):
    response = await client.patch(
        f"/tasks/{task['id']}",
        headers=auth_headers,
        json={"status": "completed"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "completed"


async def test_delete_task(client: AsyncClient, auth_headers: dict, task: dict):
    delete_response = await client.delete(f"/tasks/{task['id']}", headers=auth_headers)
    get_response = await client.get(f"/tasks/{task['id']}", headers=auth_headers)

    assert delete_response.status_code == 200
    assert delete_response.json()["detail"] == "Task deleted successfully"
    assert get_response.status_code == 404
