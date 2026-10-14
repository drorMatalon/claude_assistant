# =========================================
# Imports and defines
# =========================================
import json
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_DIR / "config" / "parameters.json"
STATE_DIR = PROJECT_DIR / "state"
# The window lives while this file exists: response_start creates it, response_end deletes it
ALIVE_PATH = STATE_DIR / ".alive"
# Holds one of the MODE_ numbers below, so the window knows which character to show
MODE_PATH = STATE_DIR / ".mode"
MODE_THINKING = 1
MODE_TOOL_RUNNING = 2
DELETE_ATTEMPTS = 10
SECONDS_BETWEEN_ATTEMPTS = 0.05

# =========================================
# Classes and functions
# =========================================
def load_config():
    """Loads the JSON parameters file of the project."""
    with open(CONFIG_PATH, encoding = "utf-8") as config_file:
        return json.load(config_file)

def write_mode(mode):
    """Writes what the agent is doing now (one of the MODE_ numbers) for the window to show."""
    STATE_DIR.mkdir(parents = True, exist_ok = True)
    with open(MODE_PATH, "w", encoding = "utf-8") as mode_file:
        mode_file.write(str(mode))

def delete_alive_file():
    """Deletes the alive file, which tells the window the response is over.
    Retries, because Windows refuses to delete a file while the window is reading it."""
    for attempt in range(DELETE_ATTEMPTS):
        try:
            ALIVE_PATH.unlink(missing_ok = True)
            return
        except PermissionError:
            time.sleep(SECONDS_BETWEEN_ATTEMPTS)
