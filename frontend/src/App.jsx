import { useEffect, useState } from "react";

const API = "/api/todos";

export default function App() {
  const [todos, setTodos] = useState([]);
  const [title, setTitle] = useState("");
  const [filter, setFilter] = useState("all");
  const [loading, setLoading] = useState(true);

  async function loadTodos() {
    try {
      const response = await fetch(API);
      setTodos(await response.json());
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadTodos();
  }, []);

  async function addTodo(event) {
    event.preventDefault();
    if (!title.trim()) return;

    const response = await fetch(API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title })
    });

    const todo = await response.json();
    setTodos(current => [todo, ...current]);
    setTitle("");
  }

  async function toggleTodo(todo) {
    const response = await fetch(`${API}/${todo.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ completed: !todo.completed })
    });

    const updated = await response.json();

    setTodos(current =>
      current.map(item => item.id === updated.id ? updated : item)
    );
  }

  async function deleteTodo(id) {
    await fetch(`${API}/${id}`, { method: "DELETE" });
    setTodos(current => current.filter(todo => todo.id !== id));
  }

  const filteredTodos = todos.filter(todo => {
    if (filter === "active") return !todo.completed;
    if (filter === "completed") return todo.completed;
    return true;
  });

  return (
    <main className="container">
      <h1>Todo App</h1>

      <form onSubmit={addTodo} className="add-form">
        <input
          value={title}
          onChange={event => setTitle(event.target.value)}
          placeholder="What do you need to do?"
        />
        <button type="submit">Add</button>
      </form>

      <div className="filters">
        {["all", "active", "completed"].map(value => (
          <button
            key={value}
            className={filter === value ? "selected" : ""}
            onClick={() => setFilter(value)}
          >
            {value[0].toUpperCase() + value.slice(1)}
          </button>
        ))}
      </div>

      {loading ? (
        <p>Loading...</p>
      ) : filteredTodos.length === 0 ? (
        <p className="empty">No todos found.</p>
      ) : (
        <ul>
          {filteredTodos.map(todo => (
            <li key={todo.id} className={todo.completed ? "completed" : ""}>
              <label>
                <input
                  type="checkbox"
                  checked={todo.completed}
                  onChange={() => toggleTodo(todo)}
                />
                <span>{todo.title}</span>
              </label>

              <button
                className="delete"
                onClick={() => deleteTodo(todo.id)}
              >
                Delete
              </button>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
