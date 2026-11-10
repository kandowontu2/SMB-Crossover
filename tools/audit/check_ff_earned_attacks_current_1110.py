"""Natural earned-flower continuation into a real FF upgraded attack receipt.

Prints CPU controller evidence only; no files, emulator, ROM, actor, terrain,
position, palette, power or damage grants. The first successful actual native
damage callback is required, with class-specific earned tier2 damage values.
"""
from collections import Counter, deque
from contextlib import redirect_stdout
from hashlib import sha256
import argparse
import io
import json
from pathlib import Path
import traceback

import check_ff_flowers_current_1110 as F

W, N = F.W, F.N
FLOWER_SHA = 'e990661e7b9fe754dede187b39dd0dfda6367f051cdd701b01ddc9b03aad50ec'
DAMAGE = (150, 50, 150, 25)


def attack(variant):
    assert sha256(Path(F.__file__).read_bytes()).hexdigest() == FLOWER_SHA
    log = io.StringIO()
    try:
        with redirect_stdout(log):
            flower, m = F.flower(variant)
    except Exception:
        print(log.getvalue(), flush=True)
        raise
    assert flower['passed'] and flower['transformation_ticks'] == 60
    b = m.bundle
    idle = W.address(b, 'IdleLoop')
    calls = Counter()
    tail = deque(maxlen=24)
    hit = pending = committed = None
    jumped = set()
    step = -1

    def state():
        return dict(step=step, x=N.get(m, 'Player_X_Position')+256*N.get(m, 'Player_PageLoc'),
                    y=N.get(m, 'Player_Y_Position'), state=N.get(m, 'Player_State'),
                    engine=N.get(m, 'GameEngineSubroutine'), lives=N.get(m, 'NumberofLives'),
                    facing=N.get(m, 'PlayerFacingDir'), power=m[0x5fc5], earned=m[0x5fc6],
                    charges=m[0x5fc7], action=m[0x5c03], age=m[0x5c04], spell=m[0x5c05])

    def actor(slot):
        return dict(slot=slot, flag=N.get(m, 'Enemy_Flag', slot), id=N.get(m, 'Enemy_ID', slot),
                    state=N.get(m, 'Enemy_State', slot),
                    x=N.get(m, 'Enemy_X_Position', slot)+256*N.get(m, 'Enemy_PageLoc', slot),
                    y=N.get(m, 'Enemy_Y_Position', slot),
                    HP=N.get(m, 'MmEnemyHealthLo', slot)+256*N.get(m, 'MmEnemyHealthHi', slot))

    def actors():
        return [actor(i) for i in range(6)]

    def observe(c):
        nonlocal pending, hit
        if pending and (c.pc, c.sp) == pending[0]:
            before = pending[1]
            if c.p & 1:
                hit = dict(before=before, after=dict(player=state(), actor=actor(before['actor']['slot'])))
            pending = None
        if c.pc < 0x8000:
            return
        point = (m.rawtags[(c.pc-0x8000)//8192], c.pc)
        if point == (3, 0xb7ae):
            calls['FfHostDamage'] += 1
            slot = c.x
            a = actor(slot)
            attack_slot = m[0x5c0f]
            projectile = None
            if attack_slot != 255:
                assert attack_slot in (0, 12, 24)
                base = 0x5c1c+attack_slot
                projectile = dict(kind=m[base], tier=m[base+10])
            before = dict(player=state(), actor=a, damage=m[0x5c15],
                          attack_slot=attack_slot, projectile=projectile)
            assert before['damage'] == DAMAGE[variant], before
            assert a['flag'] == 1 and a['id'] in (0, 3, 6) and a['state'] < 2
            if variant == 2:
                assert projectile == dict(kind=1, tier=2), before
            else:
                assert attack_slot == 255 and before['player']['action'] == 1, before
            pending = ((m[0x100+((c.sp+1)&255)]+256*m[0x100+((c.sp+2)&255)]+1, c.sp+2), before)
        elif point == (3, 0xadd8):
            raise AssertionError(('natural injury before qualified upgraded hit', state(), actors()))

    try:
        print(json.dumps(dict(event='attack_start', variant=variant, player=state(), actors=actors())), flush=True)
        for step in range(900):
            s = state()
            assert N.get(m, 'SelectedCharacter') == 22 and N.get(m, 'FfVariant') == variant
            assert N.get(m, 'CheatStartLevel') == N.get(m, 'CheatInvincible') == 0
            assert (s['power'], s['earned'], s['lives'], s['engine']) == (2, 2, 2, 8)
            if hit:
                break
            aligned = [a for a in actors() if a['flag'] == 1 and a['id'] in (0, 3, 6) and
                       a['state'] < 2 and abs(a['y']-s['y']-8) < 20 and
                       abs(a['x']-s['x']) < 100]
            pad = 1
            if committed is not None:
                pad = 1 if committed['facing'] == 1 else 2
                if step-committed['step'] > 75 and s['action'] == 0:
                    committed = None
            elif aligned and (variant != 2 or s['state'] == 0):
                a = min(aligned, key=lambda a: abs(a['x']-s['x']))
                facing = 1 if a['x'] >= s['x'] else 2
                gap = abs(a['x']-s['x'])
                pad = facing
                distance = 70 if variant == 2 else 26
                if gap <= distance and s['facing'] == facing:
                    pad |= 64
                    committed = dict(step=step, facing=facing, player=s, actor=a)
            elif s['state'] == 0:
                for left, right in ((1376, 1424), (2448, 2480)):
                    if left not in jumped and left-30 <= s['x'] < right:
                        pad |= 128
                        jumped.add(left)
                        break
            m.controller_pad = pad
            W.clear_logs(m)
            N.consume(m)
            c = N.NesMPU(memory=m, pc=idle)
            c.sp, c.p = 255, 0x31
            c.stPushWord(0xe33b)
            for _ in range(250000):
                if (c.pc, c.sp) == (idle+12, 252):
                    break
                observe(c)
                assert m[c.pc], ('BRK', step, hex(c.pc), m.rawtags)
                c.step()
            else:
                raise AssertionError(('instruction bound', step, hex(c.pc)))
            tail.append(dict(pad=pad, **state()))
            if step % 100 == 0:
                print(json.dumps(dict(event='attack_progress', variant=variant, player=state(), actors=actors())), flush=True)
            assert not m.blocked
        else:
            raise AssertionError(('attack controller bound', state(), actors()))
        assert hit and committed
        before, after = hit['before']['actor'], hit['after']['actor']
        defeated = bool(after['state'] & 32) or after['flag'] == 0
        assert defeated or after['HP'] > 0
        assert not before['HP'] or after['HP'] < before['HP']
        assert N.get(m, 'PlayerOutlinesOff') == 0
        assert sha256(W.ROM.read_bytes()).hexdigest() == W.PIN
        return dict(passed=True, ROM_sha256=W.PIN, variant=variant, class_name=F.A.CLASSES[variant],
                    CPU_controller_only=True, Mesen_run=False, output_files=0,
                    earned_mushroom_and_flower=True, issued=committed, native_damage=hit,
                    native_defeated=defeated, terminal=state(), calls=dict(calls),
                    scope='Actual earned tier2 original-input melee or Black Fire against a naturally streamed native enemy; genuine FF damage callback accepted class damage and native HP/defeat changed. Logical CPU model, not full-stage/Mesen or every attack.')
    except Exception:
        print(json.dumps(dict(passed=False, ROM_sha256=W.PIN, variant=variant,
                              terminal=state(), actors=actors(), issued=committed,
                              hit=hit, calls=dict(calls), trace=list(tail))), flush=True)
        raise


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--variant', type=int, choices=range(4))
    args = p.parse_args()
    results = []
    for variant in range(4) if args.variant is None else (args.variant,):
        result = attack(variant)
        results.append(result)
        print(json.dumps(dict(event='earned_attack_pass', result=result)), flush=True)
    print(json.dumps(dict(passed=True, ROM_sha256=W.PIN, results=results,
                          CPU_controller_only=True, Mesen_run=False, output_files=0)), flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc()
        raise SystemExit(1)
