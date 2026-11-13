"""Deliver the tested Prince fixes over the existing Karnov Ladder nightly."""
import argparse
from hashlib import sha256
import json
from types import SimpleNamespace
from unittest.mock import patch

import check_prince_entrance_current_native_1113 as Cases
import deliver_prince_moving_support_1112 as Shared
import capture_budget as Capture
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

PIN = Cases.Fix.PIN
PARENT = Cases.Fix.PARENT
PATCH_PIN = '3b896934169854e3fd668c27e9c3dacc78037dfc80568c84c3d216ff4cf12fa9'
OLD_PATCH = '7379838295982363eaefad77499da110c083b648762b410a64336e747d8239fd'
SCRIPT_PIN = '79263decae00c6effeba0c2ee12b7373ee0048b0960349d20e38107012abb153'
RECEIPTS = {
    'entry': '98e6cd908d9ecf3713cb2bd364440e58854abf3febd85912f07a29529ff06b09',
    'combat': 'd2e72c6f3aee69b25e020b50abba42ae5772b3144aba255e46fc28801b3c7ea8',
    'megaman': '961fe6377540bb296f2e4f14869f8294a55c2bd4c2e0c85e05cd99fd140df3a5',
    'luigi': 'cbf909a0f01353386ff8bfce391203df72331caeb3bb0cfd170efcc51318b284',
    'karnov': '2d748ed34b757a348c015b1568e2274dd575d554c8161b2057f679edd4dde03d',
}
REPORT = Cases.Fix.Entry.R/'docs/qa/prince-entrance-current-1113.md'


def notes(head):
    return ('Current MMC5 WIP. Apply the sole IPS to clean headered Super Mario Bros. (World).\n\n'
        f'ROM SHA-256: {PIN}\nIPS SHA-256: {PATCH_PIN}\nSource commit: {head}\n\n'
        'Prince now preserves his position when drawing the earned sword, and the '
        'automatic underground entrance lands safely before his normal movement '
        'takes over. Original fall damage remains during play. Actual Mesen verifies '
        'full 1-1 through grounded 1-2 with full health and both lives, plus natural '
        'mushroom/flower acquisition, sword parry, attack and a real enemy defeat. '
        'Both cases repeat from Downloads.\n\n'
        'Retains the tested Karnov Ladder. Karnov full 1-1/four-item/Boots/Bomb and '
        'Mega Man/Luigi movement regressions pass; all 101 character-select entries '
        'and their portraits/silhouettes remain identical. No helper locations change.\n\n'
        'Entrance visibility remains unfinished: Prince is hidden during the automatic '
        'drop and an early grounded sample; his later grounded sprite and palette '
        'are verified. This is retained for the later visual review under the current '
        'playable-roster priority. DK Jr capacity, the stock fifth Karnov pickup and '
        'broader character review remain in progress.\n')


def install():
    image, _, parent, cache = Cases.inputs()
    assert (Cases.OUT/'candidate.nes').read_bytes() == image
    assert check(Shared.NIGHTLY)['ROM_sha256'] == PARENT
    ips = Shared.ips_for(image)
    assert sha256(ips).hexdigest() == PATCH_PIN
    assert Shared.apply_ips(Shared.SOURCE_BASE.read_bytes(), ips)[0] == image
    texts = {name:Cases.controller(name, image, parent, cache) for name in ('entry', 'combat')}
    assert sha256(texts['combat'].encode()).hexdigest() == SCRIPT_PIN
    Capture.preflight(Cases.OUT/'capture', reserved_bytes=Capture.RUN_BYTES, reserved_files=0)
    try:
        Shared.NIGHTLY.write_bytes(image)
        assert check(Shared.NIGHTLY)['ROM_sha256'] == PIN
        script = Cases.OUT/'controller.lua'
        for name, text in texts.items():
            script.write_text(text, encoding='utf-8', newline='\n')
            if name == 'entry':
                result, _ = Cases.Prior.Stage.replay(script, Shared.NIGHTLY, Cases.OUT/'capture', PIN)
            else:
                result = run(script, Shared.NIGHTLY, Cases.OUT/'capture', PIN, 180, variant=3)
            print(json.dumps(dict(Downloads_case=name, passed=result['passed'],
                ROM_SHA256=PIN, script_SHA256=result['script_SHA256'],
                receipt_SHA256=result['receipt_SHA256'], terminal=result['receipt'].get('terminal')),
                separators=(',', ':')), flush=True)
            Cases.validate(name, result)
            assert result['receipt_SHA256'] == RECEIPTS[name]
        assert check(Shared.NIGHTLY)['ROM_sha256'] == PIN
        assert Shared.NIGHTLY.read_bytes() == image
    except BaseException:
        # Previous verified bytes are held only in memory, never as a backup.
        Shared.NIGHTLY.write_bytes(parent)
        assert check(Shared.NIGHTLY)['ROM_sha256'] == PARENT
        raise
    print(json.dumps(dict(installed=True, ROM_SHA256=PIN, IPS_SHA256=PATCH_PIN,
        Downloads_native_cases=2, backup_files=0)), flush=True)


def publish(report_sha):
    import publish_ff_corner_current_1110 as Publisher
    class Recipe:
        V1 = SimpleNamespace(BASE=Shared.SOURCE_BASE)
        @staticmethod
        def proposal(base):
            assert sha256(base).hexdigest() == Shared.SOURCE_PIN
            return Cases.inputs()[:2]
    with patch.multiple(Publisher, PIN=PIN, PATCH_PIN=PATCH_PIN, OLD_PATCH=OLD_PATCH,
        RECEIPTS=tuple(RECEIPTS.values()), Fix=Recipe,
        CANDIDATE=Cases.OUT/'candidate.nes', SCRIPT=Cases.OUT/'controller.lua',
        SCRIPT_PIN=SCRIPT_PIN, REPORT=REPORT, release_body=notes):
        Publisher.main(report_sha=report_sha)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--install', action='store_true')
    mode.add_argument('--publish-report-sha')
    args = p.parse_args()
    if args.install:
        install()
    else:
        publish(args.publish_report_sha)
