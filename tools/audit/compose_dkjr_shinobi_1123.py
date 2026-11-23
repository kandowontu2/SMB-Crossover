"""Compose the two DK Jr. pickup lifts with the Shinobi nightly."""

import argparse
import json
from unittest.mock import patch

import compose_shinobi_pickups_1123 as Shinobi
import probe_dkjr_life_star_pickups_1123 as Pickups


Lifts = Pickups.C
Stock = Lifts.Joined.Native
H = Pickups.H
CANDIDATE = 'a8727de4d757f3bd415c0497b01773dd6797e607d322cc256892bd8e75c9351b'
STAR_UNDER = 'c691588689f0779da6af467493c374d203e8d511d22e346a279642a3e6a8737a'
STAR_SCRIPT = '36fd34047249952efb302f8644305da997db6da624d5819d48b703cb9ba52036'
STAR_RECEIPT = '1f93a372927ab70c7ea7b5385541a962b939fb12089f8fb4de3b815bf562b81e'


def recover_parent(image):
    assert H(image) in (CANDIDATE, STAR_UNDER)
    original, _, _ = Lifts.images()
    parent = Lifts.replace(image, original)
    cookie = Lifts.S.C.Old.Head.COOKIE_AT
    parent[cookie:cookie + 16] = Lifts.COOKIE
    assert H(parent) == Shinobi.CANDIDATE
    return bytes(parent)


def compose(current, out):
    baseline = Shinobi.recover_parent(current)
    with Lifts.Joined.cache(), patch.object(Pickups, 'OUT', out), patch.object(Lifts.Probe, 'OUT', out):
        private, replay = Pickups.prepare(baseline)
        merged = bytearray(current)
        disjoint_changes = 0
        for at, (old, new) in enumerate(zip(baseline, private, strict=True)):
            if old != new:
                assert current[at] == old
                merged[at] = new
                disjoint_changes += 1
        assert disjoint_changes == 64 and H(merged) == CANDIDATE
        assert recover_parent(merged) == current
    return bytes(merged), private, replay


def pickup_controller(private, replay, kind, **options):
    program, _ = Pickups.controller(private, replay, kind, **options)
    assert Pickups.ROM_SHA in program
    return program.replace(Pickups.ROM_SHA, CANDIDATE)


def star_under(image, program):
    assert H(image) == CANDIDATE
    _, current_layout, _ = Lifts.images()
    row = Lifts.COLUMNS.index(102)
    assert Lifts.COLUMNS[row - 1:row + 2] == (88,102,161)
    rows = bytearray(current_layout['ROWS'])
    rows[row] = 101
    shifted = Lifts.replace(image, dict(current_layout, ROWS=bytes(rows)))
    cookie = Lifts.S.C.Old.Head.COOKIE_AT
    owner = Lifts.S.C.Old.Head.payload(shifted)
    shifted[cookie:cookie + 16] = b'\xa7\x28\x01' + bytes.fromhex(H(owner))[:13]
    restored = Lifts.replace(shifted, current_layout)
    restored[cookie:cookie + 16] = image[cookie:cookie + 16]
    assert restored == image and H(shifted) == STAR_UNDER
    assert recover_parent(shifted) == recover_parent(image)
    old_cookie = image[cookie:cookie + 16].hex()
    new_cookie = shifted[cookie:cookie + 16].hex()
    once = Pickups.Check.Replay.one
    program = once(program, f"cookie=='{old_cookie}'", f"cookie=='{new_cookie}'")
    program = once(program, '[1632]=176', '[1616]=176')
    program = program.replace(CANDIDATE, STAR_UNDER)
    Pickups.Check.LuaRuntime().compile(program)
    return bytes(shifted), program


def install_after_stage_and_life(parent, image, program):
    controller = program.encode()
    assert H(parent) == Shinobi.CANDIDATE and H(image) == STAR_UNDER
    assert H(controller) == STAR_SCRIPT
    rom, out = Stock.ROM, Stock.OUT
    target, script = out / 'candidate.nes', out / 'controller.lua'
    before = Stock.check(rom)
    assert before['ROM_sha256'] == H(parent) and not before['matching_patch_files']
    assert set(out.iterdir()) == {target, script} and target.read_bytes() == rom.read_bytes() == parent
    previous = script.read_bytes()
    Stock.require_free_workspace(Stock.R, rom, allow_interactive=True)
    committed = False
    try:
        assert Stock.check(rom) == before and target.read_bytes() == parent
        rom.write_bytes(image)
        installed = Stock.check(rom)
        assert installed['ROM_sha256'] == STAR_UNDER and not installed['matching_patch_files']
        script.write_bytes(controller)
        result = Stock.run(script, rom, out / 'capture', STAR_UNDER, 360, long_no_capture=True)
        assert result['passed'] and result['receipt_SHA256'] == STAR_RECEIPT
        assert result['script_SHA256'] == STAR_SCRIPT and result['outputs_written'] == 0 and not result['images']
        target.write_bytes(image)
        assert rom.read_bytes() == target.read_bytes() == image and Stock.check(rom) == installed
        committed = True
        print('DK LIFTS INSTALLED ' + json.dumps(result, separators=(',', ':')), flush=True)
    finally:
        script.write_bytes(previous)
        if not committed:
            if rom.read_bytes() != parent:
                rom.write_bytes(parent)
            if target.read_bytes() != parent:
                target.write_bytes(parent)
            assert rom.read_bytes() == target.read_bytes() == parent and Stock.check(rom) == before
        assert set(out.iterdir()) == {target, script}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', choices=('life', 'star', 'stage'), action='append', required=True)
    parser.add_argument('--star-top', type=int, default=180)
    parser.add_argument('--star-reboard', action='store_true')
    parser.add_argument('--star-under', action='store_true')
    parser.add_argument('--install', action='store_true')
    args = parser.parse_args()
    if args.install:
        assert args.star_under and args.star_top == 180 and not args.star_reboard
        assert set(args.run) >= {'stage', 'life'}
    installed = Stock.ROM.read_bytes()
    parent = installed
    if H(installed) == STAR_UNDER:
        assert args.star_under and not args.install
        parent = recover_parent(installed)
    image, private, replay = compose(parent, Stock.OUT)
    for route in args.run:
        if route == 'stage':
            program = replay.replace(Pickups.ROM_SHA, CANDIDATE)
        else:
            kind = 3 if route == 'life' else 2
            program = pickup_controller(private, replay, kind, life_timing='ascending164',
                                        star_top=args.star_top, star_reboard=args.star_reboard,
                                        star_helper=1616 if args.star_under else 1632)
        candidate, controller = star_under(image, program) if args.star_under else (image, program)
        print(f'DK SHINOBI CANDIDATE {route} {H(candidate)} {H(controller.encode())}', flush=True)
        if Lifts.root_native(candidate, controller, installed):
            return 1
    if args.install:
        program = pickup_controller(private, replay, 2, star_top=180, star_helper=1616)
        candidate, controller = star_under(image, program)
        install_after_stage_and_life(installed, candidate, controller)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
