"""Actual earned Black Mage Up+B/Down+B on frozen FFv2; stdout only.

The frozen natural flower and enemy controller is adapted only at its input,
expected original spell kind and damage assertion. No emulated state grant.
"""
from collections import Counter
from contextlib import redirect_stdout
from hashlib import sha256
import inspect
import io
import json
from pathlib import Path
from unittest.mock import patch

import check_ff_earned_attacks_current_1110 as A
import check_ff_head_corner_1110_v2 as Fix

W, N = A.W, A.N
PIN = '96e09ab1b67a7c75b89d49219e8e529582b9a05b7dd82dd3cd570fdb239212bd'
ATTACK_PIN = 'dd8015682993e4a13190e9a9e200a1ae4b227767172b5ad6036831447110b44e'
FIX_PIN = 'e508771dbac9dfb42c33ca41b3d3af4c07f98f81fd2f742205f6e4a3ce690665'
SOURCE_PIN = '6e58b2460852e808031f64ce733545ca0bffc78da05e5b68860d929e98c7f0cd'


def run_spell(kind, direction, damage):
    text = inspect.getsource(A.attack)
    changes = [('pad |= 64', f'pad |= 64 | {direction}'),
               ('projectile == dict(kind=1, tier=2)', f'projectile == dict(kind={kind}, tier=2)')]
    for old, new in changes:
        assert text.count(old) == 1
        text = text.replace(old, new)
    namespace = dict(A.__dict__, DAMAGE=(150, 50, damage, 25))
    exec(compile(text, '<frozen-earned-attack-controller-input-adapter>', 'exec'), namespace)
    ticks, allocations = [], []
    Base = N.NesMPU
    class ObservedMPU(Base):
        def step(self):
            m = self.memory
            if self.pc >= 0x8000 and m.rawtags[(self.pc-0x8000)//8192] == 3:
                if self.pc == 0xae93 and m[0x5c05] == kind and m[0x5c03] in (2, 3):
                    ticks.append(dict(action=m[0x5c03], age=m[0x5c04], spell=m[0x5c05]))
                if self.pc == 0xaf8d and m[0x5c05] == kind:
                    allocations.append(dict(action=m[0x5c03], age=m[0x5c04], spell=m[0x5c05]))
            return super().step()
    log = io.StringIO()
    try:
        with patch.object(N, 'NesMPU', ObservedMPU), redirect_stdout(log):
            result = namespace['attack'](2)
    except Exception:
        print(log.getvalue(), flush=True)
        print(json.dumps(dict(kind=kind, ticks=ticks, allocations=allocations)), flush=True)
        raise
    assert result['passed'] and result['native_defeated']
    assert result['native_damage']['before']['projectile'] == dict(kind=kind, tier=2)
    assert result['native_damage']['before']['damage'] == damage
    assert allocations and all(t['spell'] == kind for t in ticks)
    prep = [t['age'] for t in ticks if t['action'] == 2]
    assert prep == list(range(30)), (kind, prep, ticks, allocations)
    return dict(spell='Bolt' if kind == 2 else 'Ice', original_input='Up+B' if direction == 8 else 'Down+B',
                passed=True, earned_tier=2, preparation_updates=len(prep),
                action_ticks=ticks, allocations=allocations,
                issued=result['issued'], native_damage=result['native_damage'],
                native_defeated=result['native_defeated'], terminal=result['terminal'],
                calls=result['calls'])


def main():
    for path, pin in ((Path(A.__file__), ATTACK_PIN), (Path(Fix.__file__), FIX_PIN), (Fix.SOURCE, SOURCE_PIN)):
        assert sha256(path.read_bytes()).hexdigest() == pin
    original = W.ROM.read_bytes()
    assert sha256(original).hexdigest() == W.PIN
    image, kernel, cookie, *_ = Fix.proposal(original)
    assert sha256(image).hexdigest() == PIN
    class MemoryImage:
        def read_bytes(self): return image
    results = []
    with patch.object(W, 'ROM', MemoryImage()), patch.object(W, 'PIN', PIN):
        for kind, direction, damage in ((2, 8, 200), (3, 4, 150)):
            row = run_spell(kind, direction, damage)
            results.append(row)
            print(json.dumps(dict(event='earned_original_spell_pass', result=row)), flush=True)
    assert sha256(W.ROM.read_bytes()).hexdigest() == W.PIN == sha256(original).hexdigest()
    print(json.dumps(dict(passed=True, source_CPU_only=True, Mesen_run=False, ROM_written=False,
        output_files=0, candidate_SHA256=PIN, kernel_SHA256=sha256(kernel).hexdigest(),
        cookie=cookie.hex(), frozen_attack_SHA256=ATTACK_PIN, source_SHA256=SOURCE_PIN,
        proposal_checker_SHA256=FIX_PIN, results=results,
        scope='Two independent genuine menu/controller mushroom and flower routes, then original Up+B Bolt/Down+B Ice preparation and accepted native tier2 damage against a naturally streamed Goomba. Logical CPU only; no physical cadence or complete spell lifetime claim.')), flush=True)


if __name__ == '__main__': main()
