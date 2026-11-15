"""Root queue: natural current40a Bub/Bob Mushroom and Flower acquisition."""
from hashlib import sha256
from pathlib import Path
import argparse
import json
import replay_bub_flower_combat_40a_1115 as F
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=F.R/'build/smb2-flag-native-1113'
FACTORY='ed41116f5f0d9dc8d5c35bda711db48f47b5155acadbd2b16cd66f0e32931c1f'
LUA={0:'b5d201919c087e13e4587dc8f22a4112391592ad0de6528e810be9f417331896',
     1:'b9d196e96d5bc0349e55425bb60febc980fec10882bcad1728dfb7e3df7b873a'}

def execute(identity,close_defence=False,margin=False,images=False,three_images=False):
    factory,expected_factory,expected_lua=F,FACTORY,LUA[identity]
    if close_defence:
        assert identity==0
        import replay_bub_flower_close_defence_40a_1115 as Close
        factory=Close
        expected_factory='17f9eb47e1d2aa964c154994c704c015809a6bfb051a750bb143e2908b4ba154'
        expected_lua='c8e483d60fdd050f97568fdd473220b4aa59ba0b6bd93c3a74dded79b31e77ba'
    elif margin:
        assert identity in(0,1)
        import replay_bub_flower_margin_40a_1115 as Margin
        factory=Margin
        expected_factory='88a452e94489dea2749403abc193b7c4a2578b7a2e837183a0cf102af3d85b76'
        expected_lua={
            0:'e1403f313fcc58dcc30fbe5e193b3b195950dfec6f6fe62a7c59d5d6c9751763',
            1:'27577418b4ecdfe0a5ea0f43a9a31040bbbfcb21611103528aaad5c5169de813'}[identity]
    elif images:
        assert identity==0
        import replay_bub_flower_images_40a_1115 as Images
        factory=Images
        expected_factory='c1616cddfc30edae8cecdaec3d6e5ac567409c0ed8930fcc8273f91590c0a562'
        expected_lua='d62015759d04012851aa6e7031fcc17670208713858726ebcf451f1b3434ed68'
    elif three_images:
        assert identity==0
        import replay_bub_three_images_40a_1115 as Images
        factory=Images
        expected_factory='59fa9dbff4b9aa9d13759651c0baf30ed3ee9b116244093f84a1148019293526'
        expected_lua='e94c064b313bb108c943b89c5e800276ed819e283b21c4ffc178ab25efacf11c'
    assert sha256(Path(factory.__file__).read_bytes()).hexdigest()==expected_factory
    before=check(factory.ROM)
    raw=factory.ROM.read_bytes()
    assert sha256(raw).hexdigest()==factory.PIN
    text=factory.controller(raw,identity)
    assert sha256(text.encode()).hexdigest()==expected_lua
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    candidate=(OUT/'candidate.nes').read_bytes()
    script=OUT/'controller.lua'
    script.write_bytes(text.encode())
    q=run(script,factory.ROM,OUT/'capture',factory.PIN,180)
    assert q['script_SHA256']==expected_lua and len(q['images'])==(3 if three_images else 2 if images else 0)and q['outputs_written']==0
    assert factory.ROM.read_bytes()==raw and check(factory.ROM)==before
    assert (OUT/'candidate.nes').read_bytes()==candidate
    return q

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--identity',type=int,nargs='+',choices=LUA,default=[0])
    p.add_argument('--close-defence',action='store_true')
    p.add_argument('--margin',action='store_true')
    p.add_argument('--images',action='store_true')
    p.add_argument('--three-images',action='store_true')
    a=p.parse_args()
    assert not a.close_defence or a.identity==[0]
    assert not a.margin or set(a.identity)<={0,1}
    assert not a.images or a.identity==[0]
    assert not a.three_images or a.identity==[0]
    assert sum((a.close_defence,a.margin,a.images,a.three_images))<=1
    for identity in a.identity:
        q=execute(identity,a.close_defence,a.margin,a.images,a.three_images)
        print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
        assert q['passed'],('Natural Bub/Bob Flower remains native-unqualified',identity)
        assert q['receipt']['natural_flower']['actual_post_F_moves']==25
        assert q['receipt']['terminal']['lives']==2
