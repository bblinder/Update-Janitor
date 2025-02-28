from rich.console import Console
from rich.table import Table
from rich.text import Text

class StatusTracker:
    """Class to track and display status of tasks"""

    STATES = {
        "not_started": "⏳ Not Started",
        "in_progress": "🔄 In Progress",
        "done": "✅ Done",
        "failed": "❌ Failed",
        "skipped": "⏭️ Skipped"
    }

    def __init__(self):
        self.tasks = {
            "Homebrew": "not_started",
            "Python": "not_started",
            "APT": "not_started",
            "Ruby": "not_started",
            "Git": "not_started",
            "Apple Updates": "not_started"
        }
        self.console = Console()

    def update(self, task, status):
        """Update the status of a task"""
        if task in self.tasks and status in self.STATES:
            self.tasks[task] = status
            self.render()

    def get_status(self, task):
        """Get the status of a task"""
        return self.tasks.get(task, "not_started")

    def render(self):
        """Render the status table with rich formatting"""
        table = Table(title="System Update Status")
        table.add_column("Task", style="cyan")
        table.add_column("Status")

        for task, status in self.tasks.items():
            status_text = self.STATES[status]

            if status == "done":
                table.add_row(task, Text(status_text, style="green"))
            elif status == "failed":
                table.add_row(task, Text(status_text, style="red bold"))
            elif status == "in_progress":
                table.add_row(task, Text(status_text, style="yellow"))
            elif status == "skipped":
                table.add_row(task, Text(status_text, style="blue"))
            else:  # not_started
                table.add_row(task, Text(status_text))

        self.console.clear()
        self.console.print(table)
