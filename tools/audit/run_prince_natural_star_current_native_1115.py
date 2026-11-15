"""Root queue: genuine Prince Star on the actual current40a Downloads ROM."""
from hashlib import sha256
from pathlib import Path
import json
import replay_prince_natural_star_40a_1115 as F
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

R=Path(__file__).resolve().parents[2]
OUT=R/'build/smb2-flag-native-1113'
ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
FACTORY='6634302d584cefff52563261c46b33f7c4914b6f8bfa99c88aaef88f61db9122'
LUA='48097c866784b47ba20adb31d191a1d66746286f814abe87fb8921678577dc40'

def execute():
    assert sha256(Path(F.__file__).read_bytes()).hexdigest()==FACTORY
    before=check(ROM);raw=ROM.read_bytes()
    assert sha256(raw).hexdigest()==F.PIN
    text=F.controller(raw)
    assert sha256(text.encode()).hexdigest()==LUA
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    candidate=(OUT/'candidate.nes').read_bytes()
    script=OUT/'controller.lua';script.write_bytes(text.encode())
    q=run(script,ROM,OUT/'capture',F.PIN,240,variant=3)
    assert q['script_SHA256']==LUA and not q['images']and q['outputs_written']==0
    assert ROM.read_bytes()==raw and check(ROM)==before
    assert (OUT/'candidate.nes').read_bytes()==candidate
    return q

if __name__=='__main__':
    q=execute();print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    assert q['passed'],'Natural Prince Star remains native-unqualified'
    r=q['receipt'];s=r['terminal'];cold=r['new_candidate_readback']
    assert cold['both_cookies']and cold['bytes']==4193 and cold['PC']==0xbbc1
    assert r['natural_stock']['resume']==25 and s['hp']>0 and s['lives']==2
