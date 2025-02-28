import asyncio
import subprocess
import re
from functools import partial

from .base_updater import BaseUpdater

class PythonUpdater(BaseUpdater):
    def __init__(self, github_dir, status_tracker):
        super().__init__(github_dir, status_tracker)
        self.requires_sudo = False

    def pip_upgrade_new(self):
        try:
            subprocess.run(
                ["python3", "-m", "pip_review", "--auto", "--continue-on-fail"],
                check=False
            )
        except Exception as e:
            print(f"::: Error with pip-review: {str(e)}")
            raise

    def pip_upgrade_old(self):
        try:
            result = subprocess.run(
                ["python3", "-m", "pip", "list", "--outdated"],
                capture_output=True,
                check=False,
                text=True
            )

            if result.returncode != 0:
                print(f"::: Error listing outdated packages: {result.stderr}")
                return

            pip_packages = []
            for line in result.stdout.strip().split("\n"):
                if re.search(r"\s\d+\.", line):
                    pip_packages.append(line.split(" ")[0])

            if pip_packages:
                subprocess.run(
                    ["python3", "-m", "pip", "install", "--upgrade"] + pip_packages,
                    check=False
                )
        except Exception as e:
            print(f"::: Error upgrading pip packages: {str(e)}")

    def update(self, args, password=None):
        """Update python packages."""
        print("::: Updating python packages")
        try:
            self.pip_upgrade_new()
        except Exception:
            print("::: Failed with pip-review, trying the old method...")
            self.pip_upgrade_old()

    async def update_async(self, args, password=None):
        self.status_tracker.update("Python", "in_progress")
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, partial(self.update, args))
            self.status_tracker.update("Python", "done")
        except asyncio.CancelledError:
            self.status_tracker.update("Python", "failed")
            print("::: Python update cancelled")
            raise
        except Exception as e:
            print(f"::: Error updating Python: {str(e)}")
            self.status_tracker.update("Python", "failed")
