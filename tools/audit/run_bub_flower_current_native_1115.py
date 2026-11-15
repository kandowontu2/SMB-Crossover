"""Root queue: natural current40a Bub/Bob Mushroom and Flower acquisition."""
from hashlib import sha256
from pathlib import Path
import argparse
import json
import replay_bub_flower_combat_40a_1115 as F
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=F.R/'build/smb2-flag-native-1113'
FACTORY='ed41116f5f0d9dc8d5c35bda711db48f47b5155acadbd2b16cd66f0e32931c1f'
LUA={0:'b5d201919c087e13e4587dc8f22a4112391592ad0de6528e810be9f417331896',
     1:'b9d196e96d5bc0349e55425bb60febc980fec10882bcad1728dfb7e3df7b873a'}

def execute(identity,close_defence=False):
    factory,expected_factory,expected_lua=F,FACTORY,LUA[identity]
    if close_defence:
        assert identity==0
        import replay_bub_flower_close_defence_40a_1115 as Close
        factory=Close
        expected_factory='17f9eb47e1d2aa964c154994c704c015809a6bfb051a750bb143e2908b4ba154'
        expected_lua='c8e483d60fdd050f97568fdd473220b4aa59ba0b6bd93c3a74dded79b31e77ba'
    assert sha256(Path(factory.__file__).read_bytes()).hexdigest()==expected_factory
    before=check(factory.ROM)
    raw=factory.ROM.read_bytes()
    assert sha256(raw).hexdigest()==factory.PIN
    text=factory.controller(raw,identity)
    assert sha256(text.encode()).hexdigest()==expected_lua
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    candidate=(OUT/'candidate.nes').read_bytes()
    script=OUT/'controller.lua'
    script.write_bytes(text.encode())
    q=run(script,factory.ROM,OUT/'capture',factory.PIN,180)
    assert q['script_SHA256']==expected_lua and not q['images']and q['outputs_written']==0
    assert factory.ROM.read_bytes()==raw and check(factory.ROM)==before
    assert (OUT/'candidate.nes').read_bytes()==candidate
    return q

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--identity',type=int,nargs='+',choices=LUA,default=[0])
    p.add_argument('--close-defence',action='store_true')
    a=p.parse_args()
    assert not a.close_defence or a.identity==[0]
    for identity in a.identity:
        q=execute(identity,a.close_defence)
        print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
        assert q['passed'],('Natural Bub/Bob Flower remains native-unqualified',identity)
        assert q['receipt']['natural_flower']['actual_post_F_moves']==25
        assert q['receipt']['terminal']['lives']==2
