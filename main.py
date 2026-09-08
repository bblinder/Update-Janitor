#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#     "pip-review",
#     "rich",
#     "filelock",
# ]
# ///

import argparse
import asyncio
import logging
import sys
from pathlib import Path

from filelock import FileLock, Timeout as FileLockTimeout

from updaters import get_available_updaters
from utils.error_handler import handle_error, setup_signal_handlers
from utils.password_manager import PasswordManager
from utils.status_tracker import StatusTracker

SCRIPT_DIR = Path(__file__).resolve().parent
LOG_FILE = SCRIPT_DIR / "update.log"
LOCK_FILE = SCRIPT_DIR / "updater.lock"
GITHUB_DIR = Path.home() / "Github"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename=LOG_FILE,
)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Update various system packages.")
    parser.add_argument(
        "-y", "--no-input",
        action="store_true",
        help="Run without user confirmation (non-interactive mode).",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging.")
    return parser.parse_args()


async def _run_one(updater, args, password_manager):
    password = None
    if updater.requires_sudo:
        tracker = updater.status_tracker
        tracker.pause()
        try:
            password = password_manager.get_password()
        finally:
            tracker.resume()
    await updater.update_async(args, password)


async def run_batch(updaters, args, password_manager):
    """Non-interactive mode: run all updaters concurrently."""
    await asyncio.gather(*(_run_one(u, args, password_manager) for u in updaters.values()))


async def run_interactive(updaters, args, password_manager, status_tracker):
    """Interactive mode: prompt for each updater, then run it."""
    for name, updater in updaters.items():
        status_tracker.pause()
        try:
            choice = input(f"Update {name}? [y/N] --> ")
        finally:
            status_tracker.resume()

        if choice.lower() != "y":
            status_tracker.log(f"Skipping {name}")
            status_tracker.update(name, "skipped")
            continue

        await _run_one(updater, args, password_manager)


async def main() -> int:
    if sys.platform not in ("darwin", "linux"):
        print("WARNING: tested on macOS and Debian-based Linux only.")
        if input("Continue anyway? [y/N] --> ").lower() != "y":
            print("Exiting.")
            return 0

    setup_signal_handlers(asyncio.get_running_loop())

    args = parse_args()
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        with FileLock(LOCK_FILE, timeout=1):
            status_tracker = StatusTracker()
            updaters = get_available_updaters(GITHUB_DIR, status_tracker)
            status_tracker.set_tasks(updaters.keys())

            mode = "non-interactive" if args.no_input else "interactive"
            print(f"::: Running in {mode} mode")
            status_tracker.start()

            try:
                with PasswordManager() as password_manager:
                    if args.no_input:
                        await run_batch(updaters, args, password_manager)
                    else:
                        await run_interactive(updaters, args, password_manager, status_tracker)
            finally:
                status_tracker.stop()

            failed = [n for n in updaters if status_tracker.get_status(n) == "failed"]
            if failed:
                print(f"::: Finished with failures: {', '.join(failed)}")
                return 1

            print("::: All updates completed successfully!")
            return 0
    except FileLockTimeout:
        print("::: Another instance is already running. Exiting.")
        return 1
    except KeyboardInterrupt:
        print("\n::: Interrupted by user. Exiting.")
        return 130
    except asyncio.CancelledError:
        print("\n::: Tasks cancelled. Exiting.")
        return 130
    except Exception as e:
        handle_error("main process", str(e), "error")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(main()))
    except KeyboardInterrupt:
        print("\n::: Interrupted by user. Exiting.")
        sys.exit(130)
