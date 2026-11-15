"""Root single queue: typed16a natural WWF M/F with landing defense."""
import argparse,json
from hashlib import sha256
from pathlib import Path
import replay_wwf_natural_flower_defense_1115 as F
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=F.R/'build/smb2-flag-native-1113'

def execute(key):
    before=check(F.ROM);raw=F.ROM.read_bytes();assert sha256(raw).hexdigest()==F.PIN
    text=F.controller(raw,key);lua=sha256(text.encode()).hexdigest()
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    candidate=(OUT/'candidate.nes').read_bytes();script=OUT/'controller.lua';script.write_bytes(text.encode())
    q=run(script,F.ROM,OUT/'capture',F.PIN,180)
    assert q['script_SHA256']==lua and not q['images']and q['outputs_written']==0
    assert F.ROM.read_bytes()==raw and check(F.ROM)==before and(OUT/'candidate.nes').read_bytes()==candidate
    if q['passed']:
        r=q['receipt'];assert r['identity']==key and r['terminal']['power']==2 and r['terminal']['lives']==2
        for k in ('0','1'):
            item=r['items'][k];assert item['ticks']==60 and item['resumed']==25 and item['collected']['cue']&32
    return q

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--identity',nargs='+',choices=F.IDENTITIES,required=True);a=p.parse_args()
    print('FACTORY_SHA256 '+sha256(Path(F.__file__).read_bytes()).hexdigest(),flush=True)
    for key in a.identity:
        q=execute(key);print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
        assert q['passed'],('Natural per-role native M/F defense route remains unqualified',key)
