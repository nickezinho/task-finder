from fastapi import FastAPI
from api.routes.auth import auth_router
from api.routes.goal import goal_router
from api.routes.task import task_router

app = FastAPI(
    title="Task Finder API",
    description="API for finding your next task based on your goals and preferences.",
    version="1.0.0"
)

app.include_router(auth_router)
app.include_router(goal_router)
app.include_router(task_router)