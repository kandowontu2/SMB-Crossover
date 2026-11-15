"""Root queue: corrected Prince persistence private full-stage qualification."""
from hashlib import sha256
from pathlib import Path
import json
import compose_prince_sword_tier2_fresh_1115 as C
import replay_prince_sword_tier2_fresh_full_1115 as F
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from mesen_session_guard_v1 import require_free_workspace
from run_stdout_mesen_1110 import run

OUT=C.R/'build/smb2-flag-native-1113'
ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
GRANT=C.R/'docs/qa/allocations/prince-sword-tier2-fresh-native-1115.json'

def execute():
    g=json.loads(GRANT.read_bytes())
    assert g['root_private_candidate_staging_and_native_authorized']
    assert sha256(Path(C.__file__).read_bytes()).hexdigest()==g['composer_SHA256']
    assert sha256(Path(F.__file__).read_bytes()).hexdigest()==g['factory_SHA256']
    assert sha256(C.GRANT.read_bytes()).hexdigest()==g['source_grant_SHA256']
    before=check(ROM)
    parent=ROM.read_bytes()
    assert sha256(parent).hexdigest()==g['parent_SHA256']==C.PIN
    image,info=C.proposal(parent)
    assert sha256(image).hexdigest()==g['candidate_SHA256']==C.CANDIDATE
    assert C.inverse(image)==parent and C.proposal(C.inverse(image))[0]==image
    assert info['owned_decoded_bytes']==166 and info['changed_decoded_bytes']==87
    assert info['changed_physical_bytes']==9839
    allowed={*range(C.Packet.COOKIE,C.Packet.COOKIE+16),
        *(at for page in C.Packet.PAGES for at in range(C.Packet.CHR+page*1024,C.Packet.CHR+(page+1)*1024))}
    assert all(a==b for at,(a,b)in enumerate(zip(parent,image,strict=True))if at not in allowed)
    text=F.controller(image)
    assert sha256(text.encode()).hexdigest()==g['Lua_SHA256']
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    target=OUT/'candidate.nes'
    assert sha256(target.read_bytes()).hexdigest()in(C.PIN,C.CANDIDATE,
        'a90cf06bdad6778a5b01927af5bfe175fcf5dd391f52d4f8877ce622628bdde9')
    require_free_workspace(C.R,target,allow_interactive=True)
    target.write_bytes(image)
    private_guard=check(target)
    script=OUT/'controller.lua'
    script.write_bytes(text.encode())
    q=run(script,target,OUT/'capture',C.CANDIDATE,240,variant=g['variant'])
    assert q['script_SHA256']==g['Lua_SHA256']and not q['images']and q['outputs_written']==0
    assert ROM.read_bytes()==parent and check(ROM)==before
    assert target.read_bytes()==image and check(target)==private_guard
    return q

if __name__=='__main__':
    q=execute()
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    assert q['passed'],'Private Prince persistence native qualification failed'
    assert q['receipt']['persistent_sword']=={'native_PlayerStatus':2,'Sword':1}
