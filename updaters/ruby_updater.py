import asyncio
import subprocess
import sys
import shutil
from functools import partial

from .base_updater import BaseUpdater
from utils.error_handler import handle_error

class RubyUpdater(BaseUpdater):
    def __init__(self, github_dir, status_tracker):
        super().__init__(github_dir, status_tracker)
        self.requires_sudo = True

    def run_with_sudo(self, command, password):
        """Run a command with sudo, with better error handling"""
        try:
            result = subprocess.run(
                ["sudo", "-S"] + command,
                input=password.encode(),
                check=False,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                handle_error(command, result.stderr.strip())

            return result
        except Exception as e:
            handle_error(command, str(e))
            return None

    def update(self, args, password=None):
        """Update ruby gems. For some reason, MacOS doesn't like it if you don't use sudo."""
        if sys.platform == "darwin" and shutil.which("gem"):
            print("::: Updating ruby gems")
            commands = [
                ["gem", "update", "-n", "/usr/local/bin/"],
                ["gem", "update", "-n", "/usr/local/bin/", "--system"],
                ["gem", "update"],
                ["gem", "update", "--system"]
            ]

            for cmd in commands:
                result = self.run_with_sudo(cmd, password)
                if result and result.returncode != 0:
                    handle_error(cmd, result.stderr)
        else:
            print("::: Ruby gems not available on this system, skipping")

    async def update_async(self, args, password=None):
        self.status_tracker.update("Ruby", "in_progress")
        try:
            if sys.platform == "darwin" and shutil.which("gem"):
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, partial(self.update, args, password))
                self.status_tracker.update("Ruby", "done")
            else:
                self.status_tracker.update("Ruby", "skipped")
        except asyncio.CancelledError:
            self.status_tracker.update("Ruby", "failed")
            print("::: Ruby update cancelled")
            raise
        except Exception as e:
            print(f"::: Error updating Ruby: {str(e)}")
            self.status_tracker.update("Ruby", "failed")
