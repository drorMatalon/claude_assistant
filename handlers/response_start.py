# Handler for the response_start event: the user sent a prompt and the agent started thinking (orange).

# =========================================
# Imports and defines
# =========================================
import os
import subprocess
import sys

from handlers.common_functions import ALIVE_PATH, MODE_THINKING, PROJECT_DIR, write_mode

# =========================================
# Classes and functions
# =========================================
def handle_response_start():
    """Writes the state files and starts the window; if a window is already running, the new one exits and the old one follows the files.
    The agent runs this hook directly, so our parent process is the agent; the window watches it and vanishes if it dies."""
    agent_pid = os.getppid()
    write_mode(MODE_THINKING)
    with open(ALIVE_PATH, "w", encoding = "utf-8") as alive_file:
        alive_file.write(str(agent_pid))
    start_window()

def start_window():
    """Starts handlers\\character_window.py with pythonw (no console), detached from the agent.
    It runs as a module from the project folder, so its imports are found."""
    pythonw_path = sys.executable.replace("python.exe", "pythonw.exe")
    command = [pythonw_path, "-m", "handlers.character_window"]
    flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
    try:
        # Breaking away from the agent's job keeps the window alive if the agent cleans up its hook processes
        start_detached_process(command, flags | subprocess.CREATE_BREAKAWAY_FROM_JOB)
    except OSError:
        start_detached_process(command, flags)

def start_detached_process(command, flags):
    """Starts the command with no link to the hook's console or pipes, so the hook can finish right away."""
    no_pipes = subprocess.DEVNULL
    subprocess.Popen(command, cwd = PROJECT_DIR, creationflags = flags, stdin = no_pipes, stdout = no_pipes, stderr = no_pipes)
