"""Root-only exact590 real hidden1UP plus delayed credit and resumed moves."""
from hashlib import sha256
import json
from pathlib import Path
import replay_gimmick_natural_oneup_current_1115 as F
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=F.R/'build/smb2-flag-native-1113'
SOURCE='50577cb038ceb8218441f7817489f4c4c117422febc07725a93e9e5e416db25c'
LUA='8c14fb7d3ee12d468a1cdc1490366455d71d8179fff1162db046cf21a2d3bdce'


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
    return q


if __name__=='__main__':
    q=execute();print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    assert q['passed'],'Current genuine Gimmick hidden1UP remains native-unqualified'
