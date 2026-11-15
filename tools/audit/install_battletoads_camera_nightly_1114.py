"""Direct current-nightly BT camera repair with actual Downloads replays."""
from hashlib import sha256
from pathlib import Path
import argparse,json

import compose_battletoads_camera_handoff_1114 as C
import replay_battletoads_camera_full11_1114 as F
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from mesen_session_guard_v1 import require_free_workspace
from run_stdout_mesen_1110 import run

R=Path(__file__).resolve().parents[2]
OUT=R/'build/smb2-flag-native-1113'
SOURCE=OUT/'candidate.nes'
DESTINATION=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PINS={C:'3a74112540d6cb6d1f1b2af7f639ee7cc0b92c023300802decd64995296819c2',
      F:'a89b301676db5ae009802cc47f66acb2d96416ce8fd0c3635161642e35eff8e2'}
LUA={'rash':'c5539dc5f7655ccb7f8f375e22e2467648094fca6b0b8d563f285583415924ac',
     'zitz':'c1bfc6d1079069c6f697d2f492163ba41d407d31fd56d8c41928b3a90d25372d'}
RECEIPTS={'rash':'f64ec257be8f7dec5c59b10bc7fb26f1519fbc328b6cf2f10b506e314197b48b',
          'zitz':'48619365f3fbb73a02c9c205df2a8330d602d82049b4645e836d3ec4f1397579'}


def digest(data):return sha256(data).hexdigest()


def prepare():
    for module,pin in PINS.items():assert digest(Path(module.__file__).read_bytes())==pin
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    image=SOURCE.read_bytes();assert digest(image)==C.CANDIDATE
    parent=C.inverse(image);assert C.proposal(parent)[0]==image and digest(parent)==C.PIN
    before=check(DESTINATION);assert before['ROM_sha256']in(C.PIN,C.CANDIDATE)
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    scripts={key:F.controller(image,key)for key in LUA}
    for key,text in scripts.items():assert digest(text.encode())==LUA[key]
    return image,before,scripts


def install():
    assert all(RECEIPTS.values()),'Both private native full-stage receipts must be reviewed and pinned'
    image,before,scripts=prepare()
    require_free_workspace(R,DESTINATION,allow_interactive=True)
    previous=DESTINATION.read_bytes();assert digest(previous)==before['ROM_sha256']
    DESTINATION.write_bytes(image)
    assert DESTINATION.read_bytes()==image==SOURCE.read_bytes()
    after=check(DESTINATION);assert after['ROM_sha256']==C.CANDIDATE
    print('INSTALLED '+json.dumps(dict(SHA256=C.CANDIDATE,previous_SHA256=before['ROM_sha256'],
        ROM=str(DESTINATION),bytes=len(image),backup_files=0,patch_assets=0,releases_created=0)),flush=True)
    results=[]
    try:
        for key,text in scripts.items():
            script=OUT/'controller.lua';script.write_bytes(text.encode())
            q=run(script,DESTINATION,OUT/'capture',C.CANDIDATE,240)
            assert q['passed']and q['script_SHA256']==LUA[key]and q['receipt_SHA256']==RECEIPTS[key],(key,q['receipt'])
            receipt=q['receipt'];terminal=receipt['terminal']
            assert receipt['full_nonshortcut1_1']and receipt['next_area_updates']==25 and receipt['Bt_1_2_steps']>=25
            assert tuple(terminal[n]for n in('x','y','y_high','state','engine','world','level','area','lives'))==(40,176,1,0,8,0,1,2,2)
            assert terminal['source_ready']==1 and terminal['source_HP']!=255 and terminal['source_death_timer']==0
            assert terminal['variant']==(0 if key=='rash' else 32)and not q['images']and q['outputs_written']==0
            assert DESTINATION.read_bytes()==image==SOURCE.read_bytes()and check(DESTINATION)==after
            result=dict(identity=key,actual_Downloads_launch=True,passed=True,
                script_SHA256=LUA[key],receipt_SHA256=RECEIPTS[key],physical_frames=receipt['physical_frames'],
                Main_returns=receipt['Main_returned'],source_steps=receipt['Bt_source_steps'],
                next_area_updates=receipt['next_area_updates'],terminal=terminal,capture_files=0)
            results.append(result);print('DOWNLOADS_VERIFIED '+json.dumps(result,separators=(',',':')),flush=True)
    except BaseException:
        DESTINATION.write_bytes(previous)
        assert digest(DESTINATION.read_bytes())==before['ROM_sha256']and check(DESTINATION)['ROM_sha256']==before['ROM_sha256']
        print('ROLLED_BACK_TO_VERIFIED_INPUT '+before['ROM_sha256'],flush=True)
        raise
    return dict(passed=True,installed_ROM=str(DESTINATION),SHA256=C.CANDIDATE,
        installed_bytes_equal_tested_candidate=True,pre_and_post_patch_guard=True,
        no_backups_or_patch_assets_or_releases=True,native_Downloads_results=results,
        scope='Both Battletoads full1-1/flag/castle/entrance and25 grounded1-2;52-byte camera bridge. '
              'No complete natural-item ensemble, idle FPS or whole-roster qualification.')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--install',action='store_true');a=p.parse_args()
    if a.install:q=install()
    else:
        image,before,scripts=prepare()
        q=dict(metadata_only=True,candidate_SHA256=digest(image),installed_SHA256=before['ROM_sha256'],controllers=LUA,outputs=0)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
