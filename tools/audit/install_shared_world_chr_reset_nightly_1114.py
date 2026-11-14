"""Install the root-qualified common CHR fix and verify actual Downloads launch.

Run only through the bounded runner with the existing flag two-file output.
Direct replacement: no backup, patch, release, capture or receipt files.
Prince/Donkey Kong private sprite-window conflicts and Prince collision remain.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import compose_shared_world_chr_reset_1114 as Compose
import replay_shared_world_chr_reset_1114 as Replay
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from mesen_session_guard_v1 import require_free_workspace
from run_stdout_mesen_1110 import run

R=Path(__file__).resolve().parents[2]
OUT=R/'build/smb2-flag-native-1113'
SOURCE=OUT/'candidate.nes'
DESTINATION=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
COMPOSER_SHA='036228e017fcc46f956d944bb47533321cb252c97137d63ceaa24ebcbf593272'
REPLAY_SHA='0fb4e745e0ec7e47a27f43d3f8b7015e8fbc80f87225fec08751d20f444424c0'
EXPECTED={
    'hogan':dict(Lua='829f3f2529c241af8a2fe2ce3d8cf453624646a0f91a6d88480b5d91978b4165',
        receipt='b1388d1a1d4f5f38ddb34a82a11a56b013df0bc62cae94fb63896a9005057e05',
        images=['07affc626261432af5b003c6a03e1b1dc4396b0f6b2bb4facfccf5f2ff55f3a1',
                'a177ef68d0ed895ba76727c8e88bea39fe0fbd5e5f3f4941145139b20fe91722']),
    'toad':dict(Lua='a42266b5ba49dc7aa07f59431f7fee93b2fac638407728daebc2b3bec2720161',
        receipt='cd0e705ddb11054cd9bdc92d4170616b42437fe550c7338edbb6a4e5abc701f1',images=[])
}


def digest(data):return sha256(data).hexdigest()


def prepare():
    assert digest(Path(Compose.__file__).read_bytes())==COMPOSER_SHA
    assert digest(Path(Replay.__file__).read_bytes())==REPLAY_SHA
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    image=SOURCE.read_bytes();assert digest(image)==Compose.CANDIDATE
    parent=Compose.inverse(image);assert digest(parent)==Compose.PIN
    assert Compose.proposal(parent)[0]==image
    before=check(DESTINATION)
    assert before['ROM_sha256']in(Compose.PIN,Compose.CANDIDATE),'Unexpected installed nightly'
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    return image,before


def install():
    image,before=prepare()
    require_free_workspace(R,DESTINATION,allow_interactive=True)
    # This is the user-requested final location, not a generated backup/cache.
    DESTINATION.write_bytes(image)
    assert DESTINATION.read_bytes()==image==SOURCE.read_bytes()
    after=check(DESTINATION);assert after['ROM_sha256']==Compose.CANDIDATE
    print('INSTALLED '+json.dumps(dict(ROM=str(DESTINATION),SHA256=Compose.CANDIDATE,
        bytes=len(image),previous_SHA256=before['ROM_sha256'],backup_files=0,patch_assets=0,
        releases_created=0,postcopy_native_verification='running')),flush=True)
    results=[]
    for key in('hogan','toad'):
        text=Replay.controller(image,key)if key=='hogan'else Replay.stage_controller(image,key)
        assert digest(text.encode())==EXPECTED[key]['Lua']
        script=OUT/'controller.lua';script.write_bytes(text.encode())
        q=run(script,DESTINATION,OUT/'capture',Compose.CANDIDATE,180)
        assert q['passed']and q['receipt_SHA256']==EXPECTED[key]['receipt'],(key,q['passed'],q['receipt_SHA256'])
        assert [p['SHA256']for p in q['images']]==EXPECTED[key]['images']
        assert DESTINATION.read_bytes()==image==SOURCE.read_bytes()and check(DESTINATION)==after
        receipt=q['receipt']
        result=dict(identity=key,passed=True,actual_Downloads_launch=True,
            Lua_SHA256=q['script_SHA256'],receipt_SHA256=q['receipt_SHA256'],
            images=[dict(bytes=p['bytes'],SHA256=p['SHA256'])for p in q['images']],
            physical_frames=receipt['physical_frames'],
            Main_returns=receipt.get('Main_returns',receipt.get('Main_returned')),
            terminal=receipt['terminal'],capture_files=q['outputs_written'])
        results.append(result);print('DOWNLOADS_VERIFIED '+json.dumps(result,separators=(',',':')),flush=True)
    return dict(passed=True,installed_ROM=str(DESTINATION),SHA256=Compose.CANDIDATE,
        installed_bytes_equal_tested_candidate=True,matching_sidecar_patches=[],
        pre_and_post_patch_guard=True,no_backups_or_patch_assets_or_releases=True,
        native_Downloads_launch_results=results,
        scope='Common stale CHR modes repaired; all six wrestlers verified with native Goomba/mushroom patterns. '
              'Prince and Donkey Kong private-window powerup conflicts and Prince collision remain open.')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--install',action='store_true');args=p.parse_args()
    if args.install:q=install()
    else:
        image,before=prepare();q=dict(metadata_only=True,candidate_SHA256=digest(image),installed_SHA256=before['ROM_sha256'],outputs=0)
    print(json.dumps(q,separators=(',',':')),flush=True)
