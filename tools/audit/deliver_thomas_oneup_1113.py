"""Install Thomas's verified 1UP lift and publish the matching Current IPS."""

import argparse
from types import SimpleNamespace
from unittest.mock import patch

import compose_thomas_oneup_lift_1113 as Fix
import deliver_prince_moving_support_1112 as Shared
import replay_thomas_oneup_1113 as Test
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run


OUTPUT = Fix.R/'build/metal-flower-native-1112'
PIN = Fix.PIN
PARENT = Fix.Current.CURRENT
PATCH_PIN = '8d08344f5faa26ac9bf5e4405455732f23699fd6777e4d1845408b89a9c66300'
OLD_PATCH = '2588d7bde413c7464b2695a6c91ac4d47f3dcad83e63511a6d9801e886d3d1dd'
RECEIPT = '3035b17ea05fa4600ea64238fbbd59dc03a83fd680404c210e597392b5565cf3'
STAGE_RECEIPT = '0ce772a418109ffd070ea0c1d5b29d6ba290ea1f21757246c3a7ff9f3737f3de'
SCRIPT_PIN = '66de68b126ddf089e27861f33d44600216b6752c578c9c70714ac675afb6d352'
REPORT = Fix.R/'docs/qa/thomas-oneup-lift-1113.md'


def notes(head):
    return (
        'Apply the sole IPS to clean headered Super Mario Bros. (World).\n\n'
        f'ROM SHA-256: {PIN}\nIPS SHA-256: {PATCH_PIN}\nSource commit: {head}\n\n'
        'Thomas has a native vertical lift for the hidden 1UP in 1-1, in addition '
        'to his flower and pipe assists. The original jump is preserved. '
        'Mesen verified boarding, a fresh jump into the hidden block, natural '
        '1UP emergence and collection, and exactly one awarded life. '
        'The installed Downloads ROM repeats this test. A separate controller-only '
        'run earns mushroom, flower and Star, crosses all six pipes, and clears '
        '1-1 into active 1-2 with both lives.\n\n'
        'Includes preceding Karnov Bomb and Kirby capture fixes. '
        'Full roster and original ability reviews remain in progress. '
        'See docs/qa/thomas-oneup-lift-1113.md for validation scope.\n'
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--install', action='store_true')
    modes.add_argument('--publish-report-sha')
    args = parser.parse_args()
    candidate_path = OUTPUT/'candidate.nes'
    candidate = candidate_path.read_bytes()
    parent = Fix.inverse(candidate)
    assert Shared.digest(parent) == PARENT
    assert Fix.proposal(parent)[0] == candidate
    ips = Shared.ips_for(candidate)
    assert Shared.digest(ips) == PATCH_PIN
    assert Shared.apply_ips(Shared.SOURCE_BASE.read_bytes(), ips)[0] == candidate
    script = OUTPUT/'controller.lua'
    source = Test.controller().encode('utf-8')
    assert Shared.digest(source) == SCRIPT_PIN
    if args.install:
        assert check(Shared.NIGHTLY)['ROM_sha256'] == PARENT
        assert Shared.NIGHTLY.read_bytes() == parent
        script.write_bytes(source)
        try:
            Shared.NIGHTLY.write_bytes(candidate)
            assert check(Shared.NIGHTLY)['ROM_sha256'] == PIN
            result = run(script, Shared.NIGHTLY, OUTPUT/'capture', PIN, 240)
            assert result['passed'] and result['receipt_SHA256'] == RECEIPT, result['receipt']
            assert result['script_SHA256'] == SCRIPT_PIN
            assert check(Shared.NIGHTLY)['ROM_sha256'] == PIN
            assert Shared.NIGHTLY.read_bytes() == candidate
        except BaseException:
            Shared.NIGHTLY.write_bytes(parent)
            assert check(Shared.NIGHTLY)['ROM_sha256'] == PARENT
            raise
        print(dict(installed=True, ROM_SHA256=PIN, IPS_SHA256=PATCH_PIN,
                   native_receipt=RECEIPT, backup_files=0), flush=True)
    else:
        import publish_ff_corner_current_1110 as Publisher

        class Recipe:
            V1 = SimpleNamespace(BASE=Shared.SOURCE_BASE)

            @staticmethod
            def proposal(base):
                assert Shared.digest(base) == Shared.SOURCE_PIN
                return Fix.proposal(Fix.inverse(Shared.NIGHTLY.read_bytes()))

        with patch.multiple(Publisher, PIN=PIN, PATCH_PIN=PATCH_PIN, OLD_PATCH=OLD_PATCH,
                            RECEIPTS=(RECEIPT, STAGE_RECEIPT), Fix=Recipe,
                            CANDIDATE=candidate_path, SCRIPT=script, SCRIPT_PIN=SCRIPT_PIN,
                            REPORT=REPORT, release_body=notes):
            Publisher.main(report_sha=args.publish_report_sha)


if __name__ == '__main__':
    main()
