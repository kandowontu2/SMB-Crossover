"""Replace Downloads directly with the reviewed ten-byte score correction."""
from hashlib import sha256
import json
from pathlib import Path

import compose_native_floatey_score_1114 as C
import check_native_floatey_score_1114 as F
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from mesen_session_guard_v1 import require_free_workspace
from run_stdout_mesen_1110 import run

R=Path(__file__).resolve().parents[2]
OUT=R/'build/smb2-flag-native-1113'
DESTINATION=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
LUA='87ecd7d56e4e29f16a8e1e1bf9f8f2add1719ec5f0f226adf2ad755143341e84'
RECEIPT='ad76099f9cfa67a80df6bfa0b7a741d7d853ee03e78a63dbda71a61722f8e652'
PINS={C:'874ccac3b0771241c1cc84aea9ee4bde02d00bcfeb843a2d5e836a8a48a176a7',
      F:'ce2aaf7c997f953705ddacf0e835578b71d934512fce2b1a40ee483d08adff17'}


def digest(raw):return sha256(raw).hexdigest()


def install():
    for module,pin in PINS.items():assert digest(Path(module.__file__).read_bytes())==pin
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    image=(OUT/'candidate.nes').read_bytes()
    assert digest(image)==C.CANDIDATE and C.proposal(C.inverse(image))[0]==image
    before=check(DESTINATION);assert before['ROM_sha256']in(C.PIN,C.CANDIDATE)
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    text=F.controller(image);assert digest(text.encode())==LUA
    require_free_workspace(R,DESTINATION,allow_interactive=True)
    previous=DESTINATION.read_bytes();assert digest(previous)==before['ROM_sha256']
    DESTINATION.write_bytes(image)
    assert DESTINATION.read_bytes()==image==(OUT/'candidate.nes').read_bytes()
    after=check(DESTINATION);assert after['ROM_sha256']==C.CANDIDATE
    try:
        script=OUT/'controller.lua';script.write_bytes(text.encode())
        q=run(script,DESTINATION,OUT/'capture',C.CANDIDATE,240)
        assert q['passed']and q['script_SHA256']==LUA and q['receipt_SHA256']==RECEIPT
        r=q['receipt']
        assert r['pickup_before']['score']==100 and r['final_score']==1100
        assert r['terminal']['source_HP']==r['terminal']['source_max']==3
        assert r['sound_producer']['code']==69 and r['resumed_source_steps']==25
        assert r['terminal']['lives']==2 and not q['images']and q['outputs_written']==0
        assert DESTINATION.read_bytes()==image==(OUT/'candidate.nes').read_bytes()and check(DESTINATION)==after
    except BaseException:
        DESTINATION.write_bytes(previous)
        assert digest(DESTINATION.read_bytes())==before['ROM_sha256']and check(DESTINATION)==before
        print('ROLLED_BACK_TO_VERIFIED_INPUT '+before['ROM_sha256'],flush=True)
        raise
    return dict(passed=True,SHA256=C.CANDIDATE,installed_ROM=str(DESTINATION),
        previous_SHA256=before['ROM_sha256'],installed_bytes_equal_tested_candidate=True,
        actual_Downloads_launch=True,pre_and_post_patch_guard=True,script_SHA256=LUA,
        receipt_SHA256=RECEIPT,physical_frames=r['physical_frames'],Main_returns=r['Main_returned'],
        natural_mushroom_score_before=r['pickup_before']['score'],final_score=r['final_score'],
        terminal=r['terminal'],cue=r['sound_producer']['code'],resumed_calls=r['resumed_source_steps'],
        backups=0,patch_assets=0,releases_created=0,capture_files=0,
        scope='Ten native popup score award bytes and real Gimmick mushroom; no fresh full-roster/level/audio qualification')


if __name__=='__main__':print('RESULT '+json.dumps(install(),separators=(',',':')),flush=True)
