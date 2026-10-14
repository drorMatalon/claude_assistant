# =========================================
# Imports and defines
# =========================================
import json
import socket
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_DIR / "config" / "parameters.json"
SECONDS_BETWEEN_ATTEMPTS = 0.25

# =========================================
# Classes and functions
# =========================================
def load_config():
    """Loads the JSON parameters file of the project."""
    with open(CONFIG_PATH, encoding = "utf-8") as config_file:
        return json.load(config_file)

def send_window_command(cfg, command, attempts):
    """Sends a one-word command to the character window over localhost.
    Retries a few times, because the window may still be starting; returns False if it never answered."""
    port = int(cfg["character"]["port"])
    for attempt in range(attempts):
        try:
            with socket.create_connection(("127.0.0.1", port), timeout = 0.5) as connection:
                connection.sendall(command.encode("utf-8"))
                return True
        except OSError:
            time.sleep(SECONDS_BETWEEN_ATTEMPTS)
    return False
