import os
import subprocess
import sys
from pathlib import Path

def bootstrap_venv():
    """
    Bootstraps a virtual environment for the script.
    This function checks if a virtual environment exists in the script directory.
    If not, it creates a new one ('venv')
    It then activates the venv and installs dependencies from requirements.txt, if present.
    """
    script_dir = Path(__file__).resolve().parent
    venv_dir = script_dir / "venv"
    venv_python = venv_dir / "bin" / "python"

    if not venv_dir.exists():
        print("No virtual environment found. Setting one up...")
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
        print(f"Virtual environment created at {venv_dir}")
    else:
        print(f"Virtual environment already exists at {venv_dir}")

    if sys.executable != str(venv_python):
        print(f"Activating virtual environment at {venv_dir}")
        os.execv(str(venv_python), [str(venv_python), *sys.argv])

    print(f"Using virtual environment at {venv_dir}")

    requirements_path = script_dir / "requirements.txt"
    if requirements_path.exists():
        print("Installing dependencies from requirements.txt...")
        subprocess.run(
            [str(venv_python), "-m", "pip", "install", "-r", str(requirements_path)],
            check=True,
        )
    else:
        print("requirements.txt not found, skipping dependency installation.")
