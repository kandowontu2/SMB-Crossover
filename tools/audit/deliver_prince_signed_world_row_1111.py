"""Install the verified final-stair correction and refresh the Current IPS."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import compose_prince_signed_world_row_1111 as Source
from deliver_jay_machinegun_1111 import NIGHTLY, PATCH_PIN as PREVIOUS_IPS, R
from deliver_manual_title_1110 import SOURCE_BASE, SOURCE_PIN, apply_ips, ips_for
from nightly_patch_guard_v1 import check
import replay_jay_machinegun_native_1111 as Jay
import replay_prince_full_route_1111 as Prince


PIN = Source.CANDIDATE
PATCH_PIN = '38315b48d874e9c4d904b8e75a8df6085b155e3639a8d7f15f18416cee6f2ee8'
RECEIPT = '59c7e34e6e367089370bcf13456cd76fb72ff1c1bb7aac5958f400614ab97b6f'
CONTROLLER_PIN = '8d7b35f9354c0dde782971d35847273d656850b584809cb55fbc6c8c6792b270'
TAIL_PIN = 'd34e073c8337ea2eeaa4f648c7406deb9e19d953cee2173535622f6c2ca26191'
CANDIDATE = R / 'build/prince-finish-route-1111/candidate.nes'
REPORT = R / 'docs/qa/prince-late-route-1111.md'


def install(output):
    assert output == CANDIDATE.parent and check(NIGHTLY)['ROM_sha256'] == Source.PARENT
    parent = NIGHTLY.read_bytes()
    image, layout = Source.proposal(parent)
    assert image == CANDIDATE.read_bytes() and Source.recover_parent(image) == parent
    base = SOURCE_BASE.read_bytes()
    ips = ips_for(image)
    assert sha256(base).hexdigest() == SOURCE_PIN and sha256(ips).hexdigest() == PATCH_PIN
    assert apply_ips(base, ips)[0] == image

    script = output / 'controller.lua'
    script.write_text(Prince.controller(layout['cookie'], layout['support_publication']),
                      encoding='utf-8', newline='\n')
    assert sha256(script.read_bytes()).hexdigest() == CONTROLLER_PIN
    try:
        NIGHTLY.write_bytes(image)
        assert NIGHTLY.read_bytes() == image and check(NIGHTLY)['ROM_sha256'] == PIN
        prince = Prince.replay(script, NIGHTLY, output / 'prince', PIN, stop_x=3084)
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
            'Prince of Persia can climb the final staircase in 1-1 with his original controls. Mesen '
            'verifies the third gap, both late pipes and the staircase with both lives and no helper '
            'platforms. His flagpole approach remains open. Jay McCray still earns his original machine '
            'gun after 1-1 and passed the underground 1-2 replay on this update.\n')


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
                        SCRIPT=Prince.TAIL, SCRIPT_PIN=TAIL_PIN, REPORT=REPORT, release_body=release_notes):
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
