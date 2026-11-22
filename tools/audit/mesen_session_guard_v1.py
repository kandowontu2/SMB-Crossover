"""Reserve this workspace's Mesen queue without blocking other projects."""
from pathlib import Path
import json
import re
import subprocess
import time


def workspace_sessions(records, workspace, rom):
    def normalized(value):
        return str(value or '').replace('\\', '/').casefold()

    needles = (normalized(Path(workspace).resolve()) + '/', normalized(Path(rom).resolve()))
    return [p for p in records if any(n in normalized(p.get('CommandLine')) for n in needles)]


def interactive_session(record, workspace, rom):
    """Accept only a plain executable-plus-ROM invocation as interactive."""
    args = re.findall(r'"[^"]*"|\S+', str(record.get('CommandLine') or ''))
    if len(args) != 2:
        return False
    target = Path(args[1].strip('"')).resolve()
    return (target.suffix.casefold() == '.nes'
            and (target == Path(rom).resolve()
                 or target.is_relative_to(Path(workspace).resolve())))


def require_free_workspace(workspace, rom, *, allow_interactive=False):
    command = ('Get-CimInstance Win32_Process -Filter "Name like \'%Mesen%\'" '
               '| Select-Object ProcessId,Name,CommandLine | ConvertTo-Json -Compress')
    for attempt in range(3):
        try:
            output = subprocess.run(['powershell', '-NoProfile', '-Command', command],
                                    capture_output=True, text=True, check=True, timeout=12).stdout.strip()
            records = json.loads(output) if output else []
            break
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, json.JSONDecodeError):
            if attempt == 2:
                raise
            time.sleep(0.25 * (attempt + 1))
    if isinstance(records, dict):
        records = [records]
    active = workspace_sessions(records, workspace, rom)
    if allow_interactive:
        active = [p for p in active if not interactive_session(p, workspace, rom)]
    if active:
        raise RuntimeError('SMB Mesen queue is occupied; existing sessions left untouched: '
                           + json.dumps(active))
    return records
