# claude_assistant

A little desktop Claude that shows what Claude Code is doing: 🟠 thinking, 🔴 running a terminal command, 🟢 done.

## Install
1. Install the requirements:
   ```powershell
   C:\Python314\python.exe -m pip install -r requirements.txt
   ```
2. Connect the hooks: ask Claude Code to *"read CLAUDE.md and set up the hooks"*.

## Flow
```
┌─────────────┐  hook   ┌────────────────┐  call   ┌─────────────────────┐
│ Claude Code │ ──────> │ hook_notify.py │ ──────> │ handlers\<event>.py │
└─────────────┘         └────────────────┘         └──────────┬──────────┘
                                                              │ write / delete
                                                              ▼
┌──────────────────────────────┐   watch   ┌─────────────────────────────┐
│ handlers\character_window.py │ <──────── │ state\.mode    state\.alive │
│         🟠 / 🔴 / 🟢          │           └─────────────────────────────┘
└──────────────────────────────┘
```

## Supported hooks
| Event            | Claude Code hook                                       | Character             |
|------------------|--------------------------------------------------------|-----------------------|
| `response_start` | `UserPromptSubmit`                                     | 🟠 appears            |
| `tool_start`     | `PreToolUse` (Bash, PowerShell)                        | 🔴                    |
| `tool_end`       | `PostToolUse`, `PostToolUseFailure` (Bash, PowerShell) | 🟠                    |
| `response_end`   | `Stop`                                                 | 🟢, then vanishes     |

Each one can be turned off with `"enabled"` in `config\parameters.json`.
