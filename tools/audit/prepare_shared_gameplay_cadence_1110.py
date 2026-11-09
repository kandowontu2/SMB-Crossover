"""Bind matched opening replays and the candidate's full Mini route."""

import argparse
import hashlib
import json
from pathlib import Path

from prepare_current_helper_3_3_1110 import NIGHTLY, PIN, ROM
from prepare_selected_native_packet_v1 import R, prepare, sha


BASE = R / 'build/mini-platform-pair-native-1110/candidate.nes'
BASE_SHA = 'df03fc35ebdc516a8df0b501bbe2008e52836aa8fcfad5c34e4df76783e9f331'
SPARSE = R / 'build/shared-sparse-draw-native-1110/candidate.nes'
SPARSE_SHA = 'f33c7b19d27309ab4e4771125a74360f978dba08bd807d25bc6307026e568734'
SCRIPT = Path(__file__).with_name('shared_gameplay_cadence_1110.lua')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--candidate-proof', type=Path)
    args = parser.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(R / 'build') and not out.exists()
    refs = {Path(__file__), SCRIPT}
    symbols = None
    if args.candidate_proof:
        assert sha(NIGHTLY) == sha(SPARSE) == SPARSE_SHA
        proof_path = args.candidate_proof.resolve()
        proof = json.loads(proof_path.read_bytes())
        assert proof['passed'] and proof['parent_SHA256'] == SPARSE_SHA
        raw = bytearray(SPARSE.read_bytes())
        for patch in proof['patches']:
            at = patch['file_offset']
            old, new = (bytes.fromhex(patch[key]) for key in ('old_hex', 'new_hex'))
            assert 16 <= at < at + len(old) <= len(raw) and len(old) == len(new)
            assert raw[at:at + len(old)] == old
            raw[at:at + len(old)] = new
        digest = proof['expected_memory_only_SHA256']
        assert hashlib.sha256(raw).hexdigest() == digest and digest != SPARSE_SHA
        out.mkdir()
        candidate = out / 'candidate.nes'
        candidate.write_bytes(raw)
        refs.add(proof_path)
        symbols = SPARSE.with_suffix('.lbl'), SPARSE.with_suffix('.dbg')
        targets = (('candidate', candidate, digest),)
    else:
        assert sha(NIGHTLY) == sha(ROM) == PIN and sha(BASE) == BASE_SHA
        out.mkdir()
        targets = (('baseline', BASE, BASE_SHA), ('current', ROM, PIN))
    for version, rom, digest in targets:
        raw = rom.read_bytes()
        menu = 16 + 124 * 8192 + 0x40
        assert raw[menu:menu + 4] == bytes((0, 1, 2, 3))
        for slot, name in ((2, 'samus'), (3, 'bill')):
            prefix = f'local C = {{rom="{digest}",slot={slot}}}\n'
            prepare(out / f'{version}-{name}', rom, prefix + SCRIPT.read_text(encoding='utf-8'),
                    refs, expected=digest, timeout=45, allow_interactive=True, rom_symbols=symbols,
                    scope=f'{name}, cold Easy 1-1, idle and walk to the first Goomba approach')
    if args.candidate_proof:
        mini = SPARSE.parent / 'mini'
        controller, ready = mini / 'controller.lua', mini / 'ready.json'
        bound = json.loads(ready.read_bytes())
        assert bound['ROM_sha256'] == SPARSE_SHA and not bound['emulated_writes']
        assert bound['bindings'][str(controller)] == sha(controller)
        script = controller.read_text(encoding='utf-8')
        assert script.count(SPARSE_SHA) == 1
        prepare(out / 'mini', candidate, script.replace(SPARSE_SHA, digest),
                refs | {controller, ready}, expected=digest, timeout=180,
                allow_interactive=True, rom_symbols=symbols,
                scope='Mini native nonshortcut 1-1 with all three lifts, exact retained controller.')


if __name__ == '__main__':
    main()
