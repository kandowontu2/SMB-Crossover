"""Deliver Karnov's native-tested room initialization fix and matching IPS."""

import argparse
from types import SimpleNamespace
from unittest.mock import patch

import compose_karnov_scene_motor_1113 as Fix
import deliver_prince_moving_support_1112 as Shared
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run


OUTPUT = Fix.R/'build/metal-flower-native-1112'
PARENT = '65ee94ca9ac6e1b5ad44303d08f76ecbc175a88232c82ef8c32712edf150a643'
PIN = 'a3c5fa63872fbb3103ae57d9748fef233e8b2273e26d985aa4006b2492d81b8a'
PATCH_PIN = '57b84a6d2cf38f3ff2e8fc7057b03d2d3ab81602906fbe256612c9972a322827'
OLD_PATCH = '8d08344f5faa26ac9bf5e4405455732f23699fd6777e4d1845408b89a9c66300'
SCRIPT_PIN = '57763e630aeae8ea0a0792646dd200bec841410b72942b1d1cde89af96754f35'
RECEIPT = '4d0e7e4ffbf11b56b4aad0f18d87da629804d00f7993de9499687a8fe96b90e0'
REPORT = Fix.R/'docs/qa/karnov-scene-delivery-1113.md'


def notes(head):
    return (
        'Apply the sole IPS to clean headered Super Mario Bros. (World).\n\n'
        f'ROM SHA-256: {PIN}\nIPS SHA-256: {PATCH_PIN}\nSource commit: {head}\n\n'
        'Fixes Karnov dying on entry to underground 1-2. The room constructor '
        'now resets his movement selector for both facings, while retaining '
        'earned weapons and equipment. Mesen verified natural mushroom and '
        'flower collection, full non-shortcut 1-1, safe 1-2 entry and its next '
        'flower granting Boots, with both lives and no damage. The Downloads '
        'ROM repeats the identical controller route.\n\n'
        'Includes the preceding Thomas hidden-1UP lift and Kirby fixes. '
        'Natural Bomb acquisition, further Karnov equipment, Steve armor and '
        'other roster qualification remain in progress. See '
        'docs/qa/karnov-scene-delivery-1113.md for exact scope.\n'
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--install', action='store_true')
    modes.add_argument('--publish-report-sha')
    args = parser.parse_args()
    candidate_path, script = OUTPUT/'candidate.nes', OUTPUT/'controller.lua'
    candidate = candidate_path.read_bytes()
    assert Shared.digest(candidate) == PIN
    parent = Fix.inverse(candidate)
    assert Shared.digest(parent) == PARENT and Fix.transform(parent)[0] == candidate
    ips = Shared.ips_for(candidate)
    assert Shared.digest(ips) == PATCH_PIN
    assert Shared.apply_ips(Shared.SOURCE_BASE.read_bytes(), ips)[0] == candidate
    assert Shared.digest(script.read_bytes()) == SCRIPT_PIN
    if args.install:
        assert check(Shared.NIGHTLY)['ROM_sha256'] == PARENT
        assert Shared.NIGHTLY.read_bytes() == parent
        try:
            Shared.NIGHTLY.write_bytes(candidate)
            assert check(Shared.NIGHTLY)['ROM_sha256'] == PIN
            result = run(script, Shared.NIGHTLY, OUTPUT/'capture', PIN, 180)
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
                return Fix.transform(Fix.inverse(Shared.NIGHTLY.read_bytes()))

        with patch.multiple(Publisher, PIN=PIN, PATCH_PIN=PATCH_PIN, OLD_PATCH=OLD_PATCH,
                            RECEIPTS=(RECEIPT,), Fix=Recipe, CANDIDATE=candidate_path,
                            SCRIPT=script, SCRIPT_PIN=SCRIPT_PIN, REPORT=REPORT,
                            release_body=notes):
            Publisher.main(report_sha=args.publish_report_sha)


if __name__ == '__main__':
    main()
