"""Root native ordinary-controls DK Jr route with a returned-motor endpoint."""
from hashlib import sha256
from pathlib import Path
import json
import replay_dkjr_public_early_depart_bc5_1115 as F
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

C=F.Hot
OUT=C.R/'build/smb2-flag-native-1113'
GRANT=C.R/'docs/qa/allocations/dkjr-early-depart-bc5-native-1115.json'

def compact(row):
    if not isinstance(row,dict):return row
    return {k:v for k,v in row.items()if k in('Main','frame','x','y','top','left','center','phase','pipe','state','source','lives')}

if __name__=='__main__':
    g=json.loads(GRANT.read_bytes());assert g['native_ordinary_controls_authorized']and not g['ROM_game_state_or_helper_changes_authorized']
    assert sha256(Path(F.__file__).read_bytes()).hexdigest()==g['factory_SHA256']
    before=check(C.ROM);raw=C.ROM.read_bytes();assert C.H(raw)==F.PIN==g['ROM_SHA256']
    reference,identity=F.normalize(raw,kind=F.KIND)
    text=F.controller(raw,grounded12=True);assert C.H(text.encode())==g['Lua_SHA256']
    assert identity['complete11433B_DK_owner_exact']
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    prior=(OUT/'candidate.nes').read_bytes();assert prior==raw
    require_free_workspace(C.R,C.ROM,allow_interactive=True)
    script=OUT/'controller.lua';script.write_bytes(text.encode())
    q=run(script,C.ROM,OUT/'capture',F.PIN,240,variant=0,extra_env={'SMB_DKJR_FAST_ROUTE':'1'})
    assert q['script_SHA256']==g['Lua_SHA256']and not q['images']and q['outputs_written']==0
    assert C.ROM.read_bytes()==raw and check(C.ROM)==before and (OUT/'candidate.nes').read_bytes()==prior
    r=q['receipt'];out={k:v for k,v in q.items()if k not in('receipt','images','capture_preflight')}
    keys=('passed','reason','terminal','flag','castle','entrance','script_RAM_writes','controller_only',
          'injury','input_polls','grounded_12_return_count','actual_12_returns','first_grounded_12_return','last_grounded_12_return')
    out['receipt']={k:r[k]for k in keys if k in r}
    out['event_tail']=r.get('events',[])[-8:]
    out['earlier_hop_events']=[e for e in r.get('events',[])if e.get('event')in('third-depart-enemy-hop','third-static-ground-depart')]
    out['helper_births']={k:compact(v)for k,v in r.get('births',{}).items()}
    out['helper_carries']={k:dict(count=v.get('count'),first=compact(v.get('first')),last=compact(v.get('last')))for k,v in r.get('carries',{}).items()}
    out['owner_binding']=identity;out['host_Main_completion_claim']=False
    print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)
    assert q['passed'],'Current DK Jr full route remains unverified; retain negative and diagnose'
    assert r['flag']and r['castle']and r['entrance']and not r['script_RAM_writes']
    assert r['grounded_12_return_count']>=25 and r['actual_12_returns']>=25
    s=r['terminal'];assert s['world']==0 and s['level']==1 and s['engine']==8 and s['state']==0
    assert s['x']==40 and s['y']==176 and s['source']==1 and s['lives']==2
