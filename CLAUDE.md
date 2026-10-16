# claude_assistant: how to connect it

A little pixel Claude on the desktop that shows what Claude Code is doing:

| Color | Meaning |
|---|---|
| 🟠 orange | Claude is thinking / writing |
| 🔴 red | Claude is running a terminal command (Bash / PowerShell) |
| 🟢 green | Claude finished the response; vanishes after 3 s |

It also vanishes if Claude Code is closed mid-response. Left drag moves it; right click closes it.

This file is for both humans and Claude agents who are asked to set it up.

## How it works (one paragraph)
Claude Code has **hooks**: commands it runs at fixed moments (prompt sent, tool started, response finished...).
Every hook here runs the same script, `hook_notify.py <event>`. That script checks the event is enabled in
`config\parameters.json` and calls `handlers\<event>.py`. The handlers talk to the character window
(`handlers\character_window.py`, PyQt6) through two files in `state\`: `mode` holds a number (`MODE_THINKING`,
`MODE_TOOL_RUNNING` in `handlers\common_functions.py`), and `alive` exists while a response runs; when it is deleted
the window turns green and closes. The window watches them with `QFileSystemWatcher`. The first handler starts the window; a
`QLockFile` (`state\.lock`) keeps it to one window.

## Setup

### 1. Requirements
Windows and Python 3 with the packages from `requirements.txt`:
```powershell
python -m pip install -r requirements.txt
```

### 2. Add the hooks to Claude Code
Hooks live in the user settings file: **`C:\Users\<user>\.claude\settings.json`** (`~/.claude/settings.json`).

Add the `"hooks"` block below as a top-level key of that JSON.
- **If the file already has a `"hooks"` key, merge these events into it.** Don't replace it, or other hooks will be lost.
- **Replace the two placeholders:** `<python_path>` with the full path of the Python interpreter (e.g. `C:/Python314/python.exe`)
  and `<project_dir_path>` with the full path of this project folder. Use forward slashes.

```json
"hooks": {
  "UserPromptSubmit": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "<python_path>",
          "args": ["<project_dir_path>/hook_notify.py", "response_start"],
          "async": true,
          "timeout": 10
        }
      ]
    }
  ],
  "PreToolUse": [
    {
      "matcher": "Bash|PowerShell",
      "hooks": [
        {
          "type": "command",
          "command": "<python_path>",
          "args": ["<project_dir_path>/hook_notify.py", "tool_start"],
          "async": true,
          "timeout": 10
        }
      ]
    }
  ],
  "PostToolUse": [
    {
      "matcher": "Bash|PowerShell",
      "hooks": [
        {
          "type": "command",
          "command": "<python_path>",
          "args": ["<project_dir_path>/hook_notify.py", "tool_end"],
          "async": true,
          "timeout": 10
        }
      ]
    }
  ],
  "PostToolUseFailure": [
    {
      "matcher": "Bash|PowerShell",
      "hooks": [
        {
          "type": "command",
          "command": "<python_path>",
          "args": ["<project_dir_path>/hook_notify.py", "tool_end"],
          "async": true,
          "timeout": 10
        }
      ]
    }
  ],
  "Stop": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "<python_path>",
          "args": ["<project_dir_path>/hook_notify.py", "response_end"],
          "async": true,
          "timeout": 10
        }
      ]
    }
  ]
}
```

Why it looks like this:
- `"command"` + `"args"` (exec form) runs Python directly, with no shell, so Windows paths need no quoting.
  It also makes Claude Code the **parent process** of the hook, which is how the window knows which process to watch.
- `"async": true` runs the hook in the background, so it never slows Claude down.
- `"matcher": "Bash|PowerShell"`: only terminal commands turn the character red, not file reads or edits.

### 3. Check it
1. In Claude Code, type `/hooks`. The 5 events above should be listed. Opening it also reloads the settings.
2. Send any prompt. The orange Claude should appear in the top right corner (or where you last dragged it).
3. Test by hand without Claude Code:
   ```powershell
   python hook_notify.py response_start
   python hook_notify.py response_end
   ```

## Turning it off
- One event: set `"enabled": false` for it in `config\parameters.json` (no restart needed).
- Everything: remove the hook entries above from `settings.json`.

## Notes for Claude agents changing this project
- Handlers must stay fast and silent. Errors are caught in `hook_notify.py`, so a broken handler never disturbs Claude Code.
- A new event needs 4 things: a hook entry in `settings.json`, an entry in `config\parameters.json`,
  `handlers\<event>.py` with a `handle_<event>()` function, and an import plus `EVENT_HANDLERS` entry in `hook_notify.py`.
- Settings (images, size, timings) live under `"character"` in `config\parameters.json`.
- A new character state needs a new `MODE_` number in `handlers\common_functions.py` and a branch in `CharacterWindow.update_state`.
- The code style follows the owner's global `CLAUDE.md` (pipeline-style entry functions, short docstrings, banners).
