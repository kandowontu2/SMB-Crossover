"""Install Jay's tested machine gun and update the sole Current IPS."""

import argparse
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import compose_steve_full_route_1111 as Steve
from deliver_manual_title_1110 import SOURCE_BASE, SOURCE_PIN, apply_ips, ips_for
import deliver_roster_repair_1111 as Previous
from nightly_patch_guard_v1 import check
import replay_jay_machinegun_native_1111 as Replay


Source = Replay.Source
R, NIGHTLY, PIN = Replay.R, Replay.NIGHTLY, Replay.PIN
PATCH_PIN = '5a13f92827702551c8eade0df878361c8f3ab66dd28b0f512883910bb93aef74'
RECEIPT = 'b5eef90766637b792c7afec4f1dec9563aa6928d01c4aea0f912076185c060d4'
SCRIPT_PIN = 'e40a2a03ce87a0d28d5a2527d6c6613ba20395153b44101d250e6cf335a6d200'
TAIL_PIN = '8c4bd7286f1dfaede63536ff6834a339f830cc4f5095669f199f47d590444569'
TAIL = R / 'tools/playthroughs/jay_machinegun_continue_1111.lua'
REPORT = R / 'docs/qa/jay-machinegun-delivery-1111.md'


def verify_steve(script, rom, output, prior):
    # Steve shares the loader and cookie. His active workers retain their addresses.
    parent = Previous.Source.recover_parent(prior)
    delivery = Steve.Delivery
    rebuilt, program, punch, _ = delivery.proposal(delivery.recover_parent(parent))
    assert rebuilt == parent
    script.write_text(Steve.controller(), encoding='utf-8', newline='\n')
    result = delivery.Replay.replay(script, rom, output, PIN, program, punch, bytes.fromhex(Replay.COOKIE))
    receipt = result['receipt']
    assert result['passed'] and receipt['flag'] and receipt['castle'], receipt
    assert (receipt['x'], receipt['y'], receipt['hp'], receipt['lives']) == (40, 48, 4, 2)
    return result


def install(output):
    assert output.is_relative_to(R / 'build') and output != R / 'build'
    assert check(NIGHTLY)['ROM_sha256'] == Source.PIN
    parent = NIGHTLY.read_bytes()
    image, linked = Source.proposal(parent)
    assert Source.T.digest(image) == PIN and Source.recover_parent(image) == parent
    assert linked['cookie'].hex() == Replay.COOKIE
    if Replay.CANDIDATE.exists():
        assert Replay.CANDIDATE.read_bytes() == image
    base, ips = SOURCE_BASE.read_bytes(), ips_for(image)
    assert Source.T.digest(base) == SOURCE_PIN and Source.T.digest(ips) == PATCH_PIN
    assert apply_ips(base, ips)[0] == image

    output.mkdir(exist_ok=True)
    script = output / 'controller.lua'
    script.write_text(Source.controller(), encoding='utf-8', newline='\n')
    assert Source.T.digest(script.read_bytes()) == SCRIPT_PIN
    try:
        NIGHTLY.write_bytes(image)
        assert NIGHTLY.read_bytes() == image and check(NIGHTLY)['ROM_sha256'] == PIN
        result = Replay.replay(script, NIGHTLY, output / 'jay')
        assert result['passed'] and result['receipt_SHA256'] == RECEIPT, result['receipt']
        steve = verify_steve(script, NIGHTLY, output / 'steve', parent)
        assert NIGHTLY.read_bytes() == image and check(NIGHTLY)['ROM_sha256'] == PIN
    except BaseException:
        NIGHTLY.write_bytes(parent)
        assert NIGHTLY.read_bytes() == parent and check(NIGHTLY)['ROM_sha256'] == Source.PIN
        raise
    print(json.dumps(dict(installed=True, ROM_SHA256=PIN, IPS_SHA256=PATCH_PIN,
                          Jay_receipt=RECEIPT, Steve_receipt=steve['receipt_SHA256'],
                          Steve_frames=steve['receipt']['physical_frames'], backup_files=0),
                     sort_keys=True), flush=True)


def release_notes(head):
    return ('Current MMC5 WIP nightly. Apply the sole IPS to clean headered Super Mario Bros. (World).\n\n'
            f'ROM SHA-256: {PIN}\nIPS SHA-256: {PATCH_PIN}\nSource commit: {head}\n\n'
            'Jay McCray earns his original machine gun by clearing 1-1. In underground 1-2, pause and '
            'press Select to choose it, then hold B. The native replay verifies five shots, five ammo '
            'spent, and both lives retained. See docs/qa/jay-machinegun-delivery-1111.md.\n')


def publish(report_sha):
    import publish_ff_corner_current_1110 as publisher

    class Recipe:
        V1 = SimpleNamespace(BASE=SOURCE_BASE)

        @staticmethod
        def proposal(base):
            assert Source.T.digest(base) == SOURCE_PIN
            return Source.proposal(Source.recover_parent(NIGHTLY.read_bytes()))

    with patch.multiple(publisher, PIN=PIN, PATCH_PIN=PATCH_PIN, OLD_PATCH=Previous.Verification.IPS_PIN,
                        RECEIPTS=(RECEIPT,), Fix=Recipe, CANDIDATE=Replay.CANDIDATE,
                        SCRIPT=TAIL, SCRIPT_PIN=TAIL_PIN,
                        REPORT=REPORT, release_body=release_notes):
        publisher.main(report_sha=report_sha)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--install-output', type=Path)
    mode.add_argument('--publish-report-sha')
    args = parser.parse_args()
    if args.install_output:
        install(args.install_output.resolve())
    else:
        publish(args.publish_report_sha)


if __name__ == '__main__':
    main()
