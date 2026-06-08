# Test Coverage Report

## Tested Endpoints
- `POST /auth/register`
- `POST /auth/login`
- `GET /goals/my-goals`
- `POST /goals/create`
- `GET /goals/{goal_id}`
- `PATCH /goals/{goal_id}`
- `DELETE /goals/{goal_id}`
- `POST /tasks/create/`
- `GET /tasks/from-goal/{goal_id}`
- `GET /tasks/{task_id}`
- `PATCH /tasks/{task_id}`
- `DELETE /tasks/{task_id}`
- `POST /tasks{goal_id}/recommend`
- `POST /tasks{goal_id}/recommend/single/`
- `GET /tasks/{task_id}/alternative?mode=easier`
- `GET /tasks/{task_id}/alternative?mode=harder`
- `GET /tasks/{task_id}/alternative?mode=quicker`
- `GET /tasks/{task_id}/alternative?mode=slower`

## Missing Coverage
- `POST /auth/`
- `POST /auth/login-form`
- `POST /auth/refresh`
- `GET /auth/me`
- Intended recommendation paths:
  - `POST /tasks/{goal_id}/recommend`
  - `POST /tasks/{goal_id}/recommend/single/`

The intended recommendation paths are covered as expected-failure tests because the current route decorators are missing the leading `/`.

## Potential Bugs Found
- `api/routes/task.py` registers recommendation routes without a leading `/`, producing paths like `/tasks{goal_id}/recommend` instead of `/tasks/{goal_id}/recommend`.
- Invalid bearer tokens can raise unhandled exceptions and return `500` instead of `401`.
- `TaskService.create_task` accepts `user_id` but does not verify that the target `goal_id` belongs to the authenticated user.
- `TaskService.list_goal_tasks` can dereference `goal.user_id` when `goal` is `None`.
- Alternative task helpers compare `estimated_minutes` directly and can fail when a task has `estimated_minutes=None`.
- AI recommendation creation validates JSON format but does not validate that the extracted top-level payload is a list before iterating.
- Gemini SDK failures are not converted into stable HTTP errors.
- `GoalRepository.create` ignores the `deadline` field from `GoalCreate`.
- Deleting a goal may leave orphan tasks unless database foreign key enforcement/cascade behavior is configured.

## Architecture Review
- Route handlers catch `ValueError`, while services often raise `HTTPException`; error handling is inconsistent across layers.
- Authentication error conversion is split between dependencies and services, which allows JWT errors to escape as server errors.
- Ownership checks are duplicated in goal/task service methods and missing from task creation.
- Repositories commit immediately on each operation, which makes multi-record service workflows harder to roll back atomically.
- Recommendation service contains AI parsing, validation, task serialization, and persistence orchestration in one class; this could be split into smaller units.
- Route function names are duplicated or generic in task routes, which makes stack traces and OpenAPI operation IDs harder to reason about.
