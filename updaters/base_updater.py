class BaseUpdater:
    """Base class for all updaters"""

    def __init__(self, github_dir, status_tracker):
        self.github_dir = github_dir
        self.status_tracker = status_tracker
        self.requires_sudo = False

    async def update_async(self, args, password=None):
        """Update asynchronously"""
        raise NotImplementedError("Subclasses must implement update_async")

    def update(self, args, password=None):
        """Update synchronously"""
        raise NotImplementedError("Subclasses must implement update")
