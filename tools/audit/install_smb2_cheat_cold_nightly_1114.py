"""Direct no-backup fa66 delivery; root owns execution and Downloads replay."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import current_smb2_cheat_input_1114 as Current
import replay_smb2_cheat_cold_regress_1113 as Ordinary
import replay_smb2_invincible_contact_1113 as Contact
from nightly_patch_guard_v1 import check

C=Ordinary.C
SOURCE=C.R/'build/bub-empty-native-1113/candidate.nes'
NIGHTLY=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
FACTORIES={
    'ordinary':(Ordinary,'e7ab69df1a20981d854bcb676ffcc816930aac4f53510ac5da6080216542d2e6'),
    'contact':(Contact,'63031bae5c176ddddac76b5cb02a80720bcd40b0c10f6a875d40bbadcaae8078'),
}
CURRENT_SOURCE='f973573e52a2c752da3531ee6bc3706dc8e1096b79cc0fab2740ad4f0fb20f34'
NATIVE={
    'actual_UI_Inv1_full_Luigi_1_1_then25grounded1_2':dict(
        passed=True,root_run=37792,controller_SHA256='9f693d9f667bb92bda9f4b8ffb060a7a1b550486e5e12568f67303b00b23f625',
        receipt_SHA256='b53258a15a7aaaf183ea845e413221ccc962976d8551abe65343bf205135b655',
        physical_frames=4705,Main_updates=3768),
    'actual_UI_Inv1_ground_Goomba_body_overlap':dict(
        passed=True,root_run=30224,controller_SHA256=Contact.LUA_SHA,
        receipt_SHA256='badec2132dee4fde2a42c23af204c08f101b042e464ea87ecc8b9d55024fb777',
        physical_frames=728,Main_updates=255,positive_native_carry_and_box_overlaps=10,
        health=31,lives=2,natural_Star=0,quiet_grounded_updates_after_contact=30),
    'ordinary_no_cheat_full_Luigi_1_1_then25grounded1_2':dict(
        passed=True,root_run=34570,controller_SHA256=Ordinary.LUA_SHA,
        receipt_SHA256='be4760a0f150645431f4d01d716feb7674ecb24eb9f372cc1bf4b1fca4abe411',
        physical_frames=4521,Main_updates=3768,health=31,lives=2,next_area_grounded_updates=25),
}


def prepare():
    before=check(NIGHTLY)
    assert before['ROM_sha256']==Current.POSTBG
    public=NIGHTLY.read_bytes();assert sha256(public).hexdigest()==Current.POSTBG
    image=SOURCE.read_bytes()
    assert len(image)==2_097_168 and sha256(image).hexdigest()==C.CANDIDATE
    assert sha256(Path(Current.__file__).read_bytes()).hexdigest()==CURRENT_SOURCE
    normalized=Current.normalize(image,kind='cheat-fa66')
    assert normalized.postbg==public
    assert normalized.preserve(public,legacy_result_SHA256=Current.POSTBG,allowed_component_offsets=())[0]==image
    for name,(factory,pin)in FACTORIES.items():
        assert sha256(Path(factory.__file__).read_bytes()).hexdigest()==pin
        assert sha256(factory.controller(image).encode()).hexdigest()==factory.LUA_SHA
    assert len(NATIVE)==3 and all(q['passed']and len(q['receipt_SHA256'])==64 for q in NATIVE.values())
    evidence=dict(ROM_SHA256=C.CANDIDATE,previous_SHA256=Current.POSTBG,
        tested_candidate_path=str(SOURCE),installed_path=str(NIGHTLY),
        native_private_scopes=NATIVE,source_factory_SHA256={n:p for n,(_,p)in FACTORIES.items()},
        source_normalizer_SHA256=CURRENT_SOURCE,
        exact_strict_inverse_equals_installed_parent=True,current_fix_changed_bytes=66,
        pre_guard=before,backups_created=0,patches_created=0,releases_created=0,
        actual_Downloads_launch_still_required=True,
        verification_limit='Private exact-fa66 Luigi ordinary/UIInv1 full routes plus separate ground-Goomba contact; all other cheat triggers and natural Star pickup remain unqualified.')
    return image,evidence


def install():
    image,q=prepare()
    assert check(NIGHTLY)['ROM_sha256']==q['previous_SHA256']
    # The user's sole Downloads nightly is replaced directly without backups.
    assert NIGHTLY.write_bytes(image)==len(image)
    assert NIGHTLY.read_bytes()==image
    after=check(NIGHTLY)
    assert after['ROM_sha256']==C.CANDIDATE
    return dict(**q,installed=True,tested_candidate_byte_identical=True,
                post_guard=after,installed_ROM_bytes=len(image))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--metadata',action='store_true',help='Validate all exact bytes and evidence without installing.')
    args=p.parse_args()
    q=dict(**prepare()[1],installed=False,metadata_only=True)if args.metadata else install()
    print(json.dumps(q,separators=(',',':')),flush=True)
