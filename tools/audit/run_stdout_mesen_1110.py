"""Run one controller-only Mesen test with bounded in-memory receipts/images.

Keeps the existing project capture lease, free-space/workspace preflight and
live capture watchdog. No wrapper, log, screenshot, state or receipt file is
created. The Lua source is a repository file and must print a final receipt.
Use the ordinary run_bounded_build_v1 wrapper with the exact output root.
"""
import argparse
import base64
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import threading
import time

import build_storage_guard_v1 as G
import capture_budget as C
from mesen_session_guard_v1 import require_free_workspace

R = Path(__file__).resolve().parents[2]


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def run(script, rom, output, expected, timeout, variant=0, extra_env=None):
    assert digest(rom) == expected
    before_source = digest(script)
    source = script.read_text(encoding='utf-8')
    executable_source = '\n'.join(line.split('--', 1)[0] for line in source.splitlines())
    assert not re.search(r'\bio\s*[.:]|\bemu\s*[.:]\s*(?:write|save|load)|os\s*\.\s*(?:execute|remove|rename)', executable_source), 'Controller source may not write files or emulated state'
    assert 'SMB_NATIVE_RECEIPT ' in source
    emulator = Path(os.environ.get('MESEN') or shutil.which('Mesen') or 'C:/mesen2/Mesen.exe')
    assert emulator.is_file()
    assert output.resolve().is_relative_to(R / 'build')
    assert 1 <= timeout <= 240
    # This lock already exists in the shared queue. Do not introduce an
    # alternate queue or claim that unrelated emulator sessions are free.
    assert C.LOCK.is_file(), 'Existing shared capture lease is required'
    other = require_free_workspace(R, rom, allow_interactive=True)
    env = dict(os.environ, SMB_STDOUT_ROM_SHA=expected, SMB_TEST_VARIANT=str(variant),
               **(extra_env or {}))
    command = [str(emulator), '--testRunner', '--enableStdout', f'--timeout={timeout}',
               '--doNotSaveSettings', '--nes.removeSpriteLimit=false',
               '--nes.ramPowerOnState=AllZeros', '--nes.randomizeCpuPpuAlignment=false',
               '--nes.randomizeMapperPowerOnState=false', str(script.resolve()), str(rom.resolve())]
    violations, chunks = [], [bytearray(), bytearray()]
    lock, stopped = threading.Lock(), threading.Event()
    started = time.monotonic()
    with C.capture_lease():
        preflight = C.preflight(output, reserved_bytes=C.RUN_BYTES, reserved_files=1)
        baseline = C.inventory(output, C.RUN_BYTES, 1)
        assert baseline.complete
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   env=env, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)

        def stop(reason):
            with lock:
                if not violations:
                    violations.append(reason)
            if process.poll() is None:
                process.terminate()  # only this owned emulator, never other sessions.

        def read(pipe, which):
            while True:
                part = pipe.read(65536)
                if not part:
                    return
                with lock:
                    chunks[which].extend(part)
                    oversized = sum(map(len, chunks)) > C.RUN_BYTES
                if oversized:
                    stop('Combined stdout/stderr exceeded the128MB capture budget')
                    return

        def watch():
            last_global = 0
            try:
                while not stopped.wait(.1):
                    current = C.inventory(output, C.RUN_BYTES, 1)
                    if not current.complete:
                        stop('Capture output exceeded its one-file/128MB allowance'); return
                    if output.exists() and sum(1 for _ in output.rglob('*.png')) > 4:
                        stop('Capture exceeded four PNG files'); return
                    if shutil.disk_usage(R).free < C.MINIMUM_FREE:
                        stop('Capture would cross the existing25GB free-space floor'); return
                    now = time.monotonic()
                    if now - last_global >= 2:
                        G.preflight(fresh=True); last_global = now
                    if now - started > timeout + 15:
                        stop('Owned Mesen test exceeded its bounded runtime'); return
            except Exception as error:
                stop('Capture watchdog failed closed: ' + repr(error))

        readers = [threading.Thread(target=read, args=(pipe, i), daemon=True)
                   for i, pipe in enumerate((process.stdout, process.stderr))]
        monitor = threading.Thread(target=watch, daemon=True)
        for thread in readers:
            thread.start()
        monitor.start()
        try:
            process.wait(timeout=timeout + 20)
        except Exception:
            stop('Owned process wait failed')
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill(); process.wait(timeout=5)
            raise
        finally:
            stopped.set(); monitor.join(timeout=3)
            for thread in readers:
                thread.join(timeout=3)
        final = C.inventory(output, C.RUN_BYTES, 1)
        assert final.complete and final.files == baseline.files and final.bytes == baseline.bytes, 'Mesen produced an unexpected file'
        assert not violations, violations
    assert digest(rom) == expected and digest(script) == before_source
    stdout, stderr = (data.decode('utf-8', errors='replace') for data in chunks)
    receipts, images = [], []
    for line in stdout.splitlines():
        if line.startswith('SMB_NATIVE_RECEIPT '):
            receipts.append(json.loads(line.removeprefix('SMB_NATIVE_RECEIPT ')))
        elif line.startswith('SMB_NATIVE_IMAGE '):
            encoded = line.removeprefix('SMB_NATIVE_IMAGE ').strip()
            png = base64.b64decode(encoded, validate=True)
            assert png[:8] == b'\x89PNG\r\n\x1a\n'
            images.append(dict(base64=encoded, bytes=len(png), SHA256=sha256(png).hexdigest()))
    assert len(images) <= 4
    assert len(receipts) == 1, ('Expected exactly one native receipt', process.returncode, stdout[-3000:], stderr[-3000:])
    receipt = receipts[0]
    assert receipt['ROM_SHA256'] == expected
    assert bool(receipt['passed']) == (process.returncode == 0), (process.returncode, receipt, stderr[-3000:])
    return dict(passed=receipt['passed'], native_Mesen=True, outputs_written=0,
                ROM_SHA256=expected, script_SHA256=before_source, emulator_SHA256=digest(emulator),
                returncode=process.returncode, seconds=round(time.monotonic() - started, 3),
                receipt=receipt, receipt_SHA256=sha256(json.dumps(receipt, sort_keys=True).encode()).hexdigest(),
                stdout_bytes=len(chunks[0]), stderr=stderr[-3000:], images=images,
                capture_watchdog=True, shared_Mesen_queue=True,
                other_processes_untouched=[p['ProcessId'] for p in other],
                initial_output_files=baseline.files, final_output_files=final.files,
                capture_preflight=preflight)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--script', type=Path, required=True)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--expected', required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--timeout', type=int, default=120)
    p.add_argument('--variant', type=int, choices=range(4), default=0)
    args = p.parse_args()
    q = run(args.script.resolve(), args.rom.resolve(), args.output.resolve(), args.expected,
            args.timeout, args.variant)
    print(json.dumps(q, sort_keys=True), flush=True)
    raise SystemExit(0 if q['passed'] else 1)


if __name__ == '__main__':
    main()
