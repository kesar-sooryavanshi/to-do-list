import json
import csv
import os
from typing import List
from todo.models import Task

class Storage:
    def __init__(self, filepath: str):
        self.filepath = filepath

    def load_tasks(self) -> List[Task]:
        """Loads tasks from the persistent JSON file."""
        if not os.path.exists(self.filepath):
            return []
        
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [Task.from_dict(item) for item in data]
        except (json.JSONDecodeError, KeyError, PermissionError) as e:
            # Return empty but logs could be added.
            # In a production app, we would make a backup and reset
            backup_path = f"{self.filepath}.bak"
            try:
                if os.path.exists(self.filepath):
                    os.rename(self.filepath, backup_path)
            except Exception:
                pass
            return []

    def save_tasks(self, tasks: List[Task]) -> bool:
        """Saves tasks to the persistent JSON file."""
        try:
            # Ensure directories are created
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            data = [task.to_dict() for task in tasks]
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except (PermissionError, TypeError) as e:
            return False

    def export_to_csv(self, tasks: List[Task], csv_filepath: str) -> bool:
        """Exports the tasks to a CSV file."""
        try:
            with open(csv_filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                # Header row
                writer.writerow([
                    "ID", "Title", "Description", "Priority", 
                    "Category", "Due Date", "Status", "Created At", "Completed At"
                ])
                for task in tasks:
                    writer.writerow([
                        task.id,
                        task.title,
                        task.description,
                        task.priority,
                        task.category,
                        task.due_date if task.due_date else "",
                        task.status,
                        task.created_at,
                        task.completed_at if task.completed_at else ""
                    ])
            return True
        except (PermissionError, IOError):
            return False

    def import_from_csv(self, csv_filepath: str) -> List[Task]:
        """Imports tasks from a CSV file. Returns list of imported Task objects."""
        imported_tasks = []
        if not os.path.exists(csv_filepath):
            raise FileNotFoundError("CSV file not found.")

        try:
            with open(csv_filepath, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                if not header:
                    return []
                
                # Check minimum headers
                for row in reader:
                    if len(row) < 7:
                        continue
                    task = Task(
                        id=row[0] if row[0] else None,
                        title=row[1],
                        description=row[2],
                        priority=row[3] if row[3] else "Medium",
                        category=row[4] if row[4] else "Personal",
                        due_date=row[5] if row[5] else None,
                        status=row[6] if row[6] else "Pending",
                        created_at=row[7] if len(row) > 7 and row[7] else None,
                        completed_at=row[8] if len(row) > 8 and row[8] else None
                    )
                    imported_tasks.append(task)
            return imported_tasks
        except (csv.Error, PermissionError, IOError) as e:
            raise IOError(f"Failed to read CSV file: {str(e)}")
