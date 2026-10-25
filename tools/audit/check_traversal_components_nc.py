"""Verify exact packet composition and reuse component proofs by bank equality."""
from pathlib import Path
import hashlib
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'build/verification/final-roster-nc'
ROM = OUT/'full-roster.nes'


def main():
    spec = importlib.util.spec_from_file_location('nc_image', ROOT/'build/verification/agent49g-samus-crouch-fix-proposal-b/image.py')
    image = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(image)
    old = image.Image(ROOT/'build/checkpoints/full-roster-mz/build/smb-crossover-mmc5-expanded.nes')
    new = image.Image(ROM)
    def symbols(i):
        result = {}
        for s in i.data['sym']:
            if s.get('scope') != 1 or 'seg' not in s or 'val' not in s:
                continue
            segment = i.segs[s['seg']]
            bank = (segment['ooffs']+s['val']-segment['start']-16)//8192 if 'ooffs' in segment else None
            result[s['name']] = (s['val'], bank)
        return result
    before, after = symbols(old), symbols(new)
    moved = {k: [v, after.get(k)] for k, v in before.items() if after.get(k) != v}
    assert not moved, moved
    assert new.raw[:16] == old.raw[:16] and new.raw[16+1048576:] == old.raw[16+1048576:]
    def bank(raw, n):
        return raw[16+n*8192:16+(n+1)*8192]
    changed = [n for n in range(128) if bank(new.raw, n) != bank(old.raw, n)]
    assert changed == [69, 71, 84, 86], changed
    z2 = (ROOT/'build/verification/new-pipe-playability-agent/z2-food-d.nes').read_bytes()
    cv3 = (ROOT/'build/player-guide-agent/cv3-pipe-private/adapted-air2.nes').read_bytes()
    assert all(bank(new.raw, n) == bank(z2, n) for n in (69, 71))
    assert all(bank(new.raw, n) == bank(cv3, n) for n in (84, 86))
    zproof = json.loads((ROOT/'build/verification/new-pipe-playability-agent/handoff-z2-pipes-h/z2-food-guards.json').read_text())
    cproof = json.loads((ROOT/'build/player-guide-agent/cv3-pipe-private/adoption-packet/evidence/component-proof.json').read_text())
    assert zproof['passed'] and zproof['cases'] == 1728
    assert cproof['passed'] and cproof['arithmetic_exclusion_cases'] == 924 and cproof['independent_ballistic_updates'] == 288
    report = dict(passed=True, ROM_sha256=hashlib.sha256(new.raw).hexdigest(),
        previous_public_symbols=len(before), moved=moved, CHR_exact_MZ=True,
        changed_PRG_banks=changed, all_other_PRG_exact_MZ=True,
        Z2_banks_exact_frozen_candidate=[69, 71], CV3_banks_exact_frozen_candidate=[84, 86],
        component_proof_reuse='Exact whole-bank bytes and unchanged public/RAM addresses; no relabeling of private native routes as combined tests.',
        inherited_component_cases=dict(Z2=1728, CV3_scaling_exclusions=924, CV3_independent_ballistic_updates=288))
    (OUT/'traversal-composition-proof.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
