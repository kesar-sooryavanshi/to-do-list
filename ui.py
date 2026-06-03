import os
import time
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
from colorama import init as colorama_init, Fore, Style
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.align import Align
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, BarColumn, TextColumn
from rich.status import Status
from rich.text import Text

from todo.config import COLOR_PALETTE, STYLES, CATEGORIES, PRIORITIES, STATUSES
from todo.models import Task
from todo.analytics import Analytics

# Initialize colorama
colorama_init(autoreset=True)

class CLI_UI:
    def __init__(self):
        # Setup rich console with custom highlights and force truecolor
        self.console = Console(color_system="truecolor")

    def clear_screen(self):
        """Clears the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def render_logo(self) -> Panel:
        """Renders the top branding panel."""
        logo_text = Text()
        logo_text.append("✦ ", style=f"bold {COLOR_PALETTE['gold']}")
        logo_text.append("KRONOS ", style=f"bold {COLOR_PALETTE['gold']}")
        logo_text.append("│ PREMIUM TASK MANAGER", style=f"bold {COLOR_PALETTE['text']}")
        logo_text.append("\nNotion & Todoist Inspired Command-line Tool", style=f"italic {COLOR_PALETTE['gray_light']}")
        
        return Panel(
            Align.center(logo_text),
            border_style=STYLES["border"],
            padding=(0, 2),
            style=f"on {COLOR_PALETTE['bg']}"
        )

    def render_analytics_dashboard(self, summary: Dict[str, Any], weekly: Dict[str, int]) -> Table:
        """Renders the top analytics cards using a grid."""
        grid = Table.grid(expand=True, padding=1)
        grid.add_column(ratio=1)
        grid.add_column(ratio=1)
        grid.add_column(ratio=1)
        grid.add_column(ratio=1.2)

        # Card 1: Productivity Score
        score = summary["productivity_score"]
        score_color = COLOR_PALETTE["green"] if score >= 70 else (COLOR_PALETTE["orange"] if score >= 40 else COLOR_PALETTE["red"])
        score_text = Text(f"{score}%", style=f"bold {score_color} size=18")
        score_bar = "█" * int(score / 10) + "░" * (10 - int(score / 10))
        score_panel = Panel(
            Align.center(Text.assemble(score_text, f"\n[{score_color}]{score_bar}[/]\nProductivity Rating")),
            title="[bold]Productivity[/]",
            border_style=COLOR_PALETTE["gold"]
        )

        # Card 2: Completion Stats
        comp_rate = summary["completion_rate"]
        comp_panel = Panel(
            Align.center(Text(
                f"Total: {summary['total']}\n"
                f"Done: [bold {COLOR_PALETTE['green']}]{summary['completed']}[/]\n"
                f"Rate: [bold {COLOR_PALETTE['gold']}]{comp_rate}%[/]", 
                style=f"{COLOR_PALETTE['text']}"
            )),
            title="[bold]Task Completion[/]",
            border_style=STYLES["border"]
        )

        # Card 3: Status Breakdowns
        status_panel = Panel(
            Align.center(Text(
                f"Pending: [bold {COLOR_PALETTE['gray_light']}]{summary['pending']}[/]\n"
                f"In Progress: [bold {COLOR_PALETTE['orange']}]{summary['in_progress']}[/]\n"
                f"Overdue: [bold {COLOR_PALETTE['red']}]{summary['overdue']}[/]",
                style=f"{COLOR_PALETTE['text']}"
            )),
            title="[bold]Statuses[/]",
            border_style=STYLES["border"]
        )

        # Card 4: Weekly Bar Chart
        chart_lines = []
        max_val = max(weekly.values()) if weekly.values() else 0
        for day, val in weekly.items():
            bar_len = int((val / max_val) * 8) if max_val > 0 else 0
            bar = "█" * bar_len
            chart_lines.append(f"{day}: [bold {COLOR_PALETTE['gold']}]{bar:<8}[/] {val}")
        
        weekly_panel = Panel(
            Text("\n".join(chart_lines), style="font_size=8"),
            title="[bold]7-Day Progress[/]",
            border_style=STYLES["border"]
        )

        grid.add_row(score_panel, comp_panel, status_panel, weekly_panel)
        return grid

    def render_tasks_table(self, tasks: List[Task], title_prefix: str = "ALL TASKS") -> Table:
        """Renders the tasks list inside a rich Table."""
        table = Table(
            title=f"[bold {COLOR_PALETTE['gold']}]{title_prefix}[/] ({len(tasks)} items)",
            border_style=STYLES["border"],
            expand=True,
            show_header=True
        )

        table.add_column("ID", style=f"bold {COLOR_PALETTE['gray_light']}", width=10, justify="center")
        table.add_column("Status", width=12)
        table.add_column("Title", style="bold")
        table.add_column("Category", width=12, justify="center")
        table.add_column("Priority", width=10, justify="center")
        table.add_column("Due Date", width=12, justify="center")

        for task in tasks:
            # Status styling
            if task.status == "Completed":
                status_str = f"[{COLOR_PALETTE['green']}]✔ Completed[/]"
                title_style = f"dim strikethrough {COLOR_PALETTE['gray_light']}"
            elif task.status == "In Progress":
                status_str = f"[{COLOR_PALETTE['orange']}]⚡ In Progress[/]"
                title_style = "bold white"
            else:
                status_str = f"[{COLOR_PALETTE['gray_light']}]◷ Pending[/]"
                title_style = "bold white"

            # Priority styling
            p_style = STYLES.get(f"priority_{task.priority.lower()}", "white")
            p_str = f"[{p_style}]{task.priority}[/]"

            # Category styling
            cat_color = STYLES.get(f"cat_{task.category.lower()}", COLOR_PALETTE['text'])
            cat_str = f"[{cat_color}]{task.category}[/]"

            # Due Date parsing & highlight
            due_str = task.due_date if task.due_date else "-"
            if task.is_overdue:
                due_str = f"[bold {COLOR_PALETTE['red']}]{due_str} ⚠[/]"
            elif task.due_date and task.status != "Completed":
                # Check if due today
                if task.due_date == datetime.now().strftime("%Y-%m-%d"):
                    due_str = f"[bold {COLOR_PALETTE['orange']}]{due_str} 🕒[/]"
                else:
                    due_str = f"[{COLOR_PALETTE['green']}]{due_str}[/]"

            table.add_row(
                task.id,
                status_str,
                Text(task.title, style=title_style),
                cat_str,
                p_str,
                due_str
            )

        return table

    def render_menu(self) -> Panel:
        """Renders the command options dashboard."""
        menu_text = Text()
        options = [
            ("[bold gold]a[/] Add Task", "[bold gold]e[/] Edit Task", "[bold gold]d[/] Delete Task"),
            ("[bold gold]c[/] Complete Task", "[bold gold]s[/] Search Tasks", "[bold gold]f[/] Filter/Sort"),
            ("[bold gold]i[/] Import CSV", "[bold gold]o[/] Export CSV", "[bold gold]q[/] Exit Program")
        ]
        
        table = Table.grid(expand=True, padding=(0, 2))
        table.add_column(ratio=1)
        table.add_column(ratio=1)
        table.add_column(ratio=1)

        for row in options:
            table.add_row(
                Text.from_markup(row[0]),
                Text.from_markup(row[1]),
                Text.from_markup(row[2])
            )

        return Panel(
            table,
            title=f"[{COLOR_PALETTE['gold']}]ACTIONS[/]",
            border_style=COLOR_PALETTE["maroon"],
            padding=(1, 2)
        )

    def show_loading_animation(self, message: str = "Processing...", duration: float = 1.0):
        """Displays a beautiful spinner loading animation."""
        with self.console.status(f"[bold {COLOR_PALETTE['gold']}]{message}[/]", spinner="dots"):
            time.sleep(duration)

    def prompt_task_input(self, defaults: Optional[Task] = None) -> Optional[Tuple[str, str, str, str, Optional[str]]]:
        """Prompts the user for task inputs with validation and defaults."""
        self.console.print(f"\n[bold {COLOR_PALETTE['gold']}]--- ENTER TASK DETAILS ---[/]")
        
        # 1. Title
        title_prompt = f"Title"
        if defaults:
            title_prompt += f" ([dim]{defaults.title}[/])"
        title = Prompt.ask(title_prompt, default=defaults.title if defaults else "")
        if not title:
            self.console.print(f"[bold {COLOR_PALETTE['red']}]Error: Title cannot be empty![/]")
            return None

        # 2. Description
        desc_prompt = "Description"
        if defaults:
            desc_prompt += f" ([dim]{defaults.description}[/])"
        description = Prompt.ask(desc_prompt, default=defaults.description if defaults else "")

        # 3. Priority
        p_choices = ["High", "Medium", "Low"]
        p_prompt = "Priority"
        priority = Prompt.ask(p_prompt, choices=p_choices, default=defaults.priority if defaults else "Medium")

        # 4. Category
        c_prompt = "Category"
        cat_choices = CATEGORIES
        category = Prompt.ask(c_prompt, choices=cat_choices, default=defaults.category if defaults else "Personal")
        if category == "Custom":
            category = Prompt.ask("Enter custom category name")
            if not category.strip():
                category = "Custom"

        # 5. Due Date
        due_date = None
        while True:
            due_prompt = "Due Date (YYYY-MM-DD) or empty"
            default_due = defaults.due_date if defaults else ""
            if default_due:
                due_prompt += f" ([dim]{default_due}[/])"
            
            due_input = Prompt.ask(due_prompt, default=default_due)
            if not due_input:
                break
            try:
                datetime.strptime(due_input, "%Y-%m-%d")
                due_date = due_input
                break
            except ValueError:
                self.console.print(f"[bold {COLOR_PALETTE['red']}]Invalid format! Please use YYYY-MM-DD.[/]")

        return title, description, priority, category, due_date

    def prompt_filter_sort(self) -> Dict[str, Any]:
        """Prompts user for filtering and sorting parameters."""
        self.console.print(f"\n[bold {COLOR_PALETTE['gold']}]--- FILTER & SORT OPTIONS ---[/]")
        
        # Status Filter
        status_choices = ["All"] + STATUSES
        status = Prompt.ask("Filter by Status", choices=status_choices, default="All")
        status_val = None if status == "All" else status

        # Priority Filter
        priority_choices = ["All"] + PRIORITIES
        priority = Prompt.ask("Filter by Priority", choices=priority_choices, default="All")
        priority_val = None if priority == "All" else priority

        # Category Filter
        category_choices = ["All"] + CATEGORIES
        category = Prompt.ask("Filter by Category", choices=category_choices, default="All")
        category_val = None if category == "All" else category

        # Sort field
        sort_choices = ["created_at", "due_date", "priority", "status"]
        sort_by = Prompt.ask("Sort by field", choices=sort_choices, default="created_at")

        # Sort order
        reverse = Confirm.ask("Sort in descending/reverse order?", default=False)

        return {
            "status": status_val,
            "priority": priority_val,
            "category": category_val,
            "sort_by": sort_by,
            "reverse": reverse
        }

    def show_message(self, message: str, type: str = "info"):
        """Displays formatted message boxes."""
        if type == "success":
            color = COLOR_PALETTE["green"]
            prefix = "✔ SUCCESS"
        elif type == "error":
            color = COLOR_PALETTE["red"]
            prefix = "✖ ERROR"
        elif type == "warning":
            color = COLOR_PALETTE["orange"]
            prefix = "⚠ WARNING"
        else:
            color = COLOR_PALETTE["gold"]
            prefix = "✦ INFO"

        panel = Panel(
            Text(message, style="bold white"),
            title=f"[{color}]{prefix}[/]",
            border_style=color,
            expand=False
        )
        self.console.print(panel)

    def prompt_confirm(self, message: str) -> bool:
        """Prompts the user for confirmation."""
        return Confirm.ask(f"[bold {COLOR_PALETTE['orange']}]{message}[/]")
