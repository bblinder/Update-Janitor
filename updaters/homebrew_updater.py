import random
import shutil
import subprocess
import sys

from .base_updater import BaseUpdater

DOCTOR_PROBABILITY = 0.25  # run brew doctor on roughly 1 in 4 runs


class HomebrewUpdater(BaseUpdater):
    name = "Homebrew"

    @classmethod
    def is_available(cls) -> bool:
        return sys.platform in ("linux", "darwin") and shutil.which("brew") is not None

    def update(self, args, password=None):
        """Update homebrew packages."""
        if random.random() < DOCTOR_PROBABILITY:
            self.log("Running brew doctor")
            subprocess.run(["brew", "doctor"], check=False)

        self.log("Updating Homebrew")
        subprocess.run(["brew", "update"], check=False)
        subprocess.run(["brew", "upgrade"], check=False)
        subprocess.run(["brew", "upgrade", "--cask", "--greedy"], check=False)

        self.status_tracker.pause()
        try:
            wants_cleanup = args.no_input or input("Cleanup Homebrew? [y/N] --> ").lower() == "y"
        finally:
            self.status_tracker.resume()

        if wants_cleanup:
            self.log("Running brew cleanup")
            subprocess.run(["brew", "cleanup", "-s", "--prune=all"], check=False)
