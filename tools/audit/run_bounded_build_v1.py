"""Run one artifact producer with live file/byte limits on its new output tree."""
from pathlib import Path
import argparse
import os
import shutil
import signal
import subprocess
import time
import build_storage_guard_v1 as G


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--timeout',type=int,default=300)
    ap.add_argument('command',nargs=argparse.REMAINDER)
    args=ap.parse_args();output=args.output.resolve();base=G.BUILD.resolve()
    assert output.is_relative_to(base)and output!=base and not output.exists()
    assert 1<=args.timeout<=600
    command=args.command[1:]if args.command[:1]==['--']else args.command
    assert command
    G.preflight(private_root=output,reserved_bytes=G.TASK_BYTES,reserved_files=G.TASK_FILES,fresh=True)
    options=dict(creationflags=subprocess.CREATE_NEW_PROCESS_GROUP|subprocess.CREATE_NO_WINDOW)if os.name=='nt'else dict(start_new_session=True)
    child=subprocess.Popen(command,**options)
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
        if output.exists():shutil.rmtree(output)
        raise violation
    return result


if __name__=='__main__':
    raise SystemExit(main())
