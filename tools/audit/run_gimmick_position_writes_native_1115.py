"""Root-only bounded passive first-writer trace for the retained Flower miss."""
from hashlib import sha256
import json
from pathlib import Path
import replay_gimmick_flower_position_writes_current_1115 as F
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=F.R/'build/smb2-flag-native-1113'
SOURCE='312746b4233b847e1733f8af6443ab6a08feafc95fa56ea1694200b9e543e140'
LUA='04f0db601dfa741f67ea065aece1c9aa7ee5cd2a4b13424e99be9e30bfd439f2'


def execute():
    assert sha256(Path(F.__file__).read_bytes()).hexdigest()==SOURCE
    before=check(F.ROM);raw=F.ROM.read_bytes();assert sha256(raw).hexdigest()==F.PIN
    text=F.controller(raw,'mr_gimmick');assert sha256(text.encode()).hexdigest()==LUA
    assert{p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    candidate=(OUT/'candidate.nes').read_bytes();script=OUT/'controller.lua';script.write_bytes(text.encode())
    q=run(script,F.ROM,OUT/'capture',F.PIN,180)
    assert q['script_SHA256']==LUA and not q['images']and q['outputs_written']==0
    assert F.ROM.read_bytes()==raw and check(F.ROM)==before and(OUT/'candidate.nes').read_bytes()==candidate
    r=q['receipt'];rows=r.get('natural_flower',{}).get('position_write_diagnostic',{}).get('rows',[])
    observation=bool(not q['passed']and r['Main_returned']==1644 and r['physical_frames']==2189
        and r['terminal']['x']==1163 and r['terminal']['source_HP']==2 and r['terminal']['lives']==2 and 0<len(rows)<=32)
    return dict(diagnostic_complete=observation,gameplay_passed=q['passed'],**q)


if __name__=='__main__':
    q=execute();print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    assert q['diagnostic_complete'],'First-writer observation remains unqualified; native receipt retained'
