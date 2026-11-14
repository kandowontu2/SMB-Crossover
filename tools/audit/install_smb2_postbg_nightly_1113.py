"""Direct replacement with the exact eight-route/correct-return qualified ROM."""
from hashlib import sha256
import json
from pathlib import Path

import compose_smb2_postbg_mirror_1113 as C
from nightly_patch_guard_v1 import check

SOURCE=C.R/'build/smb2-flag-native-1113/candidate.nes'
NIGHTLY=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
RECEIPTS={
    'Mario':'9d7b0d9f5150c6f5d91c4d1d6a81443cf96d331c75af2f9a869d40961985ce63',
    'Luigi':'a5cbd52a589028a371850cabe5272a6ed1a721a692dc5b5347390470529bb88b',
    'Toad':'a961bb15a487ba20f60ea732c896455687e77225fcacc785e37e0f5133a71f4a',
    'Peach':'523fc037d0a624b795a7c1e87a817ee5fc9cc13433c368632892c9dc42ea59df',
    'Imajin':'9c1bcae7d569426f28449cf6ee6f9236bea0d37c83e5e67f9bba5cca7d171292',
    'Lina':'6238f4047575483ebca522742e6b11ad2d1e765a45337371d6e376e408c26af2',
    'Papa':'ee15b2e822d5f02c6949b8ed33595dbdba8c7130d7c6b1c9fed19065852b5fa6',
    'Mama':'ed61fb8cdc7b326478f045286bea241627861b3d229e518bd9b43cecb6c55b4d',
}
SCENE='ee83d3ff715123320be9bda561dcae4984158d931eb8c46029d128dbc0686ada'


def main():
    assert check(NIGHTLY)['ROM_sha256']==C.PIN
    image=SOURCE.read_bytes()
    assert len(image)==2_097_168 and sha256(image).hexdigest()==C.CANDIDATE
    assert C.inverse(image)==NIGHTLY.read_bytes()
    assert len(RECEIPTS)==8 and all(len(value)==64 for value in RECEIPTS.values())
    assert len(SCENE)==64
    # The user requests this sole file replaced directly, without backups.
    assert NIGHTLY.write_bytes(image)==len(image)
    assert NIGHTLY.read_bytes()==image and check(NIGHTLY)['ROM_sha256']==C.CANDIDATE
    print(json.dumps(dict(installed=True,path=str(NIGHTLY),ROM_SHA256=C.CANDIDATE,
        previous_SHA256=C.PIN,tested_candidate_byte_identical=True,
        native_full_route_receipts=RECEIPTS,correct_return_scene_receipt=SCENE,
        backups_created=0,patches_created=0,releases_created=0,
        actual_Downloads_launch_still_required=True)),flush=True)


if __name__=='__main__':main()
