"""Root-only passive variables around the retained native Flower negative."""
from hashlib import sha256
import json
from pathlib import Path
import replay_gimmick_flower_trajectory_current_1115 as F
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=F.R/'build/smb2-flag-native-1113'
SOURCE='1188ca4f33967412c1a817aa2d9dabc939cd60275e31a6841fa6822900aa6f12'
LUA='ff47b6e21d5275af199b38f61d0975c8b581c3e5d2d5841e804d1958662c893b'


def execute():
    assert sha256(Path(F.__file__).read_bytes()).hexdigest()==SOURCE
    before=check(F.ROM);raw=F.ROM.read_bytes();assert sha256(raw).hexdigest()==F.PIN
    text=F.controller(raw,'mr_gimmick');assert sha256(text.encode()).hexdigest()==LUA
    assert{p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    candidate=(OUT/'candidate.nes').read_bytes();script=OUT/'controller.lua';script.write_bytes(text.encode())
    q=run(script,F.ROM,OUT/'capture',F.PIN,180)
    assert q['script_SHA256']==LUA and not q['images']and q['outputs_written']==0
    assert F.ROM.read_bytes()==raw and check(F.ROM)==before and(OUT/'candidate.nes').read_bytes()==candidate
    r=q['receipt'];t=r['natural_flower']['trajectory_diagnostic']
    assert not q['passed'],'Read-only observer unexpectedly changed the retained gameplay result'
    assert r['Main_returned']==1644 and r['physical_frames']==2189
    assert r['terminal']['x']==1163 and r['terminal']['source_HP']==2 and r['terminal']['lives']==2
    assert len(t['returns'])==24 and 0<len(t['rides'])<=24 and len(t['borrowed'])<=4
    return dict(diagnostic_complete=True,gameplay_passed=False,**q)


if __name__=='__main__':print('RESULT '+json.dumps(execute(),separators=(',',':')),flush=True)
