"""Root-only current WWF two-spot pictures; RAM PNGs and reusable Lua only."""
from hashlib import sha256
import argparse,json
from pathlib import Path

import replay_wwf_world_sprite_images_current_1115 as F
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=F.R/'build/smb2-flag-native-1113'
SOURCE='7eff456ff76edc9c94cb35a7382210418428a39269b44dd78f097e3c15b68089'
LUA={'hogan':'f7a3481ec32c0a8f74159ec1243664fb35c3a4ea04953b8605184766a29bdd5a',
     'andre':'3bec48449168a32fbaa98caf1aa99b397b8eb471e0a3101c101b5b371f764db2'}


def execute(key):
    assert sha256(Path(F.__file__).read_bytes()).hexdigest()==SOURCE
    before=check(F.ROM);raw=F.ROM.read_bytes();assert sha256(raw).hexdigest()==F.PIN
    text=F.controller(raw,key);assert sha256(text.encode()).hexdigest()==LUA[key]
    assert{p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    candidate=(OUT/'candidate.nes').read_bytes()
    script=OUT/'controller.lua';script.write_bytes(text.encode())
    q=run(script,F.ROM,OUT/'capture',F.PIN,240)
    assert q['script_SHA256']==LUA[key]and len(q['images'])==2
    assert all(im['bytes']<=65536 for im in q['images'])and q['outputs_written']==0
    assert F.ROM.read_bytes()==raw and check(F.ROM)==before
    assert(OUT/'candidate.nes').read_bytes()==candidate
    return dict(identity=key,**q)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--identity',nargs='+',choices=LUA,required=True);a=p.parse_args()
    for key in a.identity:
        q=execute(key);print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
        assert q['passed'],'Named current WWF pictures remain unqualified'
