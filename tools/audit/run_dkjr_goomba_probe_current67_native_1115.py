"""Root causal Goomba contact diagnostic, unchanged cap-depart controls."""
from hashlib import sha256
from pathlib import Path
import json
import replay_dkjr_public_goomba_probe_67_1115 as P
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

F=P.F.Old
OUT=F.R/'build/smb2-flag-native-1113'
FACTORY='5bcb6bb3293ca89b38e8cdaddd35707ba374704174535bc9b0890c196fe4b9af'
LUA='4c819a7ebb79482621ebe829d5fde2857836d035491085d70ac8e8090d89da04'

if __name__=='__main__':
    assert sha256(Path(P.__file__).read_bytes()).hexdigest()==FACTORY
    before=check(F.NIGHTLY);raw=F.NIGHTLY.read_bytes();assert sha256(raw).hexdigest()==F.PIN
    text,labels=P.controller(raw);assert sha256(text.encode()).hexdigest()==LUA
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    prior=(OUT/'candidate.nes').read_bytes();require_free_workspace(F.R,F.NIGHTLY,allow_interactive=True)
    script=OUT/'controller.lua';script.write_bytes(text.encode())
    q=run(script,F.NIGHTLY,OUT/'capture',F.PIN,240,extra_env={'SMB_DKJR_FAST_ROUTE':'1'})
    assert q['script_SHA256']==LUA and not q['images']and q['outputs_written']==0
    assert F.NIGHTLY.read_bytes()==raw and check(F.NIGHTLY)==before and (OUT/'candidate.nes').read_bytes()==prior
    r=q['receipt'];out={k:v for k,v in q.items()if k not in('receipt','images','capture_preflight')}
    out['receipt']={k:v for k,v in r.items()if k.startswith('goomba3_')or k in('passed','reason','terminal','injury','script_RAM_writes','controller_only')}
    out['existing_phase_event_tail']=r.get('events',[])[-8:]
    out['hook_bindings']=labels;out['diagnostic_only']=True
    print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)
    assert r.get('goomba3_native_injury')and r.get('goomba3_first_source5')
    assert not r['script_RAM_writes']
