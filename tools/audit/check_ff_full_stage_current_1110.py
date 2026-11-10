"""Continue earned FF pickups/attack into full native 1-1, stdout only.

The frozen earned-attack controller supplies the real startup/pickup prefix.
Its existing returned model is observed, not changed, by a capture wrapper.
After confirmation all changes are controller input/normal-NMI scheduling.
No ROM, terrain, actor, power, position, damage or helper state is granted.
This is a logical CPU check, not physical Mesen/cadence/graphical proof.
"""
import argparse
from collections import Counter, deque
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
from pathlib import Path
import traceback
from unittest.mock import patch

import check_ff_earned_attacks_current_1110 as A

F, W, N = A.F, A.W, A.N
ATTACK_SHA = 'dd8015682993e4a13190e9a9e200a1ae4b227767172b5ad6036831447110b44e'


def fixture(variant):
    assert sha256(Path(A.__file__).read_bytes()).hexdigest() == ATTACK_SHA
    original, holder = F.flower, {}

    def capture(v):
        result, model = original(v)
        holder['model'] = model
        return result, model

    log = io.StringIO()
    try:
        with redirect_stdout(log), patch.object(F, 'flower', capture):
            receipt = A.attack(variant)
    except Exception:
        print(log.getvalue(), flush=True)
        raise
    assert receipt['passed'] and receipt['earned_mushroom_and_flower']
    return receipt, holder['model']


def route(variant, *, stop_at_intro=False):
    prefix, m = fixture(variant)
    b, calls, tail = m.bundle, Counter(), deque(maxlen=32)
    idle = W.address(b, 'IdleLoop')
    jumps, injuries, checkpoints = [], [], []
    contact_trace, pending_calls = [], []
    last_jump, start, flag, next_level = -100, None, None, None
    camera_previous, maximum_jump, step = None, 0, -1
    best_x, advanced_at = 0, 0
    points = {(3, 0xadd8): 'FfInjuryStart'}
    for name in ('KillPlayer', 'EnemyStomped', 'FlagpoleRoutine', 'FlagpoleCollision',
                 'ShellOrBlockDefeat', 'ScrollHandler', 'PlayerBGCollision'):
        if name in b['syms']:
            points[((W.location(b, name) - 16) // 8192 | 128, W.address(b, name))] = name
    for name in ('FfHostMovement', 'FfHostHead', 'FfHostFeet', 'FfHostSide',
                 'FfHostWall', 'FfHostRead', 'FfHostAfterTerrain'):
        points[3, W.address(b, name)] = name

    def contact_state(c):
        return dict(step=step, player=state(), PC=c.pc, SP=c.sp,
                    registers=[c.a, c.x, c.y, c.p], scratch=bytes(m[3:11]).hex(),
                    terrain=list(m[W.address(b, 'FfRenderBuffer'):W.address(b, 'FfRenderBuffer') + 8]),
                    VY=list(m[W.address(b, 'MmVY'):W.address(b, 'MmVY') + 3]),
                    block_pointers=list(m[W.address(b, 'BlockBufferAddr'):W.address(b, 'BlockBufferAddr') + 4]))

    def state():
        return dict(step=step, x=N.get(m, 'Player_X_Position') + 256 * N.get(m, 'Player_PageLoc'),
                    y=N.get(m, 'Player_Y_Position'), state=N.get(m, 'Player_State'),
                    engine=N.get(m, 'GameEngineSubroutine'), lives=N.get(m, 'NumberofLives'),
                    mode=N.get(m, 'OperMode'), task=N.get(m, 'OperMode_Task'),
                    world=N.get(m, 'WorldNumber'), level=N.get(m, 'LevelNumber'),
                    power=m[0x5fc5], earned=m[0x5fc6], action=m[0x5c03],
                    age=m[0x5c04], hurt=m[0x5c07], knockback=m[0x5c08],
                    camera=N.get(m, 'ScreenLeft_PageLoc') * 256 + N.get(m, 'ScreenLeft_X_Pos'),
                    timer=N.get(m, 'TimerControl'))

    def actors():
        return [dict(slot=i, flag=N.get(m, 'Enemy_Flag', i), id=N.get(m, 'Enemy_ID', i),
                     state=N.get(m, 'Enemy_State', i),
                     x=N.get(m, 'Enemy_X_Position', i) + 256 * N.get(m, 'Enemy_PageLoc', i),
                     y=N.get(m, 'Enemy_Y_Position', i)) for i in range(6)]

    def solid(x, y):
        if not 0 <= x < 65536 or not 32 <= y < 240:
            return False
        # Lookahead is within the engine's rendered region in this real
        # controller route. It reads actual cells; no substitute map is built.
        at = 0x300 + ((x >> 8) & 1) * 208 + ((y - 32) // 16) * 16 + ((x >> 4) & 15)
        return bool(m[W.address(b, 'MTileAttribute') + m[at]] & 1)

    def observe(c):
        nonlocal flag
        if 480 <= step < 490:
            for item in pending_calls[:]:
                if (c.pc, c.sp) == item['return']:
                    item['after'] = contact_state(c)
                    contact_trace.append(item)
                    pending_calls.remove(item)
        if c.pc < 0x8000:
            return
        name = points.get((m.rawtags[(c.pc - 0x8000) // 8192], c.pc))
        if not name:
            return
        if name.startswith('FfHost') and 480 <= step < 490 and len(contact_trace) < 256:
            back = (m[0x100 + ((c.sp + 1) & 255)] + 256 * m[0x100 + ((c.sp + 2) & 255)] + 1) & 65535
            pending_calls.append(dict(name=name, before=contact_state(c),
                                      **{'return': (back, c.sp + 2)}))
        calls[name] += 1
        if name == 'KillPlayer':
            raise AssertionError(('Native death', state(), actors()))
        if name == 'FfInjuryStart':
            injuries.append(dict(player=state(), actors=actors()))
            print(json.dumps(dict(event='natural_injury', variant=variant, result=injuries[-1])), flush=True)
        if name in ('FlagpoleRoutine', 'FlagpoleCollision') and flag is None and state()['engine'] == 4 and state()['x'] >= 3000:
            flag = dict(player=state(), routine=name)
            print(json.dumps(dict(event='native_flagpole', variant=variant, result=flag)), flush=True)

    try:
        for step in range(4500):
            s = state()
            assert N.get(m, 'SelectedCharacter') == 22 and N.get(m, 'FfVariant') == variant
            assert N.get(m, 'CheatStartLevel') == N.get(m, 'CheatInvincible') == 0
            assert s['lives'] == 2
            assert s['world'] == 0 and s['level'] in (0, 1)
            if stop_at_intro and s['level'] == 1 and s['engine'] == 7 and s['x'] >= 230:
                assert flag and not injuries
                return dict(diagnostic_stop=True, full_1_1_flag_and_level_transition=True,
                            active_1_2=False, ROM_SHA256=W.PIN, variant=variant,
                            terminal=s, native_flag=flag, prefix=prefix,
                            calls=dict(calls), injuries=injuries,
                            maximum_logical_camera_step=maximum_jump,
                            jump_events=jumps, checkpoints=checkpoints), m
            if s['level'] == 1 and (s['mode'], s['task'], s['engine']) == (1, 3, 8):
                next_level = s
                break
            assert s['earned'] == 2
            if start is None:
                start = s
            if s['x'] > best_x:
                best_x, advanced_at = s['x'], step
            elif s['engine'] == 8 and step - advanced_at > 120:
                tiles = {str(y): [m[0x300 + ((x >> 8) & 1) * 208 + ((y - 32) // 16) * 16 + ((x >> 4) & 15)]
                                  for x in range((s['x'] // 16 - 4) * 16, (s['x'] // 16 + 6) * 16, 16)]
                         for y in range(80, 224, 16)}
                raise AssertionError(('Stalled controller', s, dict(first_world_column=s['x'] // 16 - 4, tiles=tiles),
                                      list(tail)[-8:], jumps[-4:]))
            if s['level'] == 0 and s['engine'] == 8:
                if camera_previous is not None:
                    maximum_jump = max(maximum_jump, s['camera'] - camera_previous)
                    assert s['camera'] >= camera_previous, ('Backward ordinary camera', camera_previous, s)
                camera_previous = s['camera']
                pad = 1
                if s['state'] == 0 and step - last_jump > 5:
                    near = [a for a in actors() if a['flag'] == 1 and a['id'] < 21
                            and a['state'] < 2 and 0 <= a['x'] - s['x'] <= 60
                            and abs(a['y'] - s['y'] - 8) < 24]
                    foot = s['y'] + 32
                    wall = any(solid(s['x'] + ahead, foot - 1) for ahead in (18, 30, 42))
                    ledge = not solid(s['x'] + 30, foot + 1)
                    if near or wall or ledge:
                        pad |= 128
                        last_jump = step
                        jumps.append(dict(reason='enemy' if near else 'wall' if wall else 'ledge', **s))
                # The source jump has fixed height: one fresh A edge is
                # sufficient, and a fresh ground A cancels a melee recovery.
                if step == 0 and s['state'] == 0:
                    pad |= 128
                    last_jump = step
                    jumps.append(dict(reason='earned-hit-departure', **s))
            else:
                pad = 0
            if not checkpoints or s['x'] // 128 > checkpoints[-1]['x'] // 128 or s['engine'] != checkpoints[-1]['engine']:
                checkpoints.append(s)
            m.controller_pad = pad
            W.clear_logs(m)
            N.consume(m)
            c = N.NesMPU(memory=m, pc=idle)
            c.sp, c.p = 255, 0x31
            c.stPushWord(0xe33b)
            for _ in range(4_000_000 if s['engine'] == 0 else 250000):
                if (c.pc, c.sp) == (idle + 12, 252):
                    break
                observe(c)
                assert m[c.pc], ('BRK', step, hex(c.pc), m.rawtags)
                c.step()
            else:
                raise AssertionError(('Native frame bound', step, hex(c.pc)))
            tail.append(dict(pad=pad, **state()))
            assert not m.blocked
            if step % 200 == 0:
                print(json.dumps(dict(event='fullstage_progress', variant=variant, player=state(), actors=actors())), flush=True)
        else:
            raise AssertionError(('Controller route bound', state(), actors()))
        assert next_level and flag and calls['PlayerBGCollision'] > 100
        assert N.get(m, 'CrossoverBehaviorVersion') == 0
        assert sha256(W.ROM.read_bytes()).hexdigest() == W.PIN
        return dict(passed=True, ROM_SHA256=W.PIN, class_name=F.A.CLASSES[variant], variant=variant,
                    CPU_controller_only=True, Mesen_run=False, outputs_written=0, full_1_1=True,
                    route='non-shortcut', prefix_earned_pickups_and_attack=prefix['passed'],
                    start=start, native_flag=flag, active_1_2=next_level, calls=dict(calls),
                    injuries=injuries, jump_events=jumps, checkpoints=checkpoints,
                    maximum_logical_camera_step=maximum_jump,
                    scope='Natural menu/pickups/attack then native1-1 flagpole/score/active1-2, lives2, controller input only. Logical CPU model; no cadence, Mesen visuals, shortcut or every-enemy-kill claim.')
    except Exception:
        print(json.dumps(dict(passed=False, variant=variant, terminal=state(), actors=actors(),
                              jumps=jumps[-4:], injuries=injuries, tail=list(tail)[-8:],
                              contact_trace=[row for row in contact_trace if row['name'] in
                                             ('FfHostHead', 'FfHostFeet', 'FfHostAfterTerrain')][:12],
                              calls=dict(calls))), flush=True)
        raise


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--variant', type=int, choices=range(4))
    p.add_argument('--head-corner', action='store_true',
                   help='Use the proposed exact-source head-corner cartridge in memory; never write it.')
    args = p.parse_args()
    def run():
        for variant in range(4) if args.variant is None else (args.variant,):
            print(json.dumps(dict(event='full_stage_result', result=route(variant)), sort_keys=True), flush=True)
    if args.head_corner:
        import check_ff_head_corner_1110 as Fix
        image, _, cookie, _, _, _ = Fix.proposal(W.ROM.read_bytes())
        class MemoryImage:
            def read_bytes(self):
                return image
        # The frozen controller takes its input through this module's read
        # facade/PIN. Only its cartridge input changes, before genuine menu
        # startup; no memory preload or actor grant is inserted into play.
        with patch.object(W, 'ROM', MemoryImage()), patch.object(W, 'PIN', sha256(image).hexdigest()):
            print(json.dumps(dict(event='memory_only_candidate', SHA256=W.PIN, cookie=cookie.hex(),
                                  ROM_written=False, source_only=True)), flush=True)
            run()
    else:
        run()


if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc()
        raise SystemExit(1)
