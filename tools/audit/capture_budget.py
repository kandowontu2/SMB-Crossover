"""Fail-closed storage limits for this project's generated emulator evidence.

Never delete user media or historical evidence. Reject old frame-dump fixtures
before they can grow unbounded; only terminate the process this module starts.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import os
import shutil
import subprocess
import threading
import time
from contextlib import contextmanager

WORKSPACE = Path(__file__).resolve().parents[2]
ARCHIVE = Path.home()/'Videos/SMB Crossover Archive'
ARCHIVE_BYTES = 30_000_000_000
ARCHIVE_FILES = 20_000
WORKSPACE_BYTES = 30_000_000_000
# A bounded traversal ceiling for the existing source/tool checkout, not a
# capture allowance. Captures still get only 64 files.
WORKSPACE_SCAN_FILES = 1_000_000
RUN_BYTES = 2_000_000_000
RUN_FILES = 64
MINIMUM_FREE = 25_000_000_000
LOCK = WORKSPACE/'build/capture.lock'
# Leave room for this module's receipt and the driver's final log.
PAYLOAD_BYTES = RUN_BYTES-1_000_000
PAYLOAD_FILES = RUN_FILES-2


class CaptureBudgetExceeded(RuntimeError):
    pass


@dataclass
class Inventory:
    bytes: int = 0
    files: int = 0
    directories: int = 0
    links_skipped: int = 0
    complete: bool = True


def inventory(root: Path, byte_limit: int, file_limit: int) -> Inventory:
    """Bounded traversal; junction targets are never traversed or counted twice."""
    result = Inventory()
    if not root.exists():
        return result
    pending = [root]
    queued = 1
    while pending:
        folder = pending.pop()
        result.directories += 1
        with os.scandir(folder) as entries:
            for entry in entries:
                if entry.is_symlink() or getattr(os.path, 'isjunction', lambda _: False)(entry.path):
                    result.links_skipped += 1
                    continue
                if entry.is_dir(follow_symlinks=False):
                    queued += 1
                    if queued > max(file_limit, 64):
                        result.complete = False
                        return result
                    pending.append(Path(entry.path))
                elif entry.is_file(follow_symlinks=False):
                    result.files += 1
                    result.bytes += entry.stat(follow_symlinks=False).st_size
                if result.files > file_limit or result.bytes > byte_limit:
                    result.complete = False
                    return result
    return result


@contextmanager
def capture_lease():
    """One capture process project-wide, including separate Python workers."""
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    with LOCK.open('a+b') as handle:
        handle.seek(0, os.SEEK_END)
        if not handle.tell():
            handle.write(b'0')
            handle.flush()
        handle.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            raise CaptureBudgetExceeded('Another project capture owns the storage lease; no capture started.') from error
        try:
            yield
        finally:
            handle.seek(0)
            if os.name == 'nt':
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def admit(current: Inventory, reserved_bytes: int, reserved_files: int,
          free_bytes: int) -> None:
    if not current.complete:
        raise CaptureBudgetExceeded('Archive exceeds its 30 GB / 20,000-file cap; no capture started.')
    if current.bytes + reserved_bytes > ARCHIVE_BYTES:
        raise CaptureBudgetExceeded('Capture would exceed the 30 GB archive cap; no capture started.')
    if current.files + reserved_files > ARCHIVE_FILES:
        raise CaptureBudgetExceeded('Capture would exceed the 20,000-file archive cap; no capture started.')
    if free_bytes < MINIMUM_FREE + reserved_bytes:
        raise CaptureBudgetExceeded('Capture must leave at least 25 GB free; no capture started.')


def preflight(output: Path, reserved_bytes: int = RUN_BYTES,
              reserved_files: int = RUN_FILES) -> dict:
    output = output.resolve()
    allowed = (WORKSPACE.resolve(), ARCHIVE.resolve())
    if not any(output != root and output.is_relative_to(root) for root in allowed):
        raise CaptureBudgetExceeded('Capture output must stay in the project or its existing archive; no alternate storage root.')
    if not 0 < reserved_bytes <= RUN_BYTES or not 0 < reserved_files <= RUN_FILES:
        raise CaptureBudgetExceeded('Capture reservation exceeds the per-run 2 GB / 64-file cap.')
    current = inventory(ARCHIVE, ARCHIVE_BYTES, ARCHIVE_FILES)
    disk = output if output.exists() else output.parent
    while not disk.exists():
        disk = disk.parent
    free = shutil.disk_usage(disk).free
    admit(current, reserved_bytes, reserved_files, free)
    workspace = inventory(WORKSPACE, WORKSPACE_BYTES, WORKSPACE_SCAN_FILES)
    growth = reserved_bytes if output.is_relative_to(WORKSPACE.resolve()) else 0
    if not workspace.complete or workspace.bytes+growth > WORKSPACE_BYTES:
        raise CaptureBudgetExceeded('Capture would exceed the 30 GB workspace cap; no capture started.')
    return dict(archive=str(ARCHIVE),archive_bytes=current.bytes,archive_files=current.files,
                workspace_bytes=workspace.bytes,workspace_files=workspace.files,
                reserved_bytes=reserved_bytes,reserved_files=reserved_files,free_bytes=free,
                archive_byte_cap=ARCHIVE_BYTES,archive_file_cap=ARCHIVE_FILES,
                run_byte_cap=RUN_BYTES,run_file_cap=RUN_FILES,minimum_free=MINIMUM_FREE)


def run_capped(command: list[str], *, output: Path, timeout: float) -> subprocess.CompletedProcess:
    """Run one owned emulator with preflight and a live output growth watchdog."""
    with capture_lease():
        return _run_owned(command, output=output, timeout=timeout)


def _run_owned(command: list[str], *, output: Path, timeout: float) -> subprocess.CompletedProcess:
    output = output.resolve()
    receipt = preflight(output)
    output.mkdir(parents=True, exist_ok=True)
    baseline = inventory(output, PAYLOAD_BYTES, PAYLOAD_FILES)
    if not baseline.complete:
        raise CaptureBudgetExceeded('The evidence output already exceeds the per-run cap.')
    stopped = threading.Event()
    violation: list[str] = []
    flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    started = time.monotonic()
    process = subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                               text=True,creationflags=flags)
    receipt.update(pid=process.pid,command=command,owned_process_only=True)

    def watch() -> None:
        try:
            while not stopped.wait(0.1):
                size = inventory(output,PAYLOAD_BYTES,PAYLOAD_FILES)
                free = shutil.disk_usage(output).free
                if not size.complete or free < MINIMUM_FREE:
                    violation.append('Evidence exceeded the 2 GB / 64-file limit or 25 GB free-space floor.')
                    if process.poll() is None:
                        process.terminate()
                    return
        except BaseException as error:
            violation.append('Storage watchdog failed closed: '+repr(error))
            if process.poll() is None:
                process.terminate()

    watcher = threading.Thread(target=watch,name='capture-storage-budget',daemon=True)
    watcher.start()
    try:
        stdout,stderr = process.communicate(timeout=timeout)
    except BaseException:
        if process.poll() is None:
            process.terminate()
        try:
            process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate(timeout=5)
        raise
    finally:
        stopped.set()
        watcher.join(timeout=2)
        final = inventory(output,PAYLOAD_BYTES,PAYLOAD_FILES)
        if not final.complete and not violation:
            violation.append('Evidence exceeded the per-run cap before process exit.')
        total = inventory(ARCHIVE, ARCHIVE_BYTES, ARCHIVE_FILES)
        if not total.complete:
            violation.append('Archive exceeded its 30 GB / 20,000-file cap; capture result rejected.')
        receipt.update(seconds=round(time.monotonic()-started,3),returncode=process.returncode,
                       violations=violation,final=vars(final),archive_final=vars(total))
        (output/'capture-budget.json').write_text(json.dumps(receipt,indent=2)+'\n')
    if violation:
        raise CaptureBudgetExceeded(violation[0])
    return subprocess.CompletedProcess(command,process.returncode,stdout,stderr)
