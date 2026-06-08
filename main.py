from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from core.security import limiter
from api.routes.auth import auth_router
from api.routes.goal import goal_router
from api.routes.task import task_router

app = FastAPI(
    title="Task Finder API",
    description="API for finding your next task based on your goals and preferences.",
    version="1.0.0"
)

app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler
)
app.include_router(auth_router)
app.include_router(goal_router)
app.include_router(task_router)