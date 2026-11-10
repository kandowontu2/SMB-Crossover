"""Continue an actually earned mushroom into natural damage and White Heal.

Uses real current GameLoop/parser/controller/NMI execution, with no damage,
position, terrain, power or actor grants. Prints one aggregate; writes no files.
This is CPU-model evidence, not Mesen, cadence or a complete stage clear.
"""
from collections import Counter, deque
from hashlib import sha256
import json
from pathlib import Path
import traceback

import check_ff_all_mushrooms_current_1110 as A

W, N = A.W, A.W.N
ADAPTER_SHA = 'e122dc0dc793eeb7aa002389ea1112302f3cc008b19b77d38d75f695cdcc5f7e'


def main():
    assert sha256(Path(A.__file__).read_bytes()).hexdigest() == ADAPTER_SHA
    pickup, m = A.route(1)
    assert pickup['passed'] and pickup['transformation_ticks'] == 60
    b = m.bundle
    idle = W.address(b, 'IdleLoop')
    points = {(3, 0xadd8): 'FfInjuryStart', (3, 0xae93): 'FfActionTick'}
    for name in ('PlayerEnemyCollision', 'KillPlayer', 'ForceInjury'):
        if name in b['syms']:
            points[((W.location(b, name)-16)//8192 | 128, W.address(b, name))] = name
    calls = Counter()
    tail = deque(maxlen=24)
    injury = healed = pending = issued = None
    action_ages = []
    jumped = set()
    ingress = None
    seek_contact = False

    def state():
        return dict(step=step, x=N.get(m, 'Player_X_Position')+256*N.get(m, 'Player_PageLoc'),
                    y=N.get(m, 'Player_Y_Position'), state=N.get(m, 'Player_State'),
                    engine=N.get(m, 'GameEngineSubroutine'), lives=N.get(m, 'NumberofLives'),
                    power=m[0x5fc5], earned=m[0x5fc6], charges=m[0x5fc7],
                    action=m[0x5c03], age=m[0x5c04], spell=m[0x5c05],
                    hurt=m[0x5c07], knockback=m[0x5c08],
                    input=N.get(m, 'SavedJoypadBits'), sound=N.get(m, 'Square2SoundQueue'))

    def actors():
        return [dict(slot=i, flag=N.get(m, 'Enemy_Flag', i), id=N.get(m, 'Enemy_ID', i),
                     state=N.get(m, 'Enemy_State', i),
                     x=N.get(m, 'Enemy_X_Position', i)+256*N.get(m, 'Enemy_PageLoc', i),
                     y=N.get(m, 'Enemy_Y_Position', i)) for i in range(6)]

    def observe(c):
        nonlocal pending, injury, healed, ingress
        if pending and (c.pc, c.sp) == pending[0]:
            label, before = pending[1:]
            after = state()
            if label == 'FfInjuryStart' and before['power'] == 1 and after['power'] == 0:
                assert injury is None
                injury = dict(before=before, after=after, actors=ingress)
                print(json.dumps(dict(event='natural_injury', evidence=injury)), flush=True)
            elif label == 'FfActionTick' and before['charges'] == 1 and after['charges'] == 0:
                assert healed is None
                healed = dict(before=before, after=after)
                print(json.dumps(dict(event='earned_heal', evidence=healed)), flush=True)
            pending = None
        if c.pc < 0x8000:
            return
        tag = m.rawtags[(c.pc-0x8000)//8192]
        label = points.get((tag, c.pc))
        if not label:
            return
        calls[label] += 1
        if label == 'KillPlayer':
            raise AssertionError(('native death', state(), actors()))
        if label in ('FfInjuryStart', 'FfActionTick'):
            before = state()
            pending = ((m[0x100+((c.sp+1)&255)]+256*m[0x100+((c.sp+2)&255)]+1, c.sp+2), label, before)
            if label == 'FfInjuryStart':
                ingress = actors()
            elif before['action'] == 2 and before['spell'] == 5:
                action_ages.append(before['age'])

    try:
        for step in range(1200):
            s = state()
            assert N.get(m, 'SelectedCharacter') == 22 and N.get(m, 'FfVariant') == 1
            assert N.get(m, 'CheatStartLevel') == N.get(m, 'CheatInvincible') == 0
            assert s['lives'] == 2 and s['earned'] == 1
            assert s['engine'] == 8
            if healed and s['action'] == 0:
                break
            if injury:
                pad = 0
                if issued is None and s['knockback'] == 0:
                    issued = s
                    pad = 0x48
            else:
                pad = 1
                victims = [a for a in actors() if a['flag'] == 1 and a['id'] == 6 and
                           a['state'] < 32 and a['y'] >= 172]
                if s['x'] >= 672 and victims:
                    seek_contact = True
                if seek_contact and victims:
                    # Stop beyond the second cap, settle on native ground,
                    # then walk into an actual nearby Goomba. No injury grants.
                    pad = 0
                    if s['state'] == 0 and s['y'] >= 170:
                        nearest = min(victims, key=lambda a: abs(a['x']-s['x']))
                        pad = 1 if nearest['x'] >= s['x'] else 2
                elif s['state'] == 0:
                    for left in (448, 608, 736, 912):
                        if left not in jumped and left-50 <= s['x'] < left-3:
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
                print(json.dumps(dict(event='heal_progress', state=state(), actors=actors())), flush=True)
            assert not m.blocked
        else:
            raise AssertionError(('controller bound', state(), actors()))
        assert injury and healed and issued
        assert injury['after']['earned'] == injury['after']['charges'] == 1
        assert injury['after']['hurt'] == 90 and injury['after']['knockback'] == 12
        assert (healed['after']['power'], healed['after']['earned'], healed['after']['charges']) == (1, 1, 0)
        assert healed['after']['sound'] == 0x20
        assert action_ages == list(range(30)), action_ages
        assert N.get(m, 'PlayerOutlinesOff') == 0
        assert list(m.vram[0x3f11:0x3f14]) == [0x16, 0x30, 0x36]
        assert sha256(W.ROM.read_bytes()).hexdigest() == W.PIN
        print(json.dumps(dict(passed=True, ROM_sha256=W.PIN, CPU_controller_only=True,
                              Mesen_run=False, ROM_written=False, output_files=0,
                              first_mushroom_pass=pickup['passed'], natural_injury=injury,
                              issued=issued, preparation_updates=len(action_ages), healed=healed,
                              terminal=state(), calls=dict(calls),
                              scope='Natural earned mushroom/protection loss to actual native enemy contact, then original-input Up+B spends one earned charge and restores exactly one tier after30 FF preparation updates. White Heal is an authored crossover ability. No full-stage or Mesen claim.')), flush=True)
    except Exception:
        print(json.dumps(dict(passed=False, ROM_sha256=W.PIN, natural_injury=injury,
                              issued=issued, healed=healed, preparation_ages=action_ages,
                              terminal=state(), trace=list(tail), calls=dict(calls))), flush=True)
        raise


if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc()
        raise SystemExit(1)
