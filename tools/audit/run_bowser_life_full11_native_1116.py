"""Actual installed6a3 genuine1UP/full-stage regression, no captures or ROM writes."""
from pathlib import Path
import argparse,json
import replay_bowser_life_full11_1116 as F
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

C=F.C
OUT=C.R/'build/smb2-flag-native-1113'
GRANT=C.R/'docs/qa/allocations/bowser-life-full11-native-1116.json'

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--identity',type=int,choices=(0,1),default=1);args=ap.parse_args()
    g=json.loads(GRANT.read_bytes());assert g['native_ordinary_controls_authorized']
    assert not g['ROM_game_state_or_helper_changes_authorized']
    assert C.digest(Path(F.__file__).read_bytes())==g['factory_SHA256']
    assert C.digest(F.CONTROL.read_bytes())==g['controls_SHA256']
    selected=g['qualified_identities'][str(args.identity)]
    before=check(C.ROM);raw=C.ROM.read_bytes();assert C.digest(raw)==g['ROM_SHA256']==F.PIN
    assert (OUT/'candidate.nes').read_bytes()==raw and C.digest(C.inverse(raw))==C.PIN
    assert {p.name for p in OUT.iterdir() if p.is_file()}=={'candidate.nes','controller.lua'}
    text=F.controller(raw,args.identity);assert C.digest(text.encode())==selected['Lua_SHA256']
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    require_free_workspace(C.R,C.ROM,allow_interactive=True)
    script=OUT/'controller.lua';script.write_bytes(text.encode())
    q=run(script,C.ROM,OUT/'capture',F.PIN,240,variant=0)
    assert q['script_SHA256']==selected['Lua_SHA256'] and not q['images'] and q['outputs_written']==0
    assert C.ROM.read_bytes()==raw and check(C.ROM)==before and (OUT/'candidate.nes').read_bytes()==raw
    r=q['receipt'];out={k:v for k,v in q.items() if k not in ('receipt','images','capture_preflight')}
    keep=('passed','reason','identity','ROM_SHA256','controller_only','runtime_state_writes','capture_files',
        'new_helpers','all_returned_Main','physical_frames','terminal','flag','castle','entrance','next_area_updates','full')
    out['receipt']={k:r[k] for k in keep if k in r}
    out.update(actual_Downloads=True,identity=args.identity)
    print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)
    assert q['passed'],'Full genuine-life stage regression remains open'
    assert r['flag'] and r['castle'] and r['entrance'] and not r['runtime_state_writes']
    f=r['full'];assert f['completed_core_pairs']==f['completed_tail_pairs']==f['grounded_pairs']==25
    for stem in ('movement','core','tail'):assert f['counts'][stem+'_entries']==f['counts'][stem+'_returns']
    s=f['terminal'];assert (s['world'],s['level'],s['area'],s['engine'],s['native_state'])==(0,1,2,8,0)
    assert s['y']==176 and s['x']==40 and s['health']>0 and s['tier']>=1 and s['lives']==3
