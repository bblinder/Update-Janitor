import asyncio
import getpass
import subprocess
import logging

class PasswordManager:
    """A class for managing sudo passwords with enhanced security."""

    def __init__(self):
        self._password = None
        self._validated = False
        self._sudo_refresh_task = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Cancel the refresh task if it exists
        if self._sudo_refresh_task:
            self._sudo_refresh_task.cancel()

        # Securely clear the password from memory
        if self._password:
            self._password = '\0' * len(self._password)
            self._password = None
        self._validated = False

    def get_password(self, validate_sudo=True) -> str:
        """Get the sudo password, only prompting once, with validation."""
        if not self._password:
            self._password = getpass.getpass("Enter sudo password: ")

            if validate_sudo and not self._validated:
                # Validate the password
                try:
                    subprocess.run(
                        ["sudo", "-S", "true"],
                        input=self._password.encode(),
                        check=True,
                        stderr=subprocess.PIPE,
                        stdout=subprocess.PIPE
                    )
                    self._validated = True

                    # Start a task to refresh sudo credentials periodically
                    # Only do this if we're inside a running event loop
                    try:
                        loop = asyncio.get_running_loop()
                        if not self._sudo_refresh_task:
                            self._sudo_refresh_task = loop.create_task(self._refresh_sudo_credentials())
                    except RuntimeError:
                        # Not in an event loop, which is fine in some contexts
                        pass

                except subprocess.CalledProcessError:
                    print("Invalid sudo password. Please try again.")
                    self._password = None
                    return self.get_password(validate_sudo)

        return self._password

    async def _refresh_sudo_credentials(self):
        """Periodically refresh sudo credentials to prevent timeout"""
        try:
            while True:
                # Refresh sudo every 60 seconds
                await asyncio.sleep(60)
                if self._password:
                    try:
                        subprocess.run(
                            ["sudo", "-S", "-v"],  # -v refreshes the timeout
                            input=self._password.encode(),
                            check=False,  # We don't want to raise an exception
                            stderr=subprocess.PIPE,
                            stdout=subprocess.PIPE
                        )
                    except Exception as e:
                        logging.warning(f"Failed to refresh sudo credentials: {e}")
        except asyncio.CancelledError:
            # Task was cancelled, just exit
            pass
