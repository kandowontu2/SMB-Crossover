"""Root private16a composition and frozen ordinary pipe/sword native scopes."""
from hashlib import sha256
import argparse,json
from pathlib import Path
import compose_prince_body_transition_590_1115 as C
import replay_prince_body_transition_1115 as F
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from mesen_session_guard_v1 import require_free_workspace
from run_stdout_mesen_1110 import run

OUT=C.R/'build/smb2-flag-native-1113'
ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
GRANT=C.R/'docs/qa/allocations/prince-body-transition-native-1115.json'


def execute(scope):
    grant=json.loads(GRANT.read_bytes())
    assert grant['candidate_staging_authorized']and grant['native_scopes_authorized']
    assert sha256(Path(C.__file__).read_bytes()).hexdigest()==grant['composer_SHA256']
    assert sha256(Path(F.__file__).read_bytes()).hexdigest()==grant['replay_factory_SHA256']
    before=check(ROM);parent=ROM.read_bytes();assert sha256(parent).hexdigest()==C.PIN==grant['parent_SHA256']
    candidate,composition=C.proposal(parent)
    assert C.inverse(candidate)==parent and C.proposal(C.inverse(candidate))[0]==candidate
    assert sha256(candidate).hexdigest()==C.CANDIDATE==grant['candidate_SHA256']
    text=F.controller(candidate,scope=scope);lua=sha256(text.encode()).hexdigest();assert lua==grant['scopes'][scope]
    assert{p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    target=OUT/'candidate.nes';script=OUT/'controller.lua'
    assert sha256(target.read_bytes()).hexdigest()in(C.PIN,C.CANDIDATE)
    require_free_workspace(C.R,target,allow_interactive=True)
    assert ROM.read_bytes()==parent and check(ROM)==before
    target.write_bytes(candidate);script.write_bytes(text.encode());assert target.read_bytes()==candidate
    assert check(target)['ROM_sha256']==C.CANDIDATE
    q=run(script,target,OUT/'capture',C.CANDIDATE,240,variant=grant['required_variant'])
    assert q['script_SHA256']==lua and not q['images']and q['outputs_written']==0
    assert target.read_bytes()==candidate and ROM.read_bytes()==parent and check(ROM)==before
    if q['passed']:
        readback=q['receipt']['new_candidate_readback']
        assert readback['both_cookies']and readback['bytes']==4027 and readback['PC']==0xbbc1
    return dict(scope=scope,private_candidate_only=True,Downloads_unchanged=True,composition=composition,**q)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--scope',nargs='+',choices=('four-caps','opposed-loss'),required=True);a=p.parse_args()
    for scope in a.scope:
        q=execute(scope);print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
        assert q['passed'],('Private Prince native scope remains unqualified',scope)
