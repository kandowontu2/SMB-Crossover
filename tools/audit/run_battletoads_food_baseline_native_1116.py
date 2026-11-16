"""Observe the unchanged-current Rash food interception, including honest negatives."""
from pathlib import Path
import json
import replay_battletoads_food_intercept_6a3_1116 as F
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

R,ROM=F.R,F.ROM
OUT=R/'build/smb2-flag-native-1113'
GRANT=R/'docs/qa/allocations/battletoads-food-native-baseline-1116.json'
H=F.Current.digest

if __name__=='__main__':
    g=json.loads(GRANT.read_bytes());assert g['native_ordinary_controls_authorized']
    assert not g['ROM_game_state_or_helper_changes_authorized']
    assert H(Path(F.__file__).read_bytes())==g['factory_SHA256'] and H(F.CONTROL.read_bytes())==g['controls_SHA256']
    before=check(ROM);raw=ROM.read_bytes();assert H(raw)==F.PIN==g['ROM_SHA256']
    assert (OUT/'candidate.nes').read_bytes()==raw
    assert {p.name for p in OUT.iterdir() if p.is_file()}=={'candidate.nes','controller.lua'}
    text=F.controller(raw,'rash','mushroom');assert H(text.encode())==g['Lua_SHA256']
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    require_free_workspace(R,ROM,allow_interactive=True)
    script=OUT/'controller.lua';script.write_bytes(text.encode())
    q=run(script,ROM,OUT/'capture',F.PIN,240)
    assert q['script_SHA256']==g['Lua_SHA256'] and not q['images'] and q['outputs_written']==0
    assert ROM.read_bytes()==raw and check(ROM)==before and (OUT/'candidate.nes').read_bytes()==raw
    r=q['receipt'];food=r.get('food',{});births=food.get('births',[])
    if isinstance(births,dict):births=list(births.values())
    mature=any(b.get('mature') for b in births)
    out={k:v for k,v in q.items() if k not in ('receipt','images','capture_preflight')}
    out['receipt']={k:v for k,v in r.items() if k!='food'}
    out['food']={k:v for k,v in food.items() if k not in ('heads','head_queries','actual_head')}
    out.update(actual_Downloads=True,diagnostic_only=True,mature_food_observed=mature,
        no_collector_recorded=not food.get('pickups'),source_only_leaf_trace_not_claimed_as_native=True)
    print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)
