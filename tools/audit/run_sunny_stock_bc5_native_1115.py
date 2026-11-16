"""Root genuine Sunny item checks on the actual installed nightly."""
from pathlib import Path
from hashlib import sha256
import argparse,json
import replay_sunny_natural_stock_bc5_1115 as Base
import replay_sunny_star_credit_bc5_1115 as Star
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=Base.R/'build/smb2-flag-native-1113'
GRANT=Base.R/'docs/qa/allocations/sunny-stock-bc5-native-1115.json'

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--kind',nargs='+',choices=('oneup','star'),default=['oneup','star']);args=ap.parse_args()
    g=json.loads(GRANT.read_bytes());assert g['native_ordinary_controls_authorized']and not g['ROM_game_state_or_helper_changes_authorized']
    assert sha256(Base.TEMPLATE.read_bytes()).hexdigest()==g['template_SHA256']
    for kind in args.kind:
        F=Base if kind=='oneup'else Star
        assert sha256(Path(F.__file__).read_bytes()).hexdigest()==g['factories'][kind]
        before=check(Base.ROM);raw=Base.ROM.read_bytes();assert sha256(raw).hexdigest()==Base.PIN==g['ROM_SHA256']
        Base.Current.preservation(raw)
        text=F.controller(raw,kind);assert sha256(text.encode()).hexdigest()==g['Lua_SHA256'][kind]
        assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
        Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
        prior=(OUT/'candidate.nes').read_bytes();assert prior==raw
        require_free_workspace(Base.R,Base.ROM,allow_interactive=True)
        script=OUT/'controller.lua';script.write_bytes(text.encode())
        q=run(script,Base.ROM,OUT/'capture',Base.PIN,240,variant=0)
        assert q['script_SHA256']==g['Lua_SHA256'][kind]and not q['images']and q['outputs_written']==0
        assert Base.ROM.read_bytes()==raw and check(Base.ROM)==before and (OUT/'candidate.nes').read_bytes()==prior
        r=q['receipt'];out={k:v for k,v in q.items()if k not in('receipt','images','capture_preflight')}
        out['receipt']={k:v for k,v in r.items()if k not in('stock','events')}
        out['receipt']['stock']={k:v for k,v in r.get('stock',{}).items()if k!='samples'}
        out['receipt']['stock_samples']=len(r.get('stock',{}).get('samples',[]))
        out.update(actual_Downloads=True,identity='Sunny',kind=kind)
        print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)
        assert q['passed'],'Sunny natural stock native qualification remains open'
        assert r['Main_entries']==r['Main_returns']and r['Sunny_entries']==r['Sunny_returns']
        assert not r['pendingMain']and not r['pendingGuest']and not r['game_state_writes']and not r['gameplay_seeds']
        s=r['stock'];assert s['resumed']==25 and s['born']and s['mature']and s['collector']and s['collected']
        if kind=='oneup':assert s['life_credit']and r['terminal']['lives']==r['terminal']['life']==3
        else:assert s['score_credit']and r['terminal']['star']>0 and r['terminal']['lives']==2
