/**
 * Kronos Premium Task Manager Web UI Logic
 * Handles interactive state, filters, circular rating widgets, and mock weekly charts.
 */

// ==========================================
// 1. STATE & STORAGE MANAGEMENT
// ==========================================

class TaskState {
    constructor() {
        this.tasks = this.loadTasks();
        if (this.tasks.length === 0) {
            this.generateMockTasks();
        }
    }

    loadTasks() {
        try {
            return JSON.parse(localStorage.getItem('kronos_tasks')) || [];
        } catch {
            return [];
        }
    }

    saveTasks() {
        localStorage.setItem('kronos_tasks', JSON.stringify(this.tasks));
    }

    addTask(title, description, priority, category, dueDate) {
        const newTask = {
            id: Math.random().toString(36).substring(2, 10).toUpperCase(),
            title,
            description,
            priority,
            category,
            due_date: dueDate || null,
            status: "Pending",
            created_at: new Date().toISOString(),
            completed_at: null
        };
        this.tasks.push(newTask);
        this.saveTasks();
        return newTask;
    }

    editTask(id, updates) {
        const task = this.tasks.find(t => t.id === id);
        if (!task) return false;

        Object.assign(task, updates);
        
        if (updates.status === "Completed") {
            task.completed_at = new Date().toISOString();
        } else if (updates.status && updates.status !== "Completed") {
            task.completed_at = null;
        }

        this.saveTasks();
        return true;
    }

    deleteTask(id) {
        const index = this.tasks.findIndex(t => t.id === id);
        if (index === -1) return false;
        this.tasks.splice(index, 1);
        this.saveTasks();
        return true;
    }

    completeTask(id) {
        const task = this.tasks.find(t => t.id === id);
        if (!task) return false;
        task.status = "Completed";
        task.completed_at = new Date().toISOString();
        this.saveTasks();
        return true;
    }

    // Populate mock tasks if database is empty to show beautiful analytics instantly
    generateMockTasks() {
        const today = new Date();
        const getPastDateStr = (daysAgo) => {
            const d = new Date();
            d.setDate(today.getDate() - daysAgo);
            return d.toISOString().split('T')[0];
        };

        const getPastIso = (daysAgo) => {
            const d = new Date();
            d.setDate(today.getDate() - daysAgo);
            return d.toISOString();
        };

        this.tasks = [
            {
                id: "KRN-821A",
                title: "Refactor database storage schemas",
                description: "Clean up nested structures for the persistent task files.",
                priority: "High",
                category: "Work",
                due_date: getPastDateStr(2),
                status: "Completed",
                created_at: getPastIso(5),
                completed_at: getPastIso(2)
            },
            {
                id: "KRN-120C",
                title: "Prepare financial forecast for Q3",
                description: "Review balance sheet and project custom revenues.",
                priority: "High",
                category: "Finance",
                due_date: getPastDateStr(1),
                status: "Pending",
                created_at: getPastIso(4),
                completed_at: null
            },
            {
                id: "KRN-394E",
                title: "Workout: HIIT & Core training",
                description: "Complete the weekly endurance training session.",
                priority: "Low",
                category: "Health",
                due_date: getPastDateStr(0),
                status: "Completed",
                created_at: getPastIso(1),
                completed_at: getPastIso(0)
            },
            {
                id: "KRN-549B",
                title: "Complete Python OOP research module",
                description: "Examine advanced decorator classes and magic methods.",
                priority: "Medium",
                category: "Study",
                due_date: getPastDateStr(3),
                status: "Completed",
                created_at: getPastIso(6),
                completed_at: getPastIso(3)
            },
            {
                id: "KRN-730D",
                title: "Finalize glassmorphism styling tokens",
                description: "Iterate color values and translucent overlay blur factors.",
                priority: "Medium",
                category: "Work",
                due_date: getPastDateStr(-3), // Future date
                status: "In Progress",
                created_at: getPastIso(1),
                completed_at: null
            },
            {
                id: "KRN-205F",
                title: "Renew cloud domain certificates",
                description: "Check secure connection parameters on remote host.",
                priority: "High",
                category: "Work",
                due_date: getPastDateStr(4),
                status: "Completed",
                created_at: getPastIso(6),
                completed_at: getPastIso(4)
            }
        ];
        this.saveTasks();
    }
}

// ==========================================
// 2. UI RENDERER & INTERACTIVE OPERATIONS
// ==========================================

class UIController {
    constructor(state) {
        this.state = state;
        
        // Cache DOM elements
        this.taskListBody = document.getElementById('task-list-body');
        this.emptyState = document.getElementById('empty-state');
        this.taskModal = document.getElementById('task-modal');
        this.taskForm = document.getElementById('task-form');
        this.customCatGroup = document.getElementById('custom-cat-group');
        
        // Form inputs
        this.taskIdInput = document.getElementById('task-id');
        this.taskTitleInput = document.getElementById('task-title');
        this.taskDescInput = document.getElementById('task-desc');
        this.taskPriorityInput = document.getElementById('task-priority');
        this.taskCategoryInput = document.getElementById('task-category');
        this.taskCustomCatInput = document.getElementById('task-custom-cat');
        this.taskDueInput = document.getElementById('task-due');
        this.modalTitle = document.getElementById('modal-title');
        
        // Filters & Search
        this.searchInput = document.getElementById('search-input');
        this.filterStatus = document.getElementById('filter-status');
        this.filterPriority = document.getElementById('filter-priority');

        this.initEventListeners();
        this.renderDashboard();
    }

    initEventListeners() {
        // Modal toggling
        document.getElementById('btn-open-add').addEventListener('click', () => this.openModal());
        document.getElementById('btn-close-modal').addEventListener('click', () => this.closeModal());
        document.getElementById('btn-cancel-modal').addEventListener('click', () => this.closeModal());
        
        // Custom Category Toggle
        this.taskCategoryInput.addEventListener('change', (e) => {
            if (e.target.value === "Custom") {
                this.customCatGroup.style.display = "flex";
            } else {
                this.customCatGroup.style.display = "none";
            }
        });

        // Form submit
        this.taskForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleFormSubmit();
        });

        // Search & Filter change
        this.searchInput.addEventListener('input', () => this.renderDashboard());
        this.filterStatus.addEventListener('change', () => this.renderDashboard());
        this.filterPriority.addEventListener('change', () => this.renderDashboard());

        // Modal overlay click closing
        this.taskModal.addEventListener('click', (e) => {
            if (e.target === this.taskModal) this.closeModal();
        });
    }

    openModal(task = null) {
        this.taskForm.reset();
        this.customCatGroup.style.display = "none";
        
        if (task) {
            this.modalTitle.innerText = "Edit Task Parameters";
            this.taskIdInput.value = task.id;
            this.taskTitleInput.value = task.title;
            this.taskDescInput.value = task.description;
            this.taskPriorityInput.value = task.priority;
            
            const isDefaultCat = ["Personal", "Work", "Study", "Health", "Finance"].includes(task.category);
            if (isDefaultCat) {
                this.taskCategoryInput.value = task.category;
            } else {
                this.taskCategoryInput.value = "Custom";
                this.taskCustomCatInput.value = task.category;
                this.customCatGroup.style.display = "flex";
            }
            this.taskDueInput.value = task.due_date || "";
        } else {
            this.modalTitle.innerText = "New Task Details";
            this.taskIdInput.value = "";
        }
        
        this.taskModal.classList.add('active');
        this.taskModal.setAttribute('aria-hidden', 'false');
    }

    closeModal() {
        this.taskModal.classList.remove('active');
        this.taskModal.setAttribute('aria-hidden', 'true');
    }

    handleFormSubmit() {
        const id = this.taskIdInput.value;
        const title = this.taskTitleInput.value.strip ? this.taskTitleInput.value.strip() : this.taskTitleInput.value;
        const desc = this.taskDescInput.value;
        const priority = this.taskPriorityInput.value;
        const categoryVal = this.taskCategoryInput.value;
        const category = categoryVal === "Custom" ? this.taskCustomCatInput.value || "Custom" : categoryVal;
        const dueDate = this.taskDueInput.value || null;

        if (id) {
            this.state.editTask(id, { title, description: desc, priority, category, due_date: dueDate });
        } else {
            this.state.addTask(title, desc, priority, category, dueDate);
        }

        this.closeModal();
        this.renderDashboard();
    }

    // ==========================================
    // 3. GRAPHICS & DASHBOARD CALCULATIONS
    // ==========================================

    renderDashboard() {
        const tasks = this.state.tasks;
        const searchQuery = this.searchInput.value.toLowerCase().trim();
        const statusFilter = this.filterStatus.value;
        const priorityFilter = this.filterPriority.value;

        // 1. Calculate Analytics
        const total = tasks.length;
        const completed = tasks.filter(t => t.status === "Completed").length;
        const pending = tasks.filter(t => t.status === "Pending").length;
        const inProgress = tasks.filter(t => t.status === "In Progress").length;
        
        // Calculate Overdue tasks
        const todayStr = new Date().toISOString().split('T')[0];
        const overdue = tasks.filter(t => {
            if (t.status === "Completed" || !t.due_date) return false;
            return t.due_date < todayStr;
        }).length;

        const rate = total > 0 ? Math.round((completed / total) * 100) : 0;
        
        // Productivity score: rate penalized by overdue factor
        const overduePenalty = total > 0 ? (overdue / total) * 50 : 0;
        const progressBonus = total > 0 ? (inProgress / total) * 10 : 0;
        const score = Math.max(0, Math.min(100, Math.round(rate - overduePenalty + progressBonus)));

        // Update stats widgets
        document.getElementById('stat-total').innerText = total;
        document.getElementById('stat-completed').innerText = completed;
        document.getElementById('stat-rate').innerText = `${rate}%`;
        document.getElementById('stat-pending').innerText = pending;
        document.getElementById('stat-in-progress').innerText = inProgress;
        document.getElementById('stat-overdue').innerText = overdue;

        // Circular progress SVG animation
        const circle = document.querySelector('.circle-progress');
        if (circle) {
            // Circumference of r=40 is 2 * pi * 40 ≈ 251.2
            const strokeOffset = 251.2 - (251.2 * score) / 100;
            circle.style.strokeDashoffset = strokeOffset;
        }
        document.getElementById('prod-score-value').innerText = `${score}%`;

        // Render Weekly Chart
        this.renderWeeklyChart();

        // 2. Filter tasks for list view
        const filteredTasks = tasks.filter(t => {
            const matchesSearch = t.title.toLowerCase().includes(searchQuery) || 
                                  t.description.toLowerCase().includes(searchQuery) ||
                                  t.category.toLowerCase().includes(searchQuery);
            const matchesStatus = statusFilter === "all" || t.status === statusFilter;
            const matchesPriority = priorityFilter === "all" || t.priority === priorityFilter;
            return matchesSearch && matchesStatus && matchesPriority;
        });

        // 3. Render list table
        this.taskListBody.innerHTML = '';
        if (filteredTasks.length === 0) {
            this.emptyState.style.display = 'block';
        } else {
            this.emptyState.style.display = 'none';
            filteredTasks.forEach(task => {
                const tr = document.createElement('tr');
                tr.dataset.id = task.id;
                
                // Status badge
                let statusBadge = '';
                if (task.status === "Completed") {
                    statusBadge = `<span class="badge-status completed"><i class="fas fa-check-circle"></i> Completed</span>`;
                } else if (task.status === "In Progress") {
                    statusBadge = `<span class="badge-status in-progress"><i class="fas fa-spinner fa-spin"></i> In Progress</span>`;
                } else {
                    statusBadge = `<span class="badge-status pending"><i class="far fa-circle"></i> Pending</span>`;
                }

                // Priority color styles
                const pClass = task.priority.toLowerCase();

                // Due date warning formatting
                let dueHtml = '-';
                if (task.due_date) {
                    let dueClass = 'upcoming';
                    let warningSign = '';
                    if (task.status !== 'Completed') {
                        if (task.due_date < todayStr) {
                            dueClass = 'overdue';
                            warningSign = ' ⚠';
                        } else if (task.due_date === todayStr) {
                            dueClass = 'today';
                            warningSign = ' 🕒';
                        }
                    }
                    dueHtml = `<span class="due-date ${dueClass}">${task.due_date}${warningSign}</span>`;
                }

                const titleClass = task.status === "Completed" ? "task-title-cell completed" : "task-title-cell";

                tr.innerHTML = `
                    <td class="task-id">${task.id}</td>
                    <td>${statusBadge}</td>
                    <td class="${titleClass}">
                        <div class="task-title-text">${task.title}</div>
                        <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 3px;">${task.description || ''}</div>
                    </td>
                    <td><span class="badge-cat">${task.category}</span></td>
                    <td><span class="badge-priority ${pClass}">${task.priority}</span></td>
                    <td>${dueHtml}</td>
                    <td>
                        <div class="row-actions">
                            ${task.status !== 'Completed' ? `
                            <button class="action-icon complete" title="Complete Task" onclick="appUI.handleTaskComplete('${task.id}')">
                                <i class="fas fa-check"></i>
                            </button>` : ''}
                            <button class="action-icon" title="Edit Task" onclick="appUI.handleTaskEdit('${task.id}')">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="action-icon delete" title="Delete Task" onclick="appUI.handleTaskDelete('${task.id}')">
                                <i class="fas fa-trash-alt"></i>
                            </button>
                        </div>
                    </td>
                `;
                this.taskListBody.appendChild(tr);
            });
        }
    }

    renderWeeklyChart() {
        const chart = document.getElementById('weekly-chart');
        chart.innerHTML = '';

        const today = new Date();
        const days = [];
        for (let i = 6; i >= 0; i--) {
            const d = new Date();
            d.setDate(today.getDate() - i);
            days.push({
                name: d.toLocaleDateString('en-US', { weekday: 'short' }),
                dateStr: d.toISOString().split('T')[0],
                count: 0
            });
        }

        // Calculate counts
        this.state.tasks.forEach(task => {
            if (task.status === "Completed" && task.completed_at) {
                const dateStr = task.completed_at.split('T')[0];
                const dayMatch = days.find(day => day.dateStr === dateStr);
                if (dayMatch) {
                    dayMatch.count++;
                }
            }
        });

        const maxCount = Math.max(...days.map(d => d.count), 1);

        days.forEach(day => {
            const pct = (day.count / maxCount) * 100;
            const container = document.createElement('div');
            container.className = 'chart-bar-container';
            container.innerHTML = `
                <div class="chart-bar-wrap" title="${day.count} completed on ${day.name}">
                    <div class="chart-bar" style="height: ${pct}%"></div>
                </div>
                <span class="chart-day">${day.name}</span>
            `;
            chart.appendChild(container);
        });
    }

    handleTaskComplete(id) {
        this.state.completeTask(id);
        this.renderDashboard();
    }

    handleTaskEdit(id) {
        const task = this.state.tasks.find(t => t.id === id);
        if (task) {
            this.openModal(task);
        }
    }

    handleTaskDelete(id) {
        if (confirm("Are you sure you want to remove this task?")) {
            this.state.deleteTask(id);
            this.renderDashboard();
        }
    }
}

// Instantiate App
document.addEventListener('DOMContentLoaded', () => {
    window.appState = new TaskState();
    window.appUI = new UIController(window.appState);
});
