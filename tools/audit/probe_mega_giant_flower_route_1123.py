"""Separate bounded real-menu Giant Mushroom-to-Flower source trial, stdout only.

The frozen first-item kernel is reused in memory through checked source sites;
no dependency file is changed.  Only controller policy and observation differ.
"""
import argparse
from collections import deque
from hashlib import sha256
import inspect
import json
from pathlib import Path
from unittest.mock import patch

import probe_mega_giant_first_pickup_1123 as Base
import run_mega_giant_pickups_native_1123 as Native

BASE_SOURCE = 'cbe04a9035e48e97d6594f125e6e1334657defd6ab1d2ecd8d1b2f8a4d1930fb'
H = lambda data: sha256(data).hexdigest()


class Route:
    def __init__(self):
        self.tail = deque(maxlen=16)
        self.hold = 0
        self.started = None
        self.m_done = None
        self.m_returns = 0
        self.flower = None
        self.flower_ages = []
        self.flower_finish = None
        self.follow = []
        self.jumps = []
        self.flags = set()
        self.done = False
        self.last = None
        self.entered = False

    def observe(self, q, m, contacts, collector):
        if not self.entered:
            if (Base.N.get(m, 'OperMode'), Base.N.get(m, 'OperMode_Task'), q['engine']) != (1, 3, 8):
                return
            self.entered = True
        self.last = q
        self.tail.append(q)
        assert q['lives'] == 2 and Base.N.get(m, 'GuestLegacyHurt') == 0, ('Healthy original route', q)
        assert q['y'] < 224 and Base.N.get(m, 'Player_Y_HighPos') == 1, ('No fall', q)
        if q['status'] == 1 and not q['growth_active'] and q['growth_age'] == 60 and self.m_done is None:
            self.m_done = q
        elif self.m_done and self.m_returns < 25:
            assert q['status'] == 1 and q['y'] == 176 and Base.N.get(m, 'Player_State') == 0
            self.m_returns += 1
        flower = [r for r in collector if r['event'] == 'HandlePowerUpCollision' and r['kind'] == 1]
        if flower and self.flower is None:
            self.flower = flower[0]
            assert self.flower['actor_state'] >= 6 and any(r['tile'] == 0xc1 and r['x'] > 1100 for r in contacts)
        if self.flower:
            if q['growth_active']:
                assert q['growth_age'] == len(self.flower_ages)
                assert Base.N.get(m, 'GuestPowerupOld') == 1 and Base.N.get(m, 'GuestPowerupTarget') == 2
                self.flower_ages.append(q['growth_age'])
            elif self.flower_finish is None:
                assert self.flower_ages == list(range(60)) and q['growth_age'] == 60 and q['status'] == 2
                self.flower_finish = q
            else:
                assert q['status'] == 2 and q['engine'] == 8 and Base.N.get(m, 'Player_State') == 0
                self.follow.append(q)
                if len(self.follow) == 25:
                    score = lambda r: int(''.join(map(str, r['score'])))
                    assert score(q) >= score(self.flower) + 1000 and q['x'] > self.flower_finish['x']
                    self.done = True

    def drive(self, q, m):
        if self.m_returns < 25:
            return 1
        if self.started is None:
            self.started = q
        x, y, t = q['x'], q['y'], q['active']
        ground = Base.N.get(m, 'Player_State') == 0
        speed = Base.N.get(m, 'Player_X_Speed')
        def jump(key, duration):
            self.flags.add(key)
            self.hold = t+duration
            self.jumps.append(dict(reason=key, **q))
        if q['engine'] != 8:
            return 1
        if 'first_pipe' not in self.flags and 395 <= x < 430 and ground:
            jump('first_pipe', 35)
        elif 'second_pipe' not in self.flags and 580 <= x < 607 and ground:
            jump('second_pipe', 40)
        else:
            stop = next((p for p in (679, 853) if p <= x < p+32 and p not in self.flags), None)
            if stop:
                if ground and y == 176:
                    jump(stop, 28)
                else:
                    return 2 if 0 < speed < 128 else 0
            elif ground and t >= self.hold:
                for lo in (1104, 1376):
                    if lo not in self.flags and lo-30 <= x < lo:
                        jump(lo, 28)
                        break
        return 65 | (128 if t < self.hold else 0)


def once(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new, 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--limit', type=int, default=1800)
    args = ap.parse_args()
    assert 500 <= args.limit <= 2400
    args.output.mkdir(exist_ok=True)
    assert H(Path(Base.__file__).read_bytes()) == BASE_SOURCE
    current = Base.ROM.read_bytes()
    parent, image, _, _, composition = Native.three_way(current, args.output)
    route = Route()
    source = inspect.getsource(Base.run)
    source = once(source, 'for _ in range(500):', f'for _ in range({args.limit}):')
    source = once(source, 'step(1, True)', 'step(route.drive(state(), m), True)')
    source = once(source, '            resumed.append(state())',
        '            resumed.append(state())\n        route.observe(state(), m, contacts, collector)')
    source = once(source, 'if require_pickup and len(resumed) == 25:', 'if route.done:')
    source = once(source, 'if not require_pickup and first_contact_at is not None and active_updates - first_contact_at >= 60:',
        'if False:')
    captured = []
    namespace = dict(Base.__dict__, route=route, print=lambda *a, **k: captured.extend(a))
    exec(compile(source, '<Giant checked Flower continuation>', 'exec'), namespace)
    class Parent:
        def read_bytes(self):
            return parent
    result, reason = None, None
    try:
        with patch.object(Base, 'ROM', Parent()):
            namespace['ROM'] = Base.ROM
            result = namespace['run'](args.output, image=image, require_pickup=False)
        assert route.done, ('Finite Flower route', route.last)
    except AssertionError as error:
        reason = str(error)
    report = dict(passed=route.done, reason=reason, composition=composition,
        source_SHA256=H(Path(__file__).read_bytes()), baseline_kernel_SHA256=BASE_SOURCE,
        source_CPU_only=True, Mesen_run=False, output_files=0,
        Mushroom_finish=route.m_done, Mushroom_followup=route.m_returns,
        jumps=route.jumps, Flower_collection=route.flower, Flower_ages=route.flower_ages,
        Flower_finish=route.flower_finish, Flower_followup=len(route.follow),
        terminal=route.last, tail=list(route.tail))
    if result:
        report.update(native_counts=result['counts'], actual_births=result['powerup_births'],
            contacts=[q for q in result['events'] if q['event'] == 'sweep' and q['x'] > 1000])
    encoded = json.dumps(report, sort_keys=True, separators=(',', ':'))
    print(json.dumps(dict(report=report, receipt_SHA256=H(encoded.encode()))), flush=True)
    assert not list(args.output.rglob('*'))
    return int(not route.done)


if __name__ == '__main__':
    raise SystemExit(main())
