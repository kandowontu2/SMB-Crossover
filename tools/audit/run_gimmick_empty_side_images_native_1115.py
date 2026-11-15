"""Root private7a80 graphics regression, two RAM PNGs, no capture files."""
from hashlib import sha256
import json
from pathlib import Path
import compose_gimmick_empty_side_1115 as C
import replay_gimmick_empty_side_images_current_1115 as F
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=C.R/'build/smb2-flag-native-1113'
GRANT=C.R/'docs/qa/allocations/gimmick-empty-side-native-1115.json'
ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')

def verify_patterns(q,candidate):
    count=0
    for shot in q['receipt']['shots']:
        for key,values in shot['physical_pattern_bytes'].items():
            bank,offset,height=map(int,key.split('/'));size=32 if height==16 else 16
            at=1048592+1024*bank+offset
            assert len(values)==size and bytes(values)==candidate[at:at+size]
            count+=1
    assert count>0
    return count

def execute():
    grant=json.loads(GRANT.read_bytes());g=grant['image_regression']
    assert grant['root_only_private_staging_authorized']
    assert sha256(Path(C.__file__).read_bytes()).hexdigest()==grant['composer_SHA256']
    assert sha256(Path(F.__file__).read_bytes()).hexdigest()==g['factory_SHA256']
    before=check(ROM);parent=ROM.read_bytes();assert sha256(parent).hexdigest()==grant['parent_SHA256']
    target=OUT/'candidate.nes';candidate=target.read_bytes();assert C.current_inverse(candidate)==parent
    assert sha256(candidate).hexdigest()==grant['candidate_SHA256']==F.PIN
    text=F.controller(candidate,'mr_gimmick');assert sha256(text.encode()).hexdigest()==g['Lua_SHA256']
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    script=OUT/'controller.lua';script.write_bytes(text.encode())
    q=run(script,target,OUT/'capture',F.PIN,180)
    assert q['script_SHA256']==g['Lua_SHA256']and q['outputs_written']==0
    assert target.read_bytes()==candidate and ROM.read_bytes()==parent and check(ROM)==before
    if q['passed']:
        assert len(q['images'])==2 and all(x['bytes']<=65536 for x in q['images'])
        q['verified_actual_OAM_pattern_pairs']=verify_patterns(q,candidate)
    return q

if __name__=='__main__':
    q=execute();print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    assert q['passed'],'Private7a80 graphics regression remains open'
