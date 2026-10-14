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
Every hook here runs the same script, `hook_notify.py <agent> <event>`. That script checks the event is enabled in
`config\parameters.json` and calls `hook_handlers\<event>.py`. The handlers talk to the character window
(`character_window.py`, PyQt6) by sending one word to `127.0.0.1:50556`. The first handler starts the window
if it is not running.

## Setup

### 1. Requirements
Windows and Python 3 with the packages from `requirements.txt`:
```powershell
C:\Python314\python.exe -m pip install -r requirements.txt
```

### 2. Add the hooks to Claude Code
Hooks live in the user settings file: **`C:\Users\<user>\.claude\settings.json`** (`~/.claude/settings.json`).

Add the `"hooks"` block below as a top-level key of that JSON.
- **If the file already has a `"hooks"` key, merge these events into it.** Don't replace it, or other hooks will be lost.
- **Fix the two paths if needed:** the Python interpreter (`C:/Python314/python.exe`) and the project folder
  (`C:/Users/drorm/main_dir/programming/scripts/claude_assistant`). Use forward slashes.

```json
"hooks": {
  "UserPromptSubmit": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "C:/Python314/python.exe",
          "args": ["C:/Users/drorm/main_dir/programming/scripts/claude_assistant/hook_notify.py", "claude", "response_start"],
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
          "command": "C:/Python314/python.exe",
          "args": ["C:/Users/drorm/main_dir/programming/scripts/claude_assistant/hook_notify.py", "claude", "tool_start"],
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
          "command": "C:/Python314/python.exe",
          "args": ["C:/Users/drorm/main_dir/programming/scripts/claude_assistant/hook_notify.py", "claude", "tool_end"],
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
          "command": "C:/Python314/python.exe",
          "args": ["C:/Users/drorm/main_dir/programming/scripts/claude_assistant/hook_notify.py", "claude", "tool_end"],
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
          "command": "C:/Python314/python.exe",
          "args": ["C:/Users/drorm/main_dir/programming/scripts/claude_assistant/hook_notify.py", "claude", "response_end"],
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
2. Send any prompt. The orange Claude should appear in the bottom right corner.
3. Test by hand without Claude Code:
   ```powershell
   '{}' | C:\Python314\python.exe hook_notify.py claude response_start
   '{}' | C:\Python314\python.exe hook_notify.py claude response_end
   ```

## Turning it off
- One event: set `"enabled": false` for it in `config\parameters.json` (no restart needed).
- Everything: remove the hook entries above from `settings.json`.

## Notes for Claude agents changing this project
- Handlers must stay fast and silent. Errors are caught in `hook_notify.py`, so a broken handler never disturbs Claude Code.
- A new event needs 3 things: a hook entry in `settings.json`, an entry in `config\parameters.json`, and
  `hook_handlers\<event>.py` with a `handle(agent, hook_input)` function.
- Settings (images, size, port, timings) live under `"character"` in `config\parameters.json`.
- If port 50556 is taken by another program, the window never shows up. Change `"port"` there.
- The code style follows the owner's global `CLAUDE.md` (pipeline-style entry functions, short docstrings, banners).
