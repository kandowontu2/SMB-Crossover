"""Compare empty shot-bank scan timing on the two native opening replays."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys

from check_mini_funded_actor_1108_v3 import install
from prepare_current_helper_3_3_1110 import PIN, ROM
from prepare_selected_native_packet_v1 import R, prepare, sha


PATCH = 16 + 78 * 8192 + 0x1c9a
ORIGINAL = bytes.fromhex('c903f008c906d00ca908d002a900186970')
EMPTY_SKIP = bytes.fromhex('f012c903f008c906d00aa978d002a970b8')
BASE = R / 'build/shared-gameplay-cadence-1110'
MINI = ROM.parent / 'mini'


def check_mini(out):
    proof = out / 'proof.json'
    trial = json.loads(proof.read_text())
    candidate = out / 'candidate.nes'
    digest = sha(candidate)
    assert digest == trial['candidate_SHA256'] and trial['parent_SHA256'] == PIN
    controller, ready = (MINI / name for name in ('controller.lua', 'ready.json'))
    prior = json.loads(ready.read_text())
    assert prior['ROM_sha256'] == PIN and prior['bindings'][str(controller)] == sha(controller)
    code = controller.read_text(encoding='utf-8')
    assert code.count(PIN) == 1
    packet = out / 'mini'
    prepare(packet, candidate, code.replace(PIN, digest, 1), {Path(__file__), proof, controller, ready},
            expected=digest, timeout=180, allow_interactive=True,
            scope='Private shared shot-bank trial, native Mini nonshortcut 1-1 and all three lifts.')
    subprocess.run([sys.executable, '-B', str(packet / 'run.py')], check=True)
    result, timing = (json.loads((packet / 'capture' / name).read_text()) for name in ('result.json', 'timing.json'))
    cadence = timing['cadence']['fullstage']
    assert result['passed'] and result['ROM_sha256'] == timing['ROM_sha256'] == digest
    assert cadence['physical'] == cadence['updates'] and not cadence.get('no_controller_read', 0)
    assert cadence['lag_nmi'] == cadence['zero_update'] == 0
    print('Mini active 1-1', json.dumps(cadence), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--mini', action='store_true')
    parser.add_argument('--world-proof', type=Path)
    args = parser.parse_args()
    out = args.output.resolve()
    if args.mini:
        check_mini(out)
        return
    assert out.is_relative_to(R / 'build') and not out.exists()
    raw = ROM.read_bytes()
    assert sha(ROM) == PIN and len(ORIGINAL) == len(EMPTY_SKIP)
    assert raw[PATCH:PATCH + len(ORIGINAL)] == ORIGINAL and PATCH == 646314
    refs = {Path(__file__), ROM}
    trial = raw
    if args.world_proof:
        world = json.loads(args.world_proof.read_text())
        assert world['passed'] and world['parent_SHA256'] == PIN
        for p in world['patches']:
            start = p['file_offset']
            assert start+len(bytes.fromhex(p['new_hex'])) <= PATCH or start >= PATCH+len(ORIGINAL)
        trial = install(raw, world['patches'])
        assert sha256(trial).hexdigest() == world['expected_memory_only_SHA256']
        refs.add(args.world_proof)
    trial = trial[:PATCH] + EMPTY_SKIP + trial[PATCH + len(ORIGINAL):]
    digest = sha256(trial).hexdigest()
    out.mkdir()
    candidate = out / 'candidate.nes'
    candidate.write_bytes(trial)
    for suffix in ('.lbl', '.dbg'):
        shutil.copyfile(ROM.with_suffix(suffix), candidate.with_suffix(suffix))
    rows = {}
    for name in ('bill', 'samus'):
        previous = BASE / f'current-{name}'
        prior, ready, old = (previous / name for name in ('controller.lua', 'ready.json', 'capture/result.json'))
        ref = json.loads(ready.read_text())
        assert ref['ROM_sha256'] == PIN and ref['bindings'][str(prior)] == sha(prior)
        code = prior.read_text(encoding='utf-8')
        assert code.count(PIN) == 1
        packet = out / name
        prepare(packet, candidate, code.replace(PIN, digest, 1), refs | {prior, ready, old},
                expected=digest, timeout=55, allow_interactive=True,
                scope=f'Private shared shot-bank trial, {name} cold Easy 1-1 idle and walking.')
        subprocess.run([sys.executable, '-B', str(packet / 'run.py')], check=True)
        new = packet / 'capture/result.json'
        before, after = (json.loads(p.read_text()) for p in (old, new))
        assert before['ROM_sha256'] == PIN and after['ROM_sha256'] == digest and before['raw'] == after['raw']
        assert [(r['x_initial'], r['x_final'], r['updates'], r['contacts']) for r in before['phases']] == [
            (r['x_initial'], r['x_final'], r['updates'], r['contacts']) for r in after['phases']]
        rows[name] = dict(baseline=before['phases'], candidate=after['phases'],
                          baseline_SHA256=sha(old), candidate_SHA256=sha(new))
    proof = dict(parent_SHA256=PIN, candidate_SHA256=digest, offset=PATCH, before=ORIGINAL.hex(),
                 after=EMPTY_SKIP.hex(), controller_only=True, public=False, results=rows,
                 world_proof_SHA256=sha(args.world_proof) if args.world_proof else None)
    (out / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n', encoding='utf-8')
    for name, row in rows.items():
        counts = tuple([phase['no_controller_read'] for phase in row[key]] for key in ('baseline', 'candidate'))
        print(name, 'missed controller reads before/after', counts, flush=True)


if __name__ == '__main__':
    main()
