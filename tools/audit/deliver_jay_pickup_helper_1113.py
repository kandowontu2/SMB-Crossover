"""Deliver native-qualified Jay head/pickup access, retaining Quick's repair."""

import argparse
import json
from types import SimpleNamespace
from unittest.mock import patch

import compose_jay_pickup_helper_1113 as Jay
import compose_quick_climb_material_1113 as Quick
import replay_jay_pickup_helper_1113 as Replay
import replay_quick_flag_jump_1113 as QuickReplay
import deliver_prince_moving_support_1112 as Shared
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run


OUTPUT=Jay.R/'build/metal-flower-native-1112'
PARENT='4641ca4fb72699c0478e31b831d4c4ea0ffd2227be7f8446666092d2cc26e1d3'
PIN='aa50112845d1cf70cae0924f03326647b3d2514f876c756d70b134ee44f971d1'
PATCH_PIN='a5ecdd50c6e186415f9b4e3c75f53bcef7cf69df3012f02e6466a7e7413e33a1'
OLD_PATCH='ce922a8793496839efea21d2a9e15c2a3849df59415537fc910a60b6450f8225'
SCRIPT_PIN='dd7c656145ea98860e4ff3fe50828d36bb9045e031c345a8b6d53b077fcc4e60'
RECEIPTS=(
    'abe9281690573229b2b45fec8ca414c7fbbc9f823ce1b545b86344e23f73b0ca',
    '50d2332176f026d924ce91d26851b18ff220dff37cbbd8e494e928b428c8666e',
    '4e1140c6872cc1e91b7cbb0055a4938d614f51ed1ebc8d4f2d4fb3d2a089b9da',
)
REPORT=Jay.R/'docs/qa/jay-pickup-helper-delivery-1113.md'


def proposal(parent):
    assert Shared.digest(parent)==PARENT
    original=Quick.inverse(parent)
    head=Jay.Head.proposal(original)[0]
    helper,info=Jay.proposal(head)
    image=Quick.transform(helper)[0]
    assert Shared.digest(image)==PIN
    assert inverse(image)==parent
    return image,info


def inverse(image):
    assert Shared.digest(image)==PIN
    helper=Quick.inverse(image)
    original=Jay.Head.inverse(Jay.inverse(helper))
    parent=Quick.transform(original)[0]
    assert Shared.digest(parent)==PARENT
    return parent


def notes(head):
    return ('Apply the sole IPS to clean headered Super Mario Bros. (World).\n\n'
        f'ROM SHA-256: {PIN}\nIPS SHA-256: {PATCH_PIN}\nSource commit: {head}\n\n'
        'Jay now activates overhead item blocks and can collect the first health '
        'upgrade using an existing native vertical platform. The new 1-1 helper '
        'starts at left X384, center X400, top Y192 and enters from offscreen. '
        'His original jump physics and the existing X688/X880 helpers remain. '
        'Mesen verified natural mature pickup with its sound, full 1-1 and the '
        'earned machine gun in 1-2. Quick Man also repeats his four-item 1-1 '
        'clear into grounded 1-2. All three runs repeat from Downloads.\n\n'
        'Includes the prior Quick flagpole, Karnov room-entry, Thomas and Kirby '
        'fixes. The broader roster, original abilities, powerups, audio and '
        'performance review remain in progress; Steve armor is still private.\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    modes=parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--install',action='store_true')
    modes.add_argument('--publish-report-sha')
    args=parser.parse_args()
    rom,script=OUTPUT/'candidate.nes',OUTPUT/'controller.lua'
    image=rom.read_bytes()
    parent=inverse(image)
    assert proposal(parent)[0]==image
    ips=Shared.ips_for(image)
    assert Shared.digest(ips)==PATCH_PIN
    assert Shared.apply_ips(Shared.SOURCE_BASE.read_bytes(),ips)[0]==image
    helper=Quick.inverse(image)
    if args.install:
        assert check(Shared.NIGHTLY)['ROM_sha256']==PARENT
        assert Shared.NIGHTLY.read_bytes()==parent
        scripts=(Replay.controller(helper),QuickReplay.controller(image),Replay.stage_controller(helper))
        try:
            Shared.NIGHTLY.write_bytes(image)
            assert check(Shared.NIGHTLY)['ROM_sha256']==PIN
            for index,(text,receipt) in enumerate(zip(scripts,RECEIPTS)):
                script.write_text(text,encoding='utf-8',newline='\n')
                result=run(script,Shared.NIGHTLY,OUTPUT/'capture',PIN,180)
                assert result['passed'] and result['receipt_SHA256']==receipt,result['receipt']
                print(json.dumps(dict(installed_native_run=index,receipt_SHA256=receipt)),flush=True)
            assert Shared.digest(script.read_bytes())==SCRIPT_PIN
            assert check(Shared.NIGHTLY)['ROM_sha256']==PIN
            assert Shared.NIGHTLY.read_bytes()==image
        except BaseException:
            Shared.NIGHTLY.write_bytes(parent)
            assert check(Shared.NIGHTLY)['ROM_sha256']==PARENT
            raise
        print(json.dumps(dict(installed=True,ROM_SHA256=PIN,IPS_SHA256=PATCH_PIN,
            native_receipts=RECEIPTS,backup_files=0)),flush=True)
    else:
        import publish_ff_corner_current_1110 as Publisher
        class Recipe:
            V1=SimpleNamespace(BASE=Shared.SOURCE_BASE)
            @staticmethod
            def proposal(base):
                assert Shared.digest(base)==Shared.SOURCE_PIN
                return proposal(inverse(Shared.NIGHTLY.read_bytes()))
        with patch.multiple(Publisher,PIN=PIN,PATCH_PIN=PATCH_PIN,OLD_PATCH=OLD_PATCH,
                RECEIPTS=RECEIPTS,Fix=Recipe,CANDIDATE=rom,SCRIPT=script,
                SCRIPT_PIN=SCRIPT_PIN,REPORT=REPORT,release_body=notes):
            Publisher.main(report_sha=args.publish_report_sha)


if __name__=='__main__':
    main()
