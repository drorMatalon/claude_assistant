# claude_assistant

A little desktop character that shows what an AI agent (Claude Code, later Codex) is doing:
🟠 thinking, 🔴 running a terminal command, 🟢 done (for a few seconds, then it vanishes).

## Flow
```
Claude Code hook ──> hook_notify.py <agent> <event> ──> hook_handlers\<event>.py  handle(agent, hook_input)
                       reads config\parameters.json        │
                       skips disabled hooks                │  one-word command over 127.0.0.1:50556
                                                           ▼
                                                  character_window.py (PyQt6)
                                                  start → 🟠   tool_start → 🔴   tool_end → 🟠   end → 🟢 → close
```
`response_start` also launches the window (pythonw, detached) when it is not already running.

## Hooks
| Event            | Agent hook                                      | Defined in                              | Handler                            | Character      |
|------------------|-------------------------------------------------|-----------------------------------------|------------------------------------|----------------|
| `response_start` | Claude `UserPromptSubmit`                       | `C:\Users\drorm\.claude\settings.json`  | `hook_handlers\response_start.py`  | 🟠 appears     |
| `tool_start`     | Claude `PreToolUse` (Bash, PowerShell)          | `C:\Users\drorm\.claude\settings.json`  | `hook_handlers\tool_start.py`      | 🔴             |
| `tool_end`       | Claude `PostToolUse`, `PostToolUseFailure` (Bash, PowerShell) | `C:\Users\drorm\.claude\settings.json`  | `hook_handlers\tool_end.py`        | 🟠             |
| `response_end`   | Claude `Stop`                                   | `C:\Users\drorm\.claude\settings.json`  | `hook_handlers\response_end.py`    | 🟢 then gone   |

- Turn a hook on/off with `"enabled"` in `config\parameters.json` (no restart needed).
- To view the hooks inside Claude Code, type `/hooks`.

## The character
- `character_window.py`: frameless, always on top, background made transparent.
- First time in the bottom right corner. **Left drag** moves it; its last place is saved on close to `outputs\character_position.json` and reused next time.
- **Right click** closes it by hand.
- Watches the agent process (the hook's parent PID, e.g. `claude.exe`) every `agent_check_seconds` and vanishes if it dies, e.g. when the terminal is closed mid-response.
- Images, size, done time, margin and port are under `"character"` in `config\parameters.json`.
- `scripts\create_character_colors.py` makes the red/green images from the orange `data\claude_bot.jpg`. Edit `NEW_COLORS` there for more colors.

## Add a new hook
1. Add the event to Claude's `settings.json`, calling `hook_notify.py claude <event>`.
2. Add `<event>` with `enabled` and `handler` to `config\parameters.json`.
3. Create `hook_handlers\<event>.py` with a `handle(agent, hook_input)` function.

## Test by hand
```powershell
'{}' | C:\Python314\python.exe hook_notify.py claude response_start
'{}' | C:\Python314\python.exe hook_notify.py claude tool_start
'{}' | C:\Python314\python.exe hook_notify.py claude response_end
```
