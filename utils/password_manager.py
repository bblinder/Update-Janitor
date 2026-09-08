import asyncio
import getpass
import logging
import subprocess


class PasswordManager:
    """Prompt for the sudo password once, validate it, and keep sudo alive."""

    REFRESH_INTERVAL = 60  # seconds

    def __init__(self):
        self._password = None
        self._sudo_refresh_task = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._sudo_refresh_task:
            self._sudo_refresh_task.cancel()
            self._sudo_refresh_task = None
        self._password = None

    def get_password(self) -> str:
        """Return the sudo password, prompting (until valid) on first use."""
        while self._password is None:
            candidate = getpass.getpass("Enter sudo password: ")
            if self._validate(candidate):
                self._password = candidate
                self._start_sudo_refresh()
            else:
                print("Invalid sudo password. Please try again.")
        return self._password

    @staticmethod
    def _validate(password) -> bool:
        """Check the password against sudo without raising."""
        result = subprocess.run(
            ["sudo", "-S", "true"],
            input=password + "\n",
            check=False,
            capture_output=True,
            text=True,
        )
        return result.returncode == 0

    def _start_sudo_refresh(self):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return  # no running loop; sudo timestamp simply won't be refreshed
        self._sudo_refresh_task = loop.create_task(self._refresh_sudo_credentials())

    async def _refresh_sudo_credentials(self):
        """Refresh sudo's timestamp periodically so it doesn't expire mid-run."""
        try:
            while True:
                await asyncio.sleep(self.REFRESH_INTERVAL)
                if self._password:
                    try:
                        loop = asyncio.get_running_loop()
                        await loop.run_in_executor(None, self._validate, self._password)
                    except Exception as e:
                        logging.warning(f"Failed to refresh sudo credentials: {e}")
        except asyncio.CancelledError:
            pass
