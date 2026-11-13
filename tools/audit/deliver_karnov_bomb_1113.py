"""Deliver the native-tested Karnov Bomb and its matching Current patch."""

import argparse
import sys
from types import SimpleNamespace
from unittest.mock import patch

import compose_karnov_bomb_1112 as Fix
import deliver_prince_moving_support_1112 as Shared
import inventory_roster_exact_1110_v1 as Reference
from nightly_patch_guard_v1 import check
import replay_karnov_stock_fixture_1113 as Fixture


PARENT = '15a683321cde608cfe15447e90ef58d5295a16a1a6b607434f98df37162ac533'
PIN = Fixture.PIN
RECEIPT = 'c912b6e0ae1f5e575152b3dd5f41d95378ec2c6769a8c0fd46e5331d8b38bde4'
SCRIPT_PIN = 'da2b3d7f6901062f70b2109f327e733bf8a03935943f57fe1c2ee62bc424d0a3'
REPORT = Fix.R/'docs/qa/karnov-bomb-mesen-1113.md'


def previous_image(raw):
    assert Shared.digest(raw) == PIN
    reference = Reference.ROM.read_bytes()
    assert Shared.digest(reference) == Reference.PIN
    result = bytearray(raw)
    for role, (page, count, _) in Fix.OWNED.items():
        at = Fix.CHR + page*1024
        body = bytearray(reference[at:at+count*1024])
        # Preserve the later, already delivered head/block adapters absent
        # from the retained reference. Authenticate each complete old carrier.
        if role == 'actor':
            assert body[0x10b3:0x10b6] == bytes.fromhex('8d00c8')
            assert body[0x11fb:0x11fd] == bytes.fromhex('f8db')
            assert body[0x1fcb:0x1fdd] == b'\xff'*18
            body[0x10b3:0x10b6] = bytes.fromhex('20f7dd')
            body[0x11fb:0x11fd] = bytes.fromhex('cbbf')
            body[0x1fcb:0x1fdd] = bytes.fromhex('a9788d6c01a9b38d6d01a98b205a014cf8db')
            body[0x1fe0:0x1ff0] = Fix.OLD_COOKIE
        elif role == 'options':
            assert body[0x7f7:0x7fe] == b'\xff'*7
            body[0x7f7:0x7fe] = bytes.fromhex('8d00c88d66c860')
        assert Shared.digest(body) == Fix.PINNED[role], role
        result[at:at+len(body)] = body
    result[0x3bad5:0x3bae5] = Fix.OLD_COOKIE
    parent = bytes(result)
    assert Shared.digest(parent) == PARENT
    proposed, report = Fix.transform(parent)
    assert proposed == raw and Fix.inverse(raw, report) == parent
    return parent


def release_notes(head):
    return (
        'Apply the sole IPS to clean headered Super Mario Bros. (World).\n\n'
        f'ROM SHA-256: {PIN}\nSource commit: {head}\n\n'
        'Karnov can select an owned Bomb and arm it with Down+B. The original stock counter, '
        'fuse phases, Bomb sprites and HUD icon are integrated. The blast now converts SMB '
        'enemy coordinates to the original game anchors, allowing it to hit ground enemies.\n\n'
        'Mesen verified a full 1-1 clear with both lives. A separate fixture supplies one '
        'Bomb stock, then uses actual controller input and verifies consumption, explosion '
        'sprites and a native Goomba defeat. The Downloads ROM repeats that fixture. '
        'Natural Bomb acquisition and the remaining equipment are still being tested. '
        'Includes the preceding Thomas flower platform.\n'
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--install', action='store_true')
    mode.add_argument('--publish-report-sha')
    args = parser.parse_args()
    candidate_path = Fixture.OUTPUT/'candidate.nes'
    candidate = candidate_path.read_bytes()
    parent = previous_image(candidate)
    ips = Shared.ips_for(candidate)
    patch_pin = Shared.digest(ips)
    assert Shared.apply_ips(Shared.SOURCE_BASE.read_bytes(), ips)[0] == candidate
    script = Fixture.OUTPUT/'controller.lua'
    if args.install:
        assert check(Shared.NIGHTLY)['ROM_sha256'] == PARENT
        assert Shared.NIGHTLY.read_bytes() == parent
        try:
            Shared.NIGHTLY.write_bytes(candidate)
            assert check(Shared.NIGHTLY)['ROM_sha256'] == PIN
            with patch.object(sys, 'argv', ['fixture', '--contact', '--rom', str(Shared.NIGHTLY)]):
                result = Fixture.main()
            assert result['receipt_SHA256'] == RECEIPT and result['script_SHA256'] == SCRIPT_PIN
            assert check(Shared.NIGHTLY)['ROM_sha256'] == PIN
            assert Shared.NIGHTLY.read_bytes() == candidate
        except BaseException:
            Shared.NIGHTLY.write_bytes(parent)
            assert check(Shared.NIGHTLY)['ROM_sha256'] == PARENT
            raise
        print(dict(installed=True, ROM_SHA256=PIN, IPS_SHA256=patch_pin,
                   native_fixture_receipt=RECEIPT, backup_files=0), flush=True)
    else:
        import publish_ff_corner_current_1110 as Publisher

        class Recipe:
            V1 = SimpleNamespace(BASE=Shared.SOURCE_BASE)

            @staticmethod
            def proposal(base):
                assert Shared.digest(base) == Shared.SOURCE_PIN
                return Fix.transform(previous_image(Shared.NIGHTLY.read_bytes()))

        with patch.multiple(Publisher, PIN=PIN, PATCH_PIN=patch_pin,
                            OLD_PATCH='a828d2f721306368fed92a3f9146f7a6529e0cc4a5e562548a72e054ee42c32d',
                            RECEIPTS=(RECEIPT,), Fix=Recipe, CANDIDATE=candidate_path,
                            SCRIPT=script, SCRIPT_PIN=SCRIPT_PIN, REPORT=REPORT,
                            release_body=release_notes):
            Publisher.main(report_sha=args.publish_report_sha)


if __name__ == '__main__':
    main()
