"""Preserve the CPU-only chunk arithmetic trial and its exact limits."""
from pathlib import Path
import difflib
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
TRIAL = D / 'root-nmi-chunk-arithmetic-v1'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    proof_paths = {
        'preparation.json': TRIAL / 'preparation.json',
        'original-full-continuation.json': TRIAL / 'continuation-cpu-v1/proof.json',
        'parameterized-control.json': TRIAL / 'continuation-cpu-v2-control/proof.json',
        'successor-v11-equivalence.json': D / 'root-nmi-chunk-v11-equivalence-v1/proof.json'}
    for name, path in proof_paths.items():
        proof = json.loads(path.read_text())
        if name != 'preparation.json':
            assert proof['passed'] and proof['cases'] == 20284 and not proof['native_run']
    old = D / 'parodius-visibility-current50b5-v1/hud-candidate-v9/source/src/nmi_vram_fast.s'
    new = TRIAL / 'source/src/nmi_vram_fast.s'
    successor = D / 'parodius-visibility-current50b5-v1/hud-candidate-v11/source/src/nmi_vram_fast.s'
    assert sha(new) == sha(successor)
    out = ROOT / 'docs/qa/checkpoints/2026-10-25/nmi-chunk-arithmetic-study'
    out.mkdir(parents=True, exist_ok=False)
    for name, path in proof_paths.items():
        shutil.copyfile(path, out / name)
    shutil.copyfile(new, out / 'nmi_vram_fast.s')
    patch = ''.join(difflib.unified_diff(old.read_text().splitlines(True), new.read_text().splitlines(True),
                                        fromfile='a/src/nmi_vram_fast.s', tofile='b/src/nmi_vram_fast.s'))
    (out / 'implementation.patch').write_text(patch)
    report = '''Private NMI chunk arithmetic, 25 October 2026

CPU-only result; no production change, native acceptance or goal completion.
Replace eight per-byte DEX instructions with one eight-byte subtraction.
Keep the298-byte source segment and following real entry PCs with3 tail bytes.
Only83 ROM bytes in bank116 differ from each matched private parent.
Four genuine internal helper labels move by3 bytes; no fake callable aliases.

The old partial-stop catalog remains immutable. Internal A/V change before
OutputToVRAM+11; exact linked continuation SEC/TYA/ADC replaces them before
use. Full returned AXYP/SP, all nonstack RAM, ordered writes/reads and banks
have no added exclusions. All20,284 full-continuation shapes pass, including
76 actual IRQ/RTI controls. The parameterized checker additionally confines
every binary difference to the actual99-byte helper window. Both its control
and the later HUD v10/v11 pair reproduce the exact same case costs/results.

Each eight-byte literal chunk saves8 CPU cycles. Short/repeated transfers and
palette reads do not regress. Bounded packet savings are0..56 cycles; longer
synthetic transfer savings reach248. A first full HUD's28+8 literals save32.
These are instruction costs, not a claim of fewer native lag frames or a safe
whole-NMI deadline. Final HUD queue/PPU/DMA/cadence qualification is separate.
'''
    (out / 'report.txt').write_text(report)
    tools = [ROOT / 'tools/audit' / name for name in [
        'trial_nmi_chunk_arithmetic_v1.py', 'check_nmi_chunk_arithmetic_v1.py',
        'check_nmi_chunk_arithmetic_v2.py', 'checkpoint_nmi_chunk_trial_v1.py']]
    manifest = dict(goal_complete=False, production_changes=False, native_run=False,
                    adoption_qualified=False, files={p.name: sha(p) for p in out.iterdir()},
                    tools={p.relative_to(ROOT).as_posix(): sha(p) for p in tools},
                    external_proofs={p.as_posix(): sha(p) for p in proof_paths.values()},
                    external_trial=TRIAL.as_posix(),
                    limits='Only the literal-copy counter is qualified here. '
                           'Parent and successor HUD proposals are not adopted by this checkpoint.')
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(dict(checkpoint=out.as_posix(), production_changes=False)))


if __name__ == '__main__':
    main()
