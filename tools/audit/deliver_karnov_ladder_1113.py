"""Install only the verified stock-level Ladder image and publish its sole IPS."""
import argparse
from hashlib import sha256
import json
from types import SimpleNamespace
from unittest.mock import patch

import replay_karnov_ladder_stock_1113 as Stock
import deliver_prince_moving_support_1112 as Shared
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run
import capture_budget as Capture

PIN = Stock.CANDIDATE
PARENT = Stock.PARENT
PATCH_PIN = '7379838295982363eaefad77499da110c083b648762b410a64336e747d8239fd'
OLD_PATCH = 'e45931e9493a4731e2e3c6f6734a9520a30f00d7243040525dec5396000a5def'
SCRIPT_PIN = '00187419e40f04b1d60f16792a1359ffae1caea4614f6d6ae30d3ff8c20e0f62'
STOCK_RECEIPT = 'a16cfb29945b938e4d1af9e13b1f06260b036c98802b7ac9a373585230df5a15'
FIXTURE_RECEIPT = '9015fad6c7c7e690044a92bca33a104cda6325e59d3e61b0a8cffd8f798162ba'
FOREIGN_RECEIPT = '9ccbb3d413915c4ec48f52837c4630e6bca393f2badb69ff3c1dab34ac628128'
REPORT = Stock.Feature.Owner.R/'docs/qa/karnov-ladder-native-verified-1113.md'


def image():
    raw = Shared.NIGHTLY.read_bytes()
    parent = Stock.Feature.inverse_current(raw) if sha256(raw).hexdigest() == PIN else raw
    assert sha256(parent).hexdigest() == PARENT
    candidate, info = Stock.Feature.proposal_current(parent)
    assert sha256(candidate).hexdigest() == PIN
    assert Stock.Feature.inverse_current(candidate) == parent
    return candidate, info, parent


def notes(head):
    return ('Current MMC5 WIP. Apply the sole IPS to clean headered Super Mario Bros. (World).\n\n'
        f'ROM SHA-256: {PIN}\nIPS SHA-256: {PATCH_PIN}\nSource commit: {head}\n\n'
        'Karnov now has the original reusable Ladder: earn its upgrade, choose it with '
        'Select, deploy with Down+B, and climb with Up/Down. Descending to the bottom '
        'retracts it and returns ownership. Existing Boots, Bomb, music and manual '
        'helper controls remain. No public level or helper placement changes.\n\n'
        'Actual Mesen verifies five earned pickups and the complete visible ladder '
        'lifecycle in a private test level; that level is excluded. The unchanged '
        '1-1 into 1-2 route, four natural upgrades, Boots and Bomb pass separately '
        'and repeat from Downloads. Steve full-stage regression and all 101 menu '
        'portrait/silhouette comparisons pass.\n\n'
        'The stock fifth-pickup route and further original equipment remain under '
        'review. Prince entrance, DK Jr helper capacity and broader roster review '
        'remain unfinished. Private fixes for those are not included.\n')


def install():
    candidate, _, parent = image()
    assert (Stock.OUT/'candidate.nes').read_bytes() == candidate
    assert check(Shared.NIGHTLY)['ROM_sha256'] == PARENT
    ips = Shared.ips_for(candidate)
    assert sha256(ips).hexdigest() == PATCH_PIN
    assert Shared.apply_ips(Shared.SOURCE_BASE.read_bytes(), ips)[0] == candidate
    text = Stock.controller(candidate, wait_for_entry=True)
    assert sha256(text.encode()).hexdigest() == SCRIPT_PIN
    script = Stock.OUT/'controller.lua'
    script.write_text(text, encoding='utf-8', newline='\n')
    Capture.preflight(Stock.OUT/'capture', reserved_bytes=Capture.RUN_BYTES, reserved_files=0)
    try:
        Shared.NIGHTLY.write_bytes(candidate)
        assert check(Shared.NIGHTLY)['ROM_sha256'] == PIN
        result = run(script, Shared.NIGHTLY, Stock.OUT/'capture', PIN, 180)
        print(json.dumps(dict(event='Downloads_native_repeat', passed=result['passed'],
            ROM_SHA256=PIN, script_SHA256=SCRIPT_PIN,
            receipt_SHA256=result['receipt_SHA256'], receipt=result['receipt']),
            separators=(',', ':')), flush=True)
        assert result['passed'] and result['receipt_SHA256'] == STOCK_RECEIPT
        assert check(Shared.NIGHTLY)['ROM_sha256'] == PIN
        assert Shared.NIGHTLY.read_bytes() == candidate
    except BaseException:
        # Hold the previous bytes in memory only; never create a backup file.
        Shared.NIGHTLY.write_bytes(parent)
        assert check(Shared.NIGHTLY)['ROM_sha256'] == PARENT
        raise
    print(json.dumps(dict(installed=True, ROM_SHA256=PIN, IPS_SHA256=PATCH_PIN,
        Downloads_context_native_repeat=True, backup_files=0)), flush=True)


def publish(report_sha):
    import publish_ff_corner_current_1110 as Publisher
    class Recipe:
        V1 = SimpleNamespace(BASE=Shared.SOURCE_BASE)
        @staticmethod
        def proposal(base):
            assert sha256(base).hexdigest() == Shared.SOURCE_PIN
            return image()[:2]
    with patch.multiple(Publisher, PIN=PIN, PATCH_PIN=PATCH_PIN, OLD_PATCH=OLD_PATCH,
        RECEIPTS=(STOCK_RECEIPT, FIXTURE_RECEIPT, FOREIGN_RECEIPT), Fix=Recipe,
        CANDIDATE=Stock.OUT/'candidate.nes', SCRIPT=Stock.OUT/'controller.lua',
        SCRIPT_PIN=SCRIPT_PIN, REPORT=REPORT, release_body=notes):
        Publisher.main(report_sha=report_sha)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--install', action='store_true')
    mode.add_argument('--publish-report-sha')
    args = parser.parse_args()
    if args.install:
        install()
    else:
        publish(args.publish_report_sha)
