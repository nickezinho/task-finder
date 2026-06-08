import pytest
from httpx import AsyncClient

from tests.conftest import create_task


pytestmark = pytest.mark.asyncio


def current_generate_recommendation_path(goal_id: int) -> str:
    return f"/tasks/{goal_id}/recommend"


def current_single_recommendation_path(goal_id: int) -> str:
    return f"/tasks/{goal_id}/recommend/single/"


@pytest.mark.xfail(reason="Recommendation route decorators are missing a leading slash.")
async def test_intended_generate_recommendation_route_exists(
    client: AsyncClient,
    auth_headers: dict,
    goal: dict,
):
    response = await client.post(
        f"/tasks/{goal['id']}/recommend",
        headers=auth_headers,
    )

    assert response.status_code != 404


async def test_generate_recommendation_success(
    client: AsyncClient,
    auth_headers: dict,
    goal: dict,
    mock_gemini,
):
    mock_gemini(
        generate_response=[
            {
                "title": "Plan test structure",
                "description": "Define test modules and fixtures",
                "estimated_minutes": 30,
                "difficulty": "easy",
            },
            {
                "title": "Write endpoint tests",
                "description": "Cover auth, goals, and tasks",
                "estimated_minutes": 90,
                "difficulty": "medium",
            },
        ],
    )

    response = await client.post(
        current_generate_recommendation_path(goal["id"]),
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["goal_id"] == goal["id"]
    assert data[0]["title"] == "Plan test structure"


async def test_generate_recommendation_invalid_ai_response(
    client: AsyncClient,
    auth_headers: dict,
    goal: dict,
    mock_gemini,
):
    mock_gemini(generate_response="not-json")

    response = await client.post(
        current_generate_recommendation_path(goal["id"]),
        headers=auth_headers,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid response format from recommendation service"


async def test_generate_recommendation_goal_not_found(
    client: AsyncClient,
    auth_headers: dict,
    mock_gemini,
):
    mock_gemini(generate_response=[])

    response = await client.post(
        current_generate_recommendation_path(999),
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Goal not found"


@pytest.mark.xfail(reason="Single recommendation route decorator is missing a leading slash.")
async def test_intended_single_recommendation_route_exists(
    client: AsyncClient,
    auth_headers: dict,
    goal: dict,
):
    response = await client.post(
        f"/tasks/{goal['id']}/recommend/single/",
        headers=auth_headers,
    )

    assert response.status_code != 404


async def test_recommend_task_success(
    client: AsyncClient,
    auth_headers: dict,
    goal: dict,
    task: dict,
    mock_gemini,
):
    mock_gemini(
        recommend_response={
            "task_id": task["id"],
            "reason": "Best next step.",
        },
    )

    response = await client.post(
        current_single_recommendation_path(goal["id"]),
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["task"]["id"] == task["id"]
    assert data["reason"] == "Best next step."


async def test_recommend_task_no_tasks_available(
    client: AsyncClient,
    auth_headers: dict,
    goal: dict,
    mock_gemini,
):
    mock_gemini(recommend_response={"task_id": 1, "reason": "Unused."})

    response = await client.post(
        current_single_recommendation_path(goal["id"]),
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "No tasks found for this goal"


async def test_alternative_task_easier(
    client: AsyncClient,
    auth_headers: dict,
    alternative_tasks: dict,
):
    response = await client.get(
        f"/tasks/{alternative_tasks['current']['id']}/alternative",
        headers=auth_headers,
        params={"mode": "easier"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == alternative_tasks["easier_quicker"]["id"]


async def test_alternative_task_harder(
    client: AsyncClient,
    auth_headers: dict,
    alternative_tasks: dict,
):
    response = await client.get(
        f"/tasks/{alternative_tasks['current']['id']}/alternative",
        headers=auth_headers,
        params={"mode": "harder"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == alternative_tasks["harder_slower"]["id"]


async def test_alternative_task_quicker(
    client: AsyncClient,
    auth_headers: dict,
    alternative_tasks: dict,
):
    response = await client.get(
        f"/tasks/{alternative_tasks['current']['id']}/alternative",
        headers=auth_headers,
        params={"mode": "quicker"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == alternative_tasks["easier_quicker"]["id"]


async def test_alternative_task_slower(
    client: AsyncClient,
    auth_headers: dict,
    alternative_tasks: dict,
):
    response = await client.get(
        f"/tasks/{alternative_tasks['current']['id']}/alternative",
        headers=auth_headers,
        params={"mode": "slower"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == alternative_tasks["harder_slower"]["id"]


async def test_single_recommendation_ignores_completed_tasks(
    client: AsyncClient,
    auth_headers: dict,
    goal: dict,
    mock_gemini,
):
    pending_task = await create_task(
        client,
        auth_headers,
        goal["id"],
        title="Pending task",
        difficulty="medium",
        estimated_minutes=60,
    )
    completed_task = await create_task(
        client,
        auth_headers,
        goal["id"],
        title="Completed task",
        difficulty="easy",
        estimated_minutes=10,
    )
    await client.patch(
        f"/tasks/{completed_task['id']}",
        headers=auth_headers,
        json={"status": "completed"},
    )

    mock_gemini(
        recommend_response={
            "task_id": pending_task["id"],
            "reason": "Only pending option.",
        },
    )

    response = await client.post(
        current_single_recommendation_path(goal["id"]),
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["task"]["id"] == pending_task["id"]
