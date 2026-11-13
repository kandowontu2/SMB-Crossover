"""Guarded delivery of Prince's accepted-mushroom progression update."""
import argparse
from types import SimpleNamespace
from unittest.mock import patch
import deliver_prince_moving_support_1112 as Previous
import prince_pickup_progression_1112 as Fix

PARENT = Previous.PIN
PIN = 'cebb0ae64b4e6cc92e473a239cb8fd4011d54cfd5e6814013a3afbd2de2bf7d7'
RECEIPT = 'a08e3b269c53fe9f29e4284de6ba4d9896cb4780016b5b52bd719a2a09cf102a'
SCRIPT_PIN = '2192f9cabc250bd55db10d902bd36a202137c978c7b8b6a33daac0c5399ff3f2'
REPORT = Previous.Packet.R/'docs/qa/prince-powerup-progression-fix-1112.md'


def transform(image, reverse=False):
    assert Previous.digest(image) == (PIN if reverse else PARENT)
    result, layout = Fix.transform(image, reverse)
    assert Previous.digest(result) == (PARENT if reverse else PIN)
    return result, layout


def notes(head):
    return ('Current MMC5 WIP nightly. Apply the sole IPS to clean headered Super Mario Bros. (World).\n\n'
            f'ROM SHA-256: {PIN}\nSource commit: {head}\n\n'
            'Prince mushrooms now enable subsequent flower rewards while retaining health restoration. '
            'The sword remains a flower reward. Native collection/reveal and72 pickup cases checked; '
            'actual IRQ and lag-NMI cuts passed. Full1-1 into1-2 passed with both lives.\n\n'
            'Natural access to Prince powerup blocks and other roster abilities remain unfinished.\n')


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--install', action='store_true')
    mode.add_argument('--publish-report-sha')
    args = parser.parse_args()
    image = Previous.CANDIDATE.read_bytes()
    assert Previous.digest(image) == PIN
    patch_pin = Previous.digest(Previous.ips_for(image))
    if args.install:
        with patch.multiple(Previous, PARENT=PARENT, PIN=PIN, PATCH_PIN=patch_pin,
                            RECEIPT=RECEIPT, SCRIPT_PIN=SCRIPT_PIN, transform=transform):
            Previous.install()
    else:
        import publish_ff_corner_current_1110 as publisher
        class Recipe:
            V1 = SimpleNamespace(BASE=Previous.SOURCE_BASE)
            @staticmethod
            def proposal(base):
                assert Previous.digest(base) == Previous.SOURCE_PIN
                installed = Previous.NIGHTLY.read_bytes()
                parent, _ = transform(installed, True)
                return transform(parent)
        with patch.multiple(publisher, PIN=PIN, PATCH_PIN=patch_pin,
                            OLD_PATCH=Previous.PATCH_PIN, RECEIPTS=(RECEIPT,),
                            Fix=Recipe, CANDIDATE=Previous.CANDIDATE,
                            SCRIPT=Previous.OUTPUT/'controller.lua', SCRIPT_PIN=SCRIPT_PIN,
                            REPORT=REPORT, release_body=notes):
            publisher.main(report_sha=args.publish_report_sha)


if __name__ == '__main__':
    main()
