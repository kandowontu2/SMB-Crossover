"""Install the verified Thomas flower lift and publish its matching IPS."""

import argparse
from types import SimpleNamespace
from unittest.mock import patch

import compose_thomas_flower_lift_1112 as Fix
import deliver_prince_moving_support_1112 as Shared
from nightly_patch_guard_v1 import check
from replay_thomas_stage_1112 import OUTPUT, PIN
from run_stdout_mesen_1110 import run


SCRIPT = Fix.R/'tools/playthroughs/thomas_flower_stdout_1112.lua'
REPORT = Fix.R/'docs/qa/thomas-flower-lift-1112.md'
PARENT = Fix.Thomas.PIN
OLD_PATCH = '7928a88a725be35592cc2278890d53650ea74e09464ee64c8911a67b029cba74'


def previous_image(candidate):
    assert Shared.digest(candidate) == PIN
    parent = bytearray(candidate)
    for pc, old in Fix.SPANS.values():
        offset = Fix.START + pc - 0xa000
        parent[offset:offset + len(old)] = old
    parent[Fix.COOKIE:Fix.COOKIE+16] = bytes.fromhex('a70a4002a5d85501bf9e69d0625ddc43')
    parent = bytes(parent)
    assert Shared.digest(parent) == PARENT
    assert Fix.proposal(parent)[0] == candidate
    return parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--install', action='store_true')
    mode.add_argument('--publish-report-sha')
    parser.add_argument('--receipt', required=True)
    parser.add_argument('--script-sha', required=True)
    args = parser.parse_args()
    candidate_path = OUTPUT/'candidate.nes'
    candidate = candidate_path.read_bytes()
    parent = previous_image(candidate)
    ips = Shared.ips_for(candidate)
    patch_pin = Shared.digest(ips)
    assert Shared.apply_ips(Shared.SOURCE_BASE.read_bytes(), ips)[0] == candidate
    assert Shared.digest(SCRIPT.read_bytes()) == args.script_sha
    if args.install:
        assert check(Shared.NIGHTLY)['ROM_sha256'] == PARENT
        assert Shared.NIGHTLY.read_bytes() == parent
        try:
            Shared.NIGHTLY.write_bytes(candidate)
            assert check(Shared.NIGHTLY)['ROM_sha256'] == PIN
            result = run(SCRIPT, Shared.NIGHTLY, OUTPUT/'capture', PIN, 240, 1)
            assert result['passed'] and result['receipt_SHA256'] == args.receipt, result['receipt']
            assert check(Shared.NIGHTLY)['ROM_sha256'] == PIN
            assert Shared.NIGHTLY.read_bytes() == candidate
        except BaseException:
            Shared.NIGHTLY.write_bytes(parent)
            assert check(Shared.NIGHTLY)['ROM_sha256'] == PARENT
            raise
        print(dict(installed=True, ROM_SHA256=PIN, IPS_SHA256=patch_pin,
                   native_receipt=args.receipt, backup_files=0), flush=True)
    else:
        import publish_ff_corner_current_1110 as Publisher

        class Recipe:
            V1 = SimpleNamespace(BASE=Shared.SOURCE_BASE)

            @staticmethod
            def proposal(base):
                assert Shared.digest(base) == Shared.SOURCE_PIN
                return Fix.proposal(previous_image(Shared.NIGHTLY.read_bytes()))

        def notes(head):
            return (
                'Apply the sole IPS to clean headered Super Mario Bros. (World).\n\n'
                f'ROM SHA-256: {PIN}\nIPS SHA-256: {patch_pin}\nSource commit: {head}\n\n'
                'Thomas can ride a native vertical platform to the 1-1 fire flower. '
                'Mesen verified both natural pickups, both powerup animations and movement after recovery. '
                'The Downloads ROM repeated the same route. See docs/qa/thomas-flower-lift-1112.md.\n'
            )

        with patch.multiple(Publisher, PIN=PIN, PATCH_PIN=patch_pin, OLD_PATCH=OLD_PATCH,
                            RECEIPTS=(args.receipt,), Fix=Recipe, CANDIDATE=candidate_path,
                            SCRIPT=SCRIPT, SCRIPT_PIN=args.script_sha, REPORT=REPORT,
                            release_body=notes):
            Publisher.main(report_sha=args.publish_report_sha)


if __name__ == '__main__':
    main()
