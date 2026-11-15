"""Root read-only ACE native Main/ISR/service timing in the shared queue."""
from hashlib import sha256
from pathlib import Path
import json
import replay_battletoads_carry_native_profile_1115 as F
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=F.R/'build/smb2-flag-native-1113'
FACTORY='92a42eb3cf1339d800a9385cccdb51e084a9109be02be16d721dca23ee1da38c'
LUA='2c1c0fc42610d67add057f6983d750df6ab94ee4348bf2e3e6d2bfa7a6522704'

if __name__=='__main__':
    assert sha256(Path(F.__file__).read_bytes()).hexdigest()==FACTORY
    before=check(F.ROM);raw=F.ROM.read_bytes()
    assert sha256(raw).hexdigest()==F.C.CANDIDATE
    text=F.controller(raw);assert sha256(text.encode()).hexdigest()==LUA
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    prior=(OUT/'candidate.nes').read_bytes()
    require_free_workspace(F.R,F.ROM,allow_interactive=True)
    script=OUT/'controller.lua';script.write_bytes(text.encode())
    q=run(script,F.ROM,OUT/'capture',F.C.CANDIDATE,240)
    assert q['script_SHA256']==LUA and not q['images']and q['outputs_written']==0
    assert F.ROM.read_bytes()==raw and check(F.ROM)==before
    assert (OUT/'candidate.nes').read_bytes()==prior
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    assert q['passed'],'ACE native timing observer did not complete'
    p=q['receipt']['native_cycle_profile']
    assert not p['pending_Main']and p['pending_ISR']==0
    assert p['unacknowledged_getters']==p['unacknowledged_services']==0
