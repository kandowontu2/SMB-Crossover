"""Direct no-backup Prince nightly replacement with actual Downloads replay."""
from hashlib import sha256
import json
from pathlib import Path
import compose_prince_body_transition_590_1115 as C
import replay_prince_body_transition_images_1115 as F
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from mesen_session_guard_v1 import require_free_workspace
from run_stdout_mesen_1110 import run

OUT=C.R/'build/smb2-flag-native-1113'
ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
GRANT=C.R/'docs/qa/allocations/prince-body-transition-delivery-1115.json'
GRANT_SHA='a6855249ef1b03b21c8a3f85920a6c8bce52841d47c000fe421f4110bb556621'

def digest(data):return sha256(data).hexdigest()

def verify_art(q,image):
    count=0
    for shot in q['receipt']['shots']:
        patterns=shot['physical_pattern_bytes']
        for key,actual in patterns.items():
            bank,offset,height=map(int,key.split('/'));length=32 if height==16 else 16
            at=1048592+bank*1024+offset
            assert len(actual)==length and bytes(actual)==image[at:at+length],('Actual OAM-selected pattern versus ROM',key)
            count+=1
    assert count>0
    return count

def install():
    data=GRANT.read_bytes();assert digest(data)==GRANT_SHA;g=json.loads(data)
    assert g['direct_Downloads_replacement_authorized']and g['destination']==ROM.as_posix()
    assert digest(Path(C.__file__).read_bytes())==g['composer_SHA256']
    assert digest(Path(F.__file__).read_bytes())==g['image_factory_SHA256']
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    image=(OUT/'candidate.nes').read_bytes();assert digest(image)==C.CANDIDATE==g['candidate_SHA256']
    parent=C.inverse(image);assert digest(parent)==C.PIN==g['parent_SHA256']and C.proposal(parent)[0]==image
    text=F.controller(image,'prince');assert digest(text.encode())==g['Lua_SHA256']
    before=check(ROM);previous=ROM.read_bytes();assert digest(previous)==before['ROM_sha256']in(C.PIN,C.CANDIDATE)
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    require_free_workspace(C.R,ROM,allow_interactive=True);assert ROM.read_bytes()==previous
    ROM.write_bytes(image);assert ROM.read_bytes()==image==(OUT/'candidate.nes').read_bytes()
    after=check(ROM);assert after['ROM_sha256']==C.CANDIDATE
    try:
        script=OUT/'controller.lua';script.write_bytes(text.encode())
        q=run(script,ROM,OUT/'capture',C.CANDIDATE,240,variant=g['required_variant'])
        assert q['passed']and q['script_SHA256']==g['Lua_SHA256']and q['receipt_SHA256']==g['native_private_receipts']['images_and_Mushroom']
        assert [im['SHA256']for im in q['images']]==g['PNG_SHA256']and q['outputs_written']==0
        r=q['receipt'];first=r['first_publish_readback'];p=r['accepted_pickup']
        assert first['both16byte_cookies']and sorted(v['bytes']for v in first['static_graphics_extents'])==[2,3,180,219,449,3174]
        assert p['accepted']and p['carry']==1 and p['erased']and p['floatey_control']==6
        assert r['original_commits']-p['commit']==25 and r['terminal']['lives']==2
        patterns=verify_art(q,image)
        assert ROM.read_bytes()==image==(OUT/'candidate.nes').read_bytes()and check(ROM)==after
    except BaseException:
        assert ROM.read_bytes()==image,'Concurrent destination change; left untouched'
        ROM.write_bytes(previous);assert digest(ROM.read_bytes())==before['ROM_sha256']and check(ROM)==before
        print('ROLLED_BACK_TO_VERIFIED_INPUT '+before['ROM_sha256'],flush=True);raise
    return dict(passed=True,installed_ROM=str(ROM),SHA256=C.CANDIDATE,previous_SHA256=before['ROM_sha256'],
        installed_bytes_equal_tested_candidate=True,actual_Downloads_launch=True,pre_and_post_patch_guard=True,
        script_SHA256=q['script_SHA256'],receipt_SHA256=q['receipt_SHA256'],PNG_SHA256=g['PNG_SHA256'],
        verified_actual_OAM_pattern_pairs=patterns,first_publish_readback=first,actual_pickup=p,
        Main_returns=r['Main_returns'],physical_frames=r['physical_frames'],Prince_commits=r['original_commits'],terminal=r['terminal'],
        backups=0,capture_files=0,patch_assets=0,releases_created=0,scope=g['qualified_scope'],open_limits=g['open_limits'])

if __name__=='__main__':print('RESULT '+json.dumps(install(),separators=(',',':')),flush=True)
