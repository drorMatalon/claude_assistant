# Handler for the tool_start event: the agent started a terminal command (red).

# =========================================
# Imports and defines
# =========================================
from handlers.common_functions import MODE_TOOL_RUNNING, write_mode

# =========================================
# Classes and functions
# =========================================
def handle_tool_start():
    """Writes the tool running mode, so the character turns red."""
    write_mode(MODE_TOOL_RUNNING)
