"""Controller-only natural Sonic mushroom and powered injury, using native CPU Main/NMI."""
import argparse
from collections import Counter, deque
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
from pathlib import Path

import check_roster_powerup_continuation_1110 as Main
import check_sonic_native_controller_1110 as Opening
import check_sonic_native_injury_tier_1110 as Fix
import check_sonic_native_point_read_1110 as Point

N, W = Opening.N, Opening.W
STAGE = Fix.Stage
NEW_PIN = '19a5ea9001f22afd529c96c6c2401a237f487c0f851678363fb859f0ec7c1936'


def state(mem):
    return dict(x=N.get(mem, 'Player_X_Position') + 256 * N.get(mem, 'Player_PageLoc'),
                y=N.get(mem, 'Player_Y_Position'), state=N.get(mem, 'Player_State'),
                vx=int.from_bytes(mem.ram[2][0x20:0x23], 'little', signed=True),
                vy=int.from_bytes(mem.ram[2][0x60:0x63], 'little', signed=True),
                source_tick=mem.ram[2][0x92], flags=mem.ram[2][0x30],
                status=N.get(mem, 'PlayerStatus'), engine=N.get(mem, 'GameEngineSubroutine'),
                timer=N.get(mem, 'TimerControl'), age=N.get(mem, 'GuestPowerupAge'),
                powered=N.get(mem, 'GuestPowerupActive'), injury=N.get(mem, 'InjuryTimer'),
                lives=N.get(mem, 'NumberofLives'))


def actors(mem):
    return [dict(slot=i, flag=N.get(mem, 'Enemy_Flag', i), id=N.get(mem, 'Enemy_ID', i),
                 state=N.get(mem, 'Enemy_State', i), kind=N.get(mem, 'PowerUpType', i),
                 x=N.get(mem, 'Enemy_X_Position', i) + 256 * N.get(mem, 'Enemy_PageLoc', i),
                 y=N.get(mem, 'Enemy_Y_Position', i)) for i in range(6)]


def run(image, packet, *, negative=False):
    with redirect_stdout(io.StringIO()):
        opening, mem = Opening.run(image, packet, goal_x=200)
    assert opening['passed']
    b = mem.bundle
    native_names = ('PlayerHeadCollision', 'HandlePowerUpCollision', 'GuestBeginPowerup',
                    'GuestPowerupUpdate', 'InjurePlayer', 'ForceInjury', 'KillPlayer',
                    'EnemyStomped', 'PlayerEnemyCollision')
    callbacks = {(((W.location(b, name) - 16) // 8192) | 128, W.address(b, name)): name
                 for name in native_names}
    callbacks[254, 0x97a4] = 'NativeStatusStore'
    callbacks[2, 0xd31b] = 'NewInjuryDecline'
    counts, tail, cues = Counter(), deque(maxlen=14), []
    phase, jump_started, jump_until = 'approach', -100, -1
    head = birth = mature = collected = transformed = injured = recovered = None
    recovery_ticks = 0
    animation_ages = []
    stores = []
    input_path = []
    last_bits = None

    def solid(x, y):
        status, tile = Point.expected(mem, x, y)
        assert status == 0, ('Controller query unavailable', x, y, status)
        return bool(tile['attribute'] & 1)

    def request(reason, epoch, s, duration=20):
        nonlocal jump_started, jump_until
        assert s['state'] == 0 and s['flags'] & 8
        jump_started, jump_until = epoch, epoch + duration
        cues.append(dict(reason=reason, epoch=epoch, x=s['x'], y=s['y'], vx=s['vx']))

    def observe(mem, cpu):
        nonlocal head, collected, injured
        if cpu.pc < 0x8000:
            return
        label = callbacks.get((mem.rawtags[(cpu.pc - 0x8000) // 8192], cpu.pc))
        if label is None:
            return
        counts[label] += 1
        if label == 'KillPlayer':
            raise AssertionError(('Unplanned native death', phase, state(mem), actors(mem)))
        if label == 'PlayerHeadCollision' and cpu.a == 0xc1:
            head = dict(tile=cpu.a, player=state(mem), r2=N.get(mem, 'R2'),
                        r6=N.get(mem, 'R6'), r7=N.get(mem, 'R7'))
        if label == 'HandlePowerUpCollision':
            item = actors(mem)[cpu.x]
            assert head and birth and mature and collected is None
            assert item['flag'] == 1 and item['id'] == 46 and item['kind'] == 0 and item['state'] & 128
            collected = dict(actor=item, player=state(mem))
        if label == 'GuestPowerupUpdate' and N.get(mem, 'GuestPowerupActive'):
            age = N.get(mem, 'GuestPowerupAge')
            assert collected and age == len(animation_ages) and age < 60
            animation_ages.append(age)
        if label == 'ForceInjury':
            assert transformed and injured is None
            enemy = actors(mem)[cpu.x]
            assert enemy['flag'] == 1 and enemy['id'] == 6 and enemy['state'] < 2
            assert N.get(mem, 'PlayerStatus') == 1
            injured = dict(actor=enemy, player=state(mem))
        if label == 'NativeStatusStore':
            assert injured
            stores.append((cpu.a, cpu.p & 1))

    def receipt(s):
        return dict(passed=True, exact_old_negative=negative, ROM_SHA256=sha256(image).hexdigest(),
                    menu='SONIC', opening=opening['terminal'], block=head, birth=birth, mature=mature,
                    collected=collected, transformed=transformed, transformation_updates=len(animation_ages),
                    injured=injured, native_status_stores=stores, recovery_updates=recovery_ticks,
                    recovered=recovered, terminal=s, calls=dict(counts), jump_events=cues,
                    inputs=input_path, outputs_written=0, controller_only=True)

    try:
        for epoch in range(1200):
            s = state(mem)
            assert N.get(mem, 'SelectedCharacter') == 43 and s['lives'] == 2
            assert N.get(mem, 'CheatInvincible') == N.get(mem, 'CheatStartLevel') == 0
            assert (N.get(mem, 'WorldNumber'), N.get(mem, 'LevelNumber'), N.get(mem, 'AreaAddrsLOffset')) == (0, 0, 5)
            ready = s['state'] == 0 and bool(s['flags'] & 8)
            item = next((a for a in actors(mem) if a['flag'] == 1 and a['id'] == 46), None)
            if item:
                if birth is None:
                    assert head and item['kind'] == 0
                    birth = dict(actor=item, player=s)
                if mature is None and item['state'] & 128:
                    mature = dict(actor=item, player=s)
            if collected and transformed is None and not s['powered']:
                assert len(animation_ages) == 60 and (s['engine'], s['status'], s['timer']) == (8, 1, 0)
                transformed = s
                phase = 'seek_hit'
            if injured:
                if negative:
                    assert stores == [(43, 0)] and (s['status'], s['engine'], s['timer']) == (43, 10, 255)
                    return receipt(s)
                assert stores == [(0, 0)] and s['status'] == 0
                if s['engine'] == 10:
                    recovery_ticks += 1
                    assert s['source_tick'] == injured['player']['source_tick']
                elif recovered is None:
                    assert (s['engine'], s['timer'], recovery_ticks) == (8, 0, 55)
                    recovered = s
                    phase = 'resume'
                if recovered and s['x'] >= recovered['x'] + 16:
                    assert (s['source_tick'] - recovered['source_tick']) & 255 >= 6
                    return receipt(s)
            pad = 0
            if phase == 'approach':
                pad = 1
                if ready and any(a['flag'] and a['id'] == 6 and 0 <= a['x'] - s['x'] <= 56 for a in actors(mem)):
                    request('first_Goomba', epoch, s)
                    phase = 'hop_brake'
            elif phase == 'hop_brake':
                if s['x'] < 282:
                    pad = 1
                elif s['vx'] > 0:
                    pad = 2
                else:
                    phase = 'hop_land'
            elif phase == 'hop_land':
                if ready and s['y'] == 176:
                    phase = 'under_block'
            elif phase == 'under_block':
                if s['x'] < 325:
                    pad = 1
                elif s['x'] > 336:
                    pad = 2
                elif ready and epoch - jump_started > 24:
                    request('authored_mushroom_block', epoch, s)
            elif (phase == 'seek_hit' and not injured) or phase == 'resume':
                pad = 1
                if ready and epoch - jump_started > 24:
                    foot = s['y'] + 32
                    if any(solid(s['x'] + ahead, foot - 1) for ahead in (24, 36, 48)):
                        request('recovery_pipe' if recovered else 'pipe', epoch, s)
            if item and not collected:
                phase = 'mushroom'
                gap = item['x'] - s['x']
                pad = 1 if gap > 6 else 2 if gap < -6 else 0
                if ready and epoch - jump_started > 24 and abs(gap) <= 30 and item['y'] < s['y'] - 12:
                    request('rising_mushroom', epoch, s)
            if epoch < jump_until and s['engine'] == 8 and (not injured or recovered):
                pad |= 128
            if pad != last_bits:
                input_path.append((epoch, pad))
                last_bits = pad
            mem.controller_pad = pad
            Main.frame(mem, observe)
            if collected and 'completion' not in collected:
                actor = actors(mem)[collected['actor']['slot']]
                assert actor['flag'] == 0
                floaty = N.get(mem, 'FloateyNum_Control', actor['slot'])
                sound = N.get(mem, 'Square2SoundQueue')
                assert (floaty, sound) == (6, 0x20)
                collected['completion'] = dict(flag=0, floaty=floaty, sound=sound)
            tail.append(dict(epoch=epoch, phase=phase, pad=pad, **state(mem)))
        raise AssertionError(('Natural Sonic injury route bound', phase, state(mem), actors(mem)))
    except Exception:
        print(json.dumps(dict(passed=False, phase=phase, calls=dict(counts), block=head,
                              birth=birth, mature=mature, collected=collected, transformed=transformed,
                              injured=injured, ages=animation_ages, cues=cues, tail=list(tail)), sort_keys=True), flush=True)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--both', action='store_true')
    args = parser.parse_args()
    assert args.output.resolve().is_relative_to(STAGE.R / 'build') and not args.output.exists()
    old, _, original, _ = STAGE.reconstruct()
    assert sha256(old).hexdigest() == Fix.PIN
    new, packet, _ = Fix.proposal(old, original)
    assert sha256(new).hexdigest() == NEW_PIN
    positive = run(new, packet)
    if args.both:
        negative = run(old, original, negative=True)
        assert positive['inputs'][:len(negative['inputs'])] == negative['inputs']
        for key in ('block', 'birth', 'mature', 'collected', 'transformed', 'injured'):
            assert positive[key] == negative[key], key
        print(json.dumps(negative, sort_keys=True), flush=True)
    print(json.dumps(positive, sort_keys=True), flush=True)
    assert not args.output.exists()


if __name__ == '__main__':
    main()
