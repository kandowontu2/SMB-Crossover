"""Small isolated checks of the fail-closed build storage policy."""
from pathlib import Path
import json
import tempfile
import sys
import time
import build_storage_guard_v1 as G


def main():
    saved={n:getattr(G,n)for n in ['BUILD','BUILD_BYTES','BUILD_FILES','TASK_BYTES','TASK_FILES','_cached']}
    passed=[]
    def denied(name,call):
        try:call()
        except G.BuildStorageExceeded:passed.append(name)
        else:raise AssertionError(name)
    try:
        with tempfile.TemporaryDirectory(prefix='smb-storage-policy-')as name:
            root=Path(name).resolve();G.BUILD=root/'build';G.BUILD.mkdir();task=G.BUILD/'active';task.mkdir()
            G.BUILD_BYTES=100;G.BUILD_FILES=4;G.TASK_BYTES=60;G.TASK_FILES=2
            (task/'one.bin').write_bytes(bytes(20))
            q=G.preflight(private_root=task,reserved_bytes=20,reserved_files=1,fresh=True)
            assert q['build_bytes']==20 and q['build_files']==1;passed.append('admit_bounded_task')
            denied('reject_global_byte_reservation',lambda:G.preflight(reserved_bytes=81,fresh=True))
            denied('reject_global_file_reservation',lambda:G.preflight(reserved_files=4,fresh=True))
            denied('reject_workspace_escape',lambda:G.preflight(private_root=root/'outside',fresh=True))
            (task/'two.bin').write_bytes(bytes(41))
            denied('reject_task_byte_growth',lambda:G.preflight(private_root=task,fresh=True))
            (task/'two.bin').write_bytes(bytes(1));(task/'three.bin').write_bytes(bytes(1))
            denied('reject_task_file_growth',lambda:G.preflight(private_root=task,fresh=True))
            (G.BUILD/'large.bin').write_bytes(bytes(80))
            denied('reject_actual_global_growth',lambda:G.preflight(fresh=True))
            import run_bounded_build_v1 as W
            (G.BUILD/'large.bin').unlink()
            G.BUILD_BYTES=4096;G.BUILD_FILES=20;G.TASK_BYTES=20;G.TASK_FILES=4
            argv=sys.argv
            try:
                good=G.BUILD/'bounded-good'
                code=f'from pathlib import Path;p=Path({str(good)!r});p.mkdir();(p/"one.bin").write_bytes(bytes(10))'
                sys.argv=['bounded','--output',str(good),'--',sys.executable,'-c',code]
                assert W.main()==0 and (good/'one.bin').stat().st_size==10
                passed.append('bounded_runner_admits_small_producer')
                bad=G.BUILD/'bounded-overflow'
                code=f'import time;from pathlib import Path;p=Path({str(bad)!r});p.mkdir();(p/"overflow.bin").write_bytes(bytes(30));time.sleep(10)'
                sys.argv=['bounded','--output',str(bad),'--',sys.executable,'-c',code]
                started=time.monotonic()
                denied('bounded_runner_stops_owned_overflow',W.main)
                assert not bad.exists()and time.monotonic()-started<8
                passed.append('bounded_runner_removes_only_owned_partial')
            finally:sys.argv=argv
        print(json.dumps(dict(passed=True,checks=passed,temporary_outputs_removed=True)))
    finally:
        for n,v in saved.items():setattr(G,n,v)


if __name__=='__main__':
    main()
