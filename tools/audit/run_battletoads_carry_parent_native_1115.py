"""Root read-only literal-read cadence baseline on the installed174fa ROM."""
from hashlib import sha256
from pathlib import Path
import json
import compose_battletoads_carry_current_1115 as C
import replay_battletoads_carry_current_1115 as F
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=C.R/'build/smb2-flag-native-1113'
C_SHA='6b87663ae0de5a1bb8b58ab73fa5313dcc8b80def75b09102fd2b66669fd604d'
F_SHA='872d88e4efdb0a86a7a21b91c1b59789c49f320057fbecda3b670b8c1431832c'
LUA='b8b325ae2b49219242d2ba6481a8ea2557afae85de3f25c8f7285677f881c069'
BODY='f76943af78cedc9d38c6433ed438a2040ccc186c18c2dd6fb686a4fbde179f7e'

def execute():
    assert sha256(Path(C.__file__).read_bytes()).hexdigest()==C_SHA
    assert sha256(Path(F.__file__).read_bytes()).hexdigest()==F_SHA
    before=check(C.ROM);raw=C.ROM.read_bytes()
    assert sha256(raw).hexdigest()==C.PIN
    text=F.cadence_reads(raw)
    assert sha256(text.encode()).hexdigest()==LUA
    assert sha256(text.split('\n',1)[1].encode()).hexdigest()==BODY
    print('CONTROLLER_SHA256 '+LUA,flush=True)
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    target=OUT/'candidate.nes';prior=target.read_bytes()
    assert sha256(prior).hexdigest()==C.PIN
    require_free_workspace(C.R,C.ROM,allow_interactive=True)
    script=OUT/'controller.lua';script.write_bytes(text.encode())
    q=run(script,C.ROM,OUT/'capture',C.PIN,240)
    assert q['script_SHA256']==LUA and not q['images']and q['outputs_written']==0
    assert C.ROM.read_bytes()==raw and check(C.ROM)==before and target.read_bytes()==prior
    return q

if __name__=='__main__':
    q=execute();print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    assert q['passed'],'Existing174fa baseline observation did not complete'
