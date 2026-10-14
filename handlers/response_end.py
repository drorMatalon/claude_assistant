# Handler for the response_end event: the agent finished its response (green for a few seconds, then gone).

# =========================================
# Imports and defines
# =========================================
from handlers.common_functions import delete_alive_file

# =========================================
# Classes and functions
# =========================================
def handle_response_end():
    """Deletes the alive file; the window sees it is gone, turns green and closes itself after a few seconds."""
    delete_alive_file()
