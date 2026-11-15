"""Root queue: private7a80 real reflected-star Flower and resumed moves."""
from hashlib import sha256
import json
from pathlib import Path
import compose_gimmick_empty_side_1115 as C
import replay_gimmick_empty_side_flower_current_1115 as F
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=C.R/'build/smb2-flag-native-1113'
GRANT=C.R/'docs/qa/allocations/gimmick-empty-side-native-1115.json'
ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')

def execute():
    grant=json.loads(GRANT.read_bytes());g=grant['flower_regression']
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
    assert q['script_SHA256']==g['Lua_SHA256']and not q['images']and q['outputs_written']==0
    assert target.read_bytes()==candidate and ROM.read_bytes()==parent and check(ROM)==before
    return q

if __name__=='__main__':
    q=execute();print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    assert q['passed'],'Private7a80 reflected Flower pickup remains native-unqualified'
