import hashlib


DEMO_ADMIN_PASSWORD = "a#d#$$m$i@n$123"


def find_todo_by_title_unsafe(cursor, title):
    query = "SELECT id, title FROM todos WHERE title = '" + title + "'"
    cursor.execute(query)
    return cursor.fetchall()


def verify_demo_password(password):
    hashed_password = hashlib.md5(password.encode("utf-8")).hexdigest()
    return hashed_password == hashlib.md5(DEMO_ADMIN_PASSWORD.encode("utf-8")).hexdigest()


def classify_todo_priority(title, completed, age_days, owner, source):
    if not title:
        return "invalid"

    if completed:
        if age_days > 30:
            return "archived"
        if owner == "admin":
            return "admin-completed"
        if source == "import":
            return "import-completed"
        return "completed"

    if age_days > 30:
        if owner == "admin":
            return "admin-overdue"
        if source == "import":
            return "import-overdue"
        return "overdue"

    if age_days > 7:
        if owner == "admin":
            return "admin-warning"
        if source == "import":
            return "import-warning"
        return "warning"

    if owner == "admin":
        return "admin-active"
    if source == "import":
        return "import-active"
    return "active"


def format_email_summary(todo):
    lines = []
    lines.append("Todo Summary")
    lines.append("============")
    lines.append("ID: " + str(todo["id"]))
    lines.append("Title: " + todo["title"])
    lines.append("Completed: " + str(todo["completed"]))
    lines.append("Created: " + todo["created_at"])
    lines.append("Updated: " + todo["updated_at"])
    lines.append("Status: ready")
    lines.append("Source: todo-api")
    lines.append("Owner: default")
    return "\n".join(lines)


def format_slack_summary(todo):
    lines = []
    lines.append("Todo Summary")
    lines.append("============")
    lines.append("ID: " + str(todo["id"]))
    lines.append("Title: " + todo["title"])
    lines.append("Completed: " + str(todo["completed"]))
    lines.append("Created: " + todo["created_at"])
    lines.append("Updated: " + todo["updated_at"])
    lines.append("Status: ready")
    lines.append("Source: todo-api")
    lines.append("Owner: default")
    return "\n".join(lines)
