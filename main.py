#!/usr/bin/env python3

import asyncio
import sys
from pathlib import Path

# Bootstrap the virtual environment
from bootstrap import bootstrap_venv
bootstrap_venv()

from utils.status_tracker import StatusTracker
from utils.password_manager import PasswordManager
from utils.error_handler import handle_error, setup_signal_handlers
from updaters import get_available_updaters

from filelock import FileLock
import argparse
import logging
import shutil

# Configure logging
SCRIPT_DIR = Path(__file__).resolve().parent
LOG_FILE = SCRIPT_DIR / "update.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=LOG_FILE
)

# Constants
GITHUB_DIR = Path.home() / "Github"
OS = sys.platform

def parse_args() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Update various system packages.")
    parser.add_argument(
        "-y",
        "--no-input",
        action="store_true",
        help="Run without user confirmation (non-interactive mode).",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )
    return parser.parse_args()

async def main() -> int:
    # Getting the current event loop
    loop = asyncio.get_running_loop()

    # Setup traditional signal handlers
    setup_signal_handlers()

    # Create status tracker
    status_tracker = StatusTracker()
    status_tracker.render()

    # Setup file lock to prevent multiple instances
    lock_file = SCRIPT_DIR / "updater.lock"

    try:
        lock = FileLock(lock_file, timeout=1)
        with lock:
            args = parse_args()

            # Set logging level based on args
            if args.debug:
                logging.getLogger().setLevel(logging.DEBUG)

            # Get available updaters based on the current system
            updaters = get_available_updaters(GITHUB_DIR, status_tracker)

            # Setup password manager - only if needed by any updater
            password_manager = None
            if any(updater.requires_sudo for updater in updaters.values()):
                password_manager = PasswordManager()
                # Don't get the password yet -- wait until it's needed.
                # password = password_manager.get_password() if password_manager else None

            try:
                if args.no_input:
                    # Non-interactive mode
                    print("::: Running in non-interactive mode")

                    # Create task list based on OS and available updaters
                    tasks = []

                    for name, updater in updaters.items():
                        if updater.requires_sudo and password_manager:
                            tasks.append(updater.update_async(args, password_manager.get_password()))
                        else:
                            tasks.append(updater.update_async(args))

                    try:
                        # Run all tasks concurrently
                        await asyncio.gather(*tasks, return_exceptions=True)
                    except await asyncio.CancelledError:
                        print("::: Tasks were cancelled during shutdown")
                        # Let the cancellation propagate
                        raise
                else:
                    # Interactive mode
                    print("::: Running in interactive mode")

                    for name, updater in updaters.items():
                        status_tracker.update(name, "not_started")
                        status_tracker.render()

                        user_choice = input(f"Update {name}? [y/N] --> ")
                        if user_choice.lower() == "y":
                            if updater.requires_sudo and password_manager:
                                await updater.update_async(args, password_manager.get_password())
                            else:
                                await updater.update_async(args)
                            status_tracker.update(name, "done")
                        else:
                            print(f"::: Skipping {name} update")
                            status_tracker.update(name, "skipped")

                print("::: All updates completed successfully!")
                return 0

            except KeyboardInterrupt:
                print("\n::: Program interrupted by user. Exiting gracefully...")
                return 130  # Standard exit code for SIGINT
            except asyncio.CancelledError:
                print("\n::: Tasks cancelled. Exiting gracefully...")
                return 1
            except Exception as e:
                handle_error("main process", str(e), "error")
                return 1

    except TimeoutError:
        print("::: Another instance of the script is already running. Exiting...")
        return 1
    except Exception as e:
        print(f"::: Unexpected error: {str(e)}")
        logging.exception("Unexpected error in main function")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n::: Program interrupted by user. Exiting gracefully...")
        sys.exit(130)  # Standard exit code for SIGINT
