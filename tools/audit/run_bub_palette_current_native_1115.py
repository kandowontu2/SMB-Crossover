"""Root single queue: exact private Bub palette candidate or installed repeat."""
from hashlib import sha256
from pathlib import Path
import argparse,json
import compose_bub_native_palette_current_1115 as C
import replay_bub_native_palette_current_1115 as F
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=C.R/'build/smb2-flag-native-1113'
GRANT=C.R/'docs/qa/allocations/bub-native-palette-private-native-1115.json'
LUA={
 (0,'flower',False):'42bb6718691e73ef345a9757644b5fffd63ba5e39ee3c5f6f6bb119f5eded78c',
 (0,'oneup',False):'b99a9c2f25e3955a1ed6d65a361dec053644934d7dae2aa32020c2f48f1a19ec',
 (0,'flower',True):'d373fa2018193bcf9f5809588e6094801dd9b762ffeac176bfdb5585eb0b08ba',
 (1,'flower',False):'c4cb5ab92d733960f4fbd52cf02b5b9436bbf5c4b4304620aa28564aceb80ce1',
 (1,'oneup',False):'0acc0bc6c50bdad7b798613d129a5e70fe130fe1198f1194813199200b530b3c',
 (1,'flower',True):'d76f7bfee605431f564ec81b02f5982f2d48cfa6378d5c2171a3846cf009fbc6'}

def execute(identity,stock,images=False,downloads=False):
    grant=json.loads(GRANT.read_bytes())
    assert grant['private_candidate_staging_and_native_authorized']
    assert grant['parent_SHA256']==C.PARENT and grant['candidate_SHA256']==C.CANDIDATE
    assert sha256(Path(C.__file__).read_bytes()).hexdigest()==grant['composer_SHA256']
    assert sha256(Path(F.__file__).read_bytes()).hexdigest()==grant['factory_SHA256']
    assert grant['source_all_four_routes_passed']and grant['source_palette_lifecycle_passed']
    before=check(C.ROM);official=C.ROM.read_bytes();pin=sha256(official).hexdigest()
    assert pin in(C.PARENT,C.CANDIDATE)
    parent=C.inverse(official)if pin==C.CANDIDATE else official
    candidate,_=C.proposal(parent)
    assert C.inverse(candidate)==parent and C.proposal(C.inverse(candidate))[0]==candidate
    assert not downloads or official==candidate
    expected=LUA[identity,stock,images]
    text=F.controller(candidate,identity,stock=stock,images=images)
    assert sha256(text.encode()).hexdigest()==expected
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    target=OUT/'candidate.nes';script=OUT/'controller.lua';prior=target.read_bytes()
    assert sha256(prior).hexdigest()in(C.PARENT,C.CANDIDATE)
    path=C.ROM if downloads else target
    require_free_workspace(C.R,path,allow_interactive=True)
    if not downloads:target.write_bytes(candidate)
    assert check(path)['ROM_sha256']==C.CANDIDATE
    script.write_bytes(text.encode())
    q=run(script,path,OUT/'capture',C.CANDIDATE,180)
    assert q['script_SHA256']==expected and len(q['images'])<=(3 if images else 0)
    assert not q['passed']or len(q['images'])==(3 if images else 0)
    assert q['outputs_written']==0 and C.ROM.read_bytes()==official and check(C.ROM)==before
    assert target.read_bytes()==(prior if downloads else candidate)
    if q['passed']and images:
        assert len(q['receipt']['visual'])==3
        assert all(v['palette'][28:32]==[15,15,54,23]for v in q['receipt']['visual'])
    return dict(identity=identity,stock=stock,images_requested=images,
        actual_Downloads_repeat=downloads,**q)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--identity',type=int,choices=(0,1),default=0)
    p.add_argument('--stock',choices=('flower','oneup'),default='flower')
    p.add_argument('--images',action='store_true');p.add_argument('--downloads',action='store_true')
    p.add_argument('--all',action='store_true')
    a=p.parse_args();assert not a.images or a.stock=='flower'
    cases=[(0,'flower',True),(1,'flower',True),(0,'oneup',False),(1,'oneup',False)]if a.all else[(a.identity,a.stock,a.images)]
    for identity,stock,images in cases:
        q=execute(identity,stock,images,a.downloads)
        print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
        assert q['passed'],'Bub palette candidate remains native-unqualified'
        r=q['receipt'];assert r['terminal']['lives']==(3 if stock=='oneup'else 2)
        assert(r['natural_stock']['resume']if stock=='oneup'else r['natural_flower']['actual_post_F_moves'])==25
