"""Root exact private HotNew118 full-stage replays, with optional installed repeat."""
from hashlib import sha256
from pathlib import Path
import argparse,json
import replay_hot_draw_bt_67e_1115 as F
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

C=F.C
OUT=F.R/'build/smb2-flag-native-1113'
GRANT=F.R/'docs/qa/allocations/hot-draw-bt118-private-stage-1115.json'

def execute(identity,downloads=False):
    grant=json.loads(GRANT.read_bytes());assert grant['private_stage_replays_authorized']and grant['all_scoped_source_gates_complete']
    assert C.H(Path(C.__file__).read_bytes())==grant['composer_SHA256']
    assert C.H(Path(F.__file__).read_bytes())==grant['factory_SHA256']
    before=check(F.ROM);official=F.ROM.read_bytes();assert C.H(official)in(C.PIN,C.CANDIDATE)
    target=OUT/'candidate.nes';candidate=target.read_bytes();assert C.H(candidate)==grant['candidate_SHA256']==C.CANDIDATE
    assert candidate[C.FILE:C.FILE+C.SIZE]==C.NEW
    restored=bytearray(candidate);restored[C.FILE:C.FILE+C.SIZE]=C.OLD;parent=bytes(restored)
    assert C.H(parent)==C.PIN and official in(parent,candidate)
    assert not downloads or official==candidate
    text=F.controller(candidate,identity);expected=grant['stage_Lua_SHA256'][identity]
    assert C.H(text.encode())==expected
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    path=F.ROM if downloads else target;require_free_workspace(F.R,path,allow_interactive=True)
    script=OUT/'controller.lua';script.write_bytes(text.encode())
    q=run(script,path,OUT/'capture',C.CANDIDATE,240)
    assert q['script_SHA256']==expected and not q['images']and q['outputs_written']==0
    assert F.ROM.read_bytes()==official and check(F.ROM)==before and target.read_bytes()==candidate
    return q

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--identity',nargs='+',choices=('rash','zitz'),default=['rash','zitz'])
    ap.add_argument('--downloads',action='store_true');args=ap.parse_args()
    for identity in args.identity:
        q=execute(identity,args.downloads);r=q['receipt']
        out={k:v for k,v in q.items()if k not in('receipt','images','capture_preflight')}
        keep=('passed','reason','Main_entries','Main_returned','physical_frames','full_nonshortcut1_1',
              'next_area_updates','Bt_1_2_steps','Bt_source_steps','minimum_source_HP','terminal',
              'game_state_writes','first_active','menu_events','input_polls','max_x')
        out['receipt']={k:r[k]for k in keep if k in r};out.update(identity=identity,actual_Downloads_repeat=args.downloads)
        out['receipt']['checkpoint_tail']=r.get('checkpoints',[])[-12:]
        print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)
        assert q['passed']and r['Main_entries']==r['Main_returned']and not r['game_state_writes']
        assert r['full_nonshortcut1_1']and r['next_area_updates']>=25
        s=r['terminal'];assert s['world']==0 and s['level']==1 and s['engine']==8 and s['state']==0
        assert s['y']==176 and s['source_HP']>0 and s['lives']==2
