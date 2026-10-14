# Handler for the tool_start event: the agent started a terminal command (red).

# =========================================
# Imports and defines
# =========================================
from lib.common_functions import load_config, send_window_command

# =========================================
# Classes and functions
# =========================================
def handle(agent, hook_input):
    """Tells the window a terminal command is running, so the character turns red."""
    cfg = load_config()
    send_window_command(cfg, "tool_start", attempts = 8)
