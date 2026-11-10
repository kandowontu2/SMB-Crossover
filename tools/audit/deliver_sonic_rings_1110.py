"""Install the verified Sonic rings nightly and publish its sole Current IPS."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import check_sonic_ring_physical_1110 as Physical
import check_sonic_ring_draw_cadence_1110 as Build
import deliver_dkjr_four_pipe_1110 as Previous
from deliver_manual_title_1110 import SOURCE_BASE, apply_ips, ips_for
from nightly_patch_guard_v1 import check


R = Physical.R
NIGHTLY = Build.Rebase.Four.NIGHTLY
PIN = Physical.PIN
PATCH_PIN = '9ebf6513327e71f80b1a33326c6831be22b045dfb97d01692da06e655f69411c'
REPORT = R / 'docs/qa/sonic-rings-delivery-1110.md'
GAMEPLAY = {
    'rings': 'aac201ce41ac6813019c3ba7f6c743ba0f99e098272d6c823a76024e58535d2b',
    'mushroom': 'b778e53418a779c17f1c362eb730a3e7f87fe903f60b5495e1c9a1a9aedbafa7',
    'stage': '49fec282e56af7bb399c47e4a85da0d8e31fef52dcd694ae130d3d342a9169a5',
}
RING_SCRIPT_PIN = '628832f25a2e9ed7975b5523904ad91731be130df35f11c488cb327ddb8f1e37'


def install(output):
    assert output.is_relative_to(R / 'build') and output != R / 'build'
    assert not output.exists() or not any(output.iterdir())
    before = check(NIGHTLY)
    old = NIGHTLY.read_bytes()
    assert sha256(old).hexdigest() == before['ROM_sha256'] == Build.Rebase.PARENT
    image = Physical.CANDIDATE.read_bytes()
    assert sha256(image).hexdigest() == PIN
    assert sha256(Physical.RING.read_bytes()).hexdigest() == RING_SCRIPT_PIN
    ips = ips_for(image)
    assert sha256(ips).hexdigest() == PATCH_PIN
    assert apply_ips(SOURCE_BASE.read_bytes(), ips)[0] == image
    result = {}
    try:
        NIGHTLY.write_bytes(image)
        assert NIGHTLY.read_bytes() == image and check(NIGHTLY)['ROM_sha256'] == PIN
        for name, replay in (('rings', Physical.run_rings), ('mushroom', Physical.run_power),
                             ('stage', Physical.run_stage)):
            q = replay(NIGHTLY, output)
            assert q['passed'], q['receipt']
            digest = Physical.gameplay_digest(q)
            assert digest == GAMEPLAY[name], (name, digest, q['receipt'])
            result[name] = dict(gameplay_SHA256=digest, receipt_SHA256=q['receipt_SHA256'],
                                script_SHA256=q['script_SHA256'], terminal=q['receipt']['terminal'])
            print(json.dumps(dict(route=name, **result[name]), sort_keys=True), flush=True)
        after = check(NIGHTLY)
        assert NIGHTLY.read_bytes() == image and after['ROM_sha256'] == PIN
    except BaseException:
        NIGHTLY.write_bytes(old)
        assert NIGHTLY.read_bytes() == old
        raise
    print(json.dumps(dict(passed=True, installed=True, ROM_SHA256=PIN, IPS_SHA256=PATCH_PIN,
                          replays=result, guard_before=before, guard_after=after,
                          backup_files=0, output_files=0), sort_keys=True), flush=True)


class Recipe:
    V1 = Previous.Recipe.V1

    @staticmethod
    def proposal(base):
        return Build.proposal(Previous.Recipe.proposal(base)[0])


def release_notes(head):
    return ('Current MMC5 WIP nightly. Apply this IPS to clean headered Super Mario Bros. (World).\n\n'
            f'ROM SHA-256: {PIN}\nIPS SHA-256: {PATCH_PIN}\nSource commit: {head}\n\n'
            'Sonic now collects five rings in the opening stretch of 1-1. The HUD counts them, '
            'and an enemy hit triggers his original ring loss, knockback and recovery. '
            'Mesen verified the visible effects, the earned mushroom tier through ring damage, '
            'and a separate full 1-1 clear with both lives. Select Sonic from Mr. Gimmick. '
            'See docs/qa/sonic-rings-delivery-1110.md.\n')


def publish(report_sha):
    import publish_ff_corner_current_1110 as publisher

    with patch.multiple(publisher, PIN=PIN, PATCH_PIN=PATCH_PIN, OLD_PATCH=Previous.PATCH_PIN,
                        RECEIPTS=tuple(GAMEPLAY.values()), Fix=Recipe,
                        CANDIDATE=Physical.CANDIDATE, SCRIPT=Physical.RING,
                        SCRIPT_PIN=RING_SCRIPT_PIN, REPORT=REPORT, release_body=release_notes):
        publisher.main(report_sha=report_sha)


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
