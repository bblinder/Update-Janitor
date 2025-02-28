import asyncio
import subprocess
import sys
import shutil
from functools import partial

from .base_updater import BaseUpdater
from utils.error_handler import handle_error

class AppleUpdater(BaseUpdater):
    def __init__(self, github_dir, status_tracker):
        super().__init__(github_dir, status_tracker)
        self.requires_sudo = False

    def update(self, args, password=None):
        """Update MacOS software."""
        if sys.platform == "darwin":
            print("::: Checking for MacOS software updates")
            try:
                # Check for system updates
                subprocess.run(["softwareupdate", "--list"], check=False)

                # Try to install recommended updates if no input required
                if shutil.which("softwareupdate"):
                    print("::: Installing recommended updates (may require interactive input)")
                    subprocess.run(["softwareupdate", "--install", "--recommended"], check=False)

                # Check for App Store updates
                if shutil.which("mas"):
                    print("::: Checking for App Store updates")
                    outdated_result = subprocess.run(
                        ["mas", "outdated"],
                        check=False,
                        capture_output=True,
                        text=True
                    )

                    if outdated_result.returncode == 0 and outdated_result.stdout.strip():
                        print("::: Installing App Store updates")
                        subprocess.run(["mas", "upgrade"], check=False)
                    else:
                        print("::: No App Store updates available")
                else:
                    print("::: 'mas' command not found, skipping App Store updates")
            except Exception as e:
                handle_error(["apple-update"], str(e))
        else:
            print("::: Not running MacOS, skipping Apple updates")

    async def update_async(self, args, password=None):
        self.status_tracker.update("Apple Updates", "in_progress")
        try:
            if sys.platform == "darwin":
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, partial(self.update, args))
                self.status_tracker.update("Apple Updates", "done")
            else:
                self.status_tracker.update("Apple Updates", "skipped")
        except asyncio.CancelledError:
            self.status_tracker.update("Apple Updates", "failed")
            print("::: Apple update cancelled")
            raise
        except Exception as e:
            print(f"::: Error updating Apple: {str(e)}")
            self.status_tracker.update("Apple Updates", "failed")
