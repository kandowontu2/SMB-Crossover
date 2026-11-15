"""Root private7a80 staging and passive actual side-tile regression."""
from hashlib import sha256
import json
from pathlib import Path
import compose_gimmick_empty_side_1115 as C
import replay_gimmick_empty_side_probe_current_1115 as F
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from mesen_session_guard_v1 import require_free_workspace
from run_stdout_mesen_1110 import run

OUT=C.R/'build/smb2-flag-native-1113'
GRANT=C.R/'docs/qa/allocations/gimmick-empty-side-native-1115.json'
ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')

def execute():
    g=json.loads(GRANT.read_bytes());assert g['root_only_private_staging_authorized']and g['native_probe_authorized']
    assert sha256(Path(C.__file__).read_bytes()).hexdigest()==g['composer_SHA256']
    assert sha256(Path(F.__file__).read_bytes()).hexdigest()==g['probe_factory_SHA256']
    before=check(ROM);parent=ROM.read_bytes();assert sha256(parent).hexdigest()==g['parent_SHA256']
    candidate,info=C.current_proposal(parent)
    assert C.current_inverse(candidate)==parent and C.current_proposal(C.current_inverse(candidate))[0]==candidate
    assert sha256(candidate).hexdigest()==g['candidate_SHA256']==F.PIN
    allowed=set()
    for s in g['owned_physical_half_open_spans']:
        a,z=s['start'],s['end'];allowed.update(range(a,z))
        assert sha256(parent[a:z]).hexdigest()==s['old_SHA256']and sha256(candidate[a:z]).hexdigest()==s['new_SHA256']
    changed={i for i,(a,b)in enumerate(zip(parent,candidate))if a!=b}
    assert len(allowed)==191 and len(changed)==160 and changed<=allowed
    text=F.controller(candidate,'mr_gimmick');assert sha256(text.encode()).hexdigest()==g['probe_Lua_SHA256']
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    target=OUT/'candidate.nes';script=OUT/'controller.lua'
    assert sha256(target.read_bytes()).hexdigest()in(g['parent_SHA256'],g['candidate_SHA256'])
    require_free_workspace(C.R,target,allow_interactive=True)
    target.write_bytes(candidate);script.write_bytes(text.encode());assert check(target)['ROM_sha256']==F.PIN
    q=run(script,target,OUT/'capture',F.PIN,180)
    assert q['script_SHA256']==g['probe_Lua_SHA256']and not q['images']and q['outputs_written']==0
    assert target.read_bytes()==candidate and ROM.read_bytes()==parent and check(ROM)==before
    r=q['receipt'];p=r.get('natural_flower',{}).get('side_filter_candidate',{});s=r['terminal']
    markers=p.get('marker',[]);walls=p.get('solid',[])
    qualified=bool(markers and walls and p.get('calls',0)>0 and s['source_HP']>0 and s['lives']==2)
    return dict(private_only=True,diagnostic_complete=qualified,Flower_gameplay_passed=q['passed'],**q)

if __name__=='__main__':
    q=execute();print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    assert q['diagnostic_complete'],'Actual side-filter marker/realwall proof remains open'
