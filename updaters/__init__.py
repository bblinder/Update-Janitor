from .apple_updater import AppleUpdater
from .apt_updater import AptUpdater
from .git_updater import GitUpdater
from .homebrew_updater import HomebrewUpdater
from .python_updater import PythonUpdater


def get_available_updaters(github_dir, status_tracker):
    """Instantiate the updaters that can run on the current system."""
    updaters = {}

    for cls in (HomebrewUpdater, PythonUpdater, AptUpdater):
        if cls.is_available():
            updaters[cls.name] = cls(status_tracker)

    if GitUpdater.is_available() and github_dir.exists():
        updaters[GitUpdater.name] = GitUpdater(status_tracker, github_dir)

    if AppleUpdater.is_available():
        updaters[AppleUpdater.name] = AppleUpdater(status_tracker)

    return updaters
