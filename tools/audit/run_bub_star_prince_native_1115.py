"""Root queue: combined Star fix, both identities and three passive RAM pictures."""
from hashlib import sha256
from pathlib import Path
import argparse,json
import compose_bub_selected_star_palette_prince_1115 as C
import replay_bub_selected_star_palette_prince_1115 as F
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=C.R/'build/smb2-flag-native-1113'
GRANT=C.R/'docs/qa/allocations/bub-star-prince-private-native-1115.json'


def execute(identity,downloads=False):
    grant=json.loads(GRANT.read_bytes());assert grant['private_candidate_staging_and_native_authorized']
    assert grant['parent_SHA256']==C.PIN and grant['candidate_SHA256']==C.CANDIDATE
    assert sha256(Path(C.__file__).read_bytes()).hexdigest()==grant['composer_SHA256']
    assert sha256(Path(F.__file__).read_bytes()).hexdigest()==grant['factory_SHA256']
    expected=grant['controllers'][str(identity)]
    before=check(C.ROM);official=C.ROM.read_bytes();pin=sha256(official).hexdigest()
    assert pin in(C.PIN,C.CANDIDATE)
    parent=C.inverse(official)if pin==C.CANDIDATE else official
    candidate,info=C.proposal(parent);assert C.inverse(candidate)==parent
    assert not downloads or official==candidate
    text=F.controller(candidate,identity,stock='star',images=True)
    assert sha256(text.encode()).hexdigest()==expected
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    target=OUT/'candidate.nes';prior=target.read_bytes();assert sha256(prior).hexdigest()in(C.PIN,C.CANDIDATE)
    path=C.ROM if downloads else target
    require_free_workspace(C.R,path,allow_interactive=True)
    if not downloads:target.write_bytes(candidate)
    assert check(path)['ROM_sha256']==C.CANDIDATE
    script=OUT/'controller.lua';script.write_bytes(text.encode())
    q=run(script,path,OUT/'capture',C.CANDIDATE,240)
    assert q['script_SHA256']==expected and len(q['images'])<=3 and q['outputs_written']==0
    assert not q['passed']or len(q['images'])==3
    assert C.ROM.read_bytes()==official and check(C.ROM)==before
    assert target.read_bytes()==(prior if downloads else candidate)
    return q


def compact(q):
    out={k:v for k,v in q.items()if k not in('receipt','images','capture_preflight')}
    r=q['receipt'];keys=('Main_updates','physical_frames','source_updates','entered_Main',
                         'source_outside_pending','runtime_state_writes','terminal','visual','selected_draw_tail',
                         'passed','reason')
    out['receipt']={k:v for k,v in r.items()if k in keys}
    out['receipt']['natural_star']={k:v for k,v in r.get('natural_star',{}).items()if k not in('rows',)}
    out['receipt']['natural_flower']={k:v for k,v in r.get('natural_flower',{}).items()if k in('M_moves','F_moves','actual_post_F_moves','M_resume','pickups')}
    out['image_count']=len(q['images']);return out


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--identity',nargs='+',type=int,choices=(0,1),default=[0,1])
    ap.add_argument('--downloads',action='store_true');args=ap.parse_args()
    for identity in args.identity:
        q=execute(identity,args.downloads)
        print('RESULT '+json.dumps(dict(identity=identity,actual_Downloads_repeat=args.downloads,**compact(q)),separators=(',',':')),flush=True)
        for index,im in enumerate(q['images']):print('IMAGE '+json.dumps(dict(identity=identity,index=index,**im),separators=(',',':')),flush=True)
        assert q['passed'],'Combined Star palette remains native-unqualified'
        s=q['receipt']['natural_star'];assert s['post_credit_returns']==25 and s['post_collector_returns']>=25
        assert not q['receipt']['runtime_state_writes']
