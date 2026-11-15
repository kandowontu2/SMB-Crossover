"""Replace Downloads directly with qualified Gimmick graphics and verify it.

No backups, patch assets, releases, capture files or receipt forests.
"""
from hashlib import sha256
from pathlib import Path
import argparse,json

import compose_gimmick_private_window7_1114 as C
import replay_gimmick_private_window7_1114 as F
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from mesen_session_guard_v1 import require_free_workspace
from run_stdout_mesen_1110 import run

R=Path(__file__).resolve().parents[2]
OUT=R/'build/smb2-flag-native-1113'
SOURCE=OUT/'candidate.nes'
DESTINATION=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PINS={C:'31c9d998a21def8c949d2137820dbe207260e36684ba943e75340ed8f2d98ed6',
      F:'fe03002ad912ce9957a7fae5f903f45323e9ac43b8a492278a1c47c12228f9d6'}
IMAGE_LUA='d3bd74075725a490d81c99ba20c216a7d14e2d36035d1c8a21ca4c0d187bcf9a'
STAGE_LUA='84834664a8399bb5debcff2fde65912e0d6fc5fb06ed6e6223bc84786d81b3e9'
IMAGE_RECEIPT='435e53a70a7d01d485facdce5a4b60a2e239868ceb0f689b67ea4b5384e30314'
STAGE_RECEIPT='61531263c41804c81145812b72b2b0b0c7ad7db2a4d78bf664afb556ed3ab122'
IMAGE_HASHES=['6999d64224a9e2fa2c863803092d60ae1f13bbceb9b94c9638d39b05c55cef60',
              '638091d61dcbf68f91951602cf9f25d10ccd677bc1fb5c6f61e1284801f3ddd8']


def digest(data):return sha256(data).hexdigest()


def prepare():
    for module,pin in PINS.items():assert digest(Path(module.__file__).read_bytes())==pin
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    image=SOURCE.read_bytes();assert digest(image)==C.CANDIDATE
    parent=C.inverse(image);assert C.proposal(parent)[0]==image and digest(parent)==C.PIN
    before=check(DESTINATION);assert before['ROM_sha256']in(C.PIN,C.CANDIDATE)
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    scripts=(('images',F.image_controller(image),IMAGE_LUA,IMAGE_RECEIPT),
             ('stage',F.controller(image),STAGE_LUA,STAGE_RECEIPT))
    for _,text,pin,_ in scripts:assert digest(text.encode())==pin
    return image,parent,before,scripts


def install():
    assert STAGE_RECEIPT is not None,'Root must review and pin private full-stage native result first'
    image,parent,before,scripts=prepare()
    require_free_workspace(R,DESTINATION,allow_interactive=True)
    previous=DESTINATION.read_bytes();assert digest(previous)==before['ROM_sha256']
    DESTINATION.write_bytes(image)
    assert DESTINATION.read_bytes()==image==SOURCE.read_bytes()
    after=check(DESTINATION);assert after['ROM_sha256']==C.CANDIDATE
    print('INSTALLED '+json.dumps(dict(SHA256=C.CANDIDATE,previous_SHA256=before['ROM_sha256'],
        ROM=str(DESTINATION),bytes=len(image),backup_files=0,patch_assets=0,releases_created=0)),flush=True)
    results=[]
    try:
        for kind,text,pin,receipt_pin in scripts:
            script=OUT/'controller.lua';script.write_bytes(text.encode())
            q=run(script,DESTINATION,OUT/'capture',C.CANDIDATE,240)
            assert q['passed']and q['script_SHA256']==pin and q['receipt_SHA256']==receipt_pin,(kind,q['receipt'])
            receipt=q['receipt']
            if kind=='images':
                assert [p['SHA256']for p in q['images']]==IMAGE_HASHES
                assert all(s['actual_sprite_banks']==[816,16,17,18,19,20,21,818]for s in receipt['shots'])
            else:
                assert not q['images']and receipt['next_area_updates']==25 and receipt['full_nonshortcut1_1']
                assert receipt['physical_frames']==8959 and receipt['Main_returned']==7402
                assert receipt['terminal']['lives']==2 and receipt['terminal']['power']==0
            assert DESTINATION.read_bytes()==image==SOURCE.read_bytes()and check(DESTINATION)==after
            result=dict(kind=kind,actual_Downloads_launch=True,passed=True,
                script_SHA256=pin,receipt_SHA256=receipt_pin,
                physical_frames=receipt['physical_frames'],Main_returns=receipt.get('Main_returns',receipt.get('Main_returned')),
                images=[dict(bytes=p['bytes'],SHA256=p['SHA256'])for p in q['images']],
                terminal=receipt['terminal'],capture_files=q['outputs_written'])
            results.append(result);print('DOWNLOADS_VERIFIED '+json.dumps(result,separators=(',',':')),flush=True)
    except BaseException:
        DESTINATION.write_bytes(previous)
        assert digest(DESTINATION.read_bytes())==before['ROM_sha256']and check(DESTINATION)['ROM_sha256']==before['ROM_sha256']
        print('ROLLED_BACK_TO_VERIFIED_INPUT '+before['ROM_sha256'],flush=True)
        raise
    return dict(passed=True,installed_ROM=str(DESTINATION),SHA256=C.CANDIDATE,
        installed_bytes_equal_tested_candidate=True,pre_and_post_patch_guard=True,
        no_backups_or_patch_assets_or_releases=True,native_Downloads_results=results,
        scope='Mr. Gimmick natural mushroom/Goomba graphics, private source sprites and full1-1/25grounded1-2. '
              'No whole-roster, natural complete item ensemble, audio or lag qualification.')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--install',action='store_true');a=p.parse_args()
    if a.install:q=install()
    else:
        image,parent,before,scripts=prepare()
        q=dict(metadata_only=True,candidate_SHA256=digest(image),installed_SHA256=before['ROM_sha256'],
            controllers={key:pin for key,_,pin,_ in scripts},outputs=0)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
