"""Direct graphics-only nightly delivery and exact actual-path replay."""
from hashlib import sha256
import json
from pathlib import Path

import compose_prince_window567_1115 as C
import replay_prince_window567_verified_images_1115 as F
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from mesen_session_guard_v1 import require_free_workspace
from run_stdout_mesen_1110 import run

OUT=C.R/'build/smb2-flag-native-1113'
ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
GRANT=C.R/'docs/qa/allocations/prince-window567-delivery-1115.json'
GRANT_SHA='5c79f598efa32251c15baa275d8d9868031ad80965d20d133600a203b10afe4a'
PINS={C:'f721f1d9c4c321b36899c82a1705242c32d55592674324f979b7a3ea0a4def3f',
      F:'15069235637242d91a4142c20c3981ac474cab19ead091a1289c3bc448682a5a'}


def digest(data):return sha256(data).hexdigest()


def install():
    data=GRANT.read_bytes();assert digest(data)==GRANT_SHA;grant=json.loads(data)
    assert grant['direct_Downloads_replacement_authorized']and grant['candidate_SHA256']==C.CANDIDATE
    for module,pin in PINS.items():assert digest(Path(module.__file__).read_bytes())==pin
    assert{p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    image=(OUT/'candidate.nes').read_bytes();parent=C.inverse(image);assert C.proposal(parent)[0]==image
    text=F.controller(image,'prince');assert digest(text.encode())==grant['Lua_SHA256']
    before=check(ROM);previous=ROM.read_bytes()
    assert digest(previous)==before['ROM_sha256']and before['ROM_sha256']in(C.PIN,C.CANDIDATE)
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    require_free_workspace(C.R,ROM,allow_interactive=True);assert ROM.read_bytes()==previous
    ROM.write_bytes(image);assert ROM.read_bytes()==image==(OUT/'candidate.nes').read_bytes()
    after=check(ROM);assert after['ROM_sha256']==C.CANDIDATE
    try:
        script=OUT/'controller.lua';script.write_bytes(text.encode())
        q=run(script,ROM,OUT/'capture',C.CANDIDATE,240)
        assert q['passed']and q['script_SHA256']==grant['Lua_SHA256']and q['receipt_SHA256']==grant['receipt_SHA256']
        assert[q['SHA256']for q in q['images']]==grant['PNG_SHA256']and q['outputs_written']==0
        r=q['receipt'];first=r['first_publish_readback'];pickup=r['accepted_pickup']
        assert first['both16byte_cookies']and sorted(v['bytes']for v in first['static_graphics_extents'])==[2,3,3174]
        assert pickup['accepted']and pickup['carry']==1 and pickup['erased']and pickup['floatey_control']==6
        assert r['original_commits']-pickup['commit']>=25 and r['terminal']['lives']==2
        assert ROM.read_bytes()==image==(OUT/'candidate.nes').read_bytes()and check(ROM)==after
    except BaseException:
        assert ROM.read_bytes()==image,'Concurrent destination change; left untouched'
        ROM.write_bytes(previous);assert digest(ROM.read_bytes())==before['ROM_sha256']and check(ROM)==before
        print('ROLLED_BACK_TO_VERIFIED_INPUT '+before['ROM_sha256'],flush=True)
        raise
    return dict(passed=True,installed_ROM=str(ROM),SHA256=C.CANDIDATE,previous_SHA256=before['ROM_sha256'],
        installed_bytes_equal_tested_candidate=True,actual_Downloads_launch=True,pre_and_post_patch_guard=True,
        script_SHA256=q['script_SHA256'],receipt_SHA256=q['receipt_SHA256'],
        PNG_SHA256=[im['SHA256']for im in q['images']],first_publish_readback=first,
        actual_pickup=pickup,Main_returns=r['Main_returns'],physical_frames=r['physical_frames'],
        Prince_commits=r['original_commits'],terminal=r['terminal'],
        backups=0,capture_files=0,patch_assets=0,releases_created=0,
        scope='Prince sprite-bank corruption; collision/world/importer unchanged, pipe/sword/performance remain open')


if __name__=='__main__':print('RESULT '+json.dumps(install(),separators=(',',':')),flush=True)
