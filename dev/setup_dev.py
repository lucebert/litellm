#!/usr/bin/env python3
"""Development environment setup script."""
import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd: list[str], check: bool = True) -> None:
    """Run a command with proper output handling."""
    try:
        subprocess.run(cmd, check=check, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command {' '.join(cmd)}: {e}")
        sys.exit(1)

def setup_dev_environment() -> None:
    """Set up the development environment."""
    # Get project root directory
    project_root = Path(__file__).parent.parent

    # Install dependencies
    print("Installing production dependencies...")
    run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    print("Installing development dependencies...")
    run_command([sys.executable, "-m", "pip", "install", "-r", "dev-requirements.txt"])

    # Initialize pre-commit
    print("Setting up pre-commit hooks...")
    run_command([sys.executable, "-m", "pip", "install", "pre-commit"])
    run_command(["pre-commit", "install"])

    print("\nDevelopment environment setup complete!")

if __name__ == "__main__":
    setup_dev_environment()