"""Root queue: current40a genuine Bub/Bob hidden1UP, preserving the nightly."""
from hashlib import sha256
from pathlib import Path
import argparse
import json
import replay_bub_oneup_40a_1115 as F
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=F.R/'build/smb2-flag-native-1113'
FACTORY='4794173b925520ffd5fedbc917a36b25dc36f45cae5ce52e2e5d66a7019d52fe'
LUA={0:'b0cb0e3d684af18894d991b4a2cc4f9e160689385ad30f3bcdf9c79232ee642e',
     1:'1dd544076ff306a9e179d8ef2abc9b1d5d651843585068fc73f6888422687858'}

def execute(identity):
    assert sha256(Path(F.__file__).read_bytes()).hexdigest()==FACTORY
    before=check(F.ROM)
    raw=F.ROM.read_bytes()
    assert sha256(raw).hexdigest()==F.PIN
    text=F.controller(raw,identity)
    assert sha256(text.encode()).hexdigest()==LUA[identity]
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    candidate=(OUT/'candidate.nes').read_bytes()
    script=OUT/'controller.lua'
    script.write_bytes(text.encode())
    q=run(script,F.ROM,OUT/'capture',F.PIN,180)
    assert q['script_SHA256']==LUA[identity]and not q['images']and q['outputs_written']==0
    assert F.ROM.read_bytes()==raw and check(F.ROM)==before
    assert (OUT/'candidate.nes').read_bytes()==candidate
    return q

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--identity',type=int,nargs='+',choices=LUA,default=[0])
    a=p.parse_args()
    for identity in a.identity:
        q=execute(identity)
        print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
        assert q['passed'],('Natural Bub/Bob hidden1UP remains native-unqualified',identity)
        assert q['receipt']['natural_stock']['resume']==25
        assert q['receipt']['terminal']['lives']==3
