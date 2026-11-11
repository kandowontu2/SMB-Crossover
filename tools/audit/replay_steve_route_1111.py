"""Replay Steve through the stock 1-1 terrain on the delivered movement ROM."""

import argparse
from collections import Counter
import json

import deliver_steve_move_1111 as Delivery


Source = Delivery.Source
Live, S = Source.Live, Source.S
PIPES = ((448, 480), (608, 640), (736, 768), (912, 944), (2608, 2640), (2864, 2896))
GAPS = ((1104, 1136), (1376, 1424), (2448, 2480))
TAKEOFFS = {1104: 1090, 1376: 1366, 2448: 2435}
STATE = Source.Motion.FIELDS['State']


def camera(m):
    return S.N.get(m, 'ScreenLeft_PageLoc') * 256 + S.N.get(m, 'ScreenLeft_X_Pos')


def enemies(m, player_x, player_y):
    targets = []
    for slot in range(6):
        get = lambda name: S.N.get(m, name, slot)
        if not 0 < get('Enemy_Flag') < 128 or get('Enemy_State') & 0x20 or get('Enemy_ID') >= 13:
            continue
        if get('Enemy_Y_HighPos') != 1:
            continue
        x, y = get('Enemy_PageLoc') * 256 + get('Enemy_X_Position'), get('Enemy_Y_Position')
        if 0 < x - player_x <= 52 and abs(y - player_y) <= 25:
            targets.append((x, y, get('Enemy_ID'), get('Enemy_State')))
    return sorted(targets)


def first_pipe(m, punch):
    result = Live.natural_goomba(m, punch)

    def tick(pad):
        m.controller_pad = pad
        S.C.Game.frame(m)
        assert S.N.get(m, 'NumberofLives') == 2 and Live.mode(m) == S.PLAY, Live.player(m)

    for _ in range(320):
        x, y = Live.player(m)
        targets = enemies(m, x, y)
        close = targets and targets[0][0] - x <= 38
        tick(1 | (64 if close and not m.controller_pad & 64 else 0))
        if S.N.get(m, 'XgWallContact') and Live.player(m)[0] > 400:
            break
    else:
        raise AssertionError(('First pipe side unavailable', Live.player(m)))
    assert Live.player(m) == (433, 176), Live.player(m)
    tick(1)
    for age in range(100):
        tick(129 if age < 48 else 1)
        x, y = Live.player(m)
        if x >= 488 and y == 176 and S.N.get(m, 'Player_State') == 0:
            result.update(pipe1=dict(x=x, y=y, updates=age + 1, camera=camera(m)))
            return result
    raise AssertionError(('First pipe crossing unavailable', Live.player(m)))


def continue_route(m, *, target, max_updates, takeoffs=TAKEOFFS):
    best_x = Live.player(m)[0]
    progress = 0
    jump_until = 0
    last_jump = -60
    earlier_hp = S.N.get(m, 'JnHealth')
    prior_scene = None
    jumps, milestones, damage, scenes, entrance = [], [], [], [], []
    passed = {PIPES[0]}
    cap = 'approach'
    for update in range(max_updates):
        x, y = Live.player(m)
        state = S.N.get(m, 'Player_State')
        scene = (*Live.mode(m), S.N.get(m, 'LevelNumber'))
        lives = S.N.get(m, 'NumberofLives')
        health = S.N.get(m, 'JnHealth')
        if scene != prior_scene:
            scenes.append((update, scene, x, y, lives, health))
            prior_scene = scene
        if health != earlier_hp:
            damage.append((update, x, y, earlier_hp, health, enemies(m, x, y)))
            earlier_hp = health
        if scene == (1, 3, 8, 1) or lives < 2 or scene[2] in (6, 11):
            break
        if scene != (1, 3, 8, 0):
            if scene == (1, 3, 7, 1) and update % 40 == 0:
                entrance.append((update, x, y, S.N.get(m, 'Player_SprAttrib'),
                                 S.N.get(m, 'ChangeAreaTimer'), S.N.get(m, 'PlayerEntranceCtrl')))
            m.controller_pad = 0
            S.C.Game.frame(m)
            continue
        if x > best_x and scene == (1, 3, 8, 0):
            best_x, progress = x, update
        if state == 0 and y <= 176:
            for left, right in (*PIPES, *GAPS):
                if (left, right) not in passed and x >= right:
                    passed.add((left, right))
                    event = (update, left, right, x, y, camera(m), health)
                    milestones.append(event)
                    print('Crossing', json.dumps(event), flush=True)
        if x >= target and state == 0 and target < 3200:
            break
        if scene == (1, 3, 8, 0) and update - progress > 200:
            break

        pad = 1
        ground = state == 0 and m[STATE] == 0
        ahead = enemies(m, x, y)
        remaining_gaps = [pair for pair in GAPS if pair not in passed]
        gap = remaining_gaps[0] if remaining_gaps else None
        if cap == 'jump':
            if state == 0:
                cap = 'landed'
                print('Third gap near cap', json.dumps((update, x, y, health)), flush=True)
            elif x >= 2411:
                m.controller_pad = 0
                S.C.Game.frame(m)
                continue
        if ground and update - last_jump >= 13 and scene == (1, 3, 8, 0):
            reason = None
            hold = 9
            if gap and takeoffs[gap[0]] <= x < gap[0] + 8:
                reason = f'gap-{gap[0]}'
            elif gap and gap[0] == 2448 and 2398 <= x < 2416 and y == 128 and cap == 'approach':
                reason, hold = 'third-gap-cap', 1
                cap = 'jump'
            elif S.N.get(m, 'XgWallContact') or update - progress >= 15 and update - last_jump >= 38:
                reason = 'wall'
            elif ahead and ahead[0][0] - x <= 28 and (not gap or gap[0] - x > 80):
                if m[S.FIELDS['StevePunchSelector']] or ahead[0][2] == 12:
                    reason = 'enemy-hop'
            if reason:
                last_jump, jump_until = update, update + hold
                jumps.append((update, reason, x, y, camera(m), health, hold))
                print('Jump', json.dumps(jumps[-1]), flush=True)
        if update < jump_until:
            pad |= 128
        if ahead and ahead[0][0] - x <= 36 and not m.controller_pad & 64 and not pad & 128:
            pad |= 64
        m.controller_pad = pad
        S.C.Game.frame(m)
    else:
        update = max_updates
    return dict(update=update, x=Live.player(m)[0], y=Live.player(m)[1], camera=camera(m),
                health=S.N.get(m, 'JnHealth'), lives=S.N.get(m, 'NumberofLives'),
                level=S.N.get(m, 'LevelNumber'), area_type=S.N.get(m, 'AreaType'),
                furthest=best_x, passed=sorted(passed), jumps=jumps, milestones=milestones,
                damage=damage, scenes=scenes, entrance=entrance)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=int, default=3200)
    parser.add_argument('--updates', type=int, default=4000)
    args = parser.parse_args()
    raw = Delivery.NIGHTLY.read_bytes()
    assert Delivery.digest(raw) == Delivery.PIN
    candidate, _, punch, cookie = Delivery.proposal(Delivery.recover_parent(raw))
    assert candidate == raw
    m, open_updates = Live.opening(raw, 2)
    assert S.C.Common.headers(m) == (cookie,) * 2 and open_updates == 167
    print('Opening', json.dumps(first_pipe(m, punch)), flush=True)
    route = continue_route(m, target=args.target, max_updates=args.updates)
    scene = (*Live.mode(m), route['level'])
    terminal = scene == (1, 3, 8, 1) and route['area_type'] == 2
    stage_path = {row[1][2] for row in route['scenes']}
    complete = terminal and set(route['passed']) == set(PIPES + GAPS) and {4, 5} <= stage_path
    reached = complete if args.target >= 3200 else route['x'] >= args.target
    passed = reached and route['lives'] == 2 and route['health'] > 0
    print(json.dumps(dict(passed=passed, stage_complete=complete, ROM_sha256=Delivery.PIN,
                          route=route, output_files=0), sort_keys=True), flush=True)
    raise SystemExit(0 if passed else 1)


if __name__ == '__main__':
    main()
