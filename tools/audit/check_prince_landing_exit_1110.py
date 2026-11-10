"""Explore controller exits after the repaired landing, entirely in memory.

Explicit CPU terrain/enemy scene, not a native stage-clear qualification.
No cartridge, fixture, image or receipt is written by this diagnostic.
"""
import json
from pathlib import Path

import check_prince_previous_sole_1110 as C

ROM = C.R / 'build/prince-landing-native-1110/candidate.nes'
PIN = '34d2146263ef4eb950d957824c75899d49b53d80f7f30e584e0cbb694fc9bbf4'


def trial(env, seed, labels, delay, after_pad):
    model = C.N.fork(seed)
    stage = 'run'
    landing = None
    events = []
    second_jump = False
    previous_hp = 5
    for tick in range(230):
        row = C.Recovery.sample(model, tick)
        if row['hp'] != previous_hp:
            events.append(dict(event='HP change', tick=tick, before=previous_hp, after=row['hp'], x=row['x'], action=row['action']))
            previous_hp = row['hp']
        if row['hp'] == 0 or row['lives'] != 2 or row['engine'] != 8:
            stage = 'injured-or-dead'
            break
        if stage == 'run' and 745 <= row['x'] <= 752 and abs(row['y'] - 112) <= 2 and C.Recovery.running(model, row):
            stage = 'takeoff'
        if stage == 'takeoff' and row['action'] == 4:
            stage = 'flight'
        if landing is None and C.N.get(model, 'Enemy_State', 1) == 4:
            landing = tick
            events.append(dict(event='repaired landing', tick=tick, x=row['x'], action=row['action']))
        if landing is not None and row['action'] == 4 and not second_jump:
            second_jump = True
            events.append(dict(event='second original jump', tick=tick, x=row['x']))
        if landing is not None and row['x'] >= 908 and row['y'] == 176 and C.Recovery.grounded(model, row):
            stage = 'clear'
            break
        pad = 129 if stage == 'takeoff' else 1
        if landing is not None and tick - landing >= delay:
            pad = after_pad
        C.Route.controls(env, model, labels, pad)
    else:
        stage = 'bounded'
    return dict(delay=delay, after_pad=after_pad, outcome=stage, landing=landing,
                terminal={k: row[k] for k in ('epoch', 'x', 'y', 'hp', 'lives', 'engine', 'action', 'frame', 'mode')},
                events=events, actors=C.Route.actors(model))


def main():
    assert C.digest(ROM.read_bytes()) == PIN
    bundle = C.Start.W.bundle(ROM.read_bytes())
    env, seed, labels = C.fixture(bundle)
    C.N.put(seed, CrossoverBehaviorVersion=0)
    for delay, pad in ((0, 1), (0, 129), (4, 129), (8, 129), (16, 129), (0, 65)):
        result = trial(env, seed, labels, delay, pad)
        print(json.dumps(result, separators=(',', ':')), flush=True)


if __name__ == '__main__':
    main()
