const state = {
    todos: [],
    filter: 'all'
};

const api = {
    async request(endpoint, options = {}) {
        const response = await fetch(`/api/todos${endpoint}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });

        if (response.status === 204) return null;

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || 'An unexpected error occurred');
        }
        return data;
    }
};

async function loadTodos() {
    try {
        state.todos = await api.request(`/?status=${state.filter}`);
        render();
    } catch (e) {
        showError(e.message);
    }
}

async function addTodo(title) {
    try {
        const newTodo = await api.request('/', {
            method: 'POST',
            body: JSON.stringify({ title })
        });
        state.todos.push(newTodo);
        render();
    } catch (e) {
        showError(e.message);
    }
}

async function toggleTodo(id, completed) {
    try {
        await api.request(`/${id}`, {
            method: 'PATCH',
            body: JSON.stringify({ completed })
        });
        const todo = state.todos.find(t => t.id === id);
        if (todo) todo.completed = completed;
        render();
    } catch (e) {
        showError(e.message);
    }
}

async function editTodo(id, title) {
    try {
        await api.request(`/${id}`, {
            method: 'PATCH',
            body: JSON.stringify({ title })
        });
        const todo = state.todos.find(t => t.id === id);
        if (todo) todo.title = title;
        render();
    } catch (e) {
        showError(e.message);
    }
}

async function deleteTodo(id) {
    if (!confirm('Are you sure you want to delete this task?')) return;
    try {
        await api.request(`/${id}`, {
            method: 'DELETE'
        });
        state.todos = state.todos.filter(t => t.id !== id);
        render();
    } catch (e) {
        showError(e.message);
    }
}

async function clearCompleted() {
    try {
        await api.request('/completed', {
            method: 'DELETE'
        });
        state.todos = state.todos.filter(t => !t.completed);
        render();
    } catch (e) {
        showError(e.message);
    }
}

function showError(message) {
    const box = document.getElementById('error-box');
    box.textContent = message;
    box.classList.remove('d-none');
    setTimeout(() => box.classList.add('d-none'), 4000);
}

function render() {
    const list = document.getElementById('todo-list');
    const count = document.getElementById('remaining-count');
    const clearBtn = document.getElementById('clear-completed');
    
    list.innerHTML = '';
    
    if (state.todos.length === 0) {
        list.innerHTML = '<li class="list-group-item text-center text-muted">No tasks found</li>';
    } else {
        state.todos.forEach(todo => {
            const li = document.createElement('li');
            li.className = 'list-group-item d-flex align-items-center gap-3';
            
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.className = 'form-check-input';
            checkbox.checked = todo.completed;
            checkbox.dataset.id = todo.id;
            checkbox.addEventListener('change', (e) => toggleTodo(todo.id, e.target.checked));
            
            const titleSpan = document.createElement('span');
            titleSpan.className = `flex-grow-1 ${todo.completed ? 'text-decoration-line-through text-muted' : ''}`;
            titleSpan.textContent = todo.title;
            
            const editBtn = document.createElement('button');
            editBtn.className = 'btn btn-sm btn-outline-secondary';
            editBtn.textContent = 'Edit';
            editBtn.onclick = () => {
                const input = document.createElement('input');
                input.className = 'form-control form-control-sm';
                input.value = todo.title;
                
                const save = async () => {
                    const newTitle = input.value.trim();
                    if (newTitle) {
                        await editTodo(todo.id, newTitle);
                    } else {
                        render();
                    }
                };
                
                input.onblur = save;
                input.onkeydown = (e) => {
                    if (e.key === 'Enter') save();
                    if (e.key === 'Escape') render();
                };
                
                titleSpan.replaceWith(input);
                input.focus();
            };
            
            const delBtn = document.createElement('button');
            delBtn.className = 'btn btn-sm btn-outline-danger';
            delBtn.textContent = 'Delete';
            delBtn.onclick = () => deleteTodo(todo.id);
            
            li.append(checkbox, titleSpan, editBtn, delBtn);
            list.append(li);
        });
    }
    
    const activeCount = state.todos.filter(t => !t.completed).length;
    count.textContent = `${activeCount} task${activeCount !== 1 ? 's' : ''} remaining`;
    
    const hasCompleted = state.todos.some(t => t.completed);
    clearBtn.classList.toggle('d-none', !hasCompleted);
    
    // Filter buttons
    document.querySelectorAll('[data-filter]').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.filter === state.filter);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    loadTodos();
    
    document.getElementById('todo-form').onsubmit = (e) => {
        e.preventDefault();
        const input = document.getElementById('todo-input');
        addTodo(input.value.trim());
        input.value = '';
    };
    
    document.querySelectorAll('[data-filter]').forEach(btn => {
        btn.onclick = () => {
            state.filter = btn.dataset.filter;
            loadTodos();
        };
    });
    
    document.getElementById('clear-completed').onclick = clearCompleted;
});
