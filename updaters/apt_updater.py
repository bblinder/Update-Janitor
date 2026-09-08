import shutil
import sys

from .base_updater import BaseUpdater
from utils.error_handler import handle_error

APT_COMMANDS = ["update", "upgrade", "dist-upgrade", "autoremove", "autoclean"]


class AptUpdater(BaseUpdater):
    name = "APT"
    requires_sudo = True

    @classmethod
    def is_available(cls) -> bool:
        return sys.platform == "linux" and shutil.which("apt-get") is not None

    def update(self, args, password=None):
        """Update apt packages for ubuntu/debian distros."""
        for cmd in APT_COMMANDS:
            self.log(f"Running apt-get {cmd}")
            result = self.run_with_sudo(["apt-get", "-y", cmd], password)
            if result and result.returncode != 0:
                handle_error(["apt-get", cmd], result.stderr.strip())
