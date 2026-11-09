"""Compose the proven Mini adder bypass over the delivered contact/render build.

Run through run_bounded_build_v1. Native qualification remains required, and
the earlier interrupt proof must be rebound to this exact composed ROM.
"""
import argparse
import json
from pathlib import Path
import shutil

from compose_mini_frame_budget_1108 import compose, load, digest, check_full_cpu
from qualify_mini_busy_1109 import run_suite
from prepare_selected_native_packet_v1 import R, sha

CURRENT = R / 'build/mini-contact-render-typed-1109/candidate.nes'
PIN = '84d372ef9b6cea58918454fbea0ab2f5433fe051bd17c99fd86cc8e94a6da3aa'
BASE = R / 'build/mini-parser-lift-1109/candidate.nes'
PROOFS = R / 'build/mini-native-side-single-map-1109'


def build(output):
    raw, old = CURRENT.read_bytes(), BASE.read_bytes()
    assert digest(raw) == PIN
    side = bytearray(old)
    compose(old, side, load(PROOFS / 'proof.json'), parent=digest(old))
    new = bytearray(raw)
    compose(side, new, load(PROOFS / 'adder-proof.json'), parent=digest(side))
    rows = check_full_cpu(raw, new, {})
    assert all(row['min_saved'] >= 0 for row in rows)
    output.mkdir()
    rom = output / 'candidate.nes'
    rom.write_bytes(new)
    for suffix in ('.dbg', '.lbl'):
        shutil.copyfile(CURRENT.with_suffix(suffix), rom.with_suffix(suffix))
    info = load(CURRENT.with_suffix('.json'))
    info.update(parent_SHA256=PIN, candidate_SHA256=digest(new),
                whole_GameCore=rows, private_pending_current_interrupt_proof=True,
                adder_inputs={str(p): sha(p) for p in
                              (CURRENT, BASE, PROOFS / 'proof.json',
                               PROOFS / 'adder-proof.json')})
    rom.with_suffix('.json').write_text(json.dumps(info, indent=2) + '\n')
    print(json.dumps(dict(ROM_SHA256=digest(new), whole_GameCore=rows)), flush=True)
    return rom


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--test', action='store_true')
    args = parser.parse_args()
    rom = build(args.output)
    if args.test:
        run_suite(args.output / 'native', rom,
                  R / 'build/mini-kernel-transport-1109/v2/kernel.bin',
                  ('route', 'idle', 'power'))
        run_suite(args.output / 'native', rom, None, ('fire',))


if __name__ == '__main__':
    main()
