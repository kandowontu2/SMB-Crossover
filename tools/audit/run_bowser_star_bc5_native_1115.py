"""Root current-native genuine Star checks for SMB3 and SMB1 Bowser."""
from pathlib import Path
from hashlib import sha256
import argparse,json
import replay_bowser_star_landing_bc5_1115 as F
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=F.R/'build/smb2-flag-native-1113'
GRANT=F.R/'docs/qa/allocations/bowser-star-bc5-native-1115.json'

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--identity',nargs='+',type=int,choices=(0,1),default=[0,1])
    ap.add_argument('--oneup-baseline',action='store_true');args=ap.parse_args()
    # The default Star path remains the frozen positive qualification.
    if args.oneup_baseline:
        import replay_bowser_oneup_lifecycle_bc5_1115 as F
        GRANT=F.R/'docs/qa/allocations/bowser-oneup-baseline-bc5-native-1116.json'
    g=json.loads(GRANT.read_bytes());assert g['native_ordinary_controls_authorized']and not g['ROM_game_state_or_helper_changes_authorized']
    assert sha256(Path(F.__file__).read_bytes()).hexdigest()==g['factory_SHA256']
    for identity in args.identity:
        before=check(F.ROM);raw=F.ROM.read_bytes();assert sha256(raw).hexdigest()==F.PIN==g['ROM_SHA256']
        F.Current.preservation(raw)
        text=F.controller(raw,identity);expected=g['Lua_SHA256'][str(identity)]
        assert sha256(text.encode()).hexdigest()==expected
        assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
        Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
        prior=(OUT/'candidate.nes').read_bytes();assert prior==raw
        require_free_workspace(F.R,F.ROM,allow_interactive=True)
        script=OUT/'controller.lua';script.write_bytes(text.encode())
        q=run(script,F.ROM,OUT/'capture',F.PIN,240,variant=0)
        assert q['script_SHA256']==expected and not q['images']and q['outputs_written']==0
        assert F.ROM.read_bytes()==raw and check(F.ROM)==before and (OUT/'candidate.nes').read_bytes()==prior
        r=q['receipt'];out={k:v for k,v in q.items()if k not in('receipt','images','capture_preflight')}
        out['receipt']={k:v for k,v in r.items()if k not in('stock','recent','pipes','natural','events','records')}
        out['receipt']['stock']={k:v for k,v in r.get('stock',{}).items()if k not in('trace','samples')}
        out['receipt']['natural_keys']=list(r.get('natural',{}))
        out.update(actual_Downloads=True,identity='SMB3 Bowser'if identity==0 else'SMB1 Bowser')
        if args.oneup_baseline:out.update(diagnostic_only=True,kind='oneup-first-constructor')
        print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)
        if args.oneup_baseline:
            s=r['stock'];assert not q['passed']and s['life_credit']and s['reconstructed']and s['lifecycle']
            continue
        assert q['passed'],'Current Bowser native Star qualification remains open'
        s=r['stock'];assert s['resumed']==s['tail_resumed']==25 and s['credit']['after']-s['credit']['before']==1000
        assert s['born']and s['mature']and s['collector']and s['collected']and s['actual_Main_return']
        c=s['counts'];assert c['movement_entries']==c['movement_returns']and c['core_entries']==c['core_returns']and c['tail_entries']==c['tail_returns']
