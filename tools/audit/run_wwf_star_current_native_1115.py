"""Root queue: current Downloads ordinary WWF M/F/Star pickup gates."""
from hashlib import sha256
from pathlib import Path
import argparse
import json
import replay_wwf_honky_star_gap_7a80_1115 as F
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=F.R/'build/smb2-flag-native-1113'
FACTORY='2cfb4f215c16b53e466c23c2f0339f9d9d0d5e85d964316ede5de4a48525e8c8'
LUA={
 'hogan':'1cec78bb2230892d4debfdf78b7f2d679135c45d3aeb0b23e9122ca429081ae6',
 'dibiase':'732bcbcf612e74e48c44a5f9bd1b67fafc3108419a2d6f0c7d5ea636d7940708',
 'bigelow':'7f9e270ff5527ab350e2beea4602b399cbf55c908a95cd64b8cc22f089d1b04f',
 'honky':'8e38a59595da3bb9e83929f6a7abf3a1a53c18a78be952160a45958180ba7271',
 'savage':'eec0d3c67d3e4cb8e318c89830cf6c24dbc27610bbadea69175956b274b35c9d',
 'andre':'1af9d09b30e188a56aaffd446759b80d1fcb5ddf80d23882abc96bbd40d15771'}

def execute(key):
    assert sha256(Path(F.__file__).read_bytes()).hexdigest()==FACTORY
    before=check(F.ROM)
    raw=F.ROM.read_bytes()
    assert sha256(raw).hexdigest()==F.PIN
    text=F.controller(raw,key)
    assert sha256(text.encode()).hexdigest()==LUA[key]
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    candidate=(OUT/'candidate.nes').read_bytes()
    script=OUT/'controller.lua'
    script.write_bytes(text.encode())
    q=run(script,F.ROM,OUT/'capture',F.PIN,180)
    assert q['script_SHA256']==LUA[key]and not q['images']and q['outputs_written']==0
    assert F.ROM.read_bytes()==raw and check(F.ROM)==before
    assert (OUT/'candidate.nes').read_bytes()==candidate
    return q

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--identity',nargs='+',choices=LUA,default=['hogan'])
    a=p.parse_args()
    for key in a.identity:
        q=execute(key)
        print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
        assert q['passed'],('Natural WWF Star remains native-unqualified',key)
        r=q['receipt']
        assert r['terminal']['lives']==2 and r['natural_stock']['resume']==25
