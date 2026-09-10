from rich.console import Console
from rich.table import Table
from rich.text import Text


class StatusTracker:
    """Track and display status of tasks using clear-and-render."""

    STATES = {
        "not_started": "⏳ Not Started",
        "in_progress": "🔄 In Progress",
        "done": "✅ Done",
        "failed": "❌ Failed",
        "skipped": "⏩ Skipped",
    }

    def __init__(self, task_names=()):
        self.tasks = {name: "not_started" for name in task_names}
        self.console = Console()

    def set_tasks(self, task_names):
        """Register the tasks to track."""
        self.tasks = {name: "not_started" for name in task_names}

    def start(self):
        """Render initial table view."""
        self.render()

    def stop(self):
        """Finalize the tracker view."""
        self.render()

    def pause(self):
        """No-op retained for interface compatibility."""
        pass

    def resume(self):
        """No-op retained for interface compatibility."""
        pass

    def update(self, task, status):
        """Update the status of a task and redraw the table."""
        if task in self.tasks and status in self.STATES:
            self.tasks[task] = status
            self.render()

    def get_status(self, task):
        """Get the current status of a task."""
        return self.tasks.get(task, "not_started")

    def log(self, message):
        """Print status messages directly to standard output."""
        print(message)

    def render(self):
        """Render the status table with original clean styling."""
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
            else:
                table.add_row(task, Text(status_text))

        self.console.clear()
        self.console.print(table)
