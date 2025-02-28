import asyncio
import subprocess
from functools import partial

from .base_updater import BaseUpdater
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

class GitUpdater(BaseUpdater):
    def __init__(self, github_dir, status_tracker):
        super().__init__(github_dir, status_tracker)
        self.requires_sudo = False

    def is_git_repo(self, repo):
        """Check if a directory is a git repo."""
        return repo.is_dir() and (repo / ".git").exists()

    def update_git_repo(self, repo):
        """Update a single git repository with better error messages."""
        print(f"::: Updating {repo.name}")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=Console()
        ) as progress:
            # Check for uncommitted changes first
            task = progress.add_task(f"[cyan]Checking repository status {repo.name}", total=None)
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=repo,
                check=False,
                capture_output=True,
                text=True
            )

            if status_result.stdout.strip():
                progress.update(task, description=f"[yellow]Warning: Repository {repo.name} has uncommitted changes")
                print(f"[yellow]⚠️  Repository {repo.name} has uncommitted changes. Will continue with update but merge conflicts may occur.")
            else:
                progress.update(task, description=f"[green]Repository {repo.name} is clean")

            # Remote update
            task = progress.add_task(f"[cyan]Remote Update for {repo.name}", total=None)
            result = subprocess.run(
                ["git", "remote", "update"],
                cwd=repo,
                check=False,
                text=True,
                capture_output=True,
            )

            if result.returncode == 0:
                progress.update(task, description=f"[green]Remote Update for {repo.name} - Success")
            else:
                progress.update(task, description=f"[red]Remote Update for {repo.name} - Failed: {result.stderr.strip()}")

            # Pull and rebase
            task = progress.add_task(f"[cyan]Pull & Rebase for {repo.name}", total=None)
            result = subprocess.run(
                ["git", "pull", "--rebase"],
                cwd=repo,
                check=False,
                text=True,
                capture_output=True,
            )

            if result.returncode == 0:
                progress.update(task, description=f"[green]Pull & Rebase for {repo.name} - Success")
            else:
                progress.update(task, description=f"[red]Pull & Rebase for {repo.name} - Failed: {result.stderr.strip()}")

            # Git garbage collection
            task = progress.add_task(f"[cyan]Garbage Collection for {repo.name}", total=None)
            result = subprocess.run(
                ["git", "gc", "--auto"],
                cwd=repo,
                check=False,
                text=True,
                capture_output=True,
            )

            if result.returncode == 0:
                progress.update(task, description=f"[green]Garbage Collection for {repo.name} - Success")
            else:
                progress.update(task, description=f"[red]Garbage Collection for {repo.name} - Failed: {result.stderr.strip()}")

    def update(self, args, password=None):
        """Update all git repos in a directory."""
        if self.github_dir.exists():
            print(f"::: Updating git repos in {self.github_dir}")
            repos = [repo for repo in self.github_dir.iterdir() if self.is_git_repo(repo)]

            if not repos:
                print(f"::: No git repositories found in {self.github_dir}")
                return

            for repo in repos:
                try:
                    self.update_git_repo(repo)
                except Exception as e:
                    print(f"::: Error updating {repo.name}: {str(e)}")
        else:
            print(f"::: {self.github_dir} does not exist, skipping git updates")

    async def update_async(self, args, password=None):
        self.status_tracker.update("Git", "in_progress")
        try:
            if self.github_dir.exists():
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, partial(self.update, args))
                self.status_tracker.update("Git", "done")
            else:
                self.status_tracker.update("Git", "skipped")
        except asyncio.CancelledError:
            self.status_tracker.update("Git", "failed")
            print("::: Git update cancelled")
            raise
        except Exception as e:
            print(f"::: Error updating Git: {str(e)}")
            self.status_tracker.update("Git", "failed")
