"""Root matched read-only timing baseline on actual Downloads67."""
from hashlib import sha256
from pathlib import Path
import json
import replay_hot_draw_bt_67e_1115 as F
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=F.R/'build/smb2-flag-native-1113'
FACTORY='e3c497579769eb2599651f78f8c788da892f3f540794f0a06624defbdf3cdc0a'
COMPOSER='60bf0a62b3b81e56331d035aa32e11f580296f39c1f9d8223de55b02fbfff9e7'
LUA='10684e3b531425c736feaa104f40d1cb4393c773c23157048ec03a24016b0563'

if __name__=='__main__':
    assert sha256(Path(F.__file__).read_bytes()).hexdigest()==FACTORY
    assert sha256(Path(F.C.__file__).read_bytes()).hexdigest()==COMPOSER
    before=check(F.ROM);raw=F.ROM.read_bytes();assert sha256(raw).hexdigest()==F.C.PIN
    text=F.cadence_reads(raw);assert sha256(text.encode()).hexdigest()==LUA
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    prior=(OUT/'candidate.nes').read_bytes();require_free_workspace(F.R,F.ROM,allow_interactive=True)
    script=OUT/'controller.lua';script.write_bytes(text.encode())
    q=run(script,F.ROM,OUT/'capture',F.C.PIN,240)
    assert q['script_SHA256']==LUA and not q['images']and q['outputs_written']==0
    assert F.ROM.read_bytes()==raw and check(F.ROM)==before and (OUT/'candidate.nes').read_bytes()==prior
    r=q['receipt'];keep=('passed','reason','Main_entries','Main_returned','physical_frames',
        'controller_read_observations','idle_Main_returns','idle_NMI_skips','idle_physical_frames',
        'idle_max_active_actors','idle_start','idle_end','walk_Main_returns','walk_NMI_skips',
        'walk_physical_frames','walk_start','walk_end','terminal','game_state_writes')
    out={k:v for k,v in q.items()if k not in('receipt','images','capture_preflight')}
    out['receipt']={k:r[k]for k in keep if k in r}
    print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)
    assert q['passed']and r['Main_entries']==r['Main_returned']and not r['game_state_writes']
