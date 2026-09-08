import asyncio
import logging
import signal


def handle_error(command, error, severity="warning"):
    """Log and print a command failure."""
    cmd_str = " ".join(command) if isinstance(command, list) else str(command)
    message = f"Error running {cmd_str}: {error}"

    log = logging.error if severity == "error" else logging.warning
    log(message)
    print(f"{severity.upper()}: {message}")


def setup_signal_handlers(loop):
    """Cancel running tasks on SIGINT/SIGTERM, then unwind via KeyboardInterrupt.

    asyncio.run() finishes the job by cancelling anything still pending;
    executor threads are allowed to complete their current command.
    """
    def handler(sig, frame):
        print("\n::: Interrupt received. Cancelling running tasks...")
        loop.call_soon_threadsafe(_cancel_all, loop)
        raise KeyboardInterrupt

    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, handler)


def _cancel_all(loop):
    for task in asyncio.all_tasks(loop):
        task.cancel()
