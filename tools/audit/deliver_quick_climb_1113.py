"""Deliver the native-tested Quick flagpole adapter and sole Current IPS."""

import argparse
import json
from types import SimpleNamespace
from unittest.mock import patch

import compose_quick_climb_material_1113 as Fix
import deliver_prince_moving_support_1112 as Shared
import replay_quick_flag_jump_1113 as Replay
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run


OUTPUT=Fix.R/'build/metal-flower-native-1112'
PARENT='a3c5fa63872fbb3103ae57d9748fef233e8b2273e26d985aa4006b2492d81b8a'
PIN='4641ca4fb72699c0478e31b831d4c4ea0ffd2227be7f8446666092d2cc26e1d3'
PATCH_PIN='ce922a8793496839efea21d2a9e15c2a3849df59415537fc910a60b6450f8225'
OLD_PATCH='57b84a6d2cf38f3ff2e8fc7057b03d2d3ab81602906fbe256612c9972a322827'
SCRIPT_PIN='963f00a2ca58167983ef7a25da989d01df03decc60eabdba654237f227105691'
RECEIPT='cd9be0d5a648dd026bd1df1eb345d6c0f3ba4ea0dd136a878136de4092fdfbcd'
REPORT=Fix.R/'docs/qa/quick-climb-delivery-1113.md'


def notes(head):
    return ('Apply the sole IPS to clean headered Super Mario Bros. (World).\n\n'
        f'ROM SHA-256: {PIN}\nIPS SHA-256: {PATCH_PIN}\nSource commit: {head}\n\n'
        'Quick Man can now pass through the flagpole shaft and complete the level. '
        'The native flagpole base and ordinary solid blocks keep their collision. '
        'Mesen verified natural mushroom, hidden 1UP, later mushroom and Star, '
        'the full non-shortcut 1-1 route, flag/castle and a safe grounded entry '
        'into 1-2 at full health with three lives. Downloads repeats the exact run.\n\n'
        'No helper platforms changed. Includes the preceding Karnov room-entry '
        'and Thomas/Kirby fixes. Jay head/helper work, Steve armor, further '
        'equipment and the broader roster review remain in progress.\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    modes=parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--install',action='store_true')
    modes.add_argument('--publish-report-sha')
    args=parser.parse_args()
    candidate_path,script=OUTPUT/'candidate.nes',OUTPUT/'controller.lua'
    candidate=candidate_path.read_bytes()
    assert Shared.digest(candidate)==PIN
    parent=Fix.inverse(candidate)
    assert Shared.digest(parent)==PARENT and Fix.transform(parent)[0]==candidate
    ips=Shared.ips_for(candidate)
    assert Shared.digest(ips)==PATCH_PIN
    assert Shared.apply_ips(Shared.SOURCE_BASE.read_bytes(),ips)[0]==candidate
    if args.install:
        assert check(Shared.NIGHTLY)['ROM_sha256']==PARENT
        assert Shared.NIGHTLY.read_bytes()==parent
        script.write_text(Replay.controller(candidate),encoding='utf-8',newline='\n')
        assert Shared.digest(script.read_bytes())==SCRIPT_PIN
        try:
            Shared.NIGHTLY.write_bytes(candidate)
            assert check(Shared.NIGHTLY)['ROM_sha256']==PIN
            result=run(script,Shared.NIGHTLY,OUTPUT/'capture',PIN,180)
            assert result['passed'] and result['receipt_SHA256']==RECEIPT,result['receipt']
            assert result['script_SHA256']==SCRIPT_PIN
            assert check(Shared.NIGHTLY)['ROM_sha256']==PIN
            assert Shared.NIGHTLY.read_bytes()==candidate
        except BaseException:
            Shared.NIGHTLY.write_bytes(parent)
            assert check(Shared.NIGHTLY)['ROM_sha256']==PARENT
            raise
        print(json.dumps(dict(installed=True,ROM_SHA256=PIN,IPS_SHA256=PATCH_PIN,
            native_receipt=RECEIPT,backup_files=0)),flush=True)
    else:
        import publish_ff_corner_current_1110 as Publisher
        class Recipe:
            V1=SimpleNamespace(BASE=Shared.SOURCE_BASE)
            @staticmethod
            def proposal(base):
                assert Shared.digest(base)==Shared.SOURCE_PIN
                raw=Shared.NIGHTLY.read_bytes()
                prior=Fix.inverse(raw)
                assert Shared.digest(prior)==PARENT
                return Fix.transform(prior)
        with patch.multiple(Publisher,PIN=PIN,PATCH_PIN=PATCH_PIN,OLD_PATCH=OLD_PATCH,
                RECEIPTS=(RECEIPT,),Fix=Recipe,CANDIDATE=candidate_path,SCRIPT=script,
                SCRIPT_PIN=SCRIPT_PIN,REPORT=REPORT,release_body=notes):
            Publisher.main(report_sha=args.publish_report_sha)


if __name__=='__main__':
    main()
