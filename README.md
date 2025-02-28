# Update Janitor
A system update utility that automates the process of keeping your environment up-to-date.


## Overview

Update Janitor is a Python-based tool designed to streamline the maintenance of various components in your environment. It provides a unified interface for updating:

- Homebrew packages
- Python packages
- APT packages (Linux)
- Ruby gems (macOS)
- Git repositories
- Apple system updates + App store updates (macOS)

The tool features both interactive and non-interactive modes, real-time status tracking with rich terminal output, and robust error handling.

## Features

- **Multiple Package Managers**: Supports common package managers across different platforms
- **Git Repository Management**: Automatically updates all Git repositories in a specified directory
- **Interactive Mode**: Choose which components to update
- **Non-Interactive Mode**: Run all updates without prompts (great for scheduled tasks)
- **Real-time Status Tracking**: Visual feedback on update progress
- **Virtual Environment**: Automatically bootstraps a Python virtual environment
- **Error Handling**: Comprehensive error management with logging
- **Concurrent Updates**: Uses asyncio for efficient parallel processing


## Requirements

- Python 3.9+
- Sudo privileges (for some updaters)
- Package managers corresponding to the components you want to update:
    - Homebrew (macOS/Linux)
    - Pip (Python)
    - Apt (Linux)
    - Gem (Ruby, macOS)
    - Git


## Installation

1. Clone the repository:

```bash
git clone https://github.com/bblinder/update-janitor.git
cd Update-Janitor
```

2. Run the script:

```bash
python3 main.py
```


The script will automatically set up a virtual environment and install required dependencies on first run.

## Usage

### Interactive Mode

```bash
python3 main.py
```

This will prompt you for each component, allowing you to choose which ones to update.

### Non-Interactive Mode

```bash
python3 main.py -y
```

Updates all available components without prompting.

### Debug Mode

```bash
python3 main.py --debug
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
├── bootstrap.py             # Virtual environment setup
├── main.py                  # Main application entry point
└── requirements.txt         # Python dependencies
```


## Extending the Tool

To add support for additional package managers:

1. Create a new updater class in the `updaters` directory, inheriting from `BaseUpdater`
2. Implement the required methods: `update()` and `update_async()`
3. Add your updater to the `get_available_updaters()` function in `updaters/__init__.py`

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
