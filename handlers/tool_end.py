# Handler for the tool_end event: a terminal command finished, the agent is back to thinking (orange).

# =========================================
# Imports and defines
# =========================================
from handlers.common_functions import MODE_THINKING, write_mode

# =========================================
# Classes and functions
# =========================================
def handle_tool_end():
    """Writes the thinking mode, so the character turns back to orange."""
    write_mode(MODE_THINKING)
