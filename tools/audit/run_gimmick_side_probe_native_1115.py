"""Root queue: passive current590 side-tile diagnosis, no gameplay writes."""
from hashlib import sha256
import json
from pathlib import Path
import replay_gimmick_flower_side_probe_current_1115 as F
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=F.R/'build/smb2-flag-native-1113'
SOURCE='e4140378d20e700fa31e97f10a3b576c1f1df9ceb43d5a19d40bdd0ba7a6e73e'
LUA='105ffbc04e94af3f5ff41d833f372398ff52f4413099896ecb69ff454e9c43c3'

def execute():
    assert sha256(Path(F.__file__).read_bytes()).hexdigest()==SOURCE
    before=check(F.ROM);raw=F.ROM.read_bytes();assert sha256(raw).hexdigest()==F.PIN
    text=F.controller(raw,'mr_gimmick');assert sha256(text.encode()).hexdigest()==LUA
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    candidate=(OUT/'candidate.nes').read_bytes();script=OUT/'controller.lua';script.write_bytes(text.encode())
    q=run(script,F.ROM,OUT/'capture',F.PIN,180)
    assert q['script_SHA256']==LUA and not q['images']and q['outputs_written']==0
    assert F.ROM.read_bytes()==raw and check(F.ROM)==before and(OUT/'candidate.nes').read_bytes()==candidate
    r=q['receipt'];rows=r.get('natural_flower',{}).get('side_probe_diagnostic',{}).get('rows',[])
    observation=bool(not q['passed']and r['Main_returned']==1644 and r['physical_frames']==2189
        and r['terminal']['x']==1163 and r['terminal']['source_HP']==2 and r['terminal']['lives']==2 and 0<len(rows)<=32)
    return dict(diagnostic_complete=observation,gameplay_passed=q['passed'],**q)

if __name__=='__main__':
    q=execute();print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    assert q['diagnostic_complete'],'Side-probe observation incomplete; native receipt retained'
