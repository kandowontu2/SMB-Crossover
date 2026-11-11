"""Install the qualified Prince brick fix and refresh the sole Current IPS."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import compose_prince_brick_1111 as Source
from deliver_manual_title_1110 import SOURCE_BASE, SOURCE_PIN, apply_ips, ips_for
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run


R, NIGHTLY = Source.Packet.R, Source.Replay.NIGHTLY
PIN = '17122790d711b905c681dced1fd9b3a0e69e1364cb039d514ba635c31a1e4fed'
PATCH_PIN = '5849b2801e71b6d91fead73827949b3c193802e0aa79be4bfc80d9482374797e'
OLD_PATCH = '8e631e876d64396f3f869ebcecdda4ec53dc82ffa93401d2dbf0f63ddcc51954'
COOKIE = 'a72602ee912702130bffd8d05f657b4f'
RECEIPT = '94740623dbb75a06864c257913d121e82f2cce96d1dfea11014e97354ad0e002'
SCRIPT = Source.Replay.TAIL
SCRIPT_PIN = '02e56e7daf78158f61adfa9fca9245b240a614a13671c5317b244d285cab540c'
ASSEMBLED_PIN = '64f523757c6f35949f2a0b22977dc1dfb41bb7f9d3e73c73eae1cf7bfab507dd'
REPORT = R / 'docs/qa/prince-brick-support-delivery-1111.md'


def digest(data):
    return sha256(data).hexdigest()


def install(output):
    assert output.is_relative_to(R / 'build') and output != R / 'build' and not output.exists()
    parent = NIGHTLY.read_bytes()
    assert digest(parent) == check(NIGHTLY)['ROM_sha256'] == Source.Replay.PIN
    candidate, layout = Source.proposal(parent)
    assert digest(candidate) == PIN and layout['cookie'] == COOKIE
    old, new, _ = Source.support_workers()
    assert Source.replace_worker(candidate, new, old)[0] == parent
    ips = ips_for(candidate)
    base = SOURCE_BASE.read_bytes()
    assert digest(base) == SOURCE_PIN and digest(ips) == PATCH_PIN and apply_ips(base, ips)[0] == candidate

    output.mkdir()
    controller = output / 'controller.lua'
    controller.write_text(Source.Replay.published_controller(COOKIE), encoding='utf-8', newline='\n')
    assert digest(SCRIPT.read_bytes()) == SCRIPT_PIN and digest(controller.read_bytes()) == ASSEMBLED_PIN
    try:
        NIGHTLY.write_bytes(candidate)
        assert NIGHTLY.read_bytes() == candidate and check(NIGHTLY)['ROM_sha256'] == PIN
        proof = run(controller, NIGHTLY, output / 'capture', PIN, 120, variant=3,
                    extra_env={'SMB_PRINCE_KOOPA_BRAKE': '1470', 'SMB_PRINCE_KOOPA_MODE': 'runway',
                               'SMB_PRINCE_KOOPA_JUMP_X': '1501'})
        assert proof['passed'] and proof['receipt_SHA256'] == RECEIPT, proof['receipt']
        assert NIGHTLY.read_bytes() == candidate and check(NIGHTLY)['ROM_sha256'] == PIN
    except BaseException:
        NIGHTLY.write_bytes(parent)
        assert NIGHTLY.read_bytes() == parent
        raise
    print(json.dumps(dict(passed=True, installed=True, ROM_SHA256=PIN, IPS_SHA256=PATCH_PIN,
                          receipt_SHA256=RECEIPT, script_SHA256=ASSEMBLED_PIN, backup_files=0,
                          stage_scope='title through running jump admission on the coin brick')), flush=True)


def release_notes(head):
    return ('Current MMC5 WIP nightly. Apply the sole IPS to clean headered Super Mario Bros. (World).\n\n'
            f'ROM SHA-256: {PIN}\nIPS SHA-256: {PATCH_PIN}\nSource commit: {head}\n\n'
            'Prince of Persia can walk onto the exposed coin brick after the second gap in 1-1 and start '
            'his original running jump. His full stage clear is still in progress. '
            'The preceding Jay McCray update remains in the ROM. See docs/qa/prince-brick-support-delivery-1111.md.\n')


def publish(report_sha):
    import publish_ff_corner_current_1110 as publisher

    class Recipe:
        V1 = SimpleNamespace(BASE=SOURCE_BASE)

        @staticmethod
        def proposal(base):
            assert digest(base) == SOURCE_PIN
            image = NIGHTLY.read_bytes()
            assert digest(image) == PIN
            old, new, _ = Source.support_workers()
            parent, _ = Source.replace_worker(image, new, old)
            assert digest(parent) == Source.Replay.PIN
            return Source.proposal(parent)

    with patch.multiple(publisher, PIN=PIN, PATCH_PIN=PATCH_PIN, OLD_PATCH=OLD_PATCH,
                        RECEIPTS=(RECEIPT,), Fix=Recipe,
                        CANDIDATE=R / 'build/prince-brick-fixed-1111/candidate.nes',
                        SCRIPT=SCRIPT, SCRIPT_PIN=SCRIPT_PIN, REPORT=REPORT, release_body=release_notes):
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
