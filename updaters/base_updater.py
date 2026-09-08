import asyncio
import subprocess
from functools import partial

from utils.error_handler import handle_error


class BaseUpdater:
    """Base class for all updaters.

    Subclasses set `name` (and optionally `requires_sudo`), override
    `is_available()`, and implement the synchronous `update()`.
    Status tracking, executor offload, and cancellation handling live here.
    """

    name = "Unnamed"
    requires_sudo = False

    def __init__(self, status_tracker):
        self.status_tracker = status_tracker

    @classmethod
    def is_available(cls) -> bool:
        """Return True if this updater can run on the current system."""
        return True

    def log(self, message):
        """Print a status line above the live status table."""
        self.status_tracker.log(f"::: {message}")

    def run_with_sudo(self, command, password):
        """Run a command via sudo -S, feeding the password on stdin.

        Returns the CompletedProcess, or None if sudo could not be started.
        Reporting non-zero exit codes is the caller's responsibility.
        """
        if not password:
            self.log(f"No sudo password provided, skipping: {' '.join(command)}")
            return None
        try:
            return subprocess.run(
                ["sudo", "-S"] + command,
                input=password + "\n",
                check=False,
                capture_output=True,
                text=True,
            )
        except Exception as e:
            handle_error(command, str(e))
            return None

    def update(self, args, password=None):
        """Update synchronously. Subclasses must implement this."""
        raise NotImplementedError("Subclasses must implement update")

    async def update_async(self, args, password=None):
        """Run update() in an executor with status tracking."""
        self.status_tracker.update(self.name, "in_progress")
        try:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, partial(self.update, args, password))
            self.status_tracker.update(self.name, "done")
        except asyncio.CancelledError:
            self.status_tracker.update(self.name, "failed")
            self.log(f"{self.name} update cancelled")
            raise
        except Exception as e:
            self.log(f"Error updating {self.name}: {e}")
            self.status_tracker.update(self.name, "failed")
