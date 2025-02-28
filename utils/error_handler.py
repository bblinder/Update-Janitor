import logging
import signal
import sys

def handle_error(command, error, severity="warning"):
    """Centralized error handling for command failures."""
    if isinstance(command, list):
        cmd_str = ' '.join(command)
    else:
        cmd_str = str(command)

    error_msg = f"Error running {cmd_str}: {error}"

    if severity == "critical":
        logging.critical(error_msg)
        print(f"CRITICAL: {error_msg}")
        sys.exit(1)
    elif severity == "error":
        logging.error(error_msg)
        print(f"ERROR: {error_msg}")
    else:
        logging.warning(error_msg)
        print(f"WARNING: {error_msg}")

def setup_signal_handlers(loop=None):
    """Setup signal handlers for graceful shutdown"""
    # We'll use the original system signal handler for terminal signals
    # Instead of trying to manage asyncio loop shutdown
    original_sigint = signal.getsignal(signal.SIGINT)
    original_sigterm = signal.getsignal(signal.SIGTERM)

    def signal_handler(sig, frame):
        print("\n::: Received interrupt signal. Gracefully shutting down...")
        # If we have a loop, cancel all tasks
        if loop:
            for task in asyncio.all_tasks(loop):
                task.cancel()
        # Otherwise call the original handler
        if sig == signal.SIGINT and original_sigint != signal.SIG_DFL and original_sigint != signal.SIG_IGN:
            original_sigint(sig, frame)
        if sig == signal.SIGTERM and original_sigterm != signal.SIG_DFL and original_sigterm != signal.SIG_IGN:
            original_sigterm(sig, frame)
        # If we get here, there was no original handler, so just exit
        sys.exit(0)

    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, signal_handler)
