"""Root queue: private7a80 ordinary Mushroom/hidden1UP/Star regressions."""
from hashlib import sha256
import argparse,json
from pathlib import Path
import compose_gimmick_empty_side_1115 as C
import replay_gimmick_empty_side_current_1115 as F
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=C.R/'build/smb2-flag-native-1113'
GRANT=C.R/'docs/qa/allocations/gimmick-empty-side-native-1115.json'
ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')

def execute(scope):
    g=json.loads(GRANT.read_bytes());assert g['root_only_private_staging_authorized']
    assert sha256(Path(C.__file__).read_bytes()).hexdigest()==g['composer_SHA256']
    assert sha256(Path(F.__file__).read_bytes()).hexdigest()==g['natural_regression_factory_SHA256']
    before=check(ROM);parent=ROM.read_bytes();assert sha256(parent).hexdigest()==g['parent_SHA256']
    target=OUT/'candidate.nes';candidate=target.read_bytes();assert C.current_inverse(candidate)==parent
    assert sha256(candidate).hexdigest()==g['candidate_SHA256']==F.PIN
    text=F.controller(candidate,scope);assert sha256(text.encode()).hexdigest()==g['natural_regression_scopes'][scope]
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    script=OUT/'controller.lua';script.write_bytes(text.encode())
    q=run(script,target,OUT/'capture',F.PIN,180)
    assert q['script_SHA256']==g['natural_regression_scopes'][scope]and not q['images']and q['outputs_written']==0
    assert target.read_bytes()==candidate and ROM.read_bytes()==parent and check(ROM)==before
    return dict(scope=scope,private_only=True,**q)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--scope',nargs='+',choices=('oneup','star'),required=True);a=p.parse_args()
    for scope in a.scope:
        q=execute(scope);print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
        assert q['passed'],('Private7a80 natural stock regression remains open',scope)
