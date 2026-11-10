"""Install the tested SMB2 menu fix and refresh the sole Current IPS."""
import argparse
import json
from pathlib import Path
from unittest.mock import patch

import check_smb2_menu_tier_isolation_1110 as Fix
import deliver_sonic_earned_injury_1110 as Previous
from deliver_manual_title_1110 import SOURCE_BASE, apply_ips, ips_for
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

PIN = '9897c2b85489024be25b4b296d0ea57975a579ba1e3ff37a71f7ac3e0b195b97'
PATCH_PIN = 'bfc6266979f6e5ecef0344b4f7266d308b58edaefb86d59afd766662f7fb75a7'
SCRIPT = Fix.R/'tools/playthroughs/smb2_menu_tier_stdout_1110.lua'
SCRIPT_PIN = '99e7a5cc2b8ef6f33b960b9fe0196bced1015488aa5b04bbc17d18c05ca531b6'
REPORT = Fix.R/'docs/qa/smb2-menu-tier-isolation-1110.md'
RECEIPTS = (
    '483e6d7127bf43cd914e0accf04ccefabf0a764b7479991df1a477b22ae61fdf',
    'c05a01c4391f0bcfda23142af7ac751023be948f322a973fefc4e9e98fc1aee1',
    '6718cddadc3058ceb6de92ea24401de501ad953e799723fc6a21e8c7701d603c',
)


def install(output):
    assert output.is_relative_to(Fix.R/'build') and output != Fix.R/'build'
    assert not output.exists()
    before = check(Fix.NIGHTLY)
    old = Fix.NIGHTLY.read_bytes()
    assert Fix.digest(old) == before['ROM_sha256'] == Fix.PARENT
    image, _ = Fix.proposal(old)
    assert Fix.digest(image) == PIN and image == Fix.CANDIDATE.read_bytes()
    ips = ips_for(image)
    assert Fix.digest(ips) == PATCH_PIN and apply_ips(SOURCE_BASE.read_bytes(),ips)[0] == image
    assert Fix.digest(SCRIPT.read_bytes()) == SCRIPT_PIN
    try:
        Fix.NIGHTLY.write_bytes(image)
        assert Fix.NIGHTLY.read_bytes() == image and check(Fix.NIGHTLY)['ROM_sha256'] == PIN
        for variant,expected in enumerate(RECEIPTS):
            result = run(SCRIPT, Fix.NIGHTLY, output/str(variant), PIN, 90, variant)
            print(json.dumps(dict(variant=variant, passed=result['passed'],
                receipt_SHA256=result['receipt_SHA256'], reason=result['receipt']['reason']),
                sort_keys=True), flush=True)
            assert result['passed'] and result['receipt_SHA256'] == expected
        after = check(Fix.NIGHTLY)
        assert Fix.NIGHTLY.read_bytes() == image and after['ROM_sha256'] == PIN
    except BaseException:
        Fix.NIGHTLY.write_bytes(old)
        assert Fix.NIGHTLY.read_bytes() == old
        raise
    print(json.dumps(dict(passed=True, installed=True, ROM_SHA256=PIN, IPS_SHA256=PATCH_PIN,
        guard_before=before, guard_after=after, candidate_and_Downloads_receipts=RECEIPTS,
        output_files=0, backup_files=0),sort_keys=True),flush=True)


class Recipe:
    V1 = Previous.Recipe.V1

    @staticmethod
    def proposal(base):
        return Fix.proposal(Previous.Recipe.proposal(base)[0])


def release_notes(head):
    return ('Current MMC5 WIP nightly. Apply this IPS to clean headered Super Mario Bros. (World).\n\n'
        f'ROM SHA-256: {PIN}\nIPS SHA-256: {PATCH_PIN}\nSource commit: {head}\n\n'
        'Character Select now keeps SMB2 and Doki Doki preview health separate from the next character. '
        'Mesen verified all eight previews before starting Sonic, and checked Mario and Lina in 1-1. '
        'The previous Sonic injury and Prince traversal updates remain included. All 100 named entries '
        'remain available. See docs/qa/smb2-menu-tier-isolation-1110.md for verification.\n')


def publish(report_sha):
    import publish_ff_corner_current_1110 as base

    with patch.object(base,'PIN',PIN), patch.object(base,'PATCH_PIN',PATCH_PIN), \
         patch.object(base,'OLD_PATCH',Previous.PATCH_PIN), patch.object(base,'RECEIPTS',RECEIPTS), \
         patch.object(base,'Fix',Recipe), patch.object(base,'CANDIDATE',Fix.CANDIDATE), \
         patch.object(base,'SCRIPT',SCRIPT), patch.object(base,'SCRIPT_PIN',SCRIPT_PIN), \
         patch.object(base,'REPORT',REPORT), patch.object(base,'release_body',release_notes):
        base.main(report_sha=report_sha)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    command=parser.add_mutually_exclusive_group(required=True)
    command.add_argument('--output',type=Path)
    command.add_argument('--report-sha')
    args=parser.parse_args()
    if args.output:
        install(args.output.resolve())
    else:
        publish(args.report_sha)


if __name__ == '__main__':
    main()
