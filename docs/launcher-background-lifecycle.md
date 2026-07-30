# Hakoniwa Launcher background lifecycle

The Launcher can be started in the background with an explicit session file. The session file is the caller-owned handle used for later lifecycle operations; callers do not need to know POSIX or Windows signal semantics.

## Start

```bash
python -m hakoniwa_pdu.apps.launcher.hako_launcher path/to/launch.json \
  --background ./run/launcher-session.json
```

The command returns only after the background Launcher has activated the assets, completed `hako-cmd start`, opened its localhost control endpoint, and written the session file.

The Launcher writes its own stdout/stderr to `<session-file>.log` and prints a JSON summary containing the session path, PID, state, and log path.

## Status

```bash
python -m hakoniwa_pdu.apps.launcher.hako_launcher_ctl \
  status ./run/launcher-session.json
```

The command prints a JSON response such as:

```json
{"ok": true, "pid": 12345, "state": "RUNNING"}
```

## Terminate

```bash
python -m hakoniwa_pdu.apps.launcher.hako_launcher_ctl \
  terminate ./run/launcher-session.json
```

`terminate` calls the running Launcher's `LauncherService.terminate()` through a localhost control endpoint. Child-process cleanup therefore remains owned by the Launcher, including the existing OS-specific process-group behavior.

The session file is retained after termination with `state: "TERMINATED"` for post-run inspection.

## Session ownership and stale files

The session file contains the Launcher's PID, localhost control endpoint, and a random token. The control endpoint verifies both the token and expected PID before accepting lifecycle commands.

If the session file is stale and the endpoint cannot be reached, `hako_launcher_ctl` reports `STALE` and does not fall back to killing the recorded PID. This avoids terminating an unrelated process after PID reuse.

Starting with `--background` refuses to overwrite a live session. A terminal or unreachable stale session file at the same explicit path may be replaced by the new run.
