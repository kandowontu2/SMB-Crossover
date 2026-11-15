"""Root queue: current16a ordinary complete-route sword handoff experiment."""
from hashlib import sha256
import json
from pathlib import Path
import replay_prince_sword_chain_handoff_1115 as F
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

R=Path(__file__).resolve().parents[2]
OUT=R/'build/smb2-flag-native-1113'
ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PIN='16a385654e80105f83470e14cd328d8bbceaa659730f4a81a2f36ca039cfbcfb'
FACTORY='2f0a35d041e7c496579c38fed6faac5bca9a960b8cb25cdb71b026abdd6983cc'

def execute():
    assert sha256(Path(F.__file__).read_bytes()).hexdigest()==FACTORY
    before=check(ROM);raw=ROM.read_bytes();assert sha256(raw).hexdigest()==PIN==F.PIN
    text=F.controller(raw);lua=sha256(text.encode()).hexdigest();print('CONTROLLER_SHA256 '+lua,flush=True)
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    candidate=(OUT/'candidate.nes').read_bytes();script=OUT/'controller.lua';script.write_bytes(text.encode())
    q=run(script,ROM,OUT/'capture',PIN,240,variant=3)
    assert q['script_SHA256']==lua and not q['images']and q['outputs_written']==0
    assert ROM.read_bytes()==raw and check(ROM)==before and(OUT/'candidate.nes').read_bytes()==candidate
    return q

if __name__=='__main__':
    q=execute();print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    assert q['passed'],'Current Prince ordinary full-route experiment remains native-unqualified'
    r=q['receipt'];cold=r['new_candidate_readback'];s=r['terminal']
    assert cold['both_cookies']and cold['bytes']==4027 and cold['PC']==0xbbc1
    assert s['world']==0 and s['level']==1 and s['lives']==2 and s['hp']>0 and s['engine']==8
