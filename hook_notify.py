# Called by Claude Code hooks and passes each event to its handler in handlers\.
# Usage: python hook_notify.py <event>     e.g. python hook_notify.py response_end

# =========================================
# Imports and defines
# =========================================
import argparse
import sys

from handlers.common_functions import load_config
from handlers.response_end import handle_response_end
from handlers.response_start import handle_response_start
from handlers.tool_end import handle_tool_end
from handlers.tool_start import handle_tool_start

EVENT_HANDLERS = {
    "response_start": handle_response_start,
    "tool_start": handle_tool_start,
    "tool_end": handle_tool_end,
    "response_end": handle_response_end,
}

# =========================================
# Classes and functions
# =========================================
def hook_notify(event):
    """Calls the event's handler, unless the event is disabled in config/parameters.json."""
    cfg = load_config()
    if not is_hook_enabled(cfg, event):
        return
    EVENT_HANDLERS[event]()

def is_hook_enabled(cfg, event):
    """Returns True only for events that have a handler and are enabled in the config."""
    hooks_cfg = cfg["hooks"]
    if event not in EVENT_HANDLERS or event not in hooks_cfg:
        return False
    return bool(hooks_cfg[event]["enabled"])

# =========================================
# Main
# =========================================
def main():
    parser = argparse.ArgumentParser(description = "Pass a Claude Code hook event to its handler.")
    parser.add_argument("event", help = "event name, e.g. response_end")
    args = parser.parse_args()
    try:
        hook_notify(args.event)
    except Exception as error:
        print(f"hook_notify error: {error}", file = sys.stderr)

if __name__ == "__main__":
    main()
