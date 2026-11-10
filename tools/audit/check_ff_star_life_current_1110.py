"""Natural FF hidden-1UP and Star routes on current c10; stdout evidence only.

Frozen earned-mushroom/flower fixtures supply actual cold-menu continuations.
Only controller inputs and the established logical NMI scheduler are applied.
No actor/terrain/stat/position grants, ROM writes or emulator runs are made.
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

A, W, N = F.A, F.W, F.N
PINS = {'check_ff_all_mushrooms_current_1110.py':
        'e122dc0dc793eeb7aa002389ea1112302f3cc008b19b77d38d75f695cdcc5f7e',
        'check_ff_flowers_current_1110.py':
        'e990661e7b9fe754dede187b39dd0dfda6367f051cdd701b01ddc9b03aad50ec'}


def authored(b):
    raw = W.ROM.read_bytes()
    at = W.location(b, 'L_GroundArea6')
    page, records = 0, []
    kinds = ('powerup', 'coin', 'hidden_coin', 'hidden_1up', 'brick_powerup',
             'vine', 'star', 'brick_coins', 'brick_1up', 'waterpipe', 'empty', 'spring')
    for off in range(2, 250, 2):
        a, c = raw[at+off:at+off+2]
        if a == 253:
            break
        if c & 128:
            page += 1
        row = a & 15
        if row == 13 and not c & 64:
            page = c & 31
        elif row < 12 and not c & 112:
            records.append(dict(offset=off, raw=[a, c], x=page*256+(a >> 4)*16,
                                y=32+row*16, kind=kinds[c & 15]))
    life = next(r for r in records if r['kind'] == 'hidden_1up')
    star = next(r for r in records if r['kind'] == 'star')
    assert life == dict(offset=20, raw=[6, 131], x=1024, y=128, kind='hidden_1up')
    assert star == dict(offset=40, raw=[87, 6], x=1616, y=144, kind='star')
    return dict(file_offset=at, life=life, star=star)


def route(variant, kind):
    for name, pin in PINS.items():
        assert sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() == pin
    log = io.StringIO()
    try:
        with redirect_stdout(log):
            opening, m = (F.flower(variant) if kind == 'star' else A.route(variant))
    except Exception:
        print(log.getvalue(), flush=True)
        raise
    assert opening['passed']
    b, step = m.bundle, -1
    block = authored(b)[kind]
    gear = (2, 2, 3 if variant == 1 else 0) if kind == 'star' else (1, 1, int(variant == 1))
    item_type = 2 if kind == 'star' else 3
    idle = W.address(b, 'IdleLoop')
    points = {(3, 0xbb60): 'FfHostCollect', (3, 0xad65): 'FfPickup',
              (3, 0xbc1d): 'FfHostBeginFreeze', (3, 0xaabc): 'FfMovement',
              (3, 0xadd8): 'FfInjuryStart'}
    for name in ('PowerUpObjHandler', 'NrPickupCollision', 'HandlePowerUpCollision',
                 'KillPlayer', 'PlayerBGCollision', 'FloateyNumbersCore',
                 'PlayerEnemyCollision', 'EColl', 'ShellOrBlockDefeat', 'GetAreaMusic'):
        if name in b['syms']:
            points[((W.location(b, name)-16)//8192 | 128, W.address(b, name))] = name
    life_opcode = (b'\xee'+W.address(b, 'NumberofLives').to_bytes(2, 'little')+
                   b'\xa9\x40\x8d'+W.address(b, 'Square2SoundQueue').to_bytes(2, 'little'))
    calls, tail = Counter(), deque(maxlen=24)
    born = collected = pending_collect = pending_life = award = None
    collision = protected_hit = pending_defeat = expiry = None
    pending_music = music_restored = None
    palettes, timer_values, timer_changes = set(), set(), []
    jumped, last_jump = set(), -100
    collect_step = None
    step = -1

    def state():
        return dict(step=step, x=N.get(m, 'Player_X_Position')+256*N.get(m, 'Player_PageLoc'),
                    y=N.get(m, 'Player_Y_Position'), state=N.get(m, 'Player_State'),
                    engine=N.get(m, 'GameEngineSubroutine'), lives=N.get(m, 'NumberofLives'),
                    power=m[0x5fc5], earned=m[0x5fc6], charges=m[0x5fc7],
                    active=N.get(m, 'GuestPowerupActive'), timer=N.get(m, 'TimerControl'),
                    star=N.get(m, 'StarInvincibleTimer'),
                    interval=N.get(m, 'IntervalTimerControl'), frame=N.get(m, 'FrameCounter'),
                    attr=N.get(m, 'Player_SprAttrib'), hidden=N.get(m, 'Hidden1UpFlag'),
                    input=N.get(m, 'SavedJoypadBits'), action=m[0x5c03])

    def actor(slot):
        return dict(slot=slot, flag=N.get(m, 'Enemy_Flag', slot), id=N.get(m, 'Enemy_ID', slot),
                    state=N.get(m, 'Enemy_State', slot), kind=N.get(m, 'PowerUpType', slot),
                    x=N.get(m, 'Enemy_X_Position', slot)+256*N.get(m, 'Enemy_PageLoc', slot),
                    y=N.get(m, 'Enemy_Y_Position', slot),
                    floaty=N.get(m, 'FloateyNum_Control', slot),
                    floaty_timer=N.get(m, 'FloateyNum_Timer', slot))

    def actors():
        return [actor(i) for i in range(6)]

    def ret(c):
        return ((m[0x100+((c.sp+1)&255)]+256*m[0x100+((c.sp+2)&255)]+1)&65535,
                (c.sp+2)&255)

    def observe(c):
        nonlocal pending_collect, collected, pending_life, award, collision
        nonlocal protected_hit, pending_defeat
        nonlocal pending_music, music_restored
        if pending_collect and (c.pc, c.sp) == pending_collect[0]:
            before = pending_collect[1]
            assert c.p & 1
            collected = dict(before=before, after=state(), actor=actor(before['actor']['slot']),
                             sound=N.get(m, 'Square2SoundQueue'), music=N.get(m, 'AreaMusicQueue'))
            assert collected['actor']['flag'] == 0 and collected['sound'] == 32
            assert collected['actor']['floaty'] == (6 if kind == 'star' else 11)
            assert not collected['after']['active'] and not collected['after']['timer']
            assert tuple(collected['after'][k] for k in ('power', 'earned', 'charges')) == gear
            if kind == 'star':
                assert collected['after']['star'] == 35 and collected['music'] == 64
            else:
                assert collected['after']['lives'] == 2 and collected['after']['star'] == 0
            print(json.dumps(dict(event='natural_collect', variant=variant, kind=kind,
                                  evidence=collected)), flush=True)
            pending_collect = None
        if pending_life and (c.pc, c.sp) == pending_life[0]:
            award = dict(before=pending_life[1], after=state(),
                         sound=N.get(m, 'Square2SoundQueue'))
            assert award['before']['player']['lives'] == 2 and award['after']['lives'] == 3
            assert award['sound'] == 64
            pending_life = None
        if pending_music and (c.pc, c.sp) == pending_music[0]:
            music_restored = dict(before=pending_music[1], after=state(),
                                  music=N.get(m, 'AreaMusicQueue'))
            assert music_restored['before']['star'] == 4 and music_restored['before']['interval'] == 0
            assert music_restored['music'] == 1
            pending_music = None
        if pending_defeat and (c.pc, c.sp) == pending_defeat[0]:
            protected_hit = dict(before=pending_defeat[1], after=state(),
                                 actor=actor(pending_defeat[1]['actor']['slot']))
            assert protected_hit['actor']['state'] & 32
            assert protected_hit['before']['player']['input'] in (1, 2)
            assert protected_hit['before']['player']['action'] == 0
            assert protected_hit['before']['player']['state'] == 0
            assert tuple(protected_hit['after'][k] for k in ('power', 'earned', 'charges')) == gear
            print(json.dumps(dict(event='star_native_enemy_defeat', variant=variant,
                                  evidence=protected_hit)), flush=True)
            pending_defeat = None
        if collision and (c.pc, c.sp) == collision[0]:
            collision = None
        if c.pc < 0x8000:
            return
        if kind == 'life' and collected and not award and bytes(m[c.pc:c.pc+8]) == life_opcode:
            # Witness the executing native INC lives / LDA ExtraLife / STA
            # sound sequence directly; retained debug routine names do not
            # identify every current native-core copy.
            a = actor(c.x)
            assert a['floaty'] == 11 and a['floaty_timer'] == 42
            pending_life = ((c.pc+8, c.sp), dict(player=state(), actor=a,
                            PC=c.pc, tag=m.rawtags[(c.pc-0x8000)//8192], opcode=life_opcode.hex()))
        label = points.get((m.rawtags[(c.pc-0x8000)//8192], c.pc))
        if not label:
            return
        calls[label] += 1
        if label in ('KillPlayer', 'FfInjuryStart', 'FfPickup', 'FfHostBeginFreeze'):
            raise AssertionError(('unexpected native damage/tier/freeze', label, state(), actors()))
        if label == 'FfHostCollect':
            a = actor(c.x)
            assert a['id'] == 46 and a['kind'] == item_type and a['state'] & 128
            pending_collect = (ret(c), dict(player=state(), actor=a))
        elif label == 'PlayerEnemyCollision':
            collision = (ret(c), dict(player=state(), actor=actor(c.x)))
        elif label == 'GetAreaMusic' and kind == 'star' and collected:
            pending_music = (ret(c), state())
        elif label == 'ShellOrBlockDefeat' and kind == 'star' and collected and not protected_hit:
            if collision and N.get(m, 'StarInvincibleTimer'):
                a = actor(c.x)
                assert a['flag'] == 1 and a['id'] != 46 and a['state'] < 32
                pending_defeat = (ret(c), dict(player=state(), actor=a,
                                             collision_ingress=collision[1]))

    try:
        print(json.dumps(dict(event='start', variant=variant, kind=kind,
                              authored=authored(b), player=state(), actors=actors())), flush=True)
        for step in range(1800):
            s = state()
            assert N.get(m, 'SelectedCharacter') == 22 and N.get(m, 'FfVariant') == variant
            assert N.get(m, 'CheatStartLevel') == N.get(m, 'CheatInvincible') == 0
            assert (N.get(m, 'WorldNumber'), N.get(m, 'LevelNumber')) == (0, 0)
            assert tuple(s[k] for k in ('power', 'earned', 'charges')) == gear
            assert s['engine'] == 8 and not s['active'] and not s['timer']
            assert s['lives'] == (3 if award else 2)
            assert N.get(m, 'PlayerOutlinesOff') == 0
            item = next((a for a in actors() if a['flag'] == 1 and a['id'] == 46), None)
            if item and born is None:
                assert item['kind'] == item_type
                assert item['x'] == block['x'] and block['y']-10 <= item['y'] <= block['y']-8
                assert kind != 'life' or s['hidden'] == 0
                born = dict(player=s, actor=item)
                print(json.dumps(dict(event='natural_birth', variant=variant, kind=kind,
                                      evidence=born)), flush=True)
            pad = 0
            if collected:
                collect_step = s['step'] if collect_step is None else collect_step
                if kind == 'life':
                    if award and step-collect_step >= 12:
                        break
                else:
                    timer_values.add(s['star'])
                    palettes.add(tuple(m.vram[0x3f11:0x3f14]))
                    if not timer_changes or timer_changes[-1]['star'] != s['star']:
                        timer_changes.append(dict(step=step, star=s['star'], interval=s['interval']))
                    if not s['star']:
                        expiry = expiry or s
                        if step-expiry['step'] >= 3:
                            break
                    elif not protected_hit:
                        # Seek an actual streamed enemy on this long native floor.
                        victims = [a for a in actors() if a['flag'] == 1 and a['id'] in (0, 3, 6)
                                   and a['state'] < 2 and abs(a['x']-s['x']) < 200]
                        if victims:
                            nearest = min(victims, key=lambda a: abs(a['x']-s['x']))
                            pad = 1 if nearest['x'] >= s['x'] else 2
                        else:
                            pad = int(s['x'] < 1820)
            elif item:
                gap = item['x']-s['x']
                pad = int(gap > 3) | (2 if gap < -3 else 0)
                if abs(gap) < 40 and item['y'] < s['y']-16 and s['state'] == 0 and step-last_jump > 40:
                    pad |= 128
                    last_jump = step
            elif s['x'] < block['x']-8:
                pad = 1
                if s['state'] == 0 and step-last_jump > 40:
                    obstacle = next((left for left in (448, 608, 736, 912)
                                     if left not in jumped and left-50 <= s['x'] < left-3), None)
                    pit = 1346 <= s['x'] < 1424
                    near = any(a['flag'] == 1 and a['id'] in (0, 3, 6) and a['state'] < 2
                               and 60 <= a['x']-s['x'] <= 90 and abs(a['y']-s['y']-8) < 24
                               for a in actors())
                    if obstacle is not None or pit or near:
                        pad |= 128
                        last_jump = step
                        if obstacle is not None:
                            jumped.add(obstacle)
            else:
                gap = block['x']-6-s['x']
                pad = int(gap > 2) | (2 if gap < -2 else 0)
                if abs(gap) <= 2 and s['state'] == 0 and step-last_jump > 40:
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
            if step % 200 == 0:
                print(json.dumps(dict(event='progress', variant=variant, kind=kind,
                                      player=state())), flush=True)
            assert not m.blocked
        else:
            raise AssertionError(('controller bound', state(), actors()))
        assert born and collected
        assert calls['PlayerBGCollision'] == calls['FfMovement'] > 20
        palette = [0x16, 0x30, 0x36] if variant < 2 else [0x28, 0x18, 0x21]
        assert list(m.vram[0x3f11:0x3f14]) == palette
        assert any(m[0x200+4*i] < 240 for i in range(64))
        if kind == 'life':
            assert award and state()['lives'] == 3
        else:
            assert protected_hit and expiry and music_restored and len(palettes) >= 4
            assert timer_values == set(range(36))
            assert all(a['star']-b['star'] == 1 for a, b in zip(timer_changes, timer_changes[1:]))
            assert timer_changes[1]['step']-timer_changes[0]['step'] == timer_changes[0]['interval']+1
            assert all(b['step']-a['step'] == 21 and b['interval'] == 20
                       for a, b in zip(timer_changes[1:], timer_changes[2:]))
            assert state()['attr'] & 3 == 0
        assert sha256(W.ROM.read_bytes()).hexdigest() == W.PIN
        return dict(passed=True, ROM_sha256=W.PIN, variant=variant, class_name=A.CLASSES[variant],
                    kind=kind, CPU_controller_only=True, Mesen_run=False, output_files=0,
                    authored=block, born=born, collected=collected, life_award=award,
                    protected_enemy=protected_hit, timer_changes=timer_changes,
                    music_restored=music_restored,
                    palettes=sorted(palettes), terminal=state(), calls=dict(calls),
                    scope='Actual native-parser item/controller pickup; native deferred 1UP or Star gear preservation, timer decay/palette cycle and enemy immunity. Logical CPU model, not Mesen/hardware/full-stage.')
    except Exception:
        print(json.dumps(dict(passed=False, variant=variant, kind=kind, terminal=state(),
                              actors=actors(), born=born, collected=collected, award=award,
                              protected_hit=protected_hit, calls=dict(calls), trace=list(tail))), flush=True)
        raise


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--variant', type=int, choices=range(4))
    p.add_argument('--kind', choices=('life', 'star', 'both'), default='both')
    args = p.parse_args()
    results = []
    for variant in range(4) if args.variant is None else (args.variant,):
        for kind in ('life', 'star') if args.kind == 'both' else (args.kind,):
            result = route(variant, kind)
            results.append(result)
            print(json.dumps(dict(event='pass', result=result)), flush=True)
    summary = [dict(variant=r['variant'], class_name=r['class_name'], kind=r['kind'],
                    passed=r['passed'], terminal=r['terminal']) for r in results]
    print(json.dumps(dict(passed=True, ROM_sha256=W.PIN, results=summary,
                          CPU_controller_only=True, Mesen_run=False, output_files=0)), flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc()
        raise SystemExit(1)
