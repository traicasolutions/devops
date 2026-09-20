# Simple Todo DevOps Practice App

Minimal 3-tier Todo application for practicing Docker and Kubernetes.

Stack:
- Frontend: React + Vite + Nginx
- Backend: Python + FastAPI
- Database: PostgreSQL

Features:
- Create Todo
- View Todos
- Mark complete/incomplete
- Delete Todo
- Filter All / Active / Completed
- Health endpoint

Run everything:

    docker compose up --build

Open http://localhost:8080

Backend health: http://localhost:3000/health

API:
GET    /api/todos
POST   /api/todos
PUT    /api/todos/{id}
DELETE /api/todos/{id}
GET    /health
