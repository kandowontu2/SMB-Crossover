"""Install Steve's tested punch and refresh the existing Current release."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import deliver_prince_brick_1111 as Prince
import replay_jay_steve_regression_1111 as Jay
import replay_steve_native_1111 as Steve
from deliver_manual_title_1110 import SOURCE_BASE, SOURCE_PIN, apply_ips, ips_for
from nightly_patch_guard_v1 import check


R, NIGHTLY = Prince.R, Prince.NIGHTLY
PIN = Steve.PIN
PATCH_PIN = '9b6724808f6901ddd2f0ac8b2fb2035e5d70c3dc0be043c43577ff3202fc7101'
SCRIPT_PIN = 'b744c57814d8aceedc37eafc03e40b41239e62b3f5366fac3ef1550ff77d61b2'
STEVE_RECEIPT = '81643a84a33f5394ea26b341fd4e7513a08caf2dde10acd5ac9d8ae4a70e0459'
JAY_RECEIPT = 'b06b937ef22a65b45f6456183851db5690e80cb88d538d31946be154c308fab8'
JAY_SCRIPT_PIN = 'f56612a4b2d8eca5fe9df429d1d7db0b132c8fb3ead729208a35c6237b8c5458'
REPORT = R / 'docs/qa/steve-punch-delivery-1111.md'
CANDIDATE = R / 'build/steve-punch-native-1111/candidate.nes'


def digest(data):
    return sha256(data).hexdigest()


def replay_jay(rom, output):
    controller = output / 'controller.lua'
    controller.write_text(Jay.controller(), encoding='utf-8', newline='\n')
    assert digest(controller.read_bytes()) == JAY_SCRIPT_PIN
    result = Jay.replay(rom, output / 'jay-capture', controller)
    q = result['receipt']
    assert result['passed'] and result['receipt_SHA256'] == JAY_RECEIPT
    assert q['flag'] and q['castle'] and q['three_way']
    assert (q['lives'], q['scroll_entries'], q['dma_matches'], q['x'], q['y']) == (2, 2403, 1117, 40, 48)
    return result['receipt_SHA256']


def replay_prince(rom, output):
    controller = output / 'controller.lua'
    controller.write_text(Prince.Source.Replay.published_controller(Prince.COOKIE), encoding='utf-8', newline='\n')
    assert digest(controller.read_bytes()) == Prince.ASSEMBLED_PIN
    result = Steve.run(controller, rom, output / 'prince-capture', PIN, 120, variant=3,
                       extra_env={'SMB_PRINCE_KOOPA_BRAKE': '1470', 'SMB_PRINCE_KOOPA_MODE': 'runway',
                                  'SMB_PRINCE_KOOPA_JUMP_X': '1501'})
    q = result['receipt']
    assert result['passed'] and q['physical_frames'] == 6836
    assert tuple(q['terminal'][key] for key in ('x', 'y', 'action', 'hp', 'lives')) == (1513, 112, 4, 4, 2)
    return result['receipt_SHA256']


def install(output):
    assert output.is_relative_to(R / 'build') and output != R / 'build' and not output.exists()
    parent = NIGHTLY.read_bytes()
    assert digest(parent) == check(NIGHTLY)['ROM_sha256'] == Prince.PIN
    candidate, linked = Steve.Source.proposal(parent)
    assert digest(candidate) == PIN
    if CANDIDATE.exists():
        assert candidate == CANDIDATE.read_bytes()
    assert digest(Steve.SCRIPT.read_bytes()) == SCRIPT_PIN
    base, ips = SOURCE_BASE.read_bytes(), ips_for(candidate)
    assert digest(base) == SOURCE_PIN and digest(ips) == PATCH_PIN and apply_ips(base, ips)[0] == candidate

    output.mkdir()
    try:
        NIGHTLY.write_bytes(candidate)
        assert NIGHTLY.read_bytes() == candidate and check(NIGHTLY)['ROM_sha256'] == PIN
        result = Steve.replay(NIGHTLY, output / 'steve-capture', linked)
        assert result['passed'] and result['receipt_SHA256'] == STEVE_RECEIPT, result['receipt']
        jay = replay_jay(NIGHTLY, output)
        prince = replay_prince(NIGHTLY, output)
        assert NIGHTLY.read_bytes() == candidate and check(NIGHTLY)['ROM_sha256'] == PIN
    except BaseException:
        NIGHTLY.write_bytes(parent)
        assert NIGHTLY.read_bytes() == parent
        raise
    print(json.dumps(dict(passed=True, installed=True, ROM_SHA256=PIN, IPS_SHA256=PATCH_PIN,
                          Steve_receipt=STEVE_RECEIPT, Jay_receipt=jay, Prince_receipt=prince,
                          backup_files=0), sort_keys=True), flush=True)


def release_notes(head):
    return ('Current MMC5 WIP nightly. Apply the sole IPS to clean headered Super Mario Bros. (World).\n\n'
            f'ROM SHA-256: {PIN}\nIPS SHA-256: {PATCH_PIN}\nSource commit: {head}\n\n'
            'Choose Mike Jones and press Select twice for Steve Hermann. B now uses his original Shatterhand '
            'punch timings with native Goomba contact and original fist art. This is the first live attack pass. '
            'The Jay McCray 1-1 clear and Prince coin-brick fix were rechecked in the installed nightly. '
            'See docs/qa/steve-punch-delivery-1111.md.\n')


def publish(report_sha):
    import publish_ff_corner_current_1110 as publisher

    class Recipe:
        V1 = SimpleNamespace(BASE=SOURCE_BASE)

        @staticmethod
        def proposal(base):
            assert digest(base) == SOURCE_PIN
            image = NIGHTLY.read_bytes()
            assert digest(image) == PIN
            parent = Steve.Source.recover_parent(image)
            assert digest(parent) == Prince.PIN
            return Steve.Source.proposal(parent)

    with patch.multiple(publisher, PIN=PIN, PATCH_PIN=PATCH_PIN, OLD_PATCH=Prince.PATCH_PIN,
                        RECEIPTS=(STEVE_RECEIPT, JAY_RECEIPT), Fix=Recipe, CANDIDATE=CANDIDATE,
                        SCRIPT=Steve.SCRIPT, SCRIPT_PIN=SCRIPT_PIN, REPORT=REPORT, release_body=release_notes):
        publisher.main(report_sha=report_sha)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--install-output', type=Path)
    mode.add_argument('--publish-report-sha')
    args = parser.parse_args()
    if args.install_output:
        install(args.install_output.resolve())
    else:
        publish(args.publish_report_sha)


if __name__ == '__main__':
    main()
