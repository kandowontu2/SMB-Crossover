"""Root's private graphics-only ROM test; exact old behavior and RAM images."""
from hashlib import sha256
import json
from pathlib import Path

import compose_prince_window567_1115 as C
import replay_prince_window567_verified_images_1115 as F
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=C.R/'build/smb2-flag-native-1113'
ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PINS={C:'f721f1d9c4c321b36899c82a1705242c32d55592674324f979b7a3ea0a4def3f',
      F:'15069235637242d91a4142c20c3981ac474cab19ead091a1289c3bc448682a5a'}
LUA='1c724aef115ccac89ae2cc1313a3591564a2d0d47226667652d3edeb8352dea4'


def execute():
    for module,pin in PINS.items():assert sha256(Path(module.__file__).read_bytes()).hexdigest()==pin
    before=check(ROM);raw=ROM.read_bytes();assert sha256(raw).hexdigest()==C.PIN
    image,composition=C.proposal(raw);assert C.inverse(image)==raw
    text=F.controller(image,'prince');assert sha256(text.encode()).hexdigest()==LUA
    assert{p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    candidate=OUT/'candidate.nes';candidate.write_bytes(image);assert candidate.read_bytes()==image
    check(candidate)
    script=OUT/'controller.lua';script.write_bytes(text.encode())
    q=run(script,candidate,OUT/'capture',C.CANDIDATE,240)
    assert q['script_SHA256']==LUA and q['outputs_written']==0
    assert ROM.read_bytes()==raw and check(ROM)==before and candidate.read_bytes()==image
    if q['passed']:
        assert len(q['images'])==2 and all(im['bytes']<=65536 for im in q['images'])
        r=q['receipt'];cold=r['first_publish_readback'];pickup=r['accepted_pickup']
        assert cold['PC']==0xbbc1 and cold['both16byte_cookies']and cold['before_first_publication']
        assert sorted(h['bytes']for h in cold['static_graphics_extents'])==[2,3,3174]
        assert pickup['accepted']and pickup['returned']and pickup['carry']==1
        assert pickup['erased']and pickup['floatey_control']==6
        assert r['terminal']['lives']==2 and r['terminal']['power']==1 and r['terminal']['prince_hp']>0
    return dict(composition=composition,**q)


if __name__=='__main__':
    q=execute();print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    assert q['passed'],'Private graphics-only Prince remains native-unqualified'
