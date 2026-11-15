"""Root-only exact590 ordinary reflected-star Flower replay, no captures."""
from hashlib import sha256
import json
from pathlib import Path

import replay_gimmick_flower_pollboard_current_1115 as F
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=F.R/'build/smb2-flag-native-1113'
SOURCE='3c7ecde80977f5d822ec7ddb88bdf3c89add505dda38f3df5748e8f881772ede'
LUA='0a644fcb7ef09267d79e49b36b7fce3837b148ad18f6efa11db30921a4db32da'


def execute():
    assert sha256(Path(F.__file__).read_bytes()).hexdigest()==SOURCE
    before=check(F.ROM);raw=F.ROM.read_bytes();assert sha256(raw).hexdigest()==F.PIN
    text=F.controller(raw,'mr_gimmick');assert sha256(text.encode()).hexdigest()==LUA
    assert{p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    candidate=(OUT/'candidate.nes').read_bytes()
    script=OUT/'controller.lua';script.write_bytes(text.encode())
    q=run(script,F.ROM,OUT/'capture',F.PIN,180)
    assert q['script_SHA256']==LUA and not q['images']and q['outputs_written']==0
    assert F.ROM.read_bytes()==raw and check(F.ROM)==before
    assert(OUT/'candidate.nes').read_bytes()==candidate
    return q


if __name__=='__main__':
    q=execute();print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    assert q['passed'],'Current ordinary Flower poll-board remains native-unqualified'
