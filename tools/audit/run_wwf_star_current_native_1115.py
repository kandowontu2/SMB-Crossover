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

def execute(key,later_bigelow=False,later_edge=False):
    factory,expected_factory,expected_lua=F,FACTORY,LUA[key]
    if later_bigelow:
        assert key=='bigelow'
        import replay_wwf_bigelow_star_gap_7a80_1115 as Later
        factory=Later
        expected_factory='cd3e0f19001abb96aa8f1ba0d77addba6aa293b9093633fb737d1c4404d98e20'
        expected_lua='33e3288072ee95025c9a0ac0f1958ba0cfad6a48423d8c717db87648638c05b6'
    elif later_edge:
        assert key in('savage','andre')
        import replay_wwf_late_edge_star_7a80_1115 as Later
        factory=Later
        expected_factory='fa75d51bc43cb7497f6fe0b9302da5497fa7f3bc29abc6c899c1297e6445b53d'
        expected_lua={
            'savage':'2920ef20480066b44737b3d7114f5fc9c8803111951ad9e3006af2a462082ce7',
            'andre':'00cb2ebfbed45adeb0ec432d7486d2a80c2bd904501967cb0852eb53ca737d37'}[key]
    assert sha256(Path(factory.__file__).read_bytes()).hexdigest()==expected_factory
    before=check(factory.ROM)
    raw=factory.ROM.read_bytes()
    assert sha256(raw).hexdigest()==factory.PIN
    text=factory.controller(raw,key)
    assert sha256(text.encode()).hexdigest()==expected_lua
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    candidate=(OUT/'candidate.nes').read_bytes()
    script=OUT/'controller.lua'
    script.write_bytes(text.encode())
    q=run(script,factory.ROM,OUT/'capture',factory.PIN,180)
    assert q['script_SHA256']==expected_lua and not q['images']and q['outputs_written']==0
    assert factory.ROM.read_bytes()==raw and check(factory.ROM)==before
    assert (OUT/'candidate.nes').read_bytes()==candidate
    return q

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--identity',nargs='+',choices=LUA,default=['hogan'])
    p.add_argument('--bigelow-later-edge',action='store_true')
    p.add_argument('--later-edge',action='store_true')
    a=p.parse_args()
    assert not a.bigelow_later_edge or a.identity==['bigelow']
    assert not a.later_edge or set(a.identity)<=set(('savage','andre'))
    assert not(a.bigelow_later_edge and a.later_edge)
    for key in a.identity:
        q=execute(key,a.bigelow_later_edge,a.later_edge)
        print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
        assert q['passed'],('Natural WWF Star remains native-unqualified',key)
        r=q['receipt']
        assert r['terminal']['lives']==2 and r['natural_stock']['resume']==25
