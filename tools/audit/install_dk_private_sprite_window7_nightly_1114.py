"""Direct DK graphics nightly delivery with actual Downloads verification.

No backup, patch asset, release, capture or receipt file. A failed postcopy
verification restores the authenticated parent directly from memory.
"""
from copy import deepcopy
from hashlib import sha256
import argparse,json
from pathlib import Path

import compose_dk_private_sprite_window7_1114 as Compose
import replay_dk_private_sprite_window7_1114 as Replay
import replay_gb_pit_full11_current_1114 as Gb
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from mesen_session_guard_v1 import require_free_workspace
from run_stdout_mesen_1110 import run

R=Path(__file__).resolve().parents[2]
OUT=R/'build/smb2-flag-native-1113'
SOURCE=OUT/'candidate.nes'
DESTINATION=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PINS={Compose:'040abccbb525aac52b387d82e1c1d784d48ebdca83b2f8134d6454f9f3e46616',
      Replay:'693f3d005217112563435604dafa423af7cf3f22d94450a229672f71efef9402',
      Gb:'8a9d4283522e1e0630e1a22f1ca3648a76fe4971ee3682b23b7bcfb063095b21'}
DK_LUA='cf40a25c27a01bcfb4a6fe396ba0d28fa1f83456b317ed3fd35a1d5b1db8c494'
DK_RECEIPT='93758ca3c721d793c2be8708ad90bbf543fd144028603449acc5c12c004f5922'
DK_IMAGES=['120a0ebac0c651bc92c4b593f8bc04723f3fdef1018c542d33e6bfb34543c1a3',
           '4f5848db3c760505a51d5524df028e37fd343c21d4a8c04577b1bb957adb01c9',
           '43ce86a7fc91c4e36f2bf718a5796d529bb9c3c4f719e6ae911c62ba66b3dc53']
GB_LUA='b4ac5e21e7fca02bda67764f1ef3ca1e2b3050150f02e41635c42848198ec26a'


def digest(data):return sha256(data).hexdigest()


def gb_script(image):
    parent=Compose.inverse(image);config=deepcopy(Gb.bindings(parent))
    old=Gb.controller(parent);prefix='local C='+Gb.Frozen.lua(config)+'\n'
    assert old.startswith(prefix)and digest(old.encode())==Gb.LUA_PIN
    config['sha']=Compose.CANDIDATE
    for name,h in config['hooks'].items():
        at=16+h['offset'];assert image[at:at+len(h['bytes'])]==bytes(h['bytes']),name
        if 'bank'in h:
            at=16+h['bank']*8192;h['bank_SHA256']=digest(image[at:at+8192])
    result='local C='+Gb.Frozen.lua(config)+'\n'+old[len(prefix):]
    assert result[result.index('-- Normal controller inputs'):]==old[old.index('-- Normal controller inputs'):]
    Gb.Frozen.LuaRuntime().compile(result)
    return result


def prepare():
    for module,pin in PINS.items():assert digest(Path(module.__file__).read_bytes())==pin
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    image=SOURCE.read_bytes();assert digest(image)==Compose.CANDIDATE
    parent=Compose.inverse(image);assert Compose.proposal(parent)[0]==image
    assert digest(parent)==Compose.PIN
    before=check(DESTINATION);assert before['ROM_sha256']in(Compose.PIN,Compose.CANDIDATE)
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    dk=Replay.controller(image,'donkey_kong');assert digest(dk.encode())==DK_LUA
    gb=gb_script(image)
    if GB_LUA is not None:assert digest(gb.encode())==GB_LUA
    return image,parent,before,dk,gb


def install():
    assert GB_LUA is not None,'Review and pin the GB regression metadata first'
    image,parent,before,dk,gb=prepare()
    require_free_workspace(R,DESTINATION,allow_interactive=True)
    DESTINATION.write_bytes(image)
    assert DESTINATION.read_bytes()==image==SOURCE.read_bytes()
    after=check(DESTINATION);assert after['ROM_sha256']==Compose.CANDIDATE
    print('INSTALLED '+json.dumps(dict(SHA256=Compose.CANDIDATE,previous_SHA256=before['ROM_sha256'],
        ROM=str(DESTINATION),bytes=len(image),backup_files=0,patch_assets=0,releases_created=0)),flush=True)
    results=[]
    try:
        for key,text in(('donkey_kong',dk),('gb_pit',gb)):
            script=OUT/'controller.lua';script.write_bytes(text.encode())
            q=run(script,DESTINATION,OUT/'capture',Compose.CANDIDATE,240)
            assert q['passed'],(key,'Native Downloads replay failed',q['receipt'])
            receipt=q['receipt']
            if key=='donkey_kong':
                assert q['receipt_SHA256']==DK_RECEIPT
                assert [p['SHA256']for p in q['images']]==DK_IMAGES
            else:
                assert q['script_SHA256']==GB_LUA and not q['images']
                assert receipt['physical_frames']==5589 and receipt['Main_returned']==4386
                assert receipt['Pit_ability_updates']==2822 and receipt['Pit_1_2_ability_updates']==63
                assert receipt['next_area_updates']==25 and receipt['full_nonshortcut1_1']
                terminal=receipt['terminal']
                assert tuple(terminal[k]for k in('x','y','y_high','state','lives','power','star','variant'))==(40,176,1,0,2,0,0,1)
            assert DESTINATION.read_bytes()==image==SOURCE.read_bytes()and check(DESTINATION)==after
            result=dict(identity=key,passed=True,actual_Downloads_launch=True,
                script_SHA256=q['script_SHA256'],receipt_SHA256=q['receipt_SHA256'],
                physical_frames=receipt['physical_frames'],
                Main_returns=receipt.get('Main_returns',receipt.get('Main_returned')),
                images=[dict(bytes=p['bytes'],SHA256=p['SHA256'])for p in q['images']],
                terminal=receipt['terminal'],capture_files=q['outputs_written'])
            results.append(result);print('DOWNLOADS_VERIFIED '+json.dumps(result,separators=(',',':')),flush=True)
    except BaseException:
        # No on-disk backup: recover the exact authenticated parent in memory.
        DESTINATION.write_bytes(parent)
        assert digest(DESTINATION.read_bytes())==Compose.PIN and check(DESTINATION)['ROM_sha256']==Compose.PIN
        print('ROLLED_BACK_TO_VERIFIED_PARENT '+Compose.PIN,flush=True)
        raise
    return dict(passed=True,installed_ROM=str(DESTINATION),SHA256=Compose.CANDIDATE,
        installed_bytes_equal_tested_candidate=True,pre_and_post_patch_guard=True,
        no_backups_or_patch_assets_or_releases=True,native_Downloads_launch_results=results,
        scope='Classic DK Goomba/mushroom/barrel graphics and GB Pit full-stage regression. '
              'DK first-pipe/death-source limitations and Prince collision/private graphics remain open.')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--install',action='store_true');args=p.parse_args()
    if args.install:q=install()
    else:
        image,parent,before,dk,gb=prepare()
        q=dict(metadata_only=True,candidate_SHA256=digest(image),installed_SHA256=before['ROM_sha256'],
               DK_Lua_SHA256=digest(dk.encode()),GB_Lua_SHA256=digest(gb.encode()),
               GB_body_identical_to_qualified82=True,outputs=0)
    print(json.dumps(q,separators=(',',':')),flush=True)
