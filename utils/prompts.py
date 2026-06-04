generate_example = """
[
    {
        "title": "Task title",
        "description": "Task description",
        "estimated_minutes": 60,
        "difficulty": "easy"
    }
]
"""

task_example = {
    "title": "Task title",
    "description": "Task description",
    "estimated_minutes": 60,
    "difficulty": "easy"
}

recommend_task_example = """
{
    "task_id": 1,
    "reason": "max 20 words"
}
"""

def generate_recommendation_prompt(goal_title, goal_description):

    prompt = f"""
    You are an expert in productivity and goal planning.

    Your task is to break down a goal into practical, actionable tasks.

    INPUT

    Goal Title:
    {goal_title}

    Goal Description:
    {goal_description}

    INSTRUCTIONS

    - Generate between 5 and 10 tasks.
    - Tasks must be specific and actionable.
    - Avoid vague tasks.
    - Order tasks logically from first step to last step.
    - Avoid duplicate or overlapping tasks.
    - Keep tasks realistic and achievable.
    - Use the same language as the goal title and description.

    OUTPUT

    Return ONLY a valid JSON array.

    Schema:

    {generate_example}

    VALID VALUES

    difficulty must be exactly one of:
    - easy
    - medium
    - hard

    RULES

    - Do not return markdown.
    - Do not return explanations.
    - Do not return code fences.
    - Do not return any text before or after the JSON.
    - estimated_minutes must be a positive integer.
    - Every task must be directly related to the goal.
    """

    return prompt

def generate_recommended_task(goal_title, goal_description, goal_priority, goal_deadline, tasks):

    prompt = f"""
    You are an expert productivity coach.

    Your job is to select the BEST next task to execute in order to make real progress on the goal.

    GOAL

    Title:
    {goal_title}

    Description:
    {goal_description}

    Priority:
    {goal_priority}

    Deadline:
    {goal_deadline}

    AVAILABLE TASKS

    {tasks}

    INSTRUCTIONS

    - Select EXACTLY ONE task.
    - You MUST choose from the provided task list.
    - Do NOT invent new tasks or IDs.
    - Prefer tasks that:
    1. Are required before others (dependencies / logical order)
    2. Are faster to complete (quick wins) when possible
    3. Have lower difficulty if priority is low
    4. Maximize progress if priority is high or deadline is قريب
    - If a deadline is near, prefer faster and high-impact tasks.
    - Avoid tasks that are too large or unclear as a "next step".

    OUTPUT FORMAT (STRICT)

    Return ONLY valid JSON:

    {recommend_task_example}

    RULES

    - Do NOT include markdown or code blocks.
    - Do NOT include any text outside the JSON.
    - The task_id must exist in the provided task list.
    - Keep reason short, objective, and concrete.
    """
    
    return prompt