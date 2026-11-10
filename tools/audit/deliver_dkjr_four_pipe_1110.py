"""Deliver the Mesen-tested DK Jr. four-pipe update and sole Current IPS."""
import argparse
import json
from pathlib import Path
from unittest.mock import patch

import check_dkjr_four_pipe_funded_1110 as Fix
import deliver_dkjr_second_pipe_1110 as Previous
from deliver_manual_title_1110 import SOURCE_BASE, apply_ips, ips_for
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

PIN = 'b031802c7bc4f4e9596683e66f2f53c124b3a3ac155b80bbec03c5965b8e4e65'
PATCH_PIN = 'f797c2adee4f7170bfd75264480179545464547c6cedb55257978475000a3fae'
SCRIPT_PIN = 'ca2c7429cbc9198ffff21a733b39234469cdebffb89143d899b95a4c4af37eb8'
RECEIPT = '6b38ff7c623440ddca990760c2f3d59dd98691ddc3681a82553304f5ea21ba20'
SCRIPT = Fix.R / 'tools/playthroughs/dkjr_four_pipe_stdout_1110.lua'
CANDIDATE = Fix.R / 'build/dkjr-later-pipe-native-1110/candidate.nes'
REPORT = Fix.R / 'docs/qa/dkjr-four-pipe-delivery-1110.md'


def install(output):
    assert output.is_relative_to(Fix.R / 'build') and not output.exists()
    before = check(Fix.NIGHTLY)
    old = Fix.NIGHTLY.read_bytes()
    assert Fix.S.sha(old) == before['ROM_sha256'] == Fix.PARENT
    image, _, _ = Fix.proposal(old)
    assert Fix.S.sha(image) == PIN and image == CANDIDATE.read_bytes()
    assert Fix.S.sha(SCRIPT.read_bytes()) == SCRIPT_PIN
    ips = ips_for(image)
    assert Fix.S.sha(ips) == PATCH_PIN and apply_ips(SOURCE_BASE.read_bytes(), ips)[0] == image
    try:
        Fix.NIGHTLY.write_bytes(image)
        assert Fix.NIGHTLY.read_bytes() == image and check(Fix.NIGHTLY)['ROM_sha256'] == PIN
        result = run(SCRIPT, Fix.NIGHTLY, output, PIN, 240)
        assert result['passed'] and result['receipt_SHA256'] == RECEIPT, result['receipt']
        after = check(Fix.NIGHTLY)
        assert Fix.NIGHTLY.read_bytes() == image and after['ROM_sha256'] == PIN
    except BaseException:
        Fix.NIGHTLY.write_bytes(old)
        assert Fix.NIGHTLY.read_bytes() == old
        raise
    print(json.dumps(dict(passed=True, installed=True, ROM_SHA256=PIN, IPS_SHA256=PATCH_PIN,
                          receipt_SHA256=RECEIPT, guard_before=before, guard_after=after,
                          terminal=result['receipt']['terminal'], backup_files=0,
                          output_files=0), sort_keys=True), flush=True)


class Recipe:
    V1 = Previous.Recipe.V1

    @staticmethod
    def proposal(base):
        return Fix.proposal(Previous.Recipe.proposal(base)[0])


def release_notes(head):
    return ('Current MMC5 WIP nightly. Apply this IPS to clean headered Super Mario Bros. (World).\n\n'
            f'ROM SHA-256: {PIN}\nIPS SHA-256: {PATCH_PIN}\nSource commit: {head}\n\n'
            'Donkey Kong Jr. now has stock girders at the third and fourth pipes in 1-1. '
            'A controller-only Mesen replay cleared all four pipes and the first gap with both lives. '
            'The second gap, later stage, and earned powerups are still being tested. '
            'Select him from Donkey Kong. See docs/qa/dkjr-four-pipe-delivery-1110.md.\n')


def publish(report_sha):
    import publish_ff_corner_current_1110 as publisher

    with patch.multiple(publisher, PIN=PIN, PATCH_PIN=PATCH_PIN, OLD_PATCH=Previous.PATCH_PIN,
                        RECEIPTS=(RECEIPT,), Fix=Recipe, CANDIDATE=CANDIDATE,
                        SCRIPT=SCRIPT, SCRIPT_PIN=SCRIPT_PIN, REPORT=REPORT,
                        release_body=release_notes):
        publisher.main(report_sha=report_sha)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    command = parser.add_mutually_exclusive_group(required=True)
    command.add_argument('--output', type=Path)
    command.add_argument('--report-sha')
    args = parser.parse_args()
    if args.output:
        install(args.output.resolve())
    else:
        publish(args.report_sha)


if __name__ == '__main__':
    main()
