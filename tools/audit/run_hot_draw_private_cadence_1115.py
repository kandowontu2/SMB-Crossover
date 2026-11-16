"""Root limited private timing measurement, no delivery or full-stage claim."""
from hashlib import sha256
from pathlib import Path
import json
import replay_hot_draw_bt_67e_1115 as F
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

C=F.C
OUT=F.R/'build/smb2-flag-native-1113'
GRANT=F.R/'docs/qa/allocations/hot-draw-bt118-private-cadence-1115.json'

if __name__=='__main__':
    grant=json.loads(GRANT.read_bytes());assert grant['private_candidate_staging_and_cadence_authorized']
    assert not grant['Downloads_delivery_authorized']and not grant['other_native_scopes_authorized']
    assert sha256(Path(C.__file__).read_bytes()).hexdigest()==grant['composer_SHA256']
    assert sha256(Path(F.__file__).read_bytes()).hexdigest()==grant['factory_SHA256']
    before=check(F.ROM);parent=F.ROM.read_bytes();assert C.H(parent)==grant['parent_SHA256']==C.PIN
    candidate,info=C.proposal(parent);assert C.H(candidate)==grant['candidate_SHA256']==C.CANDIDATE
    assert C.inverse(candidate)==parent and info['changed_bytes']==106
    text=F.cadence_reads(candidate);assert C.H(text.encode())==grant['Lua_SHA256']
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    target=OUT/'candidate.nes';assert C.H(target.read_bytes())in(C.PIN,C.CANDIDATE)
    require_free_workspace(F.R,target,allow_interactive=True)
    target.write_bytes(candidate);assert check(target)['ROM_sha256']==C.CANDIDATE
    script=OUT/'controller.lua';script.write_bytes(text.encode())
    q=run(script,target,OUT/'capture',C.CANDIDATE,240)
    assert q['script_SHA256']==grant['Lua_SHA256']and not q['images']and q['outputs_written']==0
    assert F.ROM.read_bytes()==parent and check(F.ROM)==before and target.read_bytes()==candidate
    r=q['receipt'];keep=('passed','reason','Main_entries','Main_returned','physical_frames',
        'controller_read_observations','idle_Main_returns','idle_NMI_skips','idle_physical_frames',
        'idle_max_active_actors','idle_start','idle_end','walk_Main_returns','walk_NMI_skips',
        'walk_physical_frames','walk_start','walk_end','terminal','game_state_writes')
    out={k:v for k,v in q.items()if k not in('receipt','images','capture_preflight')}
    out['receipt']={k:r[k]for k in keep if k in r};out['private_timing_only']=True
    print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)
    assert q['passed']and r['Main_entries']==r['Main_returned']and not r['game_state_writes']
