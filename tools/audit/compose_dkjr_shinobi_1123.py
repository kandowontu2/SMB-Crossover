"""Compose the two DK Jr. pickup lifts with the Shinobi nightly."""

import argparse
from unittest.mock import patch

import compose_shinobi_pickups_1123 as Shinobi
import probe_dkjr_life_star_pickups_1123 as Pickups


Lifts = Pickups.C
Stock = Lifts.Joined.Native
H = Pickups.H
CANDIDATE = 'a8727de4d757f3bd415c0497b01773dd6797e607d322cc256892bd8e75c9351b'


def recover_parent(image):
    assert H(image) == CANDIDATE
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', choices=('life', 'star'), required=True)
    parser.add_argument('--star-top', type=int, default=180)
    parser.add_argument('--star-reboard', action='store_true')
    args = parser.parse_args()
    installed = Stock.ROM.read_bytes()
    image, private, replay = compose(installed, Stock.OUT)
    kind = 3 if args.run == 'life' else 2
    program = pickup_controller(private, replay, kind, life_timing='ascending164',
                                star_top=args.star_top, star_reboard=args.star_reboard)
    print(f'DK SHINOBI CANDIDATE {CANDIDATE} {H(program.encode())}', flush=True)
    return Lifts.root_native(image, program, installed)


if __name__ == '__main__':
    raise SystemExit(main())
