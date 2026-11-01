"""Run one artifact producer with live file/byte limits on its new output tree."""
from pathlib import Path
import argparse
import os
import shutil
import signal
import subprocess
import sys
import threading
import time
import build_storage_guard_v1 as G


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--timeout',type=int,default=300)
    ap.add_argument('--resume',action='store_true',help='Resume only an unfinished owned output tree; retain preexisting files on violation.')
    ap.add_argument('command',nargs=argparse.REMAINDER)
    args=ap.parse_args();output=args.output.resolve();base=G.BUILD.resolve()
    assert output.is_relative_to(base)and output!=base
    existed=output.exists()
    if existed:
        assert args.resume and output.is_dir(),'Existing task output needs explicit --resume'
        assert not(output/'source-stage.json').exists()and not(output/'binding.json').exists(),'Qualified output is immutable; use a new task'
    before={p.resolve()for p in output.rglob('*')if p.is_file()}if existed else set()
    assert 1<=args.timeout<=600
    command=args.command[1:]if args.command[:1]==['--']else args.command
    assert command
    G.preflight(private_root=output,reserved_bytes=G.TASK_BYTES,reserved_files=G.TASK_FILES,fresh=True)
    options=dict(creationflags=subprocess.CREATE_NEW_PROCESS_GROUP|subprocess.CREATE_NO_WINDOW)if os.name=='nt'else dict(start_new_session=True)
    child=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,**options)
    def relay():
        for line in child.stdout:sys.stdout.write(line);sys.stdout.flush()
    relay_thread=threading.Thread(target=relay,daemon=True);relay_thread.start()
    started=time.monotonic();next_global=started;violation=None
    try:
        while True:
            G.inventory(output,G.TASK_BYTES,G.TASK_FILES)
            now=time.monotonic()
            if now>=next_global:
                G.preflight(fresh=True);next_global=now+2
            if now-started>args.timeout:raise G.BuildStorageExceeded('Owned build exceeded its bounded runtime.')
            result=child.poll()
            if result is not None:break
            time.sleep(.2)
    except BaseException as error:
        violation=error
        if child.poll()is None:
            if os.name=='nt':subprocess.run(['taskkill','/PID',str(child.pid),'/T','/F'],capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
            else:os.killpg(child.pid,signal.SIGTERM)
        child.wait(timeout=10)
    if violation is not None:
        # Only this invocation's new disposable output tree is eligible.
        assert output.resolve().is_relative_to(base)and output.resolve()!=base
        if output.exists():
            if not existed:shutil.rmtree(output)
            else:
                for p in output.rglob('*'):
                    if p.is_file()and p.resolve()not in before:
                        assert p.resolve().is_relative_to(output)
                        p.unlink()
        relay_thread.join(timeout=2)
        raise violation
    relay_thread.join(timeout=2)
    return result


if __name__=='__main__':
    raise SystemExit(main())
