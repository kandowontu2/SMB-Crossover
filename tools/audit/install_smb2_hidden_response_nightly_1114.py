"""Guarded direct421 hidden-response nightly; root executes and launch-tests."""
import argparse
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import compose_smb2_hidden_response_1114 as C
import current_smb2_cheat_input_1114 as Current
import replay_smb2_hidden_ordinary_1114 as Ordinary
import replay_smb2_hidden_invincible_contact_1114 as Contact
import replay_smb2_hidden_response_1114 as Natural
from nightly_patch_guard_v1 import check

SOURCE=C.R/'build/smb2-flag-native-1113/candidate.nes'
NIGHTLY=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
COMPOSER_SOURCE='7d8e2210a38952902694efcbb5334ae9b704902679b6353e43834f361bbee71a'
NATURAL_SOURCE='2720cd7e7989988eae7cf20e9390b1c0cef2a4ece373fca56125e917fdb4106a'
FACTORIES={
    'ordinary':(Ordinary,'760c8b2713b9d7929c09457f6bd5c7ba4c8d7e159d74b0fac8bfe9f0f91b6974'),
    'contact':(Contact,'fbab921836f65adb536a3faef6f7ea7181de4f1e74f70e92740aa1212edad8dd'),
}
NATURAL_RECEIPTS=(
    'e62fc4702d984520e2a6ff5f7bf121fb25d7a1765eaff7bf51c22e9f6f186768',
    '4e588fa580101202b86ddd21b4c840841f5891c4f71434ca4a16af12bec49bb1',
    'fd1ee729dba34029df28f16fdd9a7c999bebcaaba5a638eb67479c75e815b03a',
    '7b27a25b464b329d7c8f840526b7647a7ed45aa71d73dcf13ffa35228478dcce',
    '5b1f09d5e0b5327dcb9b3796629bc1137571b36e3fa7a995c1a8d46878a0f593',
    '42283f20fdcfa2715ffabc5b7e4ee69b208f0dc7ccd77f50acdf5c804ca38501',
    '0ddafc144b45d5a4766b2e52c0bd114a4d9ac913eec03ed854d5e5cc11a0cec1',
    'b1afa600a99a33663b981fc10f07b44f8feb40f906e2d07ce554139f7e3eb7ae',
)
REGRESSION_RECEIPTS={
    'ordinary_full':dict(passed=True,controller_SHA256=Ordinary.LUA_SHA,
        receipt_SHA256='d7f79281f0fd84b420b8280b20e64ebb359fe5481f31c8fbad5c9f33d3501259',
        physical_frames=4525,Main_returns=3768,quiet_grounded1_2_updates=25),
    'actual_UI_Inv1_ground_Goomba_contact':dict(passed=True,controller_SHA256=Contact.LUA_SHA,
        receipt_SHA256='aac32967147dfc589bf2d74765262ccac7b8ba01a35f8806dca5c3f639f33f8d',
        physical_frames=728,Main_returns=255,positive_carry_and_box_overlaps=10,
        health=31,lives=2,Star=0,quiet_grounded_updates_after_contact=30),
}


def prepare():
    before=check(NIGHTLY);assert before['ROM_sha256']==C.PIN==Current.CHEAT
    parent=NIGHTLY.read_bytes();image=SOURCE.read_bytes()
    assert len(image)==2_097_168 and sha256(image).hexdigest()==C.CANDIDATE
    assert sha256(Path(C.__file__).read_bytes()).hexdigest()==COMPOSER_SOURCE
    assert sha256(Path(Natural.__file__).read_bytes()).hexdigest()==NATURAL_SOURCE
    with patch.object(C,'inverse',lru_cache(maxsize=1)(C.inverse)):
        assert C.inverse(image)==parent and C.proposal(parent)[0]==image
        _,spans,ownership=C.bindings(parent)
        allowed={i for at,old,new in spans for i in range(at,at+len(old))}
        changed={i for i,(a,b)in enumerate(zip(parent,image,strict=True))if a!=b}
        assert len(changed)==110 and len(allowed)==201 and changed<=allowed
        protected={i for at,size in Current.protected_envelopes()for i in range(at,at+size)}
        assert not allowed&protected
        assert all(image[at:at+size]==parent[at:at+size]for at,size in Current.protected_envelopes())
        for name,(factory,pin)in FACTORIES.items():
            assert sha256(Path(factory.__file__).read_bytes()).hexdigest()==pin
            assert sha256(factory.controller(image).encode()).hexdigest()==factory.LUA_SHA
    assert len(NATURAL_RECEIPTS)==8 and all(len(q)==64 for q in NATURAL_RECEIPTS)
    assert all(q['passed']and len(q['receipt_SHA256'])==64 for q in REGRESSION_RECEIPTS.values())
    return image,dict(ROM_SHA256=C.CANDIDATE,previous_SHA256=C.PIN,
        tested_candidate_path=str(SOURCE),installed_path=str(NIGHTLY),
        composer_SHA256=COMPOSER_SOURCE,natural_replay_SHA256=NATURAL_SOURCE,
        source_factory_SHA256={name:pin for name,(_,pin)in FACTORIES.items()},
        exact_strict_inverse_equals_installed_parent=True,changed_bytes=110,granted_envelope_bytes=201,
        all_unowned_bytes_exact=True,complete_current_cheat_envelopes_exact=True,
        all66_previous_cheat_fix_bytes_preserved=True,
        resource_grant_SHA256=ownership['resource_grant_SHA256'],behavior_grant_SHA256=ownership['behavior_grant_SHA256'],
        all8_native_natural1UP_receipt_SHA256=list(NATURAL_RECEIPTS),native_regressions=REGRESSION_RECEIPTS,
        scope='All8 actual natural1UP; ordinary fullLuigi1-1/25grounded1-2; separate actualUIInv1 groundGoomba contact.',
        limitations='Mama retainedHP15 after earlier damage. NaturalStar and other cheat-trigger semantics are separate.',
        pre_guard=before,backups_created=0,patches_created=0,releases_created=0,
        actual_Downloads_launch_still_required=True)


def install():
    image,q=prepare()
    assert check(NIGHTLY)['ROM_sha256']==C.PIN
    assert NIGHTLY.write_bytes(image)==len(image)
    assert NIGHTLY.read_bytes()==image
    after=check(NIGHTLY);assert after['ROM_sha256']==C.CANDIDATE
    return dict(**q,installed=True,tested_candidate_byte_identical=True,post_guard=after,installed_ROM_bytes=len(image))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--metadata',action='store_true',help='Validate exact ownership/bytes/evidence without installing.')
    args=p.parse_args()
    q=dict(**prepare()[1],installed=False,metadata_only=True)if args.metadata else install()
    print(json.dumps(q,separators=(',',':')),flush=True)
