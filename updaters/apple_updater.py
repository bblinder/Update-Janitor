import shutil
import subprocess
import sys

from .base_updater import BaseUpdater


class AppleUpdater(BaseUpdater):
    name = "Apple Updates"

    @classmethod
    def is_available(cls) -> bool:
        return sys.platform == "darwin"

    def update(self, args, password=None):
        """List macOS system updates and install App Store updates via mas."""
        if shutil.which("softwareupdate"):
            self.log("Available system updates:")
            subprocess.run(["softwareupdate", "--list"], check=False)

        if not shutil.which("mas"):
            self.log("'mas' command not found, skipping App Store updates")
            return

        self.log("Checking for App Store updates")
        outdated = subprocess.run(
            ["mas", "outdated"], check=False, capture_output=True, text=True
        )
        if outdated.returncode == 0 and outdated.stdout.strip():
            self.log("Installing App Store updates")
            subprocess.run(["mas", "upgrade"], check=False)
        else:
            self.log("No App Store updates available")
