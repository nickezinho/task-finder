import json
from collections.abc import AsyncIterator, Callable

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from api.deps import get_db
from core.database import Base
from main import app
from models import tasks as task_models  # noqa: F401
from models import users as user_models  # noqa: F401


@pytest_asyncio.fixture
async def db_sessionmaker(tmp_path) -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    db_path = tmp_path / "test.db"
    engine = create_async_engine(
        f"sqlite+aiosqlite:///{db_path}",
        echo=False,
    )
    sessionmaker_ = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield sessionmaker_

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def client(
    db_sessionmaker: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncClient]:
    async def override_get_db() -> AsyncIterator[AsyncSession]:
        async with db_sessionmaker() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def registered_user(client: AsyncClient) -> dict:
    payload = {
        "username": "qa_user",
        "name": "QA User",
        "email": "qa@example.com",
        "password": "secret123",
    }
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 200, response.text
    return payload


@pytest_asyncio.fixture
async def auth_tokens(client: AsyncClient, registered_user: dict) -> dict:
    response = await client.post(
        "/auth/login",
        json={
            "username": registered_user["username"],
            "password": registered_user["password"],
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


@pytest_asyncio.fixture
async def auth_headers(auth_tokens: dict) -> dict:
    return {"Authorization": f"Bearer {auth_tokens['access_token']}"}


@pytest_asyncio.fixture
async def goal(client: AsyncClient, auth_headers: dict) -> dict:
    response = await client.post(
        "/goals/create",
        headers=auth_headers,
        json={
            "title": "Ship API tests",
            "description": "Create automated tests for the backend API",
            "priority": "high",
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


async def create_task(
    client: AsyncClient,
    auth_headers: dict,
    goal_id: int,
    *,
    title: str,
    difficulty: str = "medium",
    estimated_minutes: int = 60,
    description: str | None = "Task created by test",
) -> dict:
    response = await client.post(
        "/tasks/create/",
        headers=auth_headers,
        json={
            "goal_id": goal_id,
            "title": title,
            "description": description,
            "estimated_minutes": estimated_minutes,
            "difficulty": difficulty,
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


@pytest_asyncio.fixture
async def task(client: AsyncClient, auth_headers: dict, goal: dict) -> dict:
    return await create_task(
        client,
        auth_headers,
        goal["id"],
        title="Write first endpoint test",
        difficulty="medium",
        estimated_minutes=60,
    )


@pytest_asyncio.fixture
async def alternative_tasks(
    client: AsyncClient,
    auth_headers: dict,
    goal: dict,
) -> dict:
    current = await create_task(
        client,
        auth_headers,
        goal["id"],
        title="Current medium task",
        difficulty="medium",
        estimated_minutes=60,
    )
    easier_quicker = await create_task(
        client,
        auth_headers,
        goal["id"],
        title="Easier quicker task",
        difficulty="easy",
        estimated_minutes=30,
    )
    harder_slower = await create_task(
        client,
        auth_headers,
        goal["id"],
        title="Harder slower task",
        difficulty="hard",
        estimated_minutes=120,
    )
    return {
        "current": current,
        "easier_quicker": easier_quicker,
        "harder_slower": harder_slower,
    }


class FakeGeminiClient:
    def __init__(
        self,
        generate_response: str | None = None,
        recommend_response: str | None = None,
    ) -> None:
        self.generate_response = generate_response
        self.recommend_response = recommend_response

    def generate_content(self, prompt):
        return self.generate_response

    def recommend_task(self, prompt):
        return self.recommend_response


@pytest.fixture
def mock_gemini(monkeypatch) -> Callable[..., FakeGeminiClient]:
    def apply_mock(
        *,
        generate_response: str | list | dict | None = None,
        recommend_response: str | list | dict | None = None,
    ) -> FakeGeminiClient:
        if isinstance(generate_response, (list, dict)):
            generate_text = json.dumps(generate_response)
        else:
            generate_text = generate_response

        if isinstance(recommend_response, (list, dict)):
            recommend_text = json.dumps(recommend_response)
        else:
            recommend_text = recommend_response

        fake = FakeGeminiClient(
            generate_response=generate_text,
            recommend_response=recommend_text,
        )
        monkeypatch.setattr(
            "services.recommendation_service.GeminiClient",
            lambda: fake,
        )
        return fake

    return apply_mock
