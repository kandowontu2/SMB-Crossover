"""Root-only actual571 Fighter hidden1UP check in the existing Lua slot."""
from hashlib import sha256
import json
from pathlib import Path

import replay_ff_natural_oneup_after_credit_1114 as F
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=F.R/'build/smb2-flag-native-1113'
FACTORY='d381a25808eed711635aa06db08ad5503a5a1832ca10045050b6585384fba3a4'
LUA='3d6fc380344c4249e61e8aa6ac946c0567237f90b807826f11ce26f7c4f4d945'


def execute():
    assert sha256(Path(F.__file__).read_bytes()).hexdigest()==FACTORY
    guard=check(F.ROM);raw=F.ROM.read_bytes();assert sha256(raw).hexdigest()==F.PIN
    text=F.controller(raw,'fighter-life');assert sha256(text.encode()).hexdigest()==LUA
    assert{p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    candidate=(OUT/'candidate.nes').read_bytes()
    script=OUT/'controller.lua';script.write_bytes(text.encode())
    q=run(script,F.ROM,OUT/'capture',F.PIN,240)
    assert q['script_SHA256']==LUA and not q['images']and q['outputs_written']==0
    assert F.ROM.read_bytes()==raw and check(F.ROM)==guard
    assert(OUT/'candidate.nes').read_bytes()==candidate
    return q


if __name__=='__main__':
    q=execute();print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    assert q['passed'],'Native Fighter1UP remains unqualified'
