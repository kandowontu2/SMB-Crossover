"""Direct no-backup nightly replacement with actual Downloads Flower replay."""
from hashlib import sha256
import json
from pathlib import Path
import compose_gimmick_empty_side_1115 as C
import replay_gimmick_empty_side_flower_current_1115 as F
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from mesen_session_guard_v1 import require_free_workspace
from run_stdout_mesen_1110 import run

OUT=C.R/'build/smb2-flag-native-1113'
ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
GRANT=C.R/'docs/qa/allocations/gimmick-empty-side-delivery-1115.json'
GRANT_SHA='0b0f8f485fd86469a1047c8e22ccca0bed53440162ab16fbf30ce52f9ed97bb3'

def digest(data):return sha256(data).hexdigest()

def install():
    data=GRANT.read_bytes();assert digest(data)==GRANT_SHA;g=json.loads(data)
    assert g['direct_Downloads_replacement_authorized']and g['destination']==ROM.as_posix()
    assert digest(Path(C.__file__).read_bytes())==g['composer_SHA256']
    assert digest(Path(F.__file__).read_bytes())==g['flower_factory_SHA256']
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    image=(OUT/'candidate.nes').read_bytes();assert digest(image)==C.CURRENT_CANDIDATE==g['candidate_SHA256']
    parent=C.current_inverse(image);assert digest(parent)==g['parent_SHA256']and C.current_proposal(parent)[0]==image
    text=F.controller(image,'mr_gimmick');assert digest(text.encode())==g['flower_Lua_SHA256']
    before=check(ROM);previous=ROM.read_bytes();assert digest(previous)==before['ROM_sha256']in(g['parent_SHA256'],g['candidate_SHA256'])
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    require_free_workspace(C.R,ROM,allow_interactive=True);assert ROM.read_bytes()==previous
    ROM.write_bytes(image);assert ROM.read_bytes()==image==(OUT/'candidate.nes').read_bytes()
    after=check(ROM);assert after['ROM_sha256']==g['candidate_SHA256']
    try:
        script=OUT/'controller.lua';script.write_bytes(text.encode())
        q=run(script,ROM,OUT/'capture',C.CURRENT_CANDIDATE,180)
        assert q['passed']and q['script_SHA256']==g['flower_Lua_SHA256']
        assert q['receipt_SHA256']==g['private_native_receipts']['natural_M_and_reflected_ride_Flower']
        assert not q['images']and q['outputs_written']==0
        r=q['receipt'];f=r['natural_flower'];s=r['terminal']
        assert f['real_support']['count']>0 and f['support_jump']['A']==172 and f['resume']==25
        assert f['after']['inventory']==2 and f['after']['next']==2 and f['cue']['code']==28 and f['erase']>0
        assert r['final_score']==f['before']['score']+1000 and s['lives']==2 and s['source_HP']>0
        assert ROM.read_bytes()==image==(OUT/'candidate.nes').read_bytes()and check(ROM)==after
    except BaseException:
        assert ROM.read_bytes()==image,'Concurrent destination change; left untouched'
        ROM.write_bytes(previous);assert digest(ROM.read_bytes())==before['ROM_sha256']and check(ROM)==before
        print('ROLLED_BACK_TO_VERIFIED_INPUT '+before['ROM_sha256'],flush=True);raise
    return dict(passed=True,installed_ROM=str(ROM),SHA256=C.CURRENT_CANDIDATE,previous_SHA256=before['ROM_sha256'],
        installed_bytes_equal_tested_candidate=True,actual_Downloads_launch=True,pre_and_post_patch_guard=True,
        script_SHA256=q['script_SHA256'],receipt_SHA256=q['receipt_SHA256'],Main_returned=r['Main_returned'],physical_frames=r['physical_frames'],
        genuine_support=f['real_support'],actual_Flower=f['before'],inventory_after=f['after'],resumed_Gm_moves=f['resume'],terminal=s,
        backups=0,capture_files=0,patch_assets=0,releases_created=0,qualified_scope=g['qualified_scope'],open_limits=g['open_limits'])

if __name__=='__main__':print('RESULT '+json.dumps(install(),separators=(',',':')),flush=True)
