"""Root actual-Downloads natural hidden1UP checks on both combined identities."""
from hashlib import sha256
from pathlib import Path
import json
import replay_bub_selected_star_palette_prince_1115 as F
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=F.R/'build/smb2-flag-native-1113'
FACTORY='f73b20f9c03b6ba2c16f88ece6acf9ea71145c9dbfea2f3887ffdc7e2a60550b'
LUA={0:'6364d990476bdac3aba6518dac77cf433e281894edaca1332c142f3f6808816c',
     1:'dead491adda89953a66a1a54e7f9eca075d5fbf2e20c6335c3772442c0590bb5'}

def execute(identity):
    assert sha256(Path(F.__file__).read_bytes()).hexdigest()==FACTORY
    before=check(F.ROM);raw=F.ROM.read_bytes();assert sha256(raw).hexdigest()==F.PIN
    text=F.controller(raw,identity,stock='oneup');assert sha256(text.encode()).hexdigest()==LUA[identity]
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    prior=(OUT/'candidate.nes').read_bytes();require_free_workspace(F.R,F.ROM,allow_interactive=True)
    script=OUT/'controller.lua';script.write_bytes(text.encode())
    q=run(script,F.ROM,OUT/'capture',F.PIN,240)
    assert q['script_SHA256']==LUA[identity]and not q['images']and q['outputs_written']==0
    assert F.ROM.read_bytes()==raw and check(F.ROM)==before and (OUT/'candidate.nes').read_bytes()==prior
    return q

if __name__=='__main__':
    for identity in(0,1):
        q=execute(identity);r=q['receipt'];s=r.get('natural_stock',{})
        out={k:v for k,v in q.items()if k not in('receipt','images','capture_preflight')}
        out['identity']=identity
        out['receipt']={k:r[k]for k in('Main_updates','entered_Main','source_updates','physical_frames','terminal','passed','reason','runtime_state_writes')if k in r}
        keep=('born','mature','collector','collected','credit','resume','target','kind','popup','erase','credit_moves','post_credit_returns')
        out['receipt']['natural_stock']={k:v for k,v in s.items()if k in keep}
        print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)
        assert q['passed']and s['resume']==25 and r['terminal']['lives']==3
        assert not r.get('runtime_state_writes')
