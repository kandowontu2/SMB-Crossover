"""Install/publish the tested Prince and roster composition, without backups."""
import argparse
from types import SimpleNamespace
from unittest.mock import patch
import compose_prince_menu_1112 as Fix
import deliver_prince_moving_support_1112 as Previous

RECEIPT = '60479ff4e2bda39d132807db13310ba272cf68d5eebbb6f98a21ddd75d21491f'
SCRIPT_PIN = '018f23db7dd7a1482c10f861db2f3c3ad546417cbdc189e56e0c1c98bdefd65e'
REPORT = Previous.Packet.R/'docs/qa/prince-reach-native-1112.md'


def notes(head):
    return ('Current MMC5 WIP nightly. Apply the sole IPS to clean headered Super Mario Bros. (World).\n\n'
            f'ROM SHA-256: {Fix.PIN}\nSource commit: {head}\n\n'
            'Prince raised-hand block activation and sword opponent detection are corrected. '
            'The combined build cleared 1-1 into 1-2 in Mesen with both lives. '
            'Sword collection, draw, parry, attack, native enemy defeat and sheathing were '
            'checked in controlled CPU scenes; natural full-stage sword acquisition remains to be tested. '
            'Backward roster previews and shared silhouettes were corrected across the 101-choice menu.\n\n'
            'The expanded roster, remaining abilities, audio, graphics and performance remain WIP.\n')


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--install', action='store_true')
    mode.add_argument('--publish-report-sha')
    args = parser.parse_args()
    image = Previous.CANDIDATE.read_bytes()
    assert Previous.digest(image) == Fix.PIN
    patch_pin = Previous.digest(Previous.ips_for(image))
    if args.install:
        with patch.multiple(Previous, PARENT=Fix.PARENT, PIN=Fix.PIN,
                            PATCH_PIN=patch_pin, RECEIPT=RECEIPT,
                            SCRIPT_PIN=SCRIPT_PIN, SUPPORT_PUBLICATION=0xd746,
                            transform=Fix.transform):
            Previous.install()
    else:
        import publish_ff_corner_current_1110 as publisher
        class Recipe:
            V1 = SimpleNamespace(BASE=Previous.SOURCE_BASE)
            @staticmethod
            def proposal(base):
                assert Previous.digest(base) == Previous.SOURCE_PIN
                parent, _ = Fix.transform(Previous.NIGHTLY.read_bytes(), True)
                return Fix.transform(parent)
        with patch.multiple(publisher, PIN=Fix.PIN, PATCH_PIN=patch_pin,
                            OLD_PATCH='9b7e72e7a772c0b1bbbd8054f86f3c08e64b7450c48f9ed0237bec80f9b7e3ad',
                            RECEIPTS=(RECEIPT,), Fix=Recipe,
                            CANDIDATE=Previous.CANDIDATE,
                            SCRIPT=Previous.OUTPUT/'controller.lua', SCRIPT_PIN=SCRIPT_PIN,
                            REPORT=REPORT, release_body=notes):
            publisher.main(report_sha=args.publish_report_sha)


if __name__ == '__main__':
    main()
