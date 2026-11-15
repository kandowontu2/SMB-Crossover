"""Root single queue: exact parent/candidate cadence and two private routes."""
from hashlib import sha256
from pathlib import Path
import argparse,json
import compose_battletoads_idle_funded_1115 as C
import replay_battletoads_idle_funded_1115 as F
import replay_battletoads_idle_funded_benchmark_1115 as B
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from mesen_session_guard_v1 import require_free_workspace
from run_stdout_mesen_1110 import run

OUT=C.R/'build/smb2-flag-native-1113'
ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
GRANT=C.R/'docs/qa/allocations/battletoads-idle-funded-native-1115.json'

def execute(scope):
    g=json.loads(GRANT.read_bytes())
    assert g['root_private_candidate_staging_authorized']and g['native_benchmark_and_two_routes_authorized']
    assert sha256(Path(C.__file__).read_bytes()).hexdigest()==g['composer_SHA256']
    assert sha256(Path(F.__file__).read_bytes()).hexdigest()==g['stage_factory_SHA256']
    assert sha256(Path(B.__file__).read_bytes()).hexdigest()==g['benchmark']['factory_SHA256']
    before=check(ROM);parent=ROM.read_bytes();assert sha256(parent).hexdigest()==g['parent_SHA256']==C.PIN
    image,info=C.proposal(parent);assert sha256(image).hexdigest()==g['candidate_SHA256']==C.CANDIDATE
    assert C.inverse(image)==parent and C.proposal(C.inverse(image))[0]==image
    allowed={i for at,n in g['envelopes']for i in range(at,at+n)}
    changed={i for i,(a,b)in enumerate(zip(parent,image))if a!=b}
    assert len(allowed)==556 and len(changed)==535 and changed<=allowed
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    target=OUT/'candidate.nes';script=OUT/'controller.lua'
    prior=target.read_bytes();assert sha256(prior).hexdigest()in(C.PIN,C.CANDIDATE)
    if scope in('parent','candidate'):
        assert g['benchmark']['qualified_both_inputs']
        raw=parent if scope=='parent'else image;text=B.controller(raw)
        expected=g['benchmark']['parent_Lua_SHA256'if scope=='parent'else'candidate_Lua_SHA256']
    else:
        raw=image;text=F.controller(image,scope);expected=g['native_stages'][scope]
    assert sha256(text.encode()).hexdigest()==expected
    require_free_workspace(C.R,ROM if scope=='parent'else target,allow_interactive=True)
    if scope!='parent':target.write_bytes(image);assert check(target)['ROM_sha256']==C.CANDIDATE
    script.write_bytes(text.encode());path=ROM if scope=='parent'else target
    q=run(script,path,OUT/'capture',sha256(raw).hexdigest(),240)
    assert q['script_SHA256']==expected and not q['images']and q['outputs_written']==0
    assert ROM.read_bytes()==parent and check(ROM)==before
    assert target.read_bytes()==(prior if scope=='parent'else image)
    return dict(scope=scope,private_only=True,Downloads_unchanged=True,**q)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--scope',nargs='+',choices=('parent','candidate','rash','zitz'),required=True);a=p.parse_args()
    for scope in a.scope:
        q=execute(scope);print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
        assert q['passed'],('Private native qualification remains open',scope)
