"""Deliver only the exact native-qualified Steve armor image and matching IPS."""
import argparse
import json
from types import SimpleNamespace
from unittest.mock import patch

import check_steve_armor_regressions_native_1113 as Cases
import profile_steve_empty_native_1113 as Perf
import deliver_prince_moving_support_1112 as Shared
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run
import capture_budget as Capture

OUT=Cases.OUT
PIN='62ba7f54117875ec018d6f85fb1c74408aa11f0fe0f6a85b8b4f601034a17639'
PARENT='aa50112845d1cf70cae0924f03326647b3d2514f876c756d70b134ee44f971d1'
PATCH_PIN='e45931e9493a4731e2e3c6f6734a9520a30f00d7243040525dec5396000a5def'
OLD_PATCH='a5ecdd50c6e186415f9b4e3c75f53bcef7cf69df3012f02e6466a7e7413e33a1'
SCRIPT_PIN='82ace2fe3ead540390e5a0eb3dd5c9003461238fba925a686fdd5aa7d9a465a6'
CADENCE_PIN='604f3c3b2a4822380af815ce0e65a517bebbe3cc8a8c569377eb6d2147417e19'
RECEIPTS={
    'cadence':'aaa90ccb8083e7e6fe07d220d8fe2e3c229642771e6b6221b05446c380e4b05b',
    'steve_stage':'98124f1b550dae5ffa0e8245ab0806e421596254b26071b1366db1feb76cbf8d',
    'jay_pickup':'0e074e671022bca1fb61f4ce758341d725973d8605c0cb2c2bddc386d4447d9d',
    'jay_stage':'29054e3e121585e6f4bc09a30a874c14b53f15350d0a8449548fcd3b594d1cd6',
    'quick_stage':'51abb4384389fa19a1f13d679cf59d8c28806329caf44a5ba24f44237c1a31b3',
    'steve_pickups':'b9fb05190e4d73b30999a268b0fb96389701e0444fed599b82d43f7d9d357cbe',
}
COMBAT_RECEIPT='2de36a11174bace173888750732f755e9fd767e20bf1c728c08fbbc543c7ae49'
REPORT=Cases.Idle.Native.Packet.Entry.ROOT/'docs/qa/steve-armor-delivery-1113.md'


def notes(head):
    return ('Apply the sole IPS to clean headered Super Mario Bros. (World).\n\n'
        f'ROM SHA-256: {PIN}\nIPS SHA-256: {PATCH_PIN}\nSource commit: {head}\n\n'
        'Steve now has the original matching-Alpha armor lifecycle, moving '
        'piercing waves, protected contact and natural expiry. A private native '
        'six-question test level verifies six real pickups, armor, two Goomba '
        'defeats, protected contact, both wave directions and expiry; that test '
        'level is not included in the ROM. Stock 1-1 pickups and full 1-1 into '
        'grounded 1-2 pass separately. The inactive armor checks no longer cause '
        'the large measured ordinary-movement slowdown. This is not an '
        'all-stage zero-lag claim.\n\n'
        'Jay pickup/full-stage/machine-gun and Quick four-item/full-stage '
        'regressions pass. Six unmodified-ROM cases repeat from Downloads. '
        'Retains the prior Jay helper, Quick, Karnov, Thomas and Kirby fixes. '
        'Broader roster, powerup, original-ability, audio and visual review '
        'remain in progress. No helper platforms or public level data change.\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--install',action='store_true')
    mode.add_argument('--publish-report-sha')
    mode.add_argument('--metadata',action='store_true')
    args=parser.parse_args()
    image,info,parent=Cases.proposal()
    rom,script=OUT/'candidate.nes',OUT/'controller.lua'
    assert image==rom.read_bytes() and Shared.digest(image)==PIN
    assert Shared.digest(parent)==PARENT
    ips=Shared.ips_for(image)
    assert Shared.digest(ips)==PATCH_PIN
    assert Shared.apply_ips(Shared.SOURCE_BASE.read_bytes(),ips)[0]==image
    if args.metadata:
        cadence=Perf.controller(image,info)
        assert Shared.digest(cadence.encode())==CADENCE_PIN
        for name in Cases.PINS:Cases.controller(name,image,info,parent)
        print(json.dumps(dict(passed=True,ROM_SHA256=PIN,IPS_SHA256=PATCH_PIN,
            readonly_bindings=6,IPS_roundtrip=True,outputs=0,native_run=False)),flush=True)
    elif args.install:
        assert check(Shared.NIGHTLY)['ROM_sha256']==PARENT
        assert Shared.NIGHTLY.read_bytes()==parent
        texts={'cadence':Perf.controller(image,info)}
        assert Shared.digest(texts['cadence'].encode())==CADENCE_PIN
        texts.update({name:Cases.controller(name,image,info,parent) for name in Cases.PINS})
        assert tuple(texts)==tuple(RECEIPTS)
        Capture.preflight(OUT/'capture',reserved_bytes=Capture.RUN_BYTES,reserved_files=0)
        try:
            Shared.NIGHTLY.write_bytes(image)
            assert check(Shared.NIGHTLY)['ROM_sha256']==PIN
            for name,text in texts.items():
                script.write_text(text,encoding='utf-8',newline='\n')
                result=run(script,Shared.NIGHTLY,OUT/'capture',PIN,180)
                assert result['passed'] and result['receipt_SHA256']==RECEIPTS[name],result
                print(json.dumps(dict(installed_native_case=name,passed=True,
                    receipt_SHA256=result['receipt_SHA256'])),flush=True)
            assert Shared.digest(script.read_bytes())==SCRIPT_PIN
            assert check(Shared.NIGHTLY)['ROM_sha256']==PIN and Shared.NIGHTLY.read_bytes()==image
        except BaseException:
            Shared.NIGHTLY.write_bytes(parent)
            assert check(Shared.NIGHTLY)['ROM_sha256']==PARENT
            raise
        print(json.dumps(dict(installed=True,ROM_SHA256=PIN,IPS_SHA256=PATCH_PIN,
                             installed_native_cases=6,backup_files=0)),flush=True)
    else:
        import publish_ff_corner_current_1110 as Publisher
        class Recipe:
            V1=SimpleNamespace(BASE=Shared.SOURCE_BASE)
            @staticmethod
            def proposal(base):
                assert Shared.digest(base)==Shared.SOURCE_PIN
                return Cases.proposal()[:2]
        with patch.multiple(Publisher,PIN=PIN,PATCH_PIN=PATCH_PIN,OLD_PATCH=OLD_PATCH,
            RECEIPTS=tuple(RECEIPTS.values())+(COMBAT_RECEIPT,),Fix=Recipe,
            CANDIDATE=rom,SCRIPT=script,SCRIPT_PIN=SCRIPT_PIN,REPORT=REPORT,release_body=notes):
            Publisher.main(report_sha=args.publish_report_sha)


if __name__=='__main__':main()
