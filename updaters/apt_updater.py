import asyncio
import subprocess
import shutil
import sys
from functools import partial

from .base_updater import BaseUpdater
from utils.error_handler import handle_error

class AptUpdater(BaseUpdater):
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
        """Update apt packages for ubuntu/debian distros."""
        if sys.platform == "linux" and shutil.which("apt-get"):
            apt_cmds = ["update", "upgrade", "dist-upgrade", "autoremove", "autoclean"]
            for cmd in apt_cmds:
                print(f"::: Running apt-get {cmd}")
                result = self.run_with_sudo(["apt-get", "-y", cmd], password)
                if result and result.returncode != 0:
                    handle_error(["apt-get", cmd], result.stderr)
        else:
            print("::: apt-get not available on this system, skipping")

    async def update_async(self, args, password=None):
        self.status_tracker.update("APT", "in_progress")
        try:
            if sys.platform == "linux" and shutil.which("apt-get"):
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, partial(self.update, args, password))
                self.status_tracker.update("APT", "done")
            else:
                self.status_tracker.update("APT", "skipped")
        except asyncio.CancelledError:
            self.status_tracker.update("APT", "failed")
