"""Install and publish Kirby's native-tested contact fixes."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import check_kirby_red_physical_1111 as Physical
import deliver_dkjr_full_1111 as Parent
from deliver_manual_title_1110 import SOURCE_BASE, apply_ips, ips_for
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run


R, NIGHTLY = Parent.R, Parent.NIGHTLY
PIN = Physical.PIN
PATCH_PIN = '1cfec71dcfe7df8ec7c7528760e64d7cd6f73a57652b2244d2d8c9e7bac1a010'
RED_RECEIPT = 'e7e1e56be9805db2d939581347e745abbaeec9638eba110c165947bda6e32526'
GREEN_RECEIPT = '404b39c869a8db016d519b6005af9ab75af24335aa94ec5b02d1c63a50a146f5'
INHALE_RECEIPT = 'e068c3509119955fce85fe4f2afc66bf34d461552e4a0a1e1c6d4f1801de9310'
DK_PARENT_RECEIPT = '0d8861c3102a5a1fb721b3ce6fe3dfde8feec385c2b0a6807e4d5c57c07d88fc'
GREEN_SCRIPT = R / 'tools/playthroughs/kirby_current_green_stdout_1110_v5.lua'
GREEN_SCRIPT_PIN = '730a40160788c5fa41b3bf8b931bfd14834bb463ae75a04b18f07f12e0d2ff20'
INHALE_SCRIPT = R / 'tools/playthroughs/kirby_current_inhale_stdout_1110_v3.lua'
CANDIDATE = R / 'build/kirby-contact-combined-1111/candidate.nes'
REPORT = R / 'docs/qa/kirby-red-sweep-1111.md'


class Recipe:
    V1 = Parent.Recipe.V1

    @staticmethod
    def proposal(base):
        previous = Parent.Recipe.proposal(base)[0]
        return (Physical.proposal(previous)[0],)


def install(output):
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
        cases = (
            (Physical.replay(NIGHTLY, PIN, output), RED_RECEIPT),
            (run(GREEN_SCRIPT, NIGHTLY, output, PIN, 105, variant=1), GREEN_RECEIPT),
            (run(INHALE_SCRIPT, NIGHTLY, output, PIN, 105), INHALE_RECEIPT),
        )
        for result, expected in cases:
            assert result['passed'] and result['receipt_SHA256'] == expected, result['receipt']
        dk = Parent.Physical.replay(NIGHTLY, PIN, output, 0xd1f0, fast=True)
        prior_receipt = dict(dk['receipt'], ROM_SHA256=Parent.PIN)
        assert dk['passed'] and sha256(json.dumps(prior_receipt, sort_keys=True).encode()).hexdigest() == DK_PARENT_RECEIPT
        assert NIGHTLY.read_bytes() == image and check(NIGHTLY)['ROM_sha256'] == PIN
    except BaseException:
        NIGHTLY.write_bytes(old)
        assert NIGHTLY.read_bytes() == old
        raise
    print(json.dumps(dict(passed=True, installed=True, ROM_SHA256=PIN, IPS_SHA256=PATCH_PIN,
                          receipts=[q['receipt_SHA256'] for q, _ in cases],
                          DK_Jr=dk['receipt_SHA256'],
                          backup_files=0, output_files=0), sort_keys=True), flush=True)


def release_notes(head):
    return ('Current MMC5 WIP nightly. Apply this IPS to clean headered Super Mario Bros. (World).\n\n'
            f'ROM SHA-256: {PIN}\nIPS SHA-256: {PATCH_PIN}\nSource commit: {head}\n\n'
            'Kirby’s returning red shell checks its full movement step for contact with enemies. '
            'Inhale now measures full vertical distance. Mesen confirmed a natural red-shell '
            'hit in 4-3, a close inhale, and a green-shell clear of 1-1. '
            'Donkey Kong Jr.’s full 1-1 platform route remains included. '
            'See docs/qa/kirby-red-sweep-1111.md.\n')


def publish(report_sha):
    import publish_ff_corner_current_1110 as publisher

    endpoint = f'repos/{publisher.REPO}/releases'
    asset, = publisher.api(f'{endpoint}/tags/Current')['assets']
    old_patch = asset['digest'].removeprefix('sha256:')
    assert asset['name'] == publisher.ASSET and old_patch in (Parent.Jay.PATCH_PIN, Parent.PATCH_PIN, PATCH_PIN)
    source_recipe = Recipe
    if old_patch != PATCH_PIN:
        previous_patch = publisher.api(f'{endpoint}/assets/{asset["id"]}', binary=True)
        assert sha256(previous_patch).hexdigest() == old_patch

        class PublishedParentRecipe:
            V1 = SimpleNamespace(BASE=SOURCE_BASE)

            @staticmethod
            def proposal(base):
                previous = apply_ips(base, previous_patch)[0]
                if old_patch == Parent.Jay.PATCH_PIN:
                    assert sha256(previous).hexdigest() == Parent.Jay.PIN
                    previous = Parent.Stage.Late.proposal(previous)[0]
                assert sha256(previous).hexdigest() == Parent.PIN
                return (Physical.proposal(previous)[0],)

        source_recipe = PublishedParentRecipe

    with patch.multiple(publisher, PIN=PIN, PATCH_PIN=PATCH_PIN, OLD_PATCH=old_patch,
                        RECEIPTS=(RED_RECEIPT, GREEN_RECEIPT, INHALE_RECEIPT), Fix=source_recipe,
                        CANDIDATE=CANDIDATE, SCRIPT=GREEN_SCRIPT, SCRIPT_PIN=GREEN_SCRIPT_PIN,
                        REPORT=REPORT, release_body=release_notes):
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
