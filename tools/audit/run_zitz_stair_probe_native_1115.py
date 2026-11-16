"""Root passive candidate Zitz stair/input diagnostic; no qualification waiver."""
from hashlib import sha256
from pathlib import Path
import json
import replay_battletoads_zitz_stair_probe_1115 as F
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

C=F.C
OUT=F.R/'build/smb2-flag-native-1113'
FACTORY='5ef661256cfb35c7eda5d0c31db6bd10a86a266e594b8639acac53c9448e41a7'
LUA='1050a790d7951b71a382a58495a1c670e36cf2c34e3493f93ee03fb07ace0da9'

if __name__=='__main__':
    assert sha256(Path(F.__file__).read_bytes()).hexdigest()==FACTORY
    before=check(F.ROM);official=F.ROM.read_bytes();assert C.H(official)==C.PIN
    target=OUT/'candidate.nes';raw=target.read_bytes();assert C.H(raw)==C.CANDIDATE
    text=F.controller(raw);assert C.H(text.encode())==LUA
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    require_free_workspace(F.R,target,allow_interactive=True)
    script=OUT/'controller.lua';script.write_bytes(text.encode())
    q=run(script,target,OUT/'capture',C.CANDIDATE,240)
    assert q['script_SHA256']==LUA and not q['images']and q['outputs_written']==0
    assert F.ROM.read_bytes()==official and check(F.ROM)==before and target.read_bytes()==raw
    r=q['receipt'];d=r.get('stair_probe')
    out={k:v for k,v in q.items()if k not in('receipt','images','capture_preflight')}
    out['receipt']={k:r[k]for k in('passed','reason','Main_entries','Main_returned','physical_frames','terminal','game_state_writes')if k in r}
    out['receipt']['stair_probe']=d;out['diagnostic_only']=True
    print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)
    assert d and d['worker_entries']==d['worker_returns']and d['decisions']>0
    assert not r['game_state_writes']
