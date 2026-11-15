"""Root queue: genuine Prince Star on the actual current40a Downloads ROM."""
from hashlib import sha256
from pathlib import Path
import argparse
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

def execute(return_boundary=False):
    factory,expected_factory,expected_lua=F,FACTORY,LUA
    if return_boundary:
        import replay_prince_natural_star_return_40a_1115 as Boundary
        factory=Boundary
        expected_factory='d0361d48072814959de6ec402d76f39ebaca0310c5c0772c6a63a78744a0b552'
        expected_lua='c64d22a697143beecb1ec12cac4ea68fef117d459b3ec7d34a26b2bc7a2e68c7'
    assert sha256(Path(factory.__file__).read_bytes()).hexdigest()==expected_factory
    before=check(ROM);raw=ROM.read_bytes()
    assert sha256(raw).hexdigest()==F.PIN
    text=factory.controller(raw)
    assert sha256(text.encode()).hexdigest()==expected_lua
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    candidate=(OUT/'candidate.nes').read_bytes()
    script=OUT/'controller.lua';script.write_bytes(text.encode())
    q=run(script,ROM,OUT/'capture',F.PIN,240,variant=3)
    assert q['script_SHA256']==expected_lua and not q['images']and q['outputs_written']==0
    assert ROM.read_bytes()==raw and check(ROM)==before
    assert (OUT/'candidate.nes').read_bytes()==candidate
    return q

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--return-boundary',action='store_true')
    a=p.parse_args()
    q=execute(a.return_boundary);print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    assert q['passed'],'Natural Prince Star remains native-unqualified'
    r=q['receipt'];s=r['terminal'];cold=r['new_candidate_readback']
    assert cold['both_cookies']and cold['bytes']==4193 and cold['PC']==0xbbc1
    assert r['natural_stock']['resume']==25 and s['hp']>0 and s['lives']==2
