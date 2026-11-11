"""Install the full Prince 1-1 clear and refresh the Current IPS."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import compose_prince_native_flag_1111 as Source
from deliver_prince_signed_world_row_1111 import NIGHTLY, PATCH_PIN as PREVIOUS_IPS, R
from deliver_manual_title_1110 import SOURCE_BASE, SOURCE_PIN, apply_ips, ips_for
from nightly_patch_guard_v1 import check
import replay_jay_machinegun_native_1111 as Jay
import replay_prince_native_flag_1111 as Prince


PIN = '2d7fb6e63ea55f2d0eb9ef3af4efc467233da013dc70e295952a4adcdd14ecdb'
PATCH_PIN = '566a1ab2789c7a15c75485d1198c0f6742f23385b72000c4ebf65bde93910ce0'
RECEIPT = '0dbfd29e1ee38afffea553c077c06545325930bfe9cbdbd0272eda708d0ab0c2'
CONTROLLER_PIN = 'fd0795e9d7c1e46a996bab6f87b75fbac2539af671c68ad7448f0b87b1d80458'
FLAG_PIN = '80b131752f2d5a47b81d003f5bff28f9da979c7491bffd346b8251c8fbef4358'
CANDIDATE = R / 'build/prince-native-flag-1111/candidate.nes'
REPORT = R / 'docs/qa/prince-native-flag-delivery-1111.md'


def install(output):
    assert output == CANDIDATE.parent and check(NIGHTLY)['ROM_sha256'] == Source.PARENT
    parent = NIGHTLY.read_bytes()
    image, layout = Source.proposal(parent)
    assert sha256(image).hexdigest() == PIN
    assert CANDIDATE.read_bytes() == image and Source.recover_parent(image) == parent
    base = SOURCE_BASE.read_bytes()
    ips = ips_for(image)
    assert sha256(base).hexdigest() == SOURCE_PIN and sha256(ips).hexdigest() == PATCH_PIN
    assert apply_ips(base, ips)[0] == image

    script = output / 'controller.lua'
    script.write_text(Prince.controller(layout['cookie'], Source.Signed.SUPPORT_PUBLICATION, brake=3100),
                      encoding='utf-8', newline='\n')
    assert sha256(script.read_bytes()).hexdigest() == CONTROLLER_PIN
    try:
        NIGHTLY.write_bytes(image)
        assert NIGHTLY.read_bytes() == image and check(NIGHTLY)['ROM_sha256'] == PIN
        prince, _ = Prince.replay(script, NIGHTLY, output / 'prince', PIN)
        assert prince['passed'] and prince['receipt_SHA256'] == RECEIPT, prince['receipt']
        script.write_text(Jay.Source.controller(), encoding='utf-8', newline='\n')
        jay = Jay.replay(script, NIGHTLY, output / 'jay', expected=PIN)
        assert jay['passed'], jay['receipt']
        assert NIGHTLY.read_bytes() == image and check(NIGHTLY)['ROM_sha256'] == PIN
    except BaseException:
        NIGHTLY.write_bytes(parent)
        assert NIGHTLY.read_bytes() == parent and check(NIGHTLY)['ROM_sha256'] == Source.PARENT
        raise
    print(json.dumps(dict(installed=True, ROM_SHA256=PIN, IPS_SHA256=PATCH_PIN,
                          Prince_receipt=RECEIPT, Jay_receipt=jay['receipt_SHA256'],
                          backup_files=0), sort_keys=True), flush=True)


def release_notes(head):
    return ('Current MMC5 WIP nightly. Apply the sole IPS to clean headered Super Mario Bros. (World).\n\n'
            f'ROM SHA-256: {PIN}\nIPS SHA-256: {PATCH_PIN}\nSource commit: {head}\n\n'
            'Prince of Persia clears the original 1-1 route with no helper platforms. His standing jump '
            'can catch the native flagpole. Mesen verifies the flag, castle and active underground 1-2 '
            'with both lives. Highlight Excitebike and press Select once for Prince. Jay McCray still '
            'earns his original machine gun on entering 1-2.\n')


def publish(report_sha):
    import publish_ff_corner_current_1110 as publisher

    class Recipe:
        V1 = SimpleNamespace(BASE=SOURCE_BASE)

        @staticmethod
        def proposal(base):
            assert sha256(base).hexdigest() == SOURCE_PIN
            return Source.proposal(Source.recover_parent(NIGHTLY.read_bytes()))

    with patch.multiple(publisher, PIN=PIN, PATCH_PIN=PATCH_PIN, OLD_PATCH=PREVIOUS_IPS,
                        RECEIPTS=(RECEIPT, CONTROLLER_PIN), Fix=Recipe, CANDIDATE=CANDIDATE,
                        SCRIPT=Prince.FLAG, SCRIPT_PIN=FLAG_PIN, REPORT=REPORT, release_body=release_notes):
        publisher.main(report_sha=report_sha)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--install-output', type=Path)
    mode.add_argument('--publish-report-sha')
    args = parser.parse_args()
    if args.install_output:
        install(args.install_output.resolve())
    else:
        publish(args.publish_report_sha)
