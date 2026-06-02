from typing import List, Dict, Any
from datetime import datetime, timedelta
from collections import Counter
from todo.models import Task

class Analytics:
    @staticmethod
    def get_summary(tasks: List[Task]) -> Dict[str, Any]:
        """Calculates high-level statistics and returns a summary dict."""
        total = len(tasks)
        if total == 0:
            return {
                "total": 0,
                "completed": 0,
                "pending": 0,
                "in_progress": 0,
                "overdue": 0,
                "completion_rate": 0.0,
                "productivity_score": 0,
                "priority_dist": {"High": 0, "Medium": 0, "Low": 0},
                "category_dist": {}
            }

        completed = sum(1 for t in tasks if t.status == "Completed")
        pending = sum(1 for t in tasks if t.status == "Pending")
        in_progress = sum(1 for t in tasks if t.status == "In Progress")
        overdue = sum(1 for t in tasks if t.is_overdue)

        completion_rate = (completed / total) * 100

        # Productivity Score formula:
        # Completion rate penalized by the percentage of overdue tasks
        overdue_penalty = (overdue / total) * 50 if total > 0 else 0
        in_progress_bonus = (in_progress / total) * 10 if total > 0 else 0
        productivity_score = max(0, min(100, int(completion_rate - overdue_penalty + in_progress_bonus)))

        # Priority Distribution
        priority_dist = Counter(t.priority for t in tasks)
        # Ensure all keys exist
        for p in ["High", "Medium", "Low"]:
            if p not in priority_dist:
                priority_dist[p] = 0

        # Category Distribution
        category_dist = Counter(t.category for t in tasks)

        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "in_progress": in_progress,
            "overdue": overdue,
            "completion_rate": round(completion_rate, 1),
            "productivity_score": productivity_score,
            "priority_dist": dict(priority_dist),
            "category_dist": dict(category_dist)
        }

    @staticmethod
    def get_weekly_progress(tasks: List[Task]) -> Dict[str, int]:
        """Calculates completed task counts for each of the last 7 days."""
        today = datetime.now().date()
        last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
        
        # Initialize day counts
        progress = {day.strftime("%a"): 0 for day in last_7_days}

        for t in tasks:
            if t.status == "Completed" and t.completed_at:
                try:
                    comp_date = datetime.fromisoformat(t.completed_at).date()
                    if comp_date in last_7_days:
                        day_name = comp_date.strftime("%a")
                        progress[day_name] += 1
                except ValueError:
                    continue

        return progress
