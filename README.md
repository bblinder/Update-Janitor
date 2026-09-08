# Update Janitor

A system update utility that automates the process of keeping your environment up-to-date.

## Overview

Update Janitor is a Python-based tool designed to streamline the maintenance of various components in your environment. It provides a unified interface for updating:

- Homebrew packages
- Python packages
- APT packages (Debian-based Linux)
- Git repositories
- Apple system updates + App Store updates (macOS)

The tool features both interactive and non-interactive modes, live status tracking with rich terminal output, and robust error handling.

## Platform Support

Currently, Update Janitor supports:

- **macOS**: Homebrew, Python, Git repositories, and Apple system/App Store updates
- **Debian-based Linux**: APT packages, Homebrew (if installed), Python packages, and Git repositories

> **Note**: Windows support is planned for future releases.

## Features

- **Multiple Package Managers**: Supports common package managers across different platforms
- **Git Repository Management**: Automatically updates all Git repositories in a specified directory
- **Interactive Mode**: Choose which components to update
- **Non-Interactive Mode**: Run all updates without prompts (great for scheduled tasks)
- **Live Status Tracking**: A `rich` Live table refreshes in place without clearing scrollback
- **Dependency Management**: Uses uv and PEP 723 for inline dependency management (no requirements.txt)
- **Error Handling**: Centralized error logging with a persistent log file
- **Concurrent Updates**: Uses asyncio for efficient parallel processing
- **Single Instance**: A file lock prevents overlapping runs

## Requirements

- Python 3.9+
- uv (for dependency management)
- Sudo privileges (for the APT updater)
- Package managers corresponding to the components you want to update:
    - Homebrew (macOS/Linux)
    - Pip (Python)
    - Apt (Debian-based Linux)
    - Git
    - mas (macOS App Store updates, optional)

## Installation

1. Install uv:
```bash
pip install uv
```

Or via homebrew:
```bash
brew install uv
```

2. Clone the repository:
```bash
git clone https://github.com/bblinder/update-janitor.git
cd Update-Janitor
```

3. Run the script:
```bash
./main.py
```

Dependencies are declared inline in `main.py` via PEP 723; uv resolves them automatically.

## Usage

### Interactive Mode

```bash
./main.py
```

This will prompt you for each component, allowing you to choose which ones to update.

### Non-Interactive Mode

```bash
./main.py -y
```

Updates all available components without prompting.

### Debug Mode

```bash
./main.py --debug
```

Enables detailed logging for troubleshooting.

## Configuration

- `GITHUB_DIR` in `main.py`: directory scanned for Git repositories (default `~/Github`)
- `DOCTOR_PROBABILITY` in `updaters/homebrew_updater.py`: odds of running `brew doctor` on any given run (default `0.25`)
- `PYTHON_BIN` in `updaters/python_updater.py`: interpreter whose pip packages get upgraded (default `sys.executable`)

## Project Structure

```
update-janitor/
├── updaters/                # Package manager modules
│   ├── __init__.py          # Updater factory (availability detection)
│   ├── apple_updater.py     # macOS system + App Store updates
│   ├── apt_updater.py       # Linux APT package manager
│   ├── base_updater.py      # Base class: status tracking, sudo helper, async wrapper
│   ├── git_updater.py       # Git repository management
│   ├── homebrew_updater.py  # Homebrew package manager
│   └── python_updater.py    # Python package manager
├── utils/                   # Utility modules
│   ├── error_handler.py     # Error logging + signal handling
│   ├── password_manager.py  # Sudo password prompting and refresh
│   └── status_tracker.py    # Live status table (rich)
└── main.py                  # Entry point (PEP 723 inline dependencies)
```

## Extending the Tool

To add support for an additional package manager:

1. Create a new updater class in the `updaters` directory, inheriting from `BaseUpdater`
2. Set `name`, implement `update(args, password=None)`, and optionally override `is_available()` and `requires_sudo`
3. Register the class in `get_available_updaters()` in `updaters/__init__.py`

Status tracking, executor offload, sudo handling, and cancellation semantics are inherited from the base class — subclasses contain only the update logic itself.

## Future Enhancements

- Windows support with appropriate package managers (Chocolatey, Scoop, etc.)
- Configuration file support for customizing update behavior
- Support for more Linux distributions (RPM-based systems, Arch Linux, etc.)
- Scheduled updates with cron/launchd integration

## License

Apache 2 License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Acknowledgments

- [Rich](https://github.com/Textualize/rich) for beautiful terminal output
- [FileLock](https://github.com/tox-dev/py-filelock) for process locking
- [uv](https://github.com/astral-sh/uv) for fast, reliable Python packaging
