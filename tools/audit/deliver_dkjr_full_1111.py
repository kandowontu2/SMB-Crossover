"""Install and publish the native DK Jr. 1-1 clear with stock platforms."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import check_dkjr_full_stage_physical_1111 as Physical
import deliver_jay_stock_draw_1111 as Jay
import stage_dkjr_late_nightly_1111 as Stage
from deliver_manual_title_1110 import SOURCE_BASE, apply_ips, ips_for
from nightly_patch_guard_v1 import check


R, NIGHTLY = Jay.R, Jay.NIGHTLY
PIN = Stage.WITH_JAY_PIN
PATCH_PIN = 'c4d7f170903bf6c7d416f358897e197a7bc9d0cd86f94b4a7440aa14a02a8c89'
PRIVATE_RECEIPT = '51064f55fb39b1dfa59e7c9e20aa67fcb57180c6d2365f78ecbb6d37fdf0069f'
DRIVER_PIN = 'b2eae50bb480049446303bdc6e56c1c771faef1a5160b62f3c5606adb91e69ee'
CANDIDATE = R / 'build/dkjr-late-with-jay-1111/candidate.nes'
REPORT = R / 'docs/qa/dkjr-full-nightly-delivery-1111.md'


class Recipe:
    V1 = Jay.Recipe.V1

    @staticmethod
    def proposal(base):
        sonic = Jay.Parent.Recipe.proposal(base)[0]
        jay = Jay.Source.proposal(sonic)[0]
        return (Stage.compose_with_jay(sonic, jay)[0],)


def install(output):
    assert output.is_relative_to(R / 'build') and output != R / 'build'
    assert not output.exists() or not any(output.iterdir())
    assert sha256(Physical.DRIVER.read_bytes()).hexdigest() == DRIVER_PIN
    old = NIGHTLY.read_bytes()
    assert sha256(old).hexdigest() == check(NIGHTLY)['ROM_sha256'] == Jay.PIN
    image = CANDIDATE.read_bytes()
    assert sha256(image).hexdigest() == PIN
    ips = ips_for(image)
    assert sha256(ips).hexdigest() == PATCH_PIN and apply_ips(SOURCE_BASE.read_bytes(), ips)[0] == image
    try:
        NIGHTLY.write_bytes(image)
        assert NIGHTLY.read_bytes() == image and check(NIGHTLY)['ROM_sha256'] == PIN
        result = Physical.replay(NIGHTLY, PIN, output, 0xd1f0, fast=True)
        q = result['receipt']
        assert result['passed'] and q.get('injury') is None, q
        takeoff = q['second_gap']['takeoff']
        assert (takeoff['Main'], takeoff['actor']) == (4747, dict(left=1402, direction=2))
        assert q['flag']['Main'] == 9605 and q['flag']['timer_expired'] == 0
        terminal = q['terminal']
        assert (terminal['level'], terminal['area_type'], terminal['lives']) == (1, 2, 2)
        assert NIGHTLY.read_bytes() == image and check(NIGHTLY)['ROM_sha256'] == PIN
    except BaseException:
        NIGHTLY.write_bytes(old)
        assert NIGHTLY.read_bytes() == old
        raise
    print(json.dumps(dict(passed=True, installed=True, ROM_SHA256=PIN, IPS_SHA256=PATCH_PIN,
                          receipt_SHA256=result['receipt_SHA256'], script_SHA256=result['script_SHA256'],
                          ingress=q['second_gap']['wait'], flag=q['flag'], terminal=terminal,
                          backup_files=0, output_files=0), sort_keys=True), flush=True)


def release_notes(head):
    return ('Current MMC5 WIP nightly. Apply this IPS to clean headered Super Mario Bros. (World).\n\n'
            f'ROM SHA-256: {PIN}\nIPS SHA-256: {PATCH_PIN}\nSource commit: {head}\n\n'
            'Donkey Kong Jr. can finish 1-1 with the original stage timer. Four additional '
            'stock moving platforms cover the last two pipes and the flagpole approach. '
            'Select Donkey Kong Jr. from Donkey Kong with one Select press. '
            'An uninterrupted Mesen replay cleared 1-1 and entered 1-2 with both lives. '
            'Jay McCray and Sonic remain included. See docs/qa/dkjr-full-nightly-delivery-1111.md.\n')


def publish(report_sha, installed_receipt):
    import publish_ff_corner_current_1110 as publisher

    assert len(installed_receipt) == 64 and bytes.fromhex(installed_receipt)
    with patch.multiple(publisher, PIN=PIN, PATCH_PIN=PATCH_PIN, OLD_PATCH=Jay.PATCH_PIN,
                        RECEIPTS=(PRIVATE_RECEIPT, installed_receipt), Fix=Recipe, CANDIDATE=CANDIDATE,
                        SCRIPT=Physical.DRIVER, SCRIPT_PIN=DRIVER_PIN, REPORT=REPORT,
                        release_body=release_notes):
        publisher.main(report_sha=report_sha)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument('--output', type=Path)
    operation.add_argument('--report-sha')
    parser.add_argument('--installed-receipt')
    args = parser.parse_args()
    if args.output:
        install(args.output.resolve())
    else:
        publish(args.report_sha, args.installed_receipt)


if __name__ == '__main__':
    main()
