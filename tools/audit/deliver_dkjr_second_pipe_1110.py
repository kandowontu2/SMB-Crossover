"""Install the tested DK Jr. lifts and refresh the sole Current IPS."""
import argparse
import json
from pathlib import Path
from unittest.mock import patch

import check_dkjr_second_pipe_lifts_1110 as Fix
import deliver_smb2_menu_tier_1110 as Previous
from deliver_manual_title_1110 import SOURCE_BASE, apply_ips, ips_for
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

PIN='a20d254d4730583ee1f039b10abcf873559987e4f989968037a38e17427faac1'
PATCH_PIN='a1621d5ef67b60d5a617651a3cb0260d56141160376454a5db2c9d6a53a13852'
SCRIPT=Fix.R/'tools/playthroughs/dkjr_second_pipe_stdout_1110.lua'
SCRIPT_PIN='e782a077485520ed8832587acd8af31839bbf58096b5b6cee4c89641bd11f43f'
RECEIPT='a3cd3ef76fb2b6423f833c2b6b4348344c15c416ad911789296a234864a3523f'
REPORT=Fix.R/'docs/qa/dkjr-second-pipe-delivery-1110.md'


def install(output):
    assert output.is_relative_to(Fix.R/'build') and output != Fix.R/'build' and not output.exists()
    before=check(Fix.NIGHTLY)
    old=Fix.NIGHTLY.read_bytes()
    assert Fix.S.sha(old)==before['ROM_sha256']==Fix.PARENT
    image,_,_=Fix.proposal(old)
    assert Fix.S.sha(image)==PIN and image==Fix.CANDIDATE.read_bytes()
    ips=ips_for(image)
    assert Fix.S.sha(ips)==PATCH_PIN and apply_ips(SOURCE_BASE.read_bytes(),ips)[0]==image
    assert Fix.S.sha(SCRIPT.read_bytes())==SCRIPT_PIN
    try:
        Fix.NIGHTLY.write_bytes(image)
        assert Fix.NIGHTLY.read_bytes()==image and check(Fix.NIGHTLY)['ROM_sha256']==PIN
        result=run(SCRIPT,Fix.NIGHTLY,output,PIN,180,0)
        assert result['passed'] and result['receipt_SHA256']==RECEIPT,result['receipt']
        after=check(Fix.NIGHTLY)
        assert Fix.NIGHTLY.read_bytes()==image and after['ROM_sha256']==PIN
    except BaseException:
        Fix.NIGHTLY.write_bytes(old)
        assert Fix.NIGHTLY.read_bytes()==old
        raise
    print(json.dumps(dict(passed=True, installed=True, ROM_SHA256=PIN, IPS_SHA256=PATCH_PIN,
        receipt_SHA256=RECEIPT,guard_before=before,guard_after=after,output_files=0,
        backup_files=0),sort_keys=True),flush=True)


class Recipe:
    V1=Previous.Recipe.V1

    @staticmethod
    def proposal(base):
        return Fix.proposal(Previous.Recipe.proposal(base)[0])


def release_notes(head):
    return ('Current MMC5 WIP nightly. Apply this IPS to clean headered Super Mario Bros. (World).\n\n'
        f'ROM SHA-256: {PIN}\nIPS SHA-256: {PATCH_PIN}\nSource commit: {head}\n\n'
        'Donkey Kong Jr. now has two additional stock girders for the second pipe in 1-1. '
        'Mesen verified the first and second pipe crossings with his original jump and both lives. '
        'Select him from Donkey Kong. The later pipes, full stage and earned powerups remain in testing. '
        'See docs/qa/dkjr-second-pipe-delivery-1110.md for the placements and verification.\n')


def publish(report_sha):
    import publish_ff_corner_current_1110 as base

    with patch.object(base,'PIN',PIN), patch.object(base,'PATCH_PIN',PATCH_PIN), \
         patch.object(base,'OLD_PATCH',Previous.PATCH_PIN), patch.object(base,'RECEIPTS',(RECEIPT,)), \
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


if __name__=='__main__':
    main()
