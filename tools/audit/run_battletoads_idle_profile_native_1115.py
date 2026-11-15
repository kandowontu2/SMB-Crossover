"""Root queue: read-only cycle attribution on current and staged BT images."""
from hashlib import sha256
from pathlib import Path
import argparse
import json
import replay_battletoads_idle_native_profile_1115 as P
from run_battletoads_idle_funded_native_1115 import C,OUT,ROM,Storage,check,run

FACTORY='93af79300b34f62161b5ff5a8c794cea0ab91dba8d726000542a17d9abdd892c'
LUA={
 'parent':'2ee638103698ae7e5f2f2d38969670ab4a6316c774644f2562e9f3060aaa276c',
 'candidate':'1158970e6dd4c492c5587ef83c3c319674f439826771cbf6c8e6896cf10dedc6'}

def execute(scope):
    assert sha256(Path(P.__file__).read_bytes()).hexdigest()==FACTORY
    before=check(ROM)
    parent=ROM.read_bytes()
    assert sha256(parent).hexdigest()==C.PIN
    image,info=C.proposal(parent)
    assert sha256(image).hexdigest()==C.CANDIDATE and C.inverse(image)==parent
    target=OUT/'candidate.nes'
    assert target.read_bytes()==image,'Use the already staged qualified private candidate'
    private_guard=check(target)
    raw=parent if scope=='parent'else image
    text=P.controller(raw)
    assert sha256(text.encode()).hexdigest()==LUA[scope]
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    script=OUT/'controller.lua'
    script.write_bytes(text.encode())
    q=run(script,ROM if scope=='parent'else target,OUT/'capture',sha256(raw).hexdigest(),180)
    assert q['script_SHA256']==LUA[scope]and not q['images']and q['outputs_written']==0
    assert ROM.read_bytes()==parent and check(ROM)==before
    assert target.read_bytes()==image and check(target)==private_guard
    return dict(scope=scope,private_only=True,Downloads_unchanged=True,**q)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--scope',nargs='+',choices=LUA,required=True)
    a=p.parse_args()
    for scope in a.scope:
        q=execute(scope)
        print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
        assert q['passed'],('Read-only native profile remains unqualified',scope)
        profile=q['receipt']['native_cycle_profile']
        assert not profile['pending_Main']and profile['pending_ISR']==0
        assert profile['unacknowledged_getters']==0
        assert profile['mapped_guard_entries']==profile['guard_returns']
