from rich import box
from rich.align import Align
from rich.console import Console, Group
from rich.live import Live
from rich.table import Table
from rich.text import Text


class StatusTracker:
    """Track task statuses and render them as a centered live-updating table."""

    # Emoji are chosen to be unambiguously double-width (East Asian Width = W)
    # so rich's cell math matches what real terminals draw. Beware glyphs like
    # ⏭ (U+23ED, eaw=N): rich measures them as width 1 even with the VS16
    # emoji selector, while terminals render them 2 cells wide -> ragged rows.
    STATES = {
        "not_started": ("⏳ Not Started", ""),
        "in_progress": ("🔄 In Progress", "yellow"),
        "done": ("✅ Done", "green"),
        "failed": ("❌ Failed", "red bold"),
        "skipped": ("⏩ Skipped", "blue"),
    }

    def __init__(self, task_names=()):
        self.tasks = {name: "not_started" for name in task_names}
        self.console = Console()
        self._live = None

    def set_tasks(self, task_names):
        """Register the tasks to display. Call before start()."""
        self.tasks = {name: "not_started" for name in task_names}

    def start(self):
        if self._live is None:
            self._live = Live(
                self._render(),
                console=self.console,
                auto_refresh=False,
                vertical_overflow="visible",
            )
            self._live.start()

    def stop(self):
        if self._live is not None:
            self._live.stop()
            self._live = None

    def pause(self):
        """Hide the live table temporarily (e.g. for input prompts)."""
        if self._live is not None:
            self._live.stop()

    def resume(self):
        if self._live is not None:
            self._live.start()
            self._live.update(self._render(), refresh=True)

    def update(self, task, status):
        """Update the status of a task and refresh the table."""
        if task in self.tasks and status in self.STATES:
            self.tasks[task] = status
            if self._live is not None:
                self._live.update(self._render(), refresh=True)

    def get_status(self, task):
        return self.tasks.get(task, "not_started")

    def log(self, message):
        """Print a log line above the centered live table."""
        if self._live is not None:
            self._live.console.print(message)
        else:
            self.console.print(message)

    def _render(self):
        """Center the complete status block, not only its table title."""
        return Align.center(self._render_table())

    def _render_table(self):
        table = Table(
            title="System Update Status",
            title_justify="center",
            box=box.ROUNDED,
        )
        table.add_column("Task", style="cyan", no_wrap=True)
        table.add_column("Status", no_wrap=True)
        for task, status in self.tasks.items():
            label, style = self.STATES[status]
            table.add_row(task, Text(label, style=style))
        return table
