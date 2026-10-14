# Called by agent hooks (Claude Code, later Codex) and passes each event to its handler in hook_handlers\.
# Usage: python hook_notify.py <agent> <event>     e.g. python hook_notify.py claude response_end

# =========================================
# Imports and defines
# =========================================
import argparse
import importlib.util
import json
import sys

from lib.common_functions import PROJECT_DIR, load_config

HANDLERS_DIR = PROJECT_DIR / "hook_handlers"

# =========================================
# Classes and functions
# =========================================
def hook_notify(agent, event):
    cfg = load_config()
    if not is_hook_enabled(cfg, event):
        return
    hook_input = read_hook_input()
    handler = load_handler(cfg, event)
    handler.handle(agent, hook_input)

def is_hook_enabled(cfg, event):
    hooks_cfg = cfg["hooks"]
    if event not in hooks_cfg:
        return False
    return bool(hooks_cfg[event]["enabled"])

def read_hook_input():
    """Reads the JSON the agent passes on stdin; returns an empty dict when run by hand."""
    if sys.stdin is None or sys.stdin.isatty():
        return {}
    raw_text = sys.stdin.buffer.read().decode("utf-8-sig", errors = "replace")
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        return {}

def load_handler(cfg, event):
    """Loads the event's handler script from hook_handlers\\ as a module, so we can call its handle()."""
    handler_file = cfg["hooks"][event]["handler"]
    handler_path = HANDLERS_DIR / handler_file
    spec = importlib.util.spec_from_file_location(handler_path.stem, handler_path)
    handler = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(handler)
    return handler

# =========================================
# Main
# =========================================
def main():
    parser = argparse.ArgumentParser(description = "Pass an agent hook event to its handler.")
    parser.add_argument("agent", help = "who sent the event, e.g. claude or codex")
    parser.add_argument("event", help = "event name as defined in config/parameters.json, e.g. response_end")
    args = parser.parse_args()
    try:
        hook_notify(args.agent, args.event)
    except Exception as error:
        print(f"hook_notify error: {error}", file = sys.stderr)

if __name__ == "__main__":
    main()
