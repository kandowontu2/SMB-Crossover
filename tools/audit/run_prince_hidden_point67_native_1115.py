"""Root queue: exact point67 candidate, qualified ordinary Prince controls."""
from hashlib import sha256
from pathlib import Path
import argparse,json
import compose_prince_hidden_point67_ace_1115 as C
import replay_prince_hidden_point67_full_ace_1115 as Full
import replay_prince_hidden_point67_star_ace_1115 as Star
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
OUT=C.R/'build/smb2-flag-native-1113'
GRANT=C.R/'docs/qa/allocations/prince-hidden-point67-private-native-1115.json'


def execute(scope,downloads=False):
    grant=json.loads(GRANT.read_bytes());assert grant['private_candidate_staging_and_native_authorized']
    assert grant['parent_SHA256']==C.PIN and grant['candidate_SHA256']==C.CANDIDATE
    assert sha256(Path(C.__file__).read_bytes()).hexdigest()==grant['composer_SHA256']
    row=grant['factories'][scope];assert row['source_passed']
    factory={'full':Full,'star':Star}[scope]
    assert sha256(Path(factory.__file__).read_bytes()).hexdigest()==row['module_SHA256']
    before=check(ROM);official=ROM.read_bytes();pin=sha256(official).hexdigest()
    assert pin in(C.PIN,C.CANDIDATE)
    parent=C.inverse(official)if pin==C.CANDIDATE else official
    candidate,info=C.proposal(parent);assert C.inverse(candidate)==parent
    assert not downloads or official==candidate
    text=factory.controller(candidate);assert sha256(text.encode()).hexdigest()==row['Lua_SHA256']
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    target=OUT/'candidate.nes';prior=target.read_bytes()
    assert sha256(prior).hexdigest()in(C.PIN,C.CANDIDATE)
    path=ROM if downloads else target
    require_free_workspace(C.R,path,allow_interactive=True)
    if not downloads:target.write_bytes(candidate)
    assert check(path)['ROM_sha256']==C.CANDIDATE
    script=OUT/'controller.lua';script.write_bytes(text.encode())
    q=run(script,path,OUT/'capture',C.CANDIDATE,240,variant=3)
    assert q['script_SHA256']==row['Lua_SHA256']and not q['images']and q['outputs_written']==0
    assert ROM.read_bytes()==official and check(ROM)==before
    assert target.read_bytes()==(prior if downloads else candidate)
    return dict(scope=scope,actual_Downloads_repeat=downloads,**q)


def compact(q):
    result={k:v for k,v in q.items()if k not in('receipt','images','capture_preflight')}
    keys=('Main_entries','Main_returns','Main_returned','Main_pending','commits',
          'source_updates','source_draws','physical_frames','controller_only',
          'added_helpers','grounded_1_2_completed_returns','full_nonshortcut1_1',
          'point67_readback','new_candidate_readback','persistent_sword',
          'terminal','passed','reason','natural_star')
    result['receipt']={k:v for k,v in q['receipt'].items()if k in keys}
    result['image_count']=len(q['images'])
    return result


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--scope',nargs='+',choices=('full','star'),default=['full'])
    ap.add_argument('--downloads',action='store_true');args=ap.parse_args()
    for scope in args.scope:
        q=execute(scope,args.downloads);print('RESULT '+json.dumps(compact(q),separators=(',',':')),flush=True)
        assert q['passed'],'Prince point67 remains native-unqualified'
        r=q['receipt'];assert r['Main_entries']==r.get('Main_returned',r.get('Main_returns'))
        assert r['point67_readback']['bytes']==67 and r['new_candidate_readback']['bytes']==4193
        assert not r.get('game_state_writes')
