# Handler for the response_end event: the agent finished its response (green for a few seconds, then gone).

# =========================================
# Imports and defines
# =========================================
from lib.common_functions import load_config, send_window_command

# =========================================
# Classes and functions
# =========================================
def handle(agent, hook_input):
    """Tells the window the response is done; it turns green and closes itself after a few seconds."""
    cfg = load_config()
    send_window_command(cfg, "end", attempts = 20)
