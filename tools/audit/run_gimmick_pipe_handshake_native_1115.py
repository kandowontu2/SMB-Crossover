"""Root-only actual590 four-pipe ordinary-input diagnostic, no captures."""
from hashlib import sha256
import json
from pathlib import Path

import replay_gimmick_pipe_handshake_current_1115 as F
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=F.R/'build/smb2-flag-native-1113'
SOURCE='1199acdfd81f540d2398f7f8c13623c539c7d2e362b7dd26b1161d469e70749d'
LUA='a3e7f6b318154b046674f061ba6a54b815d6934d1e783e91a88588787fce17b3'


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
    if q['passed']:
        r=q['receipt'];p=r['pipe_input_diagnostic'];s=r['terminal']
        assert r['reason']=='four-pipes-and25-grounded-input-consumptions'
        assert p['done']and p['quiet']==25 and p['arrived']
        assert r['first_mushroom_ready']and s['lives']==2 and s['source_HP']>0
        assert s['world']==s['level']==0 and s['engine']==8 and s['state']==0 and s['y']==176
        assert not r['full_nonshortcut1_1']
    return q


if __name__=='__main__':
    q=execute();print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    assert q['passed'],'Actual-poll four-pipe diagnostic remains native-unqualified'
