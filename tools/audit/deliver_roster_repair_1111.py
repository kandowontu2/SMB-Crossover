"""Deliver the tested roster flicker, Giant loader and Prince footing repairs."""

import argparse
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from deliver_manual_title_1110 import SOURCE_BASE, SOURCE_PIN, apply_ips, ips_for
from nightly_patch_guard_v1 import check
import replay_roster_repair_1111 as Verification


Source = Verification.Source
R, NIGHTLY, PIN = Verification.R, Verification.NIGHTLY, Verification.PIN
REPORT = R / 'docs/qa/roster-repair-delivery-1111.md'
SCRIPT_PIN = '2c3c9c267a0e94950183031d8e85bd54dcdb55d0f71d61cb732e56c14904190a'
RECEIPTS = {
    'menu': 'e844ad71ed50db8043aa719d4711f154f5215054a8c5bda12af7ca61f1bba46a',
    'giant': '108b755260e4b3e0548e178e644f19404f3c6b995e1d9ef7617783b1d22507cc',
    'prince_neutral': 'c34792eacb57239a84d592599dad376f7f19fe7be5b62060c691c700376d74db',
    'prince_goombas': 'd429efa0d32b51e92d841fad95d9ec1bcb32c1904ce9a9ced3a096590ff5bf22',
}


def install(output):
    assert output.is_relative_to(R / 'build') and output != R / 'build'
    assert check(NIGHTLY)['ROM_sha256'] == Source.Parent.PIN
    parent = NIGHTLY.read_bytes()
    image, layout = Source.proposal(parent)
    assert Source.digest(image) == PIN and Source.recover_parent(image) == parent
    if Verification.CANDIDATE.exists():
        assert Verification.CANDIDATE.read_bytes() == image
    base, ips = SOURCE_BASE.read_bytes(), ips_for(image)
    assert Source.digest(base) == SOURCE_PIN and Source.digest(ips) == Verification.IPS_PIN
    assert apply_ips(base, ips)[0] == image
    assert Source.digest(Verification.Menu.SCRIPT.read_bytes()) == SCRIPT_PIN
    output.mkdir(exist_ok=True)
    try:
        NIGHTLY.write_bytes(image)
        assert NIGHTLY.read_bytes() == image and check(NIGHTLY)['ROM_sha256'] == PIN
        assert Verification.replay(NIGHTLY, output, layout) == RECEIPTS
        assert NIGHTLY.read_bytes() == image and check(NIGHTLY)['ROM_sha256'] == PIN
    except BaseException:
        NIGHTLY.write_bytes(parent)
        assert NIGHTLY.read_bytes() == parent and check(NIGHTLY)['ROM_sha256'] == Source.Parent.PIN
        raise
    print(json.dumps(dict(installed=True, ROM_SHA256=PIN, IPS_SHA256=Verification.IPS_PIN,
                          receipts=RECEIPTS, backup_files=0), sort_keys=True), flush=True)


def release_notes(head):
    return ('Current MMC5 WIP nightly. Apply the sole IPS to clean headered Super Mario Bros. (World).\n\n'
            f'ROM SHA-256: {PIN}\nIPS SHA-256: {Verification.IPS_PIN}\nSource commit: {head}\n\n'
            'Fixes Mini Mario’s roster flicker and heading corruption. The full menu sweep checks 135 '
            'Select and D-pad transitions. Mega Giant Mario starts and clears World 1-1 again. '
            'Prince of Persia keeps his footing on the floating question block and can jump past the two '
            'Goombas. See docs/qa/roster-repair-delivery-1111.md.\n')


def publish(report_sha):
    import publish_ff_corner_current_1110 as publisher

    class Recipe:
        V1 = SimpleNamespace(BASE=SOURCE_BASE)

        @staticmethod
        def proposal(base):
            assert Source.digest(base) == SOURCE_PIN
            return Source.proposal(Source.recover_parent(NIGHTLY.read_bytes()))

    with patch.multiple(publisher, PIN=PIN, PATCH_PIN=Verification.IPS_PIN,
                        OLD_PATCH=Source.Parent.PATCH_PIN, RECEIPTS=tuple(RECEIPTS.values()),
                        Fix=Recipe, CANDIDATE=Verification.CANDIDATE, SCRIPT=Verification.Menu.SCRIPT,
                        SCRIPT_PIN=SCRIPT_PIN, REPORT=REPORT, release_body=release_notes):
        publisher.main(report_sha=report_sha)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument('--install-output', type=Path)
    operation.add_argument('--publish-report-sha')
    args = parser.parse_args()
    if args.install_output:
        install(args.install_output.resolve())
    else:
        publish(args.publish_report_sha)


if __name__ == '__main__':
    main()
