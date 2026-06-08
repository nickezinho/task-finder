import random
import json

difficulty_order = {
    "easy": 1,
    "medium": 2,
    "hard": 3
}

def get_easier_task(current_task, tasks):

    current_level = difficulty_order[
        current_task.difficulty.value
    ]

    candidate_tasks = [
        task for task in tasks
        if task.id != current_task.id 
        and difficulty_order[task.difficulty.value] < current_level
    ]

    if not candidate_tasks:
        candidate_tasks = [
            task for task in tasks
            if task.id != current_task.id
            and task.difficulty.value == current_task.difficulty.value
        ]

    return random.choice(candidate_tasks) if candidate_tasks else None

def get_harder_task(current_task, tasks):

    current_level = difficulty_order[
        current_task.difficulty.value
    ]

    candidate_tasks = [
        task for task in tasks
        if task.id != current_task.id 
        and difficulty_order[task.difficulty.value] > current_level
    ]

    if not candidate_tasks:
        candidate_tasks = [
            task for task in tasks
            if task.id != current_task.id
            and task.difficulty.value == current_task.difficulty.value
        ]

    return random.choice(candidate_tasks) if candidate_tasks else None

def get_quicker_task(current_task, tasks):

    candidate_tasks = [
        task for task in tasks
        if task.id != current_task.id 
        and task.estimated_minutes < current_task.estimated_minutes
    ]

    if not candidate_tasks:
        candidate_tasks = [
            task for task in tasks
            if task.id != current_task.id
            and task.estimated_minutes == current_task.estimated_minutes
        ]

    return random.choice(candidate_tasks) if candidate_tasks else None

def get_slower_task(current_task, tasks):

    candidate_tasks = [
        task for task in tasks
        if task.id != current_task.id 
        and task.estimated_minutes > current_task.estimated_minutes
    ]

    if not candidate_tasks:
        candidate_tasks = [
            task for task in tasks
            if task.id != current_task.id
            and task.estimated_minutes == current_task.estimated_minutes
        ]

    return random.choice(candidate_tasks) if candidate_tasks else None