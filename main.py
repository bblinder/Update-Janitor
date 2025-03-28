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

    # Check for supported OS
    if sys.platform not in ["darwin", "linux"]:
        print("WARNING: This tool has only been tested on MacOS and Debian-based Linux distributions.")
        print("Windows support is planned for future releases.")
        print("Some features may not work correctly on your system.")

        # Ask user if they want to continue
        if input("Continue anyway? [y/N] --> ").lower() != "y":
            print("Exiting.")
            return 0

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
            try:
                if any(updater.requires_sudo for updater in updaters.values()):
                    password_manager = PasswordManager()

                try:
                    if args.no_input:
                        # Non-interactive mode
                        print("::: Running in non-interactive mode")

                        # Create task list based on OS and available updaters
                        tasks = []
                        task_names = []  # Keep track of which task is which

                        for name, updater in updaters.items():
                            task_names.append(name)
                            status_tracker.update(name, "in_progress")
                            if updater.requires_sudo and password_manager:
                                tasks.append(updater.update_async(args, password_manager.get_password()))
                            else:
                                tasks.append(updater.update_async(args))

                        try:
                            # Run all tasks concurrently
                            results = await asyncio.gather(*tasks, return_exceptions=True)

                            # Process results
                            for i, result in enumerate(results):
                                if isinstance(result, Exception):
                                    name = task_names[i]
                                    print(f"::: Error updating {name}: {str(result)}")
                                    status_tracker.update(name, "failed")
                                    logging.exception(f"Error during {name} update", exc_info=result)
                        except asyncio.CancelledError:
                            print("::: Tasks were cancelled during shutdown")
                            # Update all in-progress tasks as failed
                            for name in task_names:
                                if status_tracker.get_status(name) == "in_progress":
                                    status_tracker.update(name, "failed")
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
                                try:
                                    if updater.requires_sudo and password_manager:
                                        await updater.update_async(args, password_manager.get_password())
                                    else:
                                        await updater.update_async(args)
                                    status_tracker.update(name, "done")
                                except asyncio.CancelledError:
                                    print(f"::: {name} update was cancelled")
                                    status_tracker.update(name, "failed")
                                    raise  # Re-raise to exit the program
                                except Exception as e:
                                    print(f"::: Error updating {name}: {str(e)}")
                                    status_tracker.update(name, "failed")
                                    logging.exception(f"Error during {name} update")
                                    # Continue with next updater instead of failing the entire program
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
            finally:
                # Ensure password manager is cleaned up
                if password_manager:
                    password_manager.__exit__(None, None, None)

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

