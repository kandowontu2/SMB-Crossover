"""Deliver Steve's verified Shatterhand movement and the matching Current IPS."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import replay_steve_move_native_1111 as Replay
import replay_prince_second_brick_1111 as PrinceReplay
from deliver_manual_title_1110 import SOURCE_BASE, SOURCE_PIN, apply_ips, ips_for
from nightly_patch_guard_v1 import check


Source, Parent = Replay.Source, Replay.Parent
R, NIGHTLY = Parent.R, Parent.NIGHTLY
PIN = 'e6b152e26b43449115a7ff21903ae756346052e55dbdd94d8751e8c3a0951f23'
PATCH_PIN = 'e866c1260204115be1de66474d44fcb8ae19e98ee6ea165409e92d88589f19ca'
RECEIPT = 'cfca6b729fb654f4e30de0020b09aef64e3be3250fe5ad90513268c499ab35d5'
TAIL_PIN = '33731436eb8e721ee2a022e6fbe14438965a2eb9525c7485ad8e0459591cc851'
CONTROLLER_PIN = '36b59dc6064fde3b93c6029966ab10f84e6003a3a69d67451c7a55c9c707862c'
REPORT = R / 'docs/qa/steve-move-delivery-1111.md'
CANDIDATE = R / 'build/steve-move-native-1111/candidate.nes'


def digest(data):
    return sha256(data).hexdigest()


def proposal(parent):
    raw = Parent.recover_parent(parent)
    candidate, program, punch, cookie = Source.proposal(raw)
    image, _ = Parent.Source.replace_workers(candidate, *Parent.Source.source_workers())
    assert digest(image) == PIN
    return image, program, punch, cookie


def recover_parent(image):
    assert digest(image) == PIN
    carrier, build = Source.Carrier, Source.S
    old = carrier.cold_program(carrier.ORIGINAL_DESCRIPTOR, carrier.ORIGINAL_COOKIE)
    old_code = build.link(build.W.Symbols.bundle())['images']
    spans = [
        (build.C.offset(65, carrier.T.COLD), old['images']['COLD65'].ljust(carrier.T.COLD_SIZE, b'\xea')),
        (build.C.offset(65, 0xaf01), build.address_bytes(old['symbols']['JaySelect'])),
        (build.C.offset(94, 0xb2ef), carrier.ORIGINAL_COOKIE),
        (build.C.CHR + 1024 * carrier.PAGE, bytes(1024)),
    ]
    for name, page, origin in (('COMBAT', 234, 0xbc00), ('BIRTH', 222, 0xb400)):
        address, length = build.LAYOUT[name]
        spans.append((build.C.CHR + 1024 * page + address - origin, old_code[name].ljust(length, b'\xea')))
    parent = bytearray(image)
    for start, original in spans:
        parent[start:start + len(original)] = original
    assert digest(parent) == Parent.PIN
    return bytes(parent)


def install(output):
    assert output.is_relative_to(R / 'build') and output != R / 'build'
    assert check(NIGHTLY)['ROM_sha256'] == Parent.PIN
    parent = NIGHTLY.read_bytes()
    image, program, punch, cookie = proposal(parent)
    assert recover_parent(image) == parent
    if CANDIDATE.exists():
        assert CANDIDATE.read_bytes() == image
    base, ips = SOURCE_BASE.read_bytes(), ips_for(image)
    assert digest(base) == SOURCE_PIN and digest(ips) == PATCH_PIN
    assert apply_ips(base, ips)[0] == image
    assert digest(Replay.TAIL.read_bytes()) == TAIL_PIN

    output.mkdir(exist_ok=True)
    script = output / 'controller.lua'
    script.write_text(Replay.controller(), encoding='utf-8', newline='\n')
    assert digest(script.read_bytes()) == CONTROLLER_PIN
    try:
        NIGHTLY.write_bytes(image)
        assert NIGHTLY.read_bytes() == image and check(NIGHTLY)['ROM_sha256'] == PIN
        steve = Replay.replay(script, NIGHTLY, output / 'steve-capture', PIN, program, punch, cookie)
        assert steve['passed'] and steve['receipt_SHA256'] == RECEIPT, steve['receipt']
        script.write_text(PrinceReplay.controller(Parent.COOKIE, 0xd749), encoding='utf-8', newline='\n')
        assert digest(script.read_bytes()) == Parent.CONTROLLER_PIN
        prince = PrinceReplay.replay(script, NIGHTLY, output / 'prince-capture', PIN, hold_on_cap=True)
        assert prince['passed'], prince['receipt']
        normalized = dict(prince['receipt'], ROM_SHA256=Parent.PIN)
        assert digest(json.dumps(normalized, sort_keys=True).encode()) == Parent.RECEIPTS[0]
        assert NIGHTLY.read_bytes() == image and check(NIGHTLY)['ROM_sha256'] == PIN
    except BaseException:
        NIGHTLY.write_bytes(parent)
        assert NIGHTLY.read_bytes() == parent
        raise
    print(json.dumps(dict(installed=True, ROM_SHA256=PIN, IPS_SHA256=PATCH_PIN, Steve=RECEIPT,
                          Prince=prince['receipt_SHA256'], backup_files=0)), flush=True)


def release_notes(head):
    return ('Current MMC5 WIP nightly. Apply the sole IPS to clean headered Super Mario Bros. (World).\n\n'
            f'ROM SHA-256: {PIN}\nIPS SHA-256: {PATCH_PIN}\nSource commit: {head}\n\n'
            'Choose Mike Jones and press Select twice for Steve Hermann. Steve now uses his original '
            'Shatterhand acceleration, crouch, and variable-height jump. Mesen verifies a native Goomba punch '
            'and first-pipe crossing. Prince retains the previous brick footing repair. Full stage and further '
            'upgrades remain in progress. See docs/qa/steve-move-delivery-1111.md.\n')


def publish(report_sha):
    import publish_ff_corner_current_1110 as publisher

    class Recipe:
        V1 = SimpleNamespace(BASE=SOURCE_BASE)

        @staticmethod
        def proposal(base):
            assert digest(base) == SOURCE_PIN
            return proposal(recover_parent(NIGHTLY.read_bytes()))

    with patch.multiple(publisher, PIN=PIN, PATCH_PIN=PATCH_PIN, OLD_PATCH=Parent.PATCH_PIN,
                        RECEIPTS=(RECEIPT,), Fix=Recipe, CANDIDATE=CANDIDATE,
                        SCRIPT=Replay.TAIL, SCRIPT_PIN=TAIL_PIN, REPORT=REPORT,
                        release_body=release_notes):
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
