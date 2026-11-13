"""Install and publish the combined, native-qualified Metal/Kirby nightly."""
import argparse
from types import SimpleNamespace
from unittest.mock import patch
import compose_metal_kirby_1112 as Fix
import deliver_prince_moving_support_1112 as Shared
from nightly_patch_guard_v1 import check

CASES = {
    'inhale': ('c6e7d5a7f6a52f8b6e1bcd7453108445f7a4166c345b83779478d284889ed8a6','ab88ad92e07d73a1b6f9f251f573f760976bf0baea9f451b1e913ed7285cc26d'),
    'shell': ('649388c86bbfabb7a073906e49ec66d79b6aeaccca257de43e4897f97823329e','2e8b0e1ad0edc039a95912e3a7b2786f9705ebcb2e6db30b09efb00f81f5bfa8'),
    'upgrades': ('9312b808829fe15580626f65b1d1d5e811969af179d81a4e2aa3cd2abfc19893','ee6ae3dff7349a4e13618f169fdb007f2275063f5855da5b49b07b3d9b8be884'),
    'route': ('7975a676056c5968a1fd0eb9c69a144949f5933542b8ceb45f703dd79af54321','153f0fbd5e5b18586c8331dfa5c062ac2a1ac6708475c716a35b411d132dbafe'),
}
REPORT = Fix.MR.R/'docs/qa/metal-kirby-delivery-1112.md'


def notes(head):
    return (f'Current MMC5 WIP nightly. Apply the sole IPS to clean headered Super Mario Bros. (World).\n\n'
        f'ROM SHA-256: {Fix.PIN}\nSource commit: {head}\n\n'
        'Metal Storm now bumps powerup blocks, collects mature armor and weapon upgrades, and no longer freezes '
        'waiting for its original game background streamer. Actual Mesen verified natural mushroom and flower '
        'collection, an upgraded shot, and a separate full 1-1 clear.\n\n'
        'Kirby retains inhale protection for the update that captures an enemy. Directed CPU tests verified '
        'the Lakitu/Spiny overlap while retaining rear and hazard damage. Actual Mesen verified close-range '
        'inhale and the existing natural red-shell defeat and return catch. All four replays repeated from '
        'the installed Downloads ROM. Further roster abilities, visuals and performance remain WIP.\n')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--install',action='store_true')
    parser.add_argument('--publish-report-sha')
    args=parser.parse_args()
    assert bool(args.install) != bool(args.publish_report_sha)
    candidate=(Fix.OUTPUT/'candidate.nes').read_bytes()
    parent=Fix.reverse(candidate)
    ips=Shared.ips_for(candidate)
    patch_pin=Shared.digest(ips)
    assert Shared.apply_ips(Shared.SOURCE_BASE.read_bytes(),ips)[0]==candidate
    script=Fix.OUTPUT/'controller.lua'
    if args.install:
        assert check(Shared.NIGHTLY)['ROM_sha256']==Fix.PARENT
        assert Shared.NIGHTLY.read_bytes()==parent
        try:
            Shared.NIGHTLY.write_bytes(candidate)
            assert check(Shared.NIGHTLY)['ROM_sha256']==Fix.PIN
            for mode,(receipt_pin,script_pin) in CASES.items():
                script.write_text(Fix.controller(candidate,mode),encoding='utf-8',newline='\n')
                assert Shared.digest(script.read_bytes())==script_pin
                result=Fix.MR.run(script,Shared.NIGHTLY,Fix.OUTPUT/'capture',Fix.PIN,120)
                assert result['passed'] and result['receipt_SHA256']==receipt_pin
                print(dict(installed_test=mode,passed=True,receipt=receipt_pin),flush=True)
            assert check(Shared.NIGHTLY)['ROM_sha256']==Fix.PIN
            assert Shared.NIGHTLY.read_bytes()==candidate
        except BaseException:
            Shared.NIGHTLY.write_bytes(parent)
            assert check(Shared.NIGHTLY)['ROM_sha256']==Fix.PARENT
            raise
        print(dict(installed=True,ROM_SHA256=Fix.PIN,IPS_SHA256=patch_pin,backup_files=0),flush=True)
    else:
        import publish_ff_corner_current_1110 as Publisher
        class Recipe:
            V1=SimpleNamespace(BASE=Shared.SOURCE_BASE)
            @staticmethod
            def proposal(base):
                assert Shared.digest(base)==Shared.SOURCE_PIN
                return Fix.compose(Fix.reverse(Shared.NIGHTLY.read_bytes())),{}
        with patch.multiple(Publisher,PIN=Fix.PIN,PATCH_PIN=patch_pin,
            OLD_PATCH='55381d7bfb47beb05d00863d072e04b365be48b97ae731e16b03ceb02608f86d',
            RECEIPTS=tuple(v[0] for v in CASES.values()),Fix=Recipe,
            CANDIDATE=Fix.OUTPUT/'candidate.nes',SCRIPT=script,SCRIPT_PIN=CASES['route'][1],
            REPORT=REPORT,release_body=notes):
            Publisher.main(report_sha=args.publish_report_sha)


if __name__=='__main__':
    main()
