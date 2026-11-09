"""Compose exact-preimage performance proofs and reuse Mini's native QA suite.

Run inside run_bounded_build_v1. Proofs are applied in order, each against its
own immediately preceding ROM unless --independent uses the common base.
Native and exact-image interrupt qualification
are required separately before delivery.
"""
import argparse
import json
from pathlib import Path
import shutil

from compose_mini_frame_budget_1108 import compose, load, digest, check_full_cpu
from qualify_mini_busy_1109 import run_suite
from prepare_selected_native_packet_v1 import R, sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, required=True)
    parser.add_argument('--pin', required=True)
    parser.add_argument('--proof', type=Path, action='append', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--test', action='store_true')
    parser.add_argument('--independent', action='store_true')
    args = parser.parse_args()
    original = args.base.read_bytes()
    assert digest(original) == args.pin
    candidate = bytearray(original)
    for path in args.proof:
        previous = original if args.independent else bytes(candidate)
        proof = load(path)
        if 'patch' in proof and 'patches' not in proof:
            proof = dict(proof, patches=[proof['patch']],
                         expected_memory_only_SHA256=proof['memory_only_SHA256'])
        compose(previous, candidate, proof, parent=digest(previous))
    rows = check_full_cpu(original, candidate, {})
    assert all(row['min_saved'] >= 0 for row in rows), rows
    args.output.mkdir()
    rom = args.output / 'candidate.nes'
    rom.write_bytes(candidate)
    for suffix in ('.dbg', '.lbl'):
        shutil.copyfile(args.base.with_suffix(suffix), rom.with_suffix(suffix))
    metadata = load(args.base.with_suffix('.json'))
    metadata.update(parent_SHA256=args.pin, candidate_SHA256=sha(rom),
                    whole_GameCore=rows,
                    composed_proofs={str(p.resolve()): sha(p) for p in args.proof})
    rom.with_suffix('.json').write_text(json.dumps(metadata, indent=2) + '\n')
    print(json.dumps(dict(ROM_SHA256=sha(rom), whole_GameCore=rows)), flush=True)
    if args.test:
        run_suite(args.output / 'native', rom,
                  R / 'build/mini-kernel-transport-1109/v2/kernel.bin',
                  ('route', 'idle', 'power'))
        run_suite(args.output / 'native', rom, None, ('fire',))


if __name__ == '__main__':
    main()
