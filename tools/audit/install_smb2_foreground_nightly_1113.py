"""Directly install the exact eight-route physically qualified SMB2 merge."""
from hashlib import sha256
import json
from pathlib import Path

import compose_smb2_foreground_current_1113 as C
from nightly_patch_guard_v1 import check

R=Path(__file__).resolve().parents[2]
SOURCE=R/'build/smb2-flag-native-1113/candidate.nes'
NIGHTLY=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
RECEIPTS={
    'Mario':'ad596d9940dd3be4f0460d951febe82ec85d42415708088e010049ebc21247d0',
    'Luigi':'1e1e00c74cdc901c677b97d51ab733f8cfe374d06377defa6a71af4f96ba0be0',
    'Toad':'4ae4a324a03dedc6fb64bd76d1de7847c15b817092a62bd016da861b2960ca17',
    'Peach':'2f84be2955f2723de94698140ccf674f8bf9be04834884b32d18a8cc5035e70b',
    'Imajin':'25d0718ab4ca39090d43b6c4dab386b1546f33cee865062083d1fe1320bd1c52',
    'Lina':'edbd8b49c1dc1a417c10f24d27178a47c0a84dfeaca562b18a1c2460fd5cbadf',
    'Papa':'0d1701a029bd4fc073941af7047b181c22ea497ff74b444cc5ac1e3623bce2a3',
    'Mama':'95f0e4d72d5cef16f8606fa891b15872e1dc503d451daac266913de02fa3594b',
}


def main():
    before=check(NIGHTLY)
    assert before['ROM_sha256']==C.PIN
    image=SOURCE.read_bytes()
    assert len(image)==2_097_168 and sha256(image).hexdigest()==C.CANDIDATE
    assert C.inverse(image)==NIGHTLY.read_bytes()
    assert len(RECEIPTS)==8 and all(len(value)==64 for value in RECEIPTS.values())
    # The user requests replacement of this sole path without backup files.
    assert NIGHTLY.write_bytes(image)==len(image)
    assert NIGHTLY.read_bytes()==image and check(NIGHTLY)['ROM_sha256']==C.CANDIDATE
    print(json.dumps(dict(installed=True,path=str(NIGHTLY),ROM_SHA256=C.CANDIDATE,
        previous_SHA256=C.PIN,tested_candidate_byte_identical=True,
        native_receipts=RECEIPTS,backups_created=0,patches_created=0,
        releases_created=0,post_install_launch_still_required=True)),flush=True)


if __name__=='__main__':main()
