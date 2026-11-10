"""Install the measured Sonic optimization and refresh the sole Current IPS."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import check_sonic_ring_physical_1110 as Native
import check_sonic_sms_fast_snapshot_1111 as Source
from deliver_manual_title_1110 import SOURCE_BASE, apply_ips, ips_for
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run


DK = Source.DK
R, NIGHTLY, PIN = DK.R, DK.NIGHTLY, Source.PIN
PATCH_PIN = '390c95dbf17b6356293a52c16a88a801fdc6b357e2ca830cabb3d88bb48dad7f'
COOKIE = b'a72b01ddebbb0319d58c05e05b9ea417'
SCRIPT_PIN = '628832f25a2e9ed7975b5523904ad91731be130df35f11c488cb327ddb8f1e37'
CANDIDATE = R / 'build/sonic-fast-copy-1111/candidate.nes'
REPORT = R / 'docs/qa/sonic-fast-snapshot-delivery-1111.md'
RECEIPTS = {
    'stage': 'c1cba1931533a260963dffcf6f4bd9476925c0ce5c10d0740f2d6c46a01a1b86',
    'rings': '9f2c8f769a654d7a49d684efaf50954c08587f86fd955820cc6b8f70fea15745',
    'mushroom': '3f7f6580f51a6ecbae27cdd2fc51cbe5d8344737c7134f655bb3a48b9f639d1c',
}


class Recipe:
    V1 = DK.Recipe.V1

    @staticmethod
    def proposal(base):
        return (Source.from_installed(DK.Recipe.proposal(base)[0])[0],)


def install(output):
    assert output.is_relative_to(R / 'build') and output != R / 'build'
    assert not output.exists() or not any(output.iterdir())
    before = check(NIGHTLY)
    old = NIGHTLY.read_bytes()
    assert sha256(old).hexdigest() == before['ROM_sha256'] == DK.PIN
    image, source = Source.from_installed(old)
    assert sha256(image).hexdigest() == PIN and source['cookie'].encode() == COOKIE
    ips = ips_for(image)
    assert sha256(ips).hexdigest() == PATCH_PIN
    assert apply_ips(SOURCE_BASE.read_bytes(), ips)[0] == image
    assert sha256(Native.RING.read_bytes()).hexdigest() == SCRIPT_PIN
    assert sha256(DK.SCRIPT.read_bytes()).hexdigest() == DK.SCRIPT_PIN
    results = {}
    try:
        NIGHTLY.write_bytes(image)
        assert NIGHTLY.read_bytes() == image and check(NIGHTLY)['ROM_sha256'] == PIN
        with patch.multiple(Native, PIN=PIN, RING_COOKIE=COOKIE):
            for key, replay in (('stage', Native.run_stage), ('rings', Native.run_rings),
                                ('mushroom', Native.run_power)):
                q = replay(NIGHTLY, output)
                assert q['passed'] and q['receipt_SHA256'] == RECEIPTS[key], q['receipt']
                results[key] = q['receipt_SHA256']
                print(json.dumps(dict(route=key, SHA256=results[key]), sort_keys=True), flush=True)
        q = run(DK.SCRIPT, NIGHTLY, output, PIN, 180)
        normalized = dict(q['receipt'], ROM_SHA256=DK.PIN)
        assert q['passed'] and sha256(json.dumps(normalized, sort_keys=True).encode()).hexdigest() == DK.RECEIPT, q['receipt']
        results['DK_Jr'] = q['receipt_SHA256']
        assert NIGHTLY.read_bytes() == image and check(NIGHTLY)['ROM_sha256'] == PIN
    except BaseException:
        NIGHTLY.write_bytes(old)
        assert NIGHTLY.read_bytes() == old
        raise
    print(json.dumps(dict(passed=True, installed=True, ROM_SHA256=PIN, IPS_SHA256=PATCH_PIN,
                          replays=results, backup_files=0, output_files=0), sort_keys=True), flush=True)


def release_notes(head):
    return ('Current MMC5 WIP nightly. Apply this IPS to clean headered Super Mario Bros. (World).\n\n'
            f'ROM SHA-256: {PIN}\nIPS SHA-256: {PATCH_PIN}\nSource commit: {head}\n\n'
            'Sonic saves 1,027 CPU cycles per movement update. Mesen measured 63 fewer frames '
            'without a completed update in the same World 1-1 clear, with both lives. '
            'Ring pickups, ring loss, and earned mushroom behavior passed their separate replays. '
            'Donkey Kong Jr. still crosses the four opening pipes and both early gaps. '
            'See docs/qa/sonic-fast-snapshot-delivery-1111.md.\n')


def publish(report_sha):
    import publish_ff_corner_current_1110 as publisher

    with patch.multiple(publisher, PIN=PIN, PATCH_PIN=PATCH_PIN, OLD_PATCH=DK.PATCH_PIN,
                        RECEIPTS=tuple(RECEIPTS.values()), Fix=Recipe, CANDIDATE=CANDIDATE,
                        SCRIPT=Native.RING, SCRIPT_PIN=SCRIPT_PIN, REPORT=REPORT,
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
