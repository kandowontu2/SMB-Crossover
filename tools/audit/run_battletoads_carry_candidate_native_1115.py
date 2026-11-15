"""Root queue: source-qualified carry candidate cadence and full BT routes."""
from hashlib import sha256
from pathlib import Path
import argparse,json
import compose_battletoads_carry_current_1115 as C
import replay_battletoads_carry_current_1115 as F
import replay_battletoads_carry_cadence_fixture_1115 as Read
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=C.R/'build/smb2-flag-native-1113'
GRANT=C.R/'docs/qa/allocations/battletoads-carry-private-native-1115.json'
LUA={'candidate':'8f88463c3ef8a9632e1f871cd38265e1e71e3e7d2f0412d0de5948e2c5f89225',
     'rash':'d8fa322fbef50370a8a5790cf9165d059fa7dcabf45d42299d9482086a0e9bec',
     'zitz':'93bcd70b31596a8dee973911ac5851f23b267b3a45f693fcfc7f237d57ac34c5'}

def execute(scope,downloads=False):
    grant=json.loads(GRANT.read_bytes())
    assert grant['private_candidate_staging_and_native_authorized']
    assert grant['all_source_gates_passed']and grant['parent_SHA256']==C.PIN
    assert grant['candidate_SHA256']==C.CANDIDATE
    assert sha256(Path(C.__file__).read_bytes()).hexdigest()==grant['composer_SHA256']
    assert sha256(Path(F.__file__).read_bytes()).hexdigest()==grant['stage_factory_SHA256']
    assert sha256(Path(Read.__file__).read_bytes()).hexdigest()==grant['cadence_factory_SHA256']
    before=check(C.ROM);official=C.ROM.read_bytes();pin=sha256(official).hexdigest()
    assert pin in(C.PIN,C.CANDIDATE)
    parent=C.inverse(official)if pin==C.CANDIDATE else official
    candidate,info=C.proposal(parent)
    assert C.inverse(candidate)==parent and C.proposal(C.inverse(candidate))[0]==candidate
    owned={at for lo,n in grant['envelopes']for at in range(lo,lo+n)}
    changed={i for i,(a,b)in enumerate(zip(parent,candidate,strict=True))if a!=b}
    assert len(owned)==955 and len(changed)==714 and changed<=owned
    assert not downloads or official==candidate
    text=Read.controller(candidate)if scope=='candidate'else F.controller(candidate,scope)
    assert sha256(text.encode()).hexdigest()==LUA[scope]
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    target=OUT/'candidate.nes';prior=target.read_bytes()
    assert sha256(prior).hexdigest()in(C.PIN,C.CANDIDATE)
    path=C.ROM if downloads else target
    require_free_workspace(C.R,path,allow_interactive=True)
    if not downloads:target.write_bytes(candidate)
    assert check(path)['ROM_sha256']==C.CANDIDATE
    script=OUT/'controller.lua';script.write_bytes(text.encode())
    q=run(script,path,OUT/'capture',C.CANDIDATE,240)
    assert q['script_SHA256']==LUA[scope]and not q['images']and q['outputs_written']==0
    assert C.ROM.read_bytes()==official and check(C.ROM)==before
    assert target.read_bytes()==(prior if downloads else candidate)
    return dict(scope=scope,actual_Downloads_repeat=downloads,**q)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--scope',nargs='+',choices=LUA,default=['candidate','rash','zitz'])
    p.add_argument('--downloads',action='store_true');a=p.parse_args()
    for scope in a.scope:
        q=execute(scope,a.downloads);print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
        assert q['passed'],'Corrected carry candidate remains native-unqualified'
        r=q['receipt']
        assert r['Main_entries']==r['Main_returned']and not r['game_state_writes']
        if scope!='candidate':
            s=r['terminal'];assert r['full_nonshortcut1_1']and r['next_area_updates']>=25
            assert s['world']==0 and s['level']==1 and s['engine']==8 and s['state']==0
            assert s['y']==176 and s['source_HP']>0 and s['lives']==2
