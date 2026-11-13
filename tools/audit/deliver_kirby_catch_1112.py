"""Deliver the strict native-tested Kirby red-shell catch, without backups."""
import argparse
from types import SimpleNamespace
from unittest.mock import patch
import check_kirby_red_catch_1112 as Fix
import replay_kirby_red_current_1112 as Replay
import deliver_prince_moving_support_1112 as Shared
from nightly_patch_guard_v1 import check

PARENT='c5ce8c1557f6eb27c97f1fb1b0404c7854f59feb18717f27171d7dcb890efbbd'
PIN='f228e61399432c1a205b8f5ac6dad13d990515f9c2e2f5024bcd5ce443c76653'
RECEIPT='0ba2031f64825b6188e67ecd7d6f849c70c365af5ba0e5072f61b3001e9128f6'
SCRIPT_PIN='c76e0e3236aa81a845d47c06a81605072d9f1930f7a4a26f8ab0464a862190c1'
OUTPUT=Replay.R/'build/kirby-red-current-1112'
REPORT=Replay.R/'docs/qa/kirby-red-current-1112.md'


def reverse(raw):
    assert Shared.digest(raw)==PIN
    parent=bytearray(raw)
    parent[Fix.offset(Fix.START):Fix.offset(Fix.END)]=Fix.PREIMAGE
    parent=bytes(parent)
    assert Shared.digest(parent)==PARENT and Fix.proposal(parent)[0]==raw
    return parent


def notes(head):
    return ('Current MMC5 WIP nightly. Apply the sole IPS to clean headered Super Mario Bros. (World).\n\n'
            f'ROM SHA-256: {PIN}\nSource commit: {head}\n\n'
            'Kirby now catches the returning red shell instead of oscillating at his feet until expiry. '
            'Actual Mesen verified natural copy acquisition, an enemy defeat, and a clean return catch '
            'with full health and both lives. The installed Downloads ROM repeated the test. '
            'Retains the preceding Prince reach/sword and roster-facing fixes.\n\n'
            'Other character abilities, audio, graphical fixes and performance remain WIP.\n')


def main():
    parser=argparse.ArgumentParser()
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--install',action='store_true')
    mode.add_argument('--publish-report-sha')
    args=parser.parse_args()
    candidate=(OUTPUT/'candidate.nes').read_bytes()
    assert Shared.digest(candidate)==PIN
    parent=reverse(candidate)
    ips=Shared.ips_for(candidate)
    patch_pin=Shared.digest(ips)
    assert Shared.apply_ips(Shared.SOURCE_BASE.read_bytes(),ips)[0]==candidate
    script=OUTPUT/'controller.lua'
    assert Shared.digest(script.read_bytes())==SCRIPT_PIN
    if args.install:
        assert check(Shared.NIGHTLY)['ROM_sha256']==PARENT
        assert Shared.NIGHTLY.read_bytes()==parent
        try:
            Shared.NIGHTLY.write_bytes(candidate)
            assert check(Shared.NIGHTLY)['ROM_sha256']==PIN
            result=Replay.run(script,Shared.NIGHTLY,OUTPUT/'capture',PIN,90)
            assert result['passed'] and result['receipt_SHA256']==RECEIPT
            assert result['receipt']['catch_verified']
            assert check(Shared.NIGHTLY)['ROM_sha256']==PIN
            assert Shared.NIGHTLY.read_bytes()==candidate
        except BaseException:
            Shared.NIGHTLY.write_bytes(parent)
            assert check(Shared.NIGHTLY)['ROM_sha256']==PARENT
            raise
        print({'installed':True,'ROM_SHA256':PIN,'IPS_SHA256':patch_pin,'receipt':RECEIPT,'backup_files':0})
    else:
        import publish_ff_corner_current_1110 as Publisher
        class Recipe:
            V1=SimpleNamespace(BASE=Shared.SOURCE_BASE)
            @staticmethod
            def proposal(base):
                assert Shared.digest(base)==Shared.SOURCE_PIN
                return Fix.proposal(reverse(Shared.NIGHTLY.read_bytes()))
        with patch.multiple(Publisher,PIN=PIN,PATCH_PIN=patch_pin,
                            OLD_PATCH='fd0c11b7745c1a3e4f62d46272b0540316d5ab2861667bd65749050f131357a4',
                            RECEIPTS=(RECEIPT,),Fix=Recipe,CANDIDATE=OUTPUT/'candidate.nes',
                            SCRIPT=script,SCRIPT_PIN=SCRIPT_PIN,REPORT=REPORT,release_body=notes):
            Publisher.main(report_sha=args.publish_report_sha)


if __name__=='__main__':
    main()
