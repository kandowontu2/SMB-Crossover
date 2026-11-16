"""Root read-only actual-nightly cost attribution in the shared Mesen queue."""
from hashlib import sha256
from pathlib import Path
import json
import replay_battletoads_attribution_7fb_1115 as F
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=F.R/'build/smb2-flag-native-1113'
FACTORY='fa3d4dbc85517e38a9af7ef1b4f18d546bf7e8f91c7cc73fb724b81a90df5508'
LUA='6b3371c8111759feda51a57fa8b37cbd23e5ac1717b8acc7945048d3fab73709'

if __name__=='__main__':
    assert sha256(Path(F.__file__).read_bytes()).hexdigest()==FACTORY
    before=check(F.ROM);raw=F.ROM.read_bytes();assert sha256(raw).hexdigest()==F.PIN
    text=F.controller(raw);assert sha256(text.encode()).hexdigest()==LUA
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    prior=(OUT/'candidate.nes').read_bytes()
    require_free_workspace(F.R,F.ROM,allow_interactive=True)
    script=OUT/'controller.lua';script.write_bytes(text.encode())
    q=run(script,F.ROM,OUT/'capture',F.PIN,240)
    assert q['script_SHA256']==LUA and not q['images']and q['outputs_written']==0
    assert F.ROM.read_bytes()==raw and check(F.ROM)==before
    assert (OUT/'candidate.nes').read_bytes()==prior
    r=q['receipt'];p=r.get('native_cycle_profile',{})
    keep=('controller_read_observations','idle_Main_returns','idle_NMI_skips',
          'idle_physical_frames','idle_max_active_actors','idle_start','idle_end',
          'walk_Main_returns','walk_NMI_skips','walk_physical_frames','walk_start','walk_end',
          'Main_entries','Main_returned','physical_frames','terminal','native_cycle_profile')
    out={k:v for k,v in q.items()if k not in('receipt','images','capture_preflight')}
    out['receipt']={k:v for k,v in r.items()if k in keep}
    print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)
    assert q['passed'],'Current native cost attribution did not complete'
    assert not p['pending_Main']and p['pending_ISR']==0
    assert p['unacknowledged_getters']==p['unacknowledged_services']==0
    a=p['attribution'];assert a['entries']==a['returns']and not a['unacknowledged']
