# Update Janitor

A system update utility that automates the process of keeping your environment up-to-date.

## Overview

Update Janitor is a Python-based tool designed to streamline the maintenance of various components in your environment. It provides a unified interface for updating:

- Homebrew packages
- Python packages
- APT packages (Debian-based Linux)
- Ruby gems (macOS)
- Git repositories
- Apple system updates + App store updates (macOS)

The tool features both interactive and non-interactive modes, real-time status tracking with rich terminal output, and robust error handling.

## Platform Support

Currently, Update Janitor supports:

- **macOS**: Full support including Homebrew, Python, Ruby gems, Git repositories, and Apple system updates
- **Debian-based Linux**: Support for APT packages, Homebrew (if installed), Python packages, and Git repositories

> **Note**: Windows support is planned for future releases.

## Features

- **Multiple Package Managers**: Supports common package managers across different platforms
- **Git Repository Management**: Automatically updates all Git repositories in a specified directory
- **Interactive Mode**: Choose which components to update
- **Non-Interactive Mode**: Run all updates without prompts (great for scheduled tasks)
- **Real-time Status Tracking**: Visual feedback on update progress
- **Dependency Management**: Uses uv and PEP 723 for efficient dependency management
- **Error Handling**: Comprehensive error management with logging
- **Concurrent Updates**: Uses asyncio for efficient parallel processing


## Requirements

- Python 3.9+
- uv (for dependency management)
- Sudo privileges (for some updaters)
- Package managers corresponding to the components you want to update:
    - Homebrew (macOS/Linux)
    - Pip (Python)
    - Apt (Debian-based Linux)
    - Gem (Ruby, macOS)
    - Git


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

The script will automatically handle dependencies using uv and PEP 723.

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

By default, the script looks for Git repositories in `~/Github`. You can modify this path in `main.py` by changing the `GITHUB_DIR` constant.

## Project Structure

```
update-janitor/
├── updaters/                # Package manager modules
│   ├── __init__.py          # Updater initialization
│   ├── apple_updater.py     # macOS system updates
│   ├── apt_updater.py       # Linux APT package manager
│   ├── base_updater.py      # Base class for updaters
│   ├── git_updater.py       # Git repository management
│   ├── homebrew_updater.py  # Homebrew package manager
│   ├── python_updater.py    # Python package manager
│   └── ruby_updater.py      # Ruby gems manager
├── utils/                   # Utility modules
│   ├── error_handler.py     # Error management
│   ├── password_manager.py  # Secure password handling
│   └── status_tracker.py    # Update status visualization
├── main.py                  # Main application entry point (with uv integration)
└── requirements.txt         # Python dependencies (referenced by PEP 723)
```


## Extending the Tool

To add support for additional package managers:

1. Create a new updater class in the `updaters` directory, inheriting from `BaseUpdater`
2. Implement the required methods: `update()` and `update_async()`
3. Add your updater to the `get_available_updaters()` function in `updaters/__init__.py`

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
