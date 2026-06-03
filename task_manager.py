from typing import List, Dict, Any, Optional
from datetime import datetime
from todo.models import Task
from todo.storage import Storage

class TaskManager:
    def __init__(self, storage: Storage):
        self.storage = storage
        self.tasks: List[Task] = self.storage.load_tasks()

    def add_task(self, title: str, description: str = "", priority: str = "Medium", 
                 category: str = "Personal", due_date: str = None) -> Task:
        """Creates and adds a new task."""
        new_task = Task(
            title=title,
            description=description,
            priority=priority,
            category=category,
            due_date=due_date
        )
        self.tasks.append(new_task)
        self.storage.save_tasks(self.tasks)
        return new_task

    def get_task(self, task_id: str) -> Optional[Task]:
        """Gets a task by its ID (either exact match or short prefix)."""
        for t in self.tasks:
            if t.id == task_id or t.id.startswith(task_id):
                return t
        return None

    def edit_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """Edits an existing task's fields."""
        task = self.get_task(task_id)
        if not task:
            return False
        
        # Valid fields to update
        valid_fields = ["title", "description", "priority", "category", "due_date", "status"]
        for key, val in updates.items():
            if key in valid_fields:
                if key == "status":
                    if val == "Completed":
                        task.mark_completed()
                    elif val == "In Progress":
                        task.mark_in_progress()
                    elif val == "Pending":
                        task.mark_pending()
                elif key == "priority" and val not in ["High", "Medium", "Low"]:
                    continue
                else:
                    setattr(task, key, val)
        
        self.storage.save_tasks(self.tasks)
        return True

    def delete_task(self, task_id: str) -> bool:
        """Deletes a task by ID."""
        task = self.get_task(task_id)
        if not task:
            return False
        self.tasks.remove(task)
        self.storage.save_tasks(self.tasks)
        return True

    def complete_task(self, task_id: str) -> bool:
        """Marks a task as completed."""
        task = self.get_task(task_id)
        if not task:
            return False
        task.mark_completed()
        self.storage.save_tasks(self.tasks)
        return True

    def search_tasks(self, query: str) -> List[Task]:
        """Search tasks by title or description (case-insensitive)."""
        if not query:
            return self.tasks
        
        q = query.lower()
        results = []
        for t in self.tasks:
            if q in t.title.lower() or q in t.description.lower() or q in t.category.lower():
                results.append(t)
        return results

    def get_filtered_and_sorted_tasks(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None,
        sort_by: Optional[str] = "created_at",
        reverse: bool = False
    ) -> List[Task]:
        """Filters and sorts tasks."""
        filtered = self.tasks
        
        # Apply filtering
        if status:
            filtered = [t for t in filtered if t.status.lower() == status.lower()]
        if priority:
            filtered = [t for t in filtered if t.priority.lower() == priority.lower()]
        if category:
            filtered = [t for t in filtered if t.category.lower() == category.lower()]
            
        # Apply sorting
        def sort_key(task: Task):
            if sort_by == "due_date":
                # Put None due dates at the end
                if not task.due_date:
                    return "9999-12-31"
                return task.due_date
            elif sort_by == "priority":
                # High = 0, Medium = 1, Low = 2 (so High shows on top)
                p_map = {"High": 0, "Medium": 1, "Low": 2}
                return p_map.get(task.priority, 3)
            elif sort_by == "status":
                s_map = {"In Progress": 0, "Pending": 1, "Completed": 2}
                return s_map.get(task.status, 3)
            else:  # Default to created_at
                return task.created_at

        return sorted(filtered, key=sort_key, reverse=reverse)

    def import_tasks_from_csv(self, csv_filepath: str) -> int:
        """Imports tasks from CSV file and saves them. Returns count of imported tasks."""
        imported = self.storage.import_from_csv(csv_filepath)
        # Ensure we don't duplicate IDs or cause collisions
        existing_ids = {t.id for t in self.tasks}
        count = 0
        for task in imported:
            # If ID collides, let's keep it but generate a new ID if it's already there
            if task.id in existing_ids:
                import uuid
                task.id = str(uuid.uuid4())[:8]
            self.tasks.append(task)
            existing_ids.add(task.id)
            count += 1
            
        if count > 0:
            self.storage.save_tasks(self.tasks)
        return count

    def export_tasks_to_csv(self, csv_filepath: str) -> bool:
        """Exports all current tasks to CSV."""
        return self.storage.export_to_csv(self.tasks, csv_filepath)
