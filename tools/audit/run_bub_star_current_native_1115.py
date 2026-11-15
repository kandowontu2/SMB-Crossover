"""Root queue: genuine Bub/Bob Star after the earned M/F prefix on174fa."""
from hashlib import sha256
from pathlib import Path
import argparse,json
import replay_bub_star_174fa_1115 as F
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=F.R/'build/smb2-flag-native-1113'
FACTORY='e3e7d0fed866697dcc1705e4385bcff1ff98556c32074790d4a2f068507f9e7a'
LUA={0:'2b6a634f89912ebca64dbdfa8faa1ce67635c3547468ce92e7399631849a826d',
     1:'f6937ce1a4f7f7e986bbe748b520d7dccc9bc26f36ce69234c6d14c49ec26010'}
IMAGE_LUA={0:'02bead557efd4c6afd795bc9d0620d62a055ce4f1490d1be44364e0d6ad2153a',
           1:'92750038fa3df498919a1a0624863901cfd582a8b0d4891bdc205511152cf8e3'}

def execute(identity,images=False):
    factory,expected_factory,expected_lua=F,FACTORY,LUA[identity]
    if images:
        import replay_bub_star_images_174fa_1115 as Pictures
        factory=Pictures
        expected_factory='6b82feeb52bbedcda50aedfb8ecaafe0e59fa7dba7a91df640b4c870a29553f5'
        expected_lua=IMAGE_LUA[identity]
    assert sha256(Path(factory.__file__).read_bytes()).hexdigest()==expected_factory
    before=check(F.ROM);raw=F.ROM.read_bytes()
    assert sha256(raw).hexdigest()==F.PIN
    text=factory.controller(raw,identity)
    assert sha256(text.encode()).hexdigest()==expected_lua
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    candidate=(OUT/'candidate.nes').read_bytes()
    require_free_workspace(F.R,F.ROM,allow_interactive=True)
    script=OUT/'controller.lua';script.write_bytes(text.encode())
    q=run(script,F.ROM,OUT/'capture',F.PIN,240)
    assert q['script_SHA256']==expected_lua and len(q['images'])<=(3 if images else 0)and q['outputs_written']==0
    assert not q['passed']or len(q['images'])==(3 if images else 0)
    assert F.ROM.read_bytes()==raw and check(F.ROM)==before
    assert (OUT/'candidate.nes').read_bytes()==candidate
    return q

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--identity',type=int,nargs='+',choices=LUA,default=[0])
    p.add_argument('--images',action='store_true');a=p.parse_args()
    for identity in a.identity:
        q=execute(identity,a.images);print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
        assert q['passed'],'Natural Bub/Bob Star remains native-unqualified'
        s=q['receipt']['natural_star']
        assert s['post_credit_returns']==25 and s['post_collector_returns']>=25
        assert q['receipt']['terminal']['lives']==2
