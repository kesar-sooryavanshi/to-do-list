from datetime import datetime
import uuid

class Task:
    def __init__(
        self,
        title: str,
        description: str = "",
        priority: str = "Medium",
        category: str = "Personal",
        due_date: str = None,
        status: str = "Pending",
        id: str = None,
        created_at: str = None,
        completed_at: str = None
    ):
        self.id = id if id else str(uuid.uuid4())[:8]  # Shorter UUID for cleaner CLI display
        self.title = title
        self.description = description
        self.priority = priority if priority in ["High", "Medium", "Low"] else "Medium"
        self.category = category
        self.due_date = due_date  # YYYY-MM-DD format
        self.status = status if status in ["Pending", "In Progress", "Completed"] else "Pending"
        self.created_at = created_at if created_at else datetime.now().isoformat()
        self.completed_at = completed_at

    def mark_completed(self):
        self.status = "Completed"
        self.completed_at = datetime.now().isoformat()

    def mark_in_progress(self):
        self.status = "In Progress"
        self.completed_at = None

    def mark_pending(self):
        self.status = "Pending"
        self.completed_at = None

    @property
    def is_overdue(self) -> bool:
        if self.status == "Completed" or not self.due_date:
            return False
        try:
            due = datetime.strptime(self.due_date, "%Y-%m-%d").date()
            return due < datetime.now().date()
        except ValueError:
            return False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "category": self.category,
            "due_date": self.due_date,
            "status": self.status,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        return cls(
            title=data.get("title", "Untitled Task"),
            description=data.get("description", ""),
            priority=data.get("priority", "Medium"),
            category=data.get("category", "Personal"),
            due_date=data.get("due_date"),
            status=data.get("status", "Pending"),
            id=data.get("id"),
            created_at=data.get("created_at"),
            completed_at=data.get("completed_at"),
        )
