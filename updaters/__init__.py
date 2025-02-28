import sys
import shutil
from pathlib import Path

from .base_updater import BaseUpdater
from .homebrew_updater import HomebrewUpdater
from .python_updater import PythonUpdater
from .apt_updater import AptUpdater
from .ruby_updater import RubyUpdater
from .git_updater import GitUpdater
from .apple_updater import AppleUpdater

def get_available_updaters(github_dir, status_tracker):
    """Return a dictionary of available updaters based on the current system"""
    os_platform = sys.platform
    updaters = {}

    # Check for each updater's availability
    if os_platform in ["linux", "darwin"] and shutil.which("brew"):
        updaters["Homebrew"] = HomebrewUpdater(github_dir, status_tracker)

    # Python is always available
    updaters["Python"] = PythonUpdater(github_dir, status_tracker)

    if os_platform == "linux" and shutil.which("apt-get"):
        updaters["APT"] = AptUpdater(github_dir, status_tracker)

    if os_platform == "darwin" and shutil.which("gem"):
        updaters["Ruby"] = RubyUpdater(github_dir, status_tracker)

    if github_dir.exists():
        updaters["Git"] = GitUpdater(github_dir, status_tracker)

    if os_platform == "darwin":
        updaters["Apple Updates"] = AppleUpdater(github_dir, status_tracker)

    return updaters
