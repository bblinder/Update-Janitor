import shutil
import subprocess

from .base_updater import BaseUpdater

GIT_STEPS = [
    ("remote update", ["git", "remote", "update"]),
    ("pull --rebase", ["git", "pull", "--rebase"]),
]


class GitUpdater(BaseUpdater):
    name = "Git"

    def __init__(self, status_tracker, github_dir):
        super().__init__(status_tracker)
        self.github_dir = github_dir

    @classmethod
    def is_available(cls) -> bool:
        return shutil.which("git") is not None

    @staticmethod
    def is_git_repo(path) -> bool:
        """Check if a directory is a git repo."""
        return path.is_dir() and (path / ".git").exists()

    def update_repo(self, repo):
        """Update a single git repository, warning on uncommitted changes."""
        self.log(f"Updating {repo.name}")

        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo, check=False, capture_output=True, text=True,
        )
        if status.stdout.strip():
            self.log(f"Warning: {repo.name} has uncommitted changes; merge conflicts may occur")

        for label, cmd in GIT_STEPS:
            result = subprocess.run(
                cmd, cwd=repo, check=False, capture_output=True, text=True
            )
            if result.returncode != 0:
                self.log(f"{repo.name}: git {label} failed: {result.stderr.strip()}")

    def update(self, args, password=None):
        """Update all git repos in the configured directory."""
        repos = [p for p in self.github_dir.iterdir() if self.is_git_repo(p)]
        if not repos:
            self.log(f"No git repositories found in {self.github_dir}")
            return

        self.log(f"Updating git repos in {self.github_dir}")
        for repo in repos:
            try:
                self.update_repo(repo)
            except Exception as e:
                self.log(f"Error updating {repo.name}: {e}")
