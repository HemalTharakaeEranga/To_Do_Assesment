// Same origin: backend serves API + static
const API_BASE = ""; // so we call "/tasks"

// --- Toast / Notification helper -----------------------
function getToastContainer() {
  let container = document.getElementById("toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    container.className = "toast-container";
    document.body.appendChild(container);
  }
  return container;
}

function showToast(message, type = "success") {
  const container = getToastContainer();
  const toast = document.createElement("div");
  toast.className =
    "toast " + (type === "error" ? "toast-error" : "toast-success");

  const icon = document.createElement("span");
  icon.className = "toast-icon";
  icon.textContent = type === "error" ? "⚠️" : "✅";

  const text = document.createElement("span");
  text.textContent = message;

  toast.appendChild(icon);
  toast.appendChild(text);
  container.appendChild(toast);

  // Remove after animation (~3s)
  setTimeout(() => {
    toast.remove();
  }, 3000);
}

// --- Load tasks ----------------------------------------
async function fetchTasks() {
  try {
    const r = await fetch(`${API_BASE}/tasks?limit=5`);
    if (!r.ok) throw new Error("Failed to fetch tasks");
    const data = await r.json();
    renderTasks(data);
  } catch (err) {
    console.error(err);
    document.getElementById("tasks").innerHTML =
      '<p class="muted">Could not load tasks</p>';
    showToast("Failed to load tasks", "error");
  }
}

function renderTasks(tasks) {
  const root = document.getElementById("tasks");
  root.innerHTML = "";
  if (!tasks || tasks.length === 0) {
    root.innerHTML = `
      <div class="task-card empty-card">
          <div class="task-meta">
              <div class="task-title empty-title">No pending tasks</div>
              <div class="task-desc empty-desc">Add a new task on the left</div>
          </div>
      </div>
    `;
  }

  tasks.forEach((t, index) => {
    const card = document.createElement("div");
    const colorIndex = (index % 5) + 1; // 1..5
    card.className = `task-card color-${colorIndex}`;

    const meta = document.createElement("div");
    meta.className = "task-meta";

    const title = document.createElement("div");
    title.className = "task-title";
    title.textContent = t.title;

    const desc = document.createElement("div");
    desc.className = "task-desc";
    desc.textContent = t.description || "";

    meta.appendChild(title);
    meta.appendChild(desc);

    const actions = document.createElement("div");
    actions.className = "task-actions";

    const doneBtn = document.createElement("button");
    doneBtn.className = "done-btn";
    doneBtn.textContent = "Done";

    doneBtn.onclick = async () => {
      doneBtn.disabled = true;
      try {
        const res = await fetch(`${API_BASE}/tasks/${t.id}/complete`, {
          method: "PATCH",
        });
        if (!res.ok) throw new Error("Failed to mark done");
        showToast("Task marked as done", "success");
        fetchTasks();
      } catch (err) {
        console.error(err);
        doneBtn.disabled = false;
        showToast("Failed to mark task as done", "error");
      }
    };

    actions.appendChild(doneBtn);
    card.appendChild(meta);
    card.appendChild(actions);

    root.appendChild(card);
  });
}

// --- Form submit ----------------------------------------
document.getElementById("taskForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const title = document.getElementById("title").value.trim();
  const description = document.getElementById("description").value.trim();
  if (!title) {
    alert("Title required");
    return;
  }

  try {
    const r = await fetch(`${API_BASE}/tasks`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, description }),
    });
    if (!r.ok) throw new Error("Failed to create task");
    document.getElementById("title").value = "";
    document.getElementById("description").value = "";
    showToast("Task added successfully", "success");
    fetchTasks();
  } catch (err) {
    console.error(err);
    showToast("Could not create task", "error");
  }
});

// --- Init -----------------------------------------------
fetchTasks();
