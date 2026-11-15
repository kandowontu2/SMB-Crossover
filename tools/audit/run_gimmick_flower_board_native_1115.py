"""Root-only ordinary star-platform Flower route on the exact current ROM."""
from hashlib import sha256
import json
from pathlib import Path

import replay_gimmick_flower_board_prince_current_1115 as F
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=F.R/'build/smb2-flag-native-1113'
FACTORY='4d275416f5eca9162260747b6314cb48333745bac7aa8e1680b942916488eef2'
LUA='061b6d454717b97643f894b3cc22c79d402c7e27c58008ad0e3901beeeb3325c'


def execute():
    assert sha256(Path(F.__file__).read_bytes()).hexdigest()==FACTORY
    guard=check(F.ROM);raw=F.ROM.read_bytes();assert sha256(raw).hexdigest()==F.PIN
    text=F.controller(raw,'mr_gimmick');assert sha256(text.encode()).hexdigest()==LUA
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
    assert q['passed'],'Natural current Gimmick Flower remains native-unqualified'
