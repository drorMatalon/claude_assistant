# Runs any command with the character on screen: orange while it runs, green when it finishes.
# Usage: python scripts\tracker.py <command>     e.g. python scripts\tracker.py py main.py

# =========================================
# Imports and defines
# =========================================
import argparse
import os
import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from handlers.response_end import handle_response_end
from handlers.response_start import handle_response_start

# =========================================
# Classes and functions
# =========================================
def tracker(command):
    """Shows the character, runs the command and ends the character even if the command fails or is stopped with Ctrl+C.
    The window watches this script's parent (the terminal), so closing the terminal also closes it."""
    # Set before the window starts, so the window and the command both inherit it; it is gone when this script exits
    os.environ["TRACKER_MODE"] = "TRUE"
    handle_response_start()
    try:
        # Runs through cmd, so files like script.py or run.bat open with their program, as when typed in the terminal
        return subprocess.run(command, shell = True).returncode
    finally:
        handle_response_end()

# =========================================
# Main
# =========================================
def main():
    parser = argparse.ArgumentParser(description = "Run a command with the character on screen")
    parser.add_argument("command", nargs = argparse.REMAINDER, help = "the command to run, e.g. py main.py")
    args = parser.parse_args()
    if not args.command:
        parser.error("give a command to run, e.g. python scripts\\tracker.py py main.py")
    sys.exit(tracker(args.command))

if __name__ == "__main__":
    main()
