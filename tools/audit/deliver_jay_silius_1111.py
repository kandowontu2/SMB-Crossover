"""Install Jay's tested MMC5 update and replace the sole Current IPS."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import compose_jay_silius_1111 as Source
import deliver_kirby_red_sweep_1111 as Parent
from deliver_manual_title_1110 import SOURCE_BASE, apply_ips, ips_for
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run


R, NIGHTLY = Parent.R, Parent.NIGHTLY
PIN = '4df817587ea5b0aff3f278a4201976745bad4d9dd1b2a99d6cb5fd3b9c74dadc'
PATCH_PIN = '8e631e876d64396f3f869ebcecdda4ec53dc82ffa93401d2dbf0f63ddcc51954'
COOKIE = 'a71020081fa840317c2600e2c7b30cf6'
CANDIDATE = R / 'build/jay-silius-composed-1111/candidate.nes'
SCRIPT = R / 'tools/playthroughs/jay_scroll_stdout_1111.lua'
REPORT = R / 'docs/qa/jay-silius-scrolling-delivery-1111.md'


def replay(rom, output):
    return run(SCRIPT, rom, output, PIN, 120, variant=2,
               extra_env={'SMB_JAY_COOKIE': COOKIE, 'SMB_JAY_DONOR_FLAGS': '49170'})


def install(output, receipt):
    assert output.is_relative_to(R / 'build') and output != R / 'build'
    assert not output.exists() or not any(output.iterdir())
    old = NIGHTLY.read_bytes()
    assert sha256(old).hexdigest() == check(NIGHTLY)['ROM_sha256'] == Parent.PIN
    image = CANDIDATE.read_bytes()
    assert sha256(image).hexdigest() == PIN
    ips = ips_for(image)
    assert sha256(ips).hexdigest() == PATCH_PIN and apply_ips(SOURCE_BASE.read_bytes(), ips)[0] == image
    try:
        NIGHTLY.write_bytes(image)
        assert NIGHTLY.read_bytes() == image and check(NIGHTLY)['ROM_sha256'] == PIN
        result = replay(NIGHTLY, output)
        assert result['passed'] and result['receipt_SHA256'] == receipt, result['receipt']
        q = result['receipt']
        assert q['flag'] and q['castle'] and q['three_way'] and q['lives'] == 2 and q['dma_matches']
        assert NIGHTLY.read_bytes() == image and check(NIGHTLY)['ROM_sha256'] == PIN
    except BaseException:
        NIGHTLY.write_bytes(old)
        assert NIGHTLY.read_bytes() == old
        raise
    print(json.dumps(dict(passed=True, installed=True, ROM_SHA256=PIN, IPS_SHA256=PATCH_PIN,
                          receipt_SHA256=result['receipt_SHA256'], script_SHA256=result['script_SHA256'],
                          backup_files=0, output_files=0), sort_keys=True), flush=True)


def release_notes(head):
    return ('Current MMC5 WIP nightly. Apply this IPS to clean headered Super Mario Bros. (World).\n\n'
            f'ROM SHA-256: {PIN}\nIPS SHA-256: {PATCH_PIN}\nSource commit: {head}\n\n'
            'Jay McCray keeps his original movement and stock gun while scrolling through 1-1. '
            'Press Start, then Select while paused, to switch between stock and the three-way shot. '
            'Goomba defeats can drop ammo. Two stock moving lifts help Jay reach the tall pipes. '
            'See docs/qa/jay-silius-scrolling-delivery-1111.md.\n')


def publish(report_sha, receipt):
    import publish_ff_corner_current_1110 as publisher

    endpoint = f'repos/{publisher.REPO}/releases'
    asset, = publisher.api(f'{endpoint}/tags/Current')['assets']
    assert asset['name'] == publisher.ASSET
    assert asset['digest'] == 'sha256:' + Parent.PATCH_PIN
    previous_patch = publisher.api(f'{endpoint}/assets/{asset["id"]}', binary=True)
    assert sha256(previous_patch).hexdigest() == Parent.PATCH_PIN

    class Recipe:
        V1 = SimpleNamespace(BASE=SOURCE_BASE)

        @staticmethod
        def proposal(base):
            previous = apply_ips(base, previous_patch)[0]
            assert sha256(previous).hexdigest() == Parent.PIN
            return (Source.proposal(previous)[0],)

    script_pin = sha256(SCRIPT.read_bytes()).hexdigest()
    with patch.multiple(publisher, PIN=PIN, PATCH_PIN=PATCH_PIN, OLD_PATCH=Parent.PATCH_PIN,
                        RECEIPTS=(receipt,), Fix=Recipe, CANDIDATE=CANDIDATE,
                        SCRIPT=SCRIPT, SCRIPT_PIN=script_pin, REPORT=REPORT, release_body=release_notes):
        publisher.main(report_sha=report_sha)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--output', type=Path)
    mode.add_argument('--report-sha')
    parser.add_argument('--receipt', required=True)
    args = parser.parse_args()
    assert len(bytes.fromhex(args.receipt)) == 32
    if args.output:
        install(args.output.resolve(), args.receipt)
    else:
        publish(args.report_sha, args.receipt)


if __name__ == '__main__':
    main()
