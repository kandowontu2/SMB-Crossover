"""Root queue: actual590 natural Star pickup and resumed movements."""
from hashlib import sha256
import json
from pathlib import Path
import replay_gimmick_natural_star_current_1115 as F
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=F.R/'build/smb2-flag-native-1113'
SOURCE='fdd02e7e2d0dab61aa68c665dfe17332689a4681f14102bf9c915bdb2d15bb2a'
LUA='6c112fc1de5e3365ebcd6bbd65f791a48ad2d098e8bc6d7fc3181cecaa97f0a4'

def execute():
    assert sha256(Path(F.__file__).read_bytes()).hexdigest()==SOURCE
    before=check(F.ROM);raw=F.ROM.read_bytes();assert sha256(raw).hexdigest()==F.PIN
    text=F.controller(raw,'mr_gimmick');assert sha256(text.encode()).hexdigest()==LUA
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    candidate=(OUT/'candidate.nes').read_bytes();script=OUT/'controller.lua';script.write_bytes(text.encode())
    q=run(script,F.ROM,OUT/'capture',F.PIN,180)
    assert q['script_SHA256']==LUA and not q['images']and q['outputs_written']==0
    assert F.ROM.read_bytes()==raw and check(F.ROM)==before and(OUT/'candidate.nes').read_bytes()==candidate
    return q

if __name__=='__main__':
    q=execute();print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    assert q['passed'],'Current genuine Gimmick Star remains native-unqualified'
