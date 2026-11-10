"""Zero-output current-ROM FF flower controller qualification in the CPU model.

The unchanged frozen first-mushroom route supplies a real menu/parser/pickup
continuation. This then uses ordinary pad inputs, complete native GameLoop and
normal NMI calls. No ROM, terrain, power, damage, actor, palette or position
grants are made. CPU logical-update evidence is not Mesen/cadence proof.
"""
from collections import Counter, deque
from contextlib import redirect_stdout
from hashlib import sha256
import argparse
import io
import json
from pathlib import Path
import traceback

import check_ff_all_mushrooms_current_1110 as A

W, N = A.W, A.W.N
FROZEN_ADAPTER = 'e122dc0dc793eeb7aa002389ea1112302f3cc008b19b77d38d75f695cdcc5f7e'


def flower(variant):
    assert sha256(Path(A.__file__).read_bytes()).hexdigest() == FROZEN_ADAPTER
    opening_log = io.StringIO()
    try:
        with redirect_stdout(opening_log):
            first, m = A.route(variant)
    except Exception:
        print(opening_log.getvalue(), flush=True)
        raise
    assert first['passed'] and first['transformation_ticks'] == 60
    b = m.bundle
    idle = W.address(b, 'IdleLoop')
    calls = Counter()
    tail = deque(maxlen=24)
    ticks, births = [], []
    collected = recovered = pending_collect = pending_tick = None
    collect_slot = 5
    launch = None
    retreat = False
    last_jump = -100
    jumped = set()
    points = {(3, 0xbb60): 'FfHostCollect', (3, 0xad65): 'FfPickup',
              (3, 0xbc40): 'FfHostPowerupTick', (3, 0xaabc): 'FfMovement',
              (3, 0xadd8): 'FfInjuryStart'}
    for name in ('PowerUpObjHandler', 'NrPickupCollision', 'HandlePowerUpCollision',
                 'KillPlayer', 'PlayerBGCollision'):
        if name in b['syms']:
            points[((W.location(b, name)-16)//8192 | 128, W.address(b, name))] = name

    def state():
        return dict(step=step, x=N.get(m, 'Player_X_Position')+256*N.get(m, 'Player_PageLoc'),
                    y=N.get(m, 'Player_Y_Position'), state=N.get(m, 'Player_State'),
                    engine=N.get(m, 'GameEngineSubroutine'), lives=N.get(m, 'NumberofLives'),
                    power=m[0x5fc5], earned=m[0x5fc6], charges=m[0x5fc7],
                    active=N.get(m, 'GuestPowerupActive'), age=N.get(m, 'GuestPowerupAge'),
                    timer=N.get(m, 'TimerControl'), hurt=m[0x5c07])

    def actors():
        return [dict(slot=i, flag=N.get(m, 'Enemy_Flag', i), id=N.get(m, 'Enemy_ID', i),
                     state=N.get(m, 'Enemy_State', i), kind=N.get(m, 'PowerUpType', i),
                     x=N.get(m, 'Enemy_X_Position', i)+256*N.get(m, 'Enemy_PageLoc', i),
                     y=N.get(m, 'Enemy_Y_Position', i)) for i in range(6)]

    def observe(c):
        nonlocal collected, pending_collect, pending_tick
        if pending_collect and (c.pc, c.sp) == pending_collect:
            if N.get(m, 'GuestPowerupActive') and m[0x5fc5] == 2:
                collected = dict(**state(), carry=bool(c.p & 1),
                                 sound=N.get(m, 'Square2SoundQueue'),
                                 erased_flag=N.get(m, 'Enemy_Flag', collect_slot),
                                 floaty=N.get(m, 'FloateyNum_Control', collect_slot))
                print(json.dumps(dict(event='flower_collected', variant=variant, result=collected)), flush=True)
            pending_collect = None
        if pending_tick and (c.pc, c.sp) == pending_tick:
            ticks[-1]['returned'] = state()
            pending_tick = None
        if c.pc < 0x8000:
            return
        point = (m.rawtags[(c.pc-0x8000)//8192], c.pc)
        label = points.get(point)
        if not label:
            return
        calls[label] += 1
        if label in ('KillPlayer', 'FfInjuryStart'):
            raise AssertionError(('native injury/death before flower qualification', label, state(), actors()))
        ret = (m[0x100+((c.sp+1)&255)]+256*m[0x100+((c.sp+2)&255)]+1, c.sp+2)
        if label == 'FfHostCollect':
            pending_collect = ret
        elif label == 'FfHostPowerupTick' and N.get(m, 'GuestPowerupActive'):
            ticks.append(state())
            pending_tick = ret

    def solid(wx, y):
        if y < 32 or y >= 240:
            return False
        at = 0x300 + ((wx >> 8) & 1)*208 + ((y-32)//16)*16 + ((wx >> 4)&15)
        return bool(m[W.address(b, 'MTileAttribute')+m[at]] & 1)

    try:
        for step in range(1100):
            s = state()
            assert N.get(m, 'SelectedCharacter') == 22 and N.get(m, 'FfVariant') == variant
            assert N.get(m, 'CheatStartLevel') == N.get(m, 'CheatInvincible') == 0
            assert s['lives'] == 2
            assert (N.get(m, 'WorldNumber'), N.get(m, 'LevelNumber'), N.get(m, 'AreaAddrsLOffset')) == (0, 0, 5)
            if collected and s['engine'] == 8:
                recovered = recovered or s
                assert (s['power'], s['earned'], s['charges']) == (2, 2, 3 if variant == 1 else 0)
                assert s['active'] == s['timer'] == 0
                if s['x'] >= recovered['x']+16:
                    break
                pad = 1
            elif s['engine'] == 9:
                pad = 0
            else:
                assert s['engine'] == 8 and (s['power'], s['earned']) == (1, 1), s
                item = next((a for a in actors() if a['flag'] == 1 and a['id'] == 46), None)
                if item:
                    collect_slot = item['slot']
                    assert item['kind'] == 1, item
                    if not births:
                        births.append(dict(player=s, actor=item))
                        print(json.dumps(dict(event='natural_flower', variant=variant, result=births[-1])), flush=True)
                    if step-births[0]['player']['step'] < 40:
                        # Let the native emerging item mature and the genuine
                        # lower Goomba walk clear before backing up to jump.
                        pad = 0
                    elif launch is None:
                        if s['x'] > item['x']-48:
                            pad = 2
                        elif s['state'] == 0:
                            launch = step
                            pad = 129
                        else:
                            pad = 0
                    else:
                        pad = 1 | (128 if step-launch < 23 else 0)
                        if step-launch > 75 and s['state'] == 0:
                            launch = None
                elif s['x'] < 1224:
                    pad = 1
                    if s['state'] == 0 and step-last_jump > 35:
                        obstacle = any(left not in jumped and left-50 <= s['x'] < left-3
                                       for left in (448, 608, 736, 912))
                        if obstacle:
                            jumped.add(next(left for left in (448, 608, 736, 912)
                                            if left not in jumped and left-50 <= s['x'] < left-3))
                        pit = 1074 <= s['x'] < 1136
                        ledge = 1150 <= s['x'] < 1200 and s['y'] >= 160
                        if obstacle or pit or ledge or (s['x'] > 970 and solid(s['x']+25, s['y']+24)):
                            pad |= 128
                            last_jump = step
                else:
                    gap = 1242-s['x']
                    pad = int(gap > 2) | (2 if gap < -2 else 0)
                    if abs(gap) <= 2 and s['state'] == 0 and step-last_jump > 35:
                        pad |= 128
                        last_jump = step
                if not item:
                    # Actual parsed cell1248/Y144 contains the flower. A
                    # character atop that row must first step off underneath.
                    if s['x'] >= 1224 and s['state'] == 0 and s['y'] <= 112:
                        retreat = True
                    if retreat:
                        pad = 2 if s['x'] > 1212 else 0
                        if s['x'] <= 1212 and s['state'] == 0 and s['y'] >= 160:
                            retreat = False
                    elif s['x'] > 1140 and s['state'] == 0 and step-last_jump > 35:
                        near = any(a['flag'] == 1 and a['id'] == 6 and a['state'] < 32 and
                                   12 <= a['x']-s['x'] <= 45 and abs(a['y']-s['y']-8) < 24
                                   for a in actors())
                        if near:
                            pad |= 128
                            last_jump = step
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
                print(json.dumps(dict(event='flower_progress', variant=variant, state=state())), flush=True)
            assert not m.blocked
        else:
            raise AssertionError(('controller bound', state(), actors()))
        assert births and collected and recovered
        assert collected['carry'] and collected['sound'] == 32 and collected['floaty'] == 6 and collected['erased_flag'] == 0
        assert len(ticks) == 60 and [s['age'] for s in ticks] == list(range(60))
        assert all(s['engine'] == 9 and s['active'] == 1 for s in ticks)
        assert all(s['returned']['engine'] == 9 and s['returned']['active'] == 1 and s['returned']['timer'] == 255 for s in ticks[:-1])
        assert (ticks[-1]['returned']['engine'], ticks[-1]['returned']['active'], ticks[-1]['returned']['timer']) == (8, 0, 0)
        assert N.get(m, 'PlayerOutlinesOff') == 0
        palette = [0x16, 0x30, 0x36] if variant < 2 else [0x28, 0x18, 0x21]
        assert list(m.vram[0x3f11:0x3f14]) == palette
        assert any(m[0x200+4*i] < 240 for i in range(64))
        assert calls['PlayerBGCollision'] == calls['FfMovement'] > 100
        assert sha256(W.ROM.read_bytes()).hexdigest() == W.PIN
        result = dict(passed=True, ROM_sha256=W.PIN, variant=variant, class_name=A.CLASSES[variant],
                      CPU_controller_only=True, Mesen_run=False, first_mushroom_pass=first['passed'],
                      flower=births[0], collected=collected, transformation_ticks=len(ticks),
                      recovered=recovered, terminal=state(), calls=dict(calls),
                      palette=palette, outlines_off=N.get(m, 'PlayerOutlinesOff'),
                      OAM_shadow_visible_records=sum(m[0x200+4*i] < 240 for i in range(64)),
                      scope='Natural first mushroom then earned flower, actual native collector/60 FF ticks/tier2/resumed movement. Logical CPU controller/NMI model; no full-stage or Mesen qualification.')
        return result, m
    except Exception:
        print(json.dumps(dict(passed=False, ROM_sha256=W.PIN, variant=variant,
                              flower=births, collected=collected, ticks=len(ticks),
                              terminal=state(), actors=actors(), trace=list(tail), calls=dict(calls))), flush=True)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--variant', type=int, choices=range(4))
    args = parser.parse_args()
    results = []
    for variant in range(4) if args.variant is None else (args.variant,):
        result, _ = flower(variant)
        results.append(result)
        print(json.dumps(dict(event='class_flower_pass', result=result)), flush=True)
    print(json.dumps(dict(passed=True, ROM_sha256=W.PIN, CPU_controller_only=True,
                          Mesen_run=False, ROM_written=False, output_files=0,
                          results=results, full_stage=False, earned_attack_use=False)), flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc()
        raise SystemExit(1)
