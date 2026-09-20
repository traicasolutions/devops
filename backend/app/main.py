import os
from contextlib import contextmanager

import psycopg
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="Todo API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def db_config():
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "dbname": os.getenv("DB_NAME", "todos"),
        "user": os.getenv("DB_USER", "todo"),
        "password": os.getenv("DB_PASSWORD", "todo"),
    }


@contextmanager
def get_connection():
    conn = psycopg.connect(**db_config())
    try:
        yield conn
    finally:
        conn.close()


class TodoCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)


class TodoUpdate(BaseModel):
    completed: bool


def row_to_dict(row):
    return {
        "id": row[0],
        "title": row[1],
        "completed": row[2],
        "created_at": row[3].isoformat(),
        "updated_at": row[4].isoformat(),
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/todos")
def get_todos():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, title, completed, created_at, updated_at
                FROM todos
                ORDER BY id DESC
            """)
            rows = cur.fetchall()
    return [row_to_dict(row) for row in rows]


@app.post("/api/todos", status_code=201)
def create_todo(todo: TodoCreate):
    title = todo.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="Title is required")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO todos (title)
                VALUES (%s)
                RETURNING id, title, completed, created_at, updated_at
            """, (title,))
            row = cur.fetchone()
        conn.commit()
    return row_to_dict(row)


@app.put("/api/todos/{todo_id}")
def update_todo(todo_id: int, todo: TodoUpdate):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE todos
                SET completed = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING id, title, completed, created_at, updated_at
            """, (todo.completed, todo_id))
            row = cur.fetchone()
        conn.commit()

    if row is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    return row_to_dict(row)


@app.delete("/api/todos/{todo_id}")
def delete_todo(todo_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM todos WHERE id = %s RETURNING id",
                (todo_id,)
            )
            row = cur.fetchone()
        conn.commit()

    if row is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    return {"message": "Todo deleted"}
