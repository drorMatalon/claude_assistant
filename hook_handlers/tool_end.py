# Handler for the tool_end event: a terminal command finished, the agent is back to thinking (orange).

# =========================================
# Imports and defines
# =========================================
from lib.common_functions import load_config, send_window_command

# =========================================
# Classes and functions
# =========================================
def handle(agent, hook_input):
    """Tells the window a terminal command finished; it turns orange once no command is left running."""
    cfg = load_config()
    send_window_command(cfg, "tool_end", attempts = 8)
