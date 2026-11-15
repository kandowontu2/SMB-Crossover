"""Root private16a real Goomba/Mushroom images and natural pickup regression."""
from hashlib import sha256
import json
from pathlib import Path
import compose_prince_body_transition_590_1115 as C
import replay_prince_body_transition_images_1115 as F
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=C.R/'build/smb2-flag-native-1113'
ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
GRANT=C.R/'docs/qa/allocations/prince-body-transition-native-1115.json'

def execute():
    grant=json.loads(GRANT.read_bytes());g=grant['image_regression']
    assert sha256(Path(C.__file__).read_bytes()).hexdigest()==grant['composer_SHA256']
    assert sha256(Path(F.__file__).read_bytes()).hexdigest()==g['factory_SHA256']
    before=check(ROM);raw=ROM.read_bytes();assert sha256(raw).hexdigest()==C.PIN
    target=OUT/'candidate.nes';image=target.read_bytes();assert C.inverse(image)==raw and C.proposal(raw)[0]==image
    text=F.controller(image,'prince');assert sha256(text.encode()).hexdigest()==g['Lua_SHA256']
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    script=OUT/'controller.lua';script.write_bytes(text.encode())
    q=run(script,target,OUT/'capture',C.CANDIDATE,240,variant=3)
    assert q['script_SHA256']==g['Lua_SHA256']and q['outputs_written']==0
    assert ROM.read_bytes()==raw and check(ROM)==before and target.read_bytes()==image
    if q['passed']:
        assert len(q['images'])==2 and all(im['bytes']<=65536 for im in q['images'])
        r=q['receipt'];cold=r['first_publish_readback'];pickup=r['accepted_pickup']
        assert cold['PC']==0xbbc1 and cold['both16byte_cookies']and cold['before_first_publication']
        assert sorted(h['bytes']for h in cold['static_graphics_extents'])==[2,3,180,219,449,3174]
        assert pickup['accepted']and pickup['returned']and pickup['carry']==1 and pickup['erased']and pickup['floatey_control']==6
        assert r['original_commits']-pickup['commit']>=25 and r['terminal']['lives']==2 and r['terminal']['power']==1 and r['terminal']['prince_hp']>0
    return q

if __name__=='__main__':
    q=execute();print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    assert q['passed'],'Private16a natural image/pickup regression remains native-unqualified'
