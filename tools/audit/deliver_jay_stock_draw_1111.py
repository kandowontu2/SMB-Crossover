"""Deliver the Mesen-verified Jay stock gun and its sole Current IPS."""

import argparse
from hashlib import sha256
import json
from pathlib import Path

import check_jay_stock_draw_sonic_rebase_1111 as Source
import check_sonic_ring_physical_1110 as SonicNative
import deliver_sonic_fast_snapshot_1111 as Parent
from deliver_manual_title_1110 import SOURCE_BASE, apply_ips, ips_for
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run


R, NIGHTLY, DK = Parent.R, Parent.NIGHTLY, Parent.DK
PIN = '6cb828b3c97bd287f5fb3421e01a478319bf3615e5f2eeed8a6b7888b15c9657'
PATCH_PIN = 'ae8d1671f8ddf94071acc64c1383814ffd834434a5c8e78db91e0f8eb72c0367'
COOKIE = 'a7102007de73e237c21c140b1055419b'
SCRIPT = R / 'tools/playthroughs/jay_stock_draw_stdout_1111.lua'
SCRIPT_PIN = '0a8ec015f54c6b58bd86c8c3935b53fb264934d2ed2e5a5a8bf3335f822ba821'
RECEIPT = '6f7fda7b8db4ecb414bc9b6387d5330bcffdb6e00bf591dbd29eb49c1cd46701'
CANDIDATE = R / 'build/jay-stock-native-rom-1111/candidate.nes'
REPORT = R / 'docs/qa/jay-stock-nightly-delivery-1111.md'


class Recipe:
    V1 = Parent.Recipe.V1

    @staticmethod
    def proposal(base):
        before = Parent.Recipe.proposal(base)[0]
        return (Source.proposal(before)[0],)


def replay(rom, output):
    assert sha256(SCRIPT.read_bytes()).hexdigest() == SCRIPT_PIN
    return run(SCRIPT, rom, output, PIN, 120, extra_env={'SMB_JAY_COOKIE': COOKIE})


def regression(script, output, prior, receipt, extra_env=None):
    result = run(script, NIGHTLY, output, PIN, 180, extra_env=extra_env)
    normalized = dict(result['receipt'], ROM_SHA256=prior)
    digest = sha256(json.dumps(normalized, sort_keys=True).encode()).hexdigest()
    assert result['passed'] and digest == receipt, result['receipt']
    return result['receipt_SHA256']


def install(output):
    assert output.is_relative_to(R / 'build') and output != R / 'build'
    assert not output.exists() or not any(output.iterdir())
    old = NIGHTLY.read_bytes()
    assert sha256(old).hexdigest() == check(NIGHTLY)['ROM_sha256'] == Parent.PIN
    image = CANDIDATE.read_bytes()
    assert sha256(image).hexdigest() == PIN
    ips = ips_for(image)
    assert sha256(ips).hexdigest() == PATCH_PIN
    assert apply_ips(SOURCE_BASE.read_bytes(), ips)[0] == image
    try:
        NIGHTLY.write_bytes(image)
        assert NIGHTLY.read_bytes() == image and check(NIGHTLY)['ROM_sha256'] == PIN
        jay = replay(NIGHTLY, output)
        assert jay['passed'] and jay['receipt_SHA256'] == RECEIPT, jay['receipt']
        sonic = regression(SonicNative.RING, output, Parent.PIN, Parent.RECEIPTS['rings'],
                           extra_env={'SMB_STDOUT_IMAGES': '0', 'SMB_SONIC_COOKIE': Parent.COOKIE.decode()})
        donkey = regression(DK.SCRIPT, output, DK.PIN, DK.RECEIPT)
        assert NIGHTLY.read_bytes() == image and check(NIGHTLY)['ROM_sha256'] == PIN
    except BaseException:
        NIGHTLY.write_bytes(old)
        assert NIGHTLY.read_bytes() == old
        raise
    print(json.dumps(dict(passed=True, installed=True, ROM_SHA256=PIN, IPS_SHA256=PATCH_PIN,
                          Jay=RECEIPT, Sonic=sonic, DK_Jr=donkey, backup_files=0,
                          output_files=0), sort_keys=True), flush=True)


def release_notes(head):
    return ('Current MMC5 WIP nightly. Apply this IPS to clean headered Super Mario Bros. (World).\n\n'
            f'ROM SHA-256: {PIN}\nIPS SHA-256: {PATCH_PIN}\nSource commit: {head}\n\n'
            'Jay McCray has his original Silius movement and stock projectile. '
            'Select him from Mike Jones with one Select press. '
            'Mesen verified the donor bullet through actual sprite DMA and offscreen retirement. '
            'Sonic ring loss and Donkey Kong Jr. early crossings repeated. '
            'See docs/qa/jay-stock-nightly-delivery-1111.md.\n')


def publish(report_sha):
    import publish_ff_corner_current_1110 as publisher
    from unittest.mock import patch

    with patch.multiple(publisher, PIN=PIN, PATCH_PIN=PATCH_PIN, OLD_PATCH=Parent.PATCH_PIN,
                        RECEIPTS=(RECEIPT,), Fix=Recipe, CANDIDATE=CANDIDATE,
                        SCRIPT=SCRIPT, SCRIPT_PIN=SCRIPT_PIN, REPORT=REPORT,
                        release_body=release_notes):
        publisher.main(report_sha=report_sha)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument('--output', type=Path)
    operation.add_argument('--report-sha')
    args = parser.parse_args()
    if args.output:
        install(args.output.resolve())
    else:
        publish(args.report_sha)


if __name__ == '__main__':
    main()
