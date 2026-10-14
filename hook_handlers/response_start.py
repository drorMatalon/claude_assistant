# Handler for the response_start event: the user sent a prompt and the agent started thinking (orange).

# =========================================
# Imports and defines
# =========================================
import os
import subprocess
import sys
from pathlib import Path

from lib.common_functions import PROJECT_DIR, load_config, send_window_command

# =========================================
# Classes and functions
# =========================================
def handle(agent, hook_input):
    """Turns a running character orange, or starts the window (orange) if it is not running.
    The agent runs this hook directly, so our parent process is the agent; the window watches it and vanishes if it dies."""
    cfg = load_config()
    agent_pid = os.getppid()
    if send_window_command(cfg, f"start {agent_pid}", attempts = 1):
        return
    pythonw_path = Path(sys.executable).with_name("pythonw.exe")
    window_script = PROJECT_DIR / "character_window.py"
    command = [str(pythonw_path), str(window_script), "--agent-pid", str(agent_pid)]
    detached = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
    try:
        # Breaking away from the agent's job object keeps the window alive if the agent cleans up its hook processes
        start_window_process(command, detached | subprocess.CREATE_BREAKAWAY_FROM_JOB)
    except OSError:
        start_window_process(command, detached)

def start_window_process(command, creation_flags):
    """Starts the command fully detached from the hook's console and pipes."""
    subprocess.Popen(
        command,
        cwd = PROJECT_DIR,
        creationflags = creation_flags,
        stdin = subprocess.DEVNULL,
        stdout = subprocess.DEVNULL,
        stderr = subprocess.DEVNULL,
    )
