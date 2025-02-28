#!/usr/bin/env python3
from main import main, parse_args

if __name__ == "__main__":
    import asyncio
    import sys

    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n::: Program interrupted by user. Exiting gracefully...")
        sys.exit(130)  # Standard exit code for SIGINT
