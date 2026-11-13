"""Deliver the native-tested raised-hand block-reach fix without backups."""
import argparse
from types import SimpleNamespace
from unittest.mock import patch
import deliver_prince_moving_support_1112 as Previous
import prince_pickup_reach_1112 as Fix

PARENT='cebb0ae64b4e6cc92e473a239cb8fd4011d54cfd5e6814013a3afbd2de2bf7d7'
PIN='3b7990bc59b490a1c5e488133a7c65d05526944d63b7e987f0b3f44df733343d'
RECEIPT='7e0c5e0b240534db58fd7085ae1157205128bc16333c98ccd60b9120b73a442b'
SCRIPT_PIN='9ca6e81186d62096b7d818fd14986dd23c435bc2fabb70d9261fe3e1c15d1037'
REPORT=Previous.Packet.R/'docs/qa/prince-reach-native-1112.md'


def transform(image,reverse=False):
    assert Previous.digest(image)==(PIN if reverse else PARENT)
    if reverse:
        changed=Fix.reverse(image)
        layout={'cookie':changed[Previous.Packet.COOKIE:Previous.Packet.COOKIE+16].hex()}
    else:
        changed,_,layout=Fix.transform(image)
    assert Previous.digest(changed)==(PARENT if reverse else PIN)
    return changed,layout


def notes(head):
    return ('Current MMC5 WIP nightly. Apply the sole IPS to clean headered Super Mario Bros. (World).\n\n'
            f'ROM SHA-256: {PIN}\nSource commit: {head}\n\n'
            'Prince can activate overhead blocks with his raised-hand move. Native Mesen tests '
            'verified mushroom emergence, maturation and collection with progression to status1, '
            'and a separate full1-1 clear into1-2 with both lives. Cold loader and interrupt checks passed.\n\n'
            'The expanded roster, remaining abilities, audio, graphical fixes and performance remain WIP.\n')


def main():
    parser=argparse.ArgumentParser()
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--install',action='store_true')
    mode.add_argument('--publish-report-sha')
    args=parser.parse_args()
    image=Previous.CANDIDATE.read_bytes()
    assert Previous.digest(image)==PIN
    patch_pin=Previous.digest(Previous.ips_for(image))
    if args.install:
        with patch.multiple(Previous,PARENT=PARENT,PIN=PIN,PATCH_PIN=patch_pin,
                            RECEIPT=RECEIPT,SCRIPT_PIN=SCRIPT_PIN,transform=transform):
            Previous.install()
    else:
        import publish_ff_corner_current_1110 as publisher
        class Recipe:
            V1=SimpleNamespace(BASE=Previous.SOURCE_BASE)
            @staticmethod
            def proposal(base):
                assert Previous.digest(base)==Previous.SOURCE_PIN
                parent,_=transform(Previous.NIGHTLY.read_bytes(),True)
                return transform(parent)
        with patch.multiple(publisher,PIN=PIN,PATCH_PIN=patch_pin,
                            OLD_PATCH='9b7e72e7a772c0b1bbbd8054f86f3c08e64b7450c48f9ed0237bec80f9b7e3ad',
                            RECEIPTS=(RECEIPT,),Fix=Recipe,CANDIDATE=Previous.CANDIDATE,
                            SCRIPT=Previous.OUTPUT/'controller.lua',SCRIPT_PIN=SCRIPT_PIN,
                            REPORT=REPORT,release_body=notes):
            publisher.main(report_sha=args.publish_report_sha)


if __name__=='__main__':
    main()
