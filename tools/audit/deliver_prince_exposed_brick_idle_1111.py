"""Install the verified Prince footing fix and refresh the existing Current IPS."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import check_prince_exposed_brick_idle_1111 as Source
import replay_prince_second_brick_1111 as Replay
from deliver_manual_title_1110 import SOURCE_BASE, SOURCE_PIN, apply_ips, ips_for
from deliver_steve_punch_1111 import PATCH_PIN as OLD_PATCH
from nightly_patch_guard_v1 import check


R, NIGHTLY = Replay.Delivery.R, Replay.Delivery.NIGHTLY
PIN = 'ac2624467d4c3abc8988088ab22a4d2a0f52059e2e2d23373940fc9d17006066'
PATCH_PIN = '924671aa4670c1948e2374cb759a847157eea63b0e5dc168ef405d3aee069f3c'
COOKIE = 'a726023ffc16e97ef60a2a63631902d4'
RECEIPTS = (
    '29714b4d23560d7b0834abb8278d5522ca9790bc68b78580e837536a0a068f94',
    '623c8d2385d18fcadc1331c0c459850227446b6a39bc93c0e79a4cf0f5bdcb82',
)
SCRIPT_PIN = '20bb02bebee0949abf9e935927c8abd9c446e8f970254020a0c6420dd4b6e93f'
CONTROLLER_PIN = '11803da41c62bf1ac931a2ade0745362c0d8806864694bc724bd9f97c9df3375'
REPORT = R / 'docs/qa/prince-exposed-brick-idle-delivery-1111.md'
CANDIDATE = R / 'build/prince-ordinary-brick-1111/candidate.nes'


def digest(data):
    return sha256(data).hexdigest()


def recover_parent(image):
    assert digest(image) == PIN
    old, new = Source.source_workers()
    parent, _ = Source.replace_workers(image, new, old)
    assert digest(parent) == Source.PIN
    return parent


def verify_route(script, rom, output, *, hold):
    result = Replay.replay(script, rom, output, PIN, hold_on_cap=hold)
    receipt = result['receipt']
    assert result['passed'] and result['receipt_SHA256'] == RECEIPTS[0 if hold else 1], receipt
    assert receipt['controller_only'] and not receipt['added_helpers']
    terminal = receipt['terminal']
    expected = (1587, 112, 3221) if hold else (1713, 176, 3369)
    assert tuple(terminal[key] for key in ('x', 'y', 'commit')) == expected
    assert (terminal['hp'], terminal['lives'], terminal['ground']) == (4, 2, 0)
    return result['receipt_SHA256']


def install(output):
    assert output.is_relative_to(R / 'build') and output != R / 'build'
    assert check(NIGHTLY)['ROM_sha256'] == Source.PIN
    parent = NIGHTLY.read_bytes()
    candidate, layout = Source.proposal(parent)
    assert digest(candidate) == PIN and layout['cookie'] == COOKIE
    assert recover_parent(candidate) == parent
    if CANDIDATE.exists():
        assert CANDIDATE.read_bytes() == candidate
    base, ips = SOURCE_BASE.read_bytes(), ips_for(candidate)
    assert digest(base) == SOURCE_PIN and digest(ips) == PATCH_PIN
    assert apply_ips(base, ips)[0] == candidate
    assert digest(Replay.TAIL.read_bytes()) == SCRIPT_PIN
    output.mkdir(exist_ok=True)
    script = output / 'controller.lua'
    script.write_text(Replay.controller(COOKIE, 0xd749), encoding='utf-8', newline='\n')
    assert digest(script.read_bytes()) == CONTROLLER_PIN
    try:
        NIGHTLY.write_bytes(candidate)
        assert NIGHTLY.read_bytes() == candidate and check(NIGHTLY)['ROM_sha256'] == PIN
        receipts = tuple(verify_route(script, NIGHTLY, output / 'capture', hold=hold)
                         for hold in (True, False))
        assert NIGHTLY.read_bytes() == candidate and check(NIGHTLY)['ROM_sha256'] == PIN
    except BaseException:
        NIGHTLY.write_bytes(parent)
        assert NIGHTLY.read_bytes() == parent
        raise
    print(json.dumps(dict(installed=True, ROM_SHA256=PIN, IPS_SHA256=PATCH_PIN,
                          receipts=receipts, controller_SHA256=CONTROLLER_PIN,
                          backup_files=0)), flush=True)


def release_notes(head):
    return ('Current MMC5 WIP nightly. Apply the sole IPS to clean headered Super Mario Bros. (World).\n\n'
            f'ROM SHA-256: {PIN}\nIPS SHA-256: {PATCH_PIN}\nSource commit: {head}\n\n'
            'Prince of Persia keeps his footing after climbing onto the ordinary brick pair after the second '
            'gap in 1-1. Mesen verifies standing on the bricks and passing the live Koopa with both lives. '
            'Steve Hermann’s punch remains in this nightly. See docs/qa/prince-exposed-brick-idle-delivery-1111.md.\n')


def publish(report_sha):
    import publish_ff_corner_current_1110 as publisher

    class Recipe:
        V1 = SimpleNamespace(BASE=SOURCE_BASE)

        @staticmethod
        def proposal(base):
            assert digest(base) == SOURCE_PIN
            return Source.proposal(recover_parent(NIGHTLY.read_bytes()))

    with patch.multiple(publisher, PIN=PIN, PATCH_PIN=PATCH_PIN, OLD_PATCH=OLD_PATCH,
                        RECEIPTS=RECEIPTS, Fix=Recipe, CANDIDATE=CANDIDATE,
                        SCRIPT=Replay.TAIL, SCRIPT_PIN=SCRIPT_PIN, REPORT=REPORT,
                        release_body=release_notes):
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
