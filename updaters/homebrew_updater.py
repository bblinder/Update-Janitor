import asyncio
import subprocess
import random
from functools import partial

from .base_updater import BaseUpdater

class HomebrewUpdater(BaseUpdater):
    def __init__(self, github_dir, status_tracker):
        super().__init__(github_dir, status_tracker)
        self.requires_sudo = False

    def run_brew_doctor(self):
        print("::: Running brew doctor")
        subprocess.run(["brew", "doctor"], check=False)

    def update_homebrew(self):
        print("::: Updating Homebrew")
        subprocess.run(["brew", "update"], check=False)
        subprocess.run(["brew", "upgrade"], check=False)
        subprocess.run(["brew", "upgrade", "--cask", "--greedy"], check=False)

    def cleanup_homebrew(self):
        print("::: Running brew cleanup")
        subprocess.run(["brew", "cleanup"], check=False)
        subprocess.run(["brew", "cleanup", "-s", "--prune=all"], check=False)

    def update(self, args, password=None):
        """Update homebrew packages."""
        if random.randint(0, 3) == 1:
            self.run_brew_doctor()

        self.update_homebrew()

        if args.no_input or input("Cleanup Homebrew? [y/N] --> ").lower() == "y":
            self.cleanup_homebrew()

    async def update_async(self, args, password=None):
        self.status_tracker.update("Homebrew", "in_progress")
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, partial(self.update, args))
            self.status_tracker.update("Homebrew", "done")
        except asyncio.CancelledError:
            self.status_tracker.update("Homebrew", "failed")
            print("::: Homebrew update cancelled")
            raise
        except Exception as e:
            print(f"::: Error updating Homebrew: {str(e)}")
            self.status_tracker.update("Homebrew", "failed")
