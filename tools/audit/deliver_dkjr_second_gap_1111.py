"""Reproduce and deliver the second-gap DK Jr. nightly."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import check_dkjr_second_gap_admission_1110 as Gap
import deliver_dkjr_four_pipe_1110 as Four
import deliver_sonic_rings_1110 as Sonic
from deliver_manual_title_1110 import SOURCE_BASE, apply_ips, ips_for
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run


R, NIGHTLY = Gap.R, Sonic.NIGHTLY
PIN = '3d327d47b8127c1e76d9868191d34b8ebb1ca9ec29d6bb609ccab9c60c6cb3d8'
PATCH_PIN = 'ba9b6a0460d76341ba96bdf620eeba4f3fba2a9ba59194c06d896732acba05e6'
SCRIPT = R / 'tools/playthroughs/dkjr_second_gap_stdout_1110.lua'
SCRIPT_PIN = '97c4da3f2bcc228b022a01e2b8cf4aa89c480e57e6fb762905d4dc0c6bb19697'
RECEIPT = '1aa9e6dfcaf255ae750717eb69e7a394f7c3f1773e2871a5989e54c7998bcfad'
CANDIDATE = R / 'build/dkjr-second-gap-physical-1111/candidate.nes'
REPORT = R / 'docs/qa/dkjr-second-gap-delivery-1111.md'


def merge(original, parent):
    assert sha256(parent).hexdigest() == Sonic.PIN
    gap, _, _ = Gap.proposal(original)
    edits = [at for at, (before, after) in enumerate(zip(original, gap, strict=True))
             if before != after]
    assert len(edits) == 248 and all(parent[at] == original[at] for at in edits)
    image = bytearray(parent)
    for at in edits:
        image[at] = gap[at]
    assert sha256(image).hexdigest() == PIN
    return bytes(image)


class Recipe:
    V1 = Four.Recipe.V1

    @staticmethod
    def proposal(base):
        original = Four.Recipe.proposal(base)[0]
        return (merge(original, Sonic.Build.proposal(original)[0]),)


def replay(rom, output):
    assert sha256(SCRIPT.read_bytes()).hexdigest() == SCRIPT_PIN
    return run(SCRIPT, rom, output, PIN, 180)


def release_notes(head):
    return ('Current MMC5 WIP nightly. Apply this IPS to clean headered Super Mario Bros. (World).\n\n'
            f'ROM SHA-256: {PIN}\nIPS SHA-256: {PATCH_PIN}\nSource commit: {head}\n\n'
            'Donkey Kong Jr. uses a stock moving platform to cross the second gap in 1-1. '
            'A continuous controller-only Mesen replay crossed the four pipes and both early gaps '
            'with both lives. Select Donkey Kong Jr. from Donkey Kong. '
            'The Sonic opening-ring update remains included. '
            'See docs/qa/dkjr-second-gap-delivery-1111.md.\n')


def publish(report_sha):
    import publish_ff_corner_current_1110 as publisher

    with patch.multiple(publisher, PIN=PIN, PATCH_PIN=PATCH_PIN, OLD_PATCH=Sonic.PATCH_PIN,
                        RECEIPTS=(RECEIPT,), Fix=Recipe, CANDIDATE=CANDIDATE,
                        SCRIPT=SCRIPT, SCRIPT_PIN=SCRIPT_PIN, REPORT=REPORT,
                        release_body=release_notes):
        publisher.main(report_sha=report_sha)


def install(output):
    assert output.is_relative_to(R / 'build') and output != R / 'build'
    assert not output.exists() or not any(output.iterdir())
    before = check(NIGHTLY)
    old = NIGHTLY.read_bytes()
    assert sha256(old).hexdigest() == before['ROM_sha256'] == Sonic.PIN
    image = CANDIDATE.read_bytes()
    assert sha256(image).hexdigest() == PIN
    ips = ips_for(image)
    assert sha256(ips).hexdigest() == PATCH_PIN
    assert apply_ips(SOURCE_BASE.read_bytes(), ips)[0] == image
    try:
        NIGHTLY.write_bytes(image)
        assert NIGHTLY.read_bytes() == image and check(NIGHTLY)['ROM_sha256'] == PIN
        result = replay(NIGHTLY, output)
        assert result['passed'] and result['receipt_SHA256'] == RECEIPT, result['receipt']
        after = check(NIGHTLY)
        assert NIGHTLY.read_bytes() == image and after['ROM_sha256'] == PIN
    except BaseException:
        NIGHTLY.write_bytes(old)
        assert NIGHTLY.read_bytes() == old
        raise
    print(json.dumps(dict(passed=True, installed=True, ROM_SHA256=PIN, IPS_SHA256=PATCH_PIN,
                          receipt_SHA256=RECEIPT, guard_before=before, guard_after=after,
                          terminal=result['receipt']['terminal'], backup_files=0,
                          output_files=0), sort_keys=True), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    command = parser.add_mutually_exclusive_group(required=True)
    command.add_argument('--output', type=Path)
    command.add_argument('--report-sha')
    args = parser.parse_args()
    if args.output:
        install(args.output.resolve())
    else:
        publish(args.report_sha)


if __name__ == '__main__':
    main()
