"""Reserve this workspace's Mesen queue without blocking other projects."""
from pathlib import Path
import json
import subprocess


def workspace_sessions(records, workspace, rom):
    def normalized(value):
        return str(value or '').replace('\\', '/').casefold()

    needles = (normalized(Path(workspace).resolve()) + '/', normalized(Path(rom).resolve()))
    return [p for p in records if any(n in normalized(p.get('CommandLine')) for n in needles)]


def require_free_workspace(workspace, rom):
    command = ('Get-CimInstance Win32_Process -Filter "Name like \'%Mesen%\'" '
               '| Select-Object ProcessId,Name,CommandLine | ConvertTo-Json -Compress')
    output = subprocess.run(['powershell', '-NoProfile', '-Command', command],
                            capture_output=True, text=True, check=True).stdout.strip()
    records = json.loads(output) if output else []
    if isinstance(records, dict):
        records = [records]
    active = workspace_sessions(records, workspace, rom)
    if active:
        raise RuntimeError('SMB Mesen queue is occupied; existing sessions left untouched: '
                           + json.dumps(active))
    return records
