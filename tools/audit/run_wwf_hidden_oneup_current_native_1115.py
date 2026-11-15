"""Root queue: actual7a80 ordinary wrestler Mushroom and hidden1UP."""
from hashlib import sha256
from pathlib import Path
import argparse,json
import replay_wwf_natural_stock_7a80_1115 as F
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=F.R/'build/smb2-flag-native-1113'
FACTORY='1b9879d692c3a50de881c605d8f9b0b3e7257761b8b4958affaddde63675a211'
LUA={
 'hogan':'41e9b7e31b67e5463c2ce3173093fcb9dbb96d1883ce25c29bd7ffc3830f562f',
 'dibiase':'1b24827a24faefee9a733c0fed934810784dac594804b59c67ab105f8d2d10d6',
 'bigelow':'863c52acfcc2a9118edf3cfd00ee6c1bdf161b187086337d2800e25cae5eb0d1',
 'honky':'5c02b6af6b821b73402fcb93a91625cdffcfa853c876a63cd63f7f5db6d8b970',
 'savage':'ffc8359bdad2d70f2d5c067f077abce977d3db3daccde376c3936e15b3d0dc88',
 'andre':'36b850ccb3d0d63df8fbf451825d8b435349e7f7e5ad68e36bc59bc5e937a1a3'}

def execute(key):
    assert sha256(Path(F.__file__).read_bytes()).hexdigest()==FACTORY
    before=check(F.ROM);raw=F.ROM.read_bytes();assert sha256(raw).hexdigest()==F.PIN
    text=F.controller(raw,key,'oneup');assert sha256(text.encode()).hexdigest()==LUA[key]
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    candidate=(OUT/'candidate.nes').read_bytes();script=OUT/'controller.lua';script.write_bytes(text.encode())
    q=run(script,F.ROM,OUT/'capture',F.PIN,180)
    assert q['script_SHA256']==LUA[key]and not q['images']and q['outputs_written']==0
    assert F.ROM.read_bytes()==raw and check(F.ROM)==before and(OUT/'candidate.nes').read_bytes()==candidate
    return q

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--identity',nargs='+',choices=LUA,default=['hogan']);a=p.parse_args()
    for key in a.identity:
        q=execute(key);print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
        assert q['passed'],('Natural WWF hidden1UP remains native-unqualified',key)
        r=q['receipt'];assert r['terminal']['lives']==3 and r['natural_stock']['resume']==25
