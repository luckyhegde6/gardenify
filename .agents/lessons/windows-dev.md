# Lessons — Windows Dev Workflow (Detached Processes, Server Management)

## 2026-07-29 → 07-30: Detached Process Launch on Windows — Use PowerShell `Start-Process` or `start "Title" cmd /c`

**Context:** Launching long-running servers (Expo dev server, Python uvicorn backend) from the agent's bash tool on Windows. The bash tool blocks until the command exits, so servers must run detached.

**Verified working patterns (all tested):**

```powershell
# Backend (detached, normal window) — run from project root so Python imports the api module
powershell -Command "Start-Process -FilePath 'cmd' -ArgumentList '/c cd /d F:\Local_git\gardenify && python -m uvicorn api.main:app --reload --port 8000' -WindowStyle Normal"

# Expo (must use direct .cmd path, NOT npx — npx.cmd is a batch file Start-Process can't run)
powershell -Command "Start-Process -FilePath 'F:\Local_git\gardenify\node_modules\.bin\expo.cmd' -ArgumentList 'start --port 8083' -WorkingDirectory 'F:\Local_git\gardenify' -WindowStyle Normal"

# Alternative that returns immediately — opens new window
start "Gardenify-Backend" cmd /c "cd /d F:\Local_git\gardenify && python -m uvicorn api.main:app --reload --port 8000"
```

**Patterns that BLOCK (never use):**

- `start /B command` — same console group, blocks the agent shell ❌
- `python -c "subprocess.Popen(..., DETACHED_PROCESS)"` — python.exe parent waits for the child ❌
- `subprocess.Popen(creationflags=0x00000008)` — hangs parent ❌
- `task` subagent wrapping any of the above — the subagent's own bash tool blocks ❌
- `subprocess.run(['curl', ...])` — hangs on Windows in this env ❌

**Key details:**

- `Start-Process` without `-Wait` returns immediately; the spawned cmd.exe is independent of the bash tool's shell, so it survives timeout/kill.
- Always include `-ArgumentList` as a single string to avoid parameter splitting.
- Use `-WindowStyle Normal` (debuggable) or `-WindowStyle Hidden` (headless).
- `start /B` runs in same process group, killed on timeout — do not use.

## 2026-07-30: Verify PID Before Killing Servers

**Context:** Made edits to `plantnet.py` but the server kept returning old responses. `taskkill` commands were killing wrong PIDs (netstat returned a different PID each time — children of the startup window). The real server (7h uptime) survived all kill attempts.

**Fix:**

1. Always verify `netstat -ano | findstr ":PORT "` to get the actual listening PID.
2. Kill with `taskkill /F /PID <actual_pid>`.
3. Verify port is free with `netstat` again.
4. Start new server.
5. Verify with `uptime_seconds` (should be < 10).

**Working launch patterns:**

- `subprocess.Popen(['python','-m','uvicorn','api.main:app','--port','8000'], creationflags=0x00000010)` — `CREATE_NEW_CONSOLE`, truly detached ✅
- `start "" python -m uvicorn api.main:app --host 0.0.0.0 --port 8000` — opens new window ✅
