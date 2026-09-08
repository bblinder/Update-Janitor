import json
import subprocess
import sys

from .base_updater import BaseUpdater

# Interpreter whose packages get upgraded. Under `uv run --script`, sys.executable
# is the ephemeral script environment; point this at your primary interpreter
# (e.g. "/usr/bin/python3") if that is the environment you want to maintain.
PYTHON_BIN = sys.executable


class PythonUpdater(BaseUpdater):
    name = "Python"

    def pip_upgrade_new(self) -> bool:
        """Upgrade outdated packages via pip-review. Returns True on success."""
        result = subprocess.run(
            [PYTHON_BIN, "-m", "pip_review", "--auto", "--continue-on-fail"],
            check=False,
        )
        return result.returncode == 0

    def pip_upgrade_old(self):
        """Fallback: ask pip for outdated packages as JSON and upgrade them."""
        result = subprocess.run(
            [PYTHON_BIN, "-m", "pip", "list", "--outdated", "--format", "json"],
            capture_output=True,
            check=False,
            text=True,
        )
        if result.returncode != 0:
            self.log(f"Error listing outdated packages: {result.stderr.strip()}")
            return

        packages = [pkg["name"] for pkg in json.loads(result.stdout)]
        if packages:
            subprocess.run(
                [PYTHON_BIN, "-m", "pip", "install", "--upgrade", *packages],
                check=False,
            )

    def update(self, args, password=None):
        """Update python packages."""
        self.log("Updating python packages")
        try:
            succeeded = self.pip_upgrade_new()
        except OSError as e:
            self.log(f"pip-review unavailable: {e}")
            succeeded = False

        if not succeeded:
            self.log("Falling back to the pip list method")
            try:
                self.pip_upgrade_old()
            except (OSError, json.JSONDecodeError) as e:
                self.log(f"Error upgrading pip packages: {e}")
