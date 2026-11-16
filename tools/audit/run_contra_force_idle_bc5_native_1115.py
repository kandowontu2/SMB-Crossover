"""Root actual-current Burns idle/walk baseline with literal port-read observations."""
from pathlib import Path
import json
import replay_contra_force_current_idle_1115 as F
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

C=F.C
OUT=F.R/'build/smb2-flag-native-1113'
GRANT=F.R/'docs/qa/allocations/contra-force-idle-bc5-native-1115.json'

if __name__=='__main__':
    g=json.loads(GRANT.read_bytes())
    assert g['read_only_native_baseline_authorized']and not g['ROM_game_state_or_helper_changes_authorized']
    assert C.H(Path(F.__file__).read_bytes())==g['factory_SHA256']
    before=check(F.ROM);raw=F.ROM.read_bytes();assert C.H(raw)==F.PIN==g['ROM_SHA256']
    text=F.controller(raw,'burns');assert C.H(text.encode())==g['Lua_SHA256']
    assert C.H(F.body().encode())==g['observer_body_SHA256']
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    prior=(OUT/'candidate.nes').read_bytes();assert prior==raw
    require_free_workspace(F.R,F.ROM,allow_interactive=True)
    script=OUT/'controller.lua';script.write_bytes(text.encode())
    q=run(script,F.ROM,OUT/'capture',F.PIN,240,variant=0)
    assert q['script_SHA256']==g['Lua_SHA256']and not q['images']and q['outputs_written']==0
    assert F.ROM.read_bytes()==raw and check(F.ROM)==before and (OUT/'candidate.nes').read_bytes()==prior
    out={k:v for k,v in q.items()if k not in('images','capture_preflight')}
    out.update(actual_Downloads_baseline=True,ROM_changes=0)
    print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)
    assert q['passed'],'Current Burns observer must qualify before its timing is used'
    r=q['receipt'];assert not r['game_state_writes']
    assert len(r['phases'])==2
    assert [p['Main_returns']for p in r['phases']]==[48,16]
    assert all(p['Main_entries']==p['Main_returns']for p in r['phases'])
