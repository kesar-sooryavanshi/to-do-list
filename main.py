import sys
import time
from rich.prompt import Prompt
from todo.config import DB_FILE, COLOR_PALETTE
from todo.storage import Storage
from todo.task_manager import TaskManager
from todo.analytics import Analytics
from todo.ui import CLI_UI

def main():
    # Initialize Core modules
    storage = Storage(DB_FILE)
    manager = TaskManager(storage)
    ui = CLI_UI()

    # App loop state
    filter_status = None
    filter_priority = None
    filter_category = None
    sort_by = "created_at"
    sort_reverse = False
    
    # Active search query
    search_query = None

    ui.clear_screen()
    ui.show_loading_animation("Booting KRONOS Engine...", duration=0.8)

    while True:
        try:
            ui.clear_screen()
            
            # 1. Render Logo/Header
            ui.console.print(ui.render_logo())
            ui.console.print()

            # 2. Render Analytics Dashboard
            summary = Analytics.get_summary(manager.tasks)
            weekly = Analytics.get_weekly_progress(manager.tasks)
            ui.console.print(ui.render_analytics_dashboard(summary, weekly))
            ui.console.print()

            # 3. Fetch and Render Task List
            if search_query:
                # If we are in search mode, display search results
                display_tasks = manager.search_tasks(search_query)
                title_prefix = f"SEARCH RESULTS FOR '{search_query.upper()}'"
            else:
                # Normal mode: display filtered and sorted tasks
                display_tasks = manager.get_filtered_and_sorted_tasks(
                    status=filter_status,
                    priority=filter_priority,
                    category=filter_category,
                    sort_by=sort_by,
                    reverse=sort_reverse
                )
                
                # Create filter badge title
                filters = []
                if filter_status: filters.append(f"Status: {filter_status}")
                if filter_priority: filters.append(f"Priority: {filter_priority}")
                if filter_category: filters.append(f"Category: {filter_category}")
                filter_str = f" [dim]({', '.join(filters)})[/]" if filters else ""
                title_prefix = f"TASKS │ Sort: {sort_by}{filter_str}"

            ui.console.print(ui.render_tasks_table(display_tasks, title_prefix))
            ui.console.print()

            # 4. Render Menu
            ui.console.print(ui.render_menu())
            
            # 5. Prompt Action
            action = Prompt.ask(
                f"[bold {COLOR_PALETTE['gold']}]kronos[/] >",
                choices=["a", "e", "d", "c", "s", "f", "i", "o", "q"],
                default="q"
            ).lower().strip()

            # 6. Action Handlers
            if action == "q":
                ui.clear_screen()
                ui.console.print(f"[bold {COLOR_PALETTE['gold']}]✦ Thank you for using KRONOS. Have a productive day! ✦[/]")
                break
                
            elif action == "a":
                details = ui.prompt_task_input()
                if details:
                    title, description, priority, category, due_date = details
                    ui.show_loading_animation("Creating task...")
                    manager.add_task(
                        title=title,
                        description=description,
                        priority=priority,
                        category=category,
                        due_date=due_date
                    )
                    ui.show_message("Task created successfully!", type="success")
                    time.sleep(1.0)
                    search_query = None # Clear search to view new task
                    
            elif action == "e":
                task_id = Prompt.ask(f"[bold {COLOR_PALETTE['gold']}]Enter task ID to edit[/]").strip()
                task = manager.get_task(task_id)
                if not task:
                    ui.show_message(f"No task found with ID starting with '{task_id}'", type="error")
                    time.sleep(1.5)
                    continue
                
                details = ui.prompt_task_input(defaults=task)
                if details:
                    title, description, priority, category, due_date = details
                    # Ask if status should change
                    status_choices = ["Pending", "In Progress", "Completed"]
                    status = Prompt.ask("Set Status", choices=status_choices, default=task.status)
                    
                    ui.show_loading_animation("Updating task...")
                    updates = {
                        "title": title,
                        "description": description,
                        "priority": priority,
                        "category": category,
                        "due_date": due_date,
                        "status": status
                    }
                    manager.edit_task(task.id, updates)
                    ui.show_message("Task updated successfully!", type="success")
                    time.sleep(1.0)
                    
            elif action == "d":
                task_id = Prompt.ask(f"[bold {COLOR_PALETTE['gold']}]Enter task ID to delete[/]").strip()
                task = manager.get_task(task_id)
                if not task:
                    ui.show_message(f"No task found with ID starting with '{task_id}'", type="error")
                    time.sleep(1.5)
                    continue
                
                if ui.prompt_confirm(f"Are you sure you want to delete task '{task.title}'?"):
                    ui.show_loading_animation("Removing task...")
                    manager.delete_task(task.id)
                    ui.show_message("Task deleted successfully!", type="success")
                else:
                    ui.show_message("Deletion cancelled.", type="info")
                time.sleep(1.0)
                
            elif action == "c":
                task_id = Prompt.ask(f"[bold {COLOR_PALETTE['gold']}]Enter task ID to complete[/]").strip()
                task = manager.get_task(task_id)
                if not task:
                    ui.show_message(f"No task found with ID starting with '{task_id}'", type="error")
                    time.sleep(1.5)
                    continue
                
                ui.show_loading_animation("Completing task...")
                manager.complete_task(task.id)
                ui.show_message(f"Task '{task.title}' completed!", type="success")
                time.sleep(1.0)
                
            elif action == "s":
                search_query = Prompt.ask(f"[bold {COLOR_PALETTE['gold']}]Search query (leave empty to clear search)[/]").strip()
                if not search_query:
                    search_query = None
                    
            elif action == "f":
                filters = ui.prompt_filter_sort()
                filter_status = filters["status"]
                filter_priority = filters["priority"]
                filter_category = filters["category"]
                sort_by = filters["sort_by"]
                sort_reverse = filters["reverse"]
                ui.show_message("Filters and sorting updated!", type="success")
                time.sleep(1.0)
                
            elif action == "i":
                csv_path = Prompt.ask(f"[bold {COLOR_PALETTE['gold']}]Enter CSV file path to import[/]").strip()
                ui.show_loading_animation("Importing tasks from CSV...")
                try:
                    count = manager.import_tasks_from_csv(csv_path)
                    ui.show_message(f"Successfully imported {count} tasks!", type="success")
                except Exception as e:
                    ui.show_message(f"Failed to import: {str(e)}", type="error")
                Prompt.ask("\nPress [bold]Enter[/] to continue")
                
            elif action == "o":
                csv_path = Prompt.ask(f"[bold {COLOR_PALETTE['gold']}]Enter CSV file destination path[/]", default="tasks_export.csv").strip()
                ui.show_loading_animation("Exporting tasks to CSV...")
                if manager.export_tasks_to_csv(csv_path):
                    ui.show_message(f"Successfully exported tasks to {csv_path}!", type="success")
                else:
                    ui.show_message("Failed to export tasks.", type="error")
                time.sleep(1.5)

        except Exception as e:
            ui.show_message(f"An unexpected error occurred: {str(e)}", type="error")
            Prompt.ask("\nPress [bold]Enter[/] to recover and continue")

if __name__ == "__main__":
    main()
