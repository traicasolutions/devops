from datetime import datetime

import pytest
from pydantic import ValidationError

from app.main import TodoCreate, TodoUpdate, health, row_to_dict


def test_health_returns_ok_status():
    assert health() == {"status": "ok"}


def test_todo_create_accepts_valid_title():
    todo = TodoCreate(title="Learn SonarCloud")

    assert todo.title == "Learn SonarCloud"


def test_todo_create_rejects_empty_title():
    with pytest.raises(ValidationError):
        TodoCreate(title="")


def test_todo_update_requires_boolean_completed_value():
    todo = TodoUpdate(completed=True)

    assert todo.completed is True


def test_row_to_dict_converts_database_row_to_api_response():
    created_at = datetime(2026, 9, 20, 10, 30, 0)
    updated_at = datetime(2026, 9, 20, 11, 45, 0)
    row = (1, "Write tests", False, created_at, updated_at)

    result = row_to_dict(row)

    assert result == {
        "id": 1,
        "title": "Write tests",
        "completed": False,
        "created_at": "2026-09-20T10:30:00",
        "updated_at": "2026-09-20T11:45:00",
    }
