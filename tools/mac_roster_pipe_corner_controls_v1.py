"""Ordered real Mac movement/BG controls for ascending past a pipe side.

Finite typed CPU arenas, separate from native clear/PPU/cadence qualification.
Preserves the predecessor's actual trajectory instead of weakening its result.
"""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import mac_roster_terrain_controls_v1 as terrain


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def trajectory(bundle, variant, mode, face, pipe, kind):
    start = pipe-14 if face == 1 else pipe+30
    q = terrain.fresh(bundle, variant, 0, start, 176, 0)
    q.put(CrossoverBehaviorVersion=mode, Player_State=0,
          PlayerFacingDir=face, Player_CollisionBits=255, ScrollLock=1)
    terrain.floor(q)
    for dx in (0, 16):
        for y in range(144, 208, 16):
            tile = 0xc4 if kind == 'solid' else ((0x12 if dx == 0 else 0x13)
                    if y == 144 else (0x14 if dx == 0 else 0x15))
            terrain.cell(q, pipe+dx, y, tile)
    rows = []
    for tick in range(120):
        q.put(SavedJoypadBits=128|face, A_B_Buttons=128,
              PreviousA_B_Buttons=128 if tick else 0)
        q.invoke('LmMovementGate')
        before = dict(x=terrain.pos(q)[0], y=terrain.pos(q)[1],
                      vy=q.get('Player_Y_Speed'))
        q.invoke('PlayerBGCollision')
        rows.append(dict(tick=tick, before=before, x=terrain.pos(q)[0],
                         y=terrain.pos(q)[1], vy=q.get('Player_Y_Speed'),
                         bits=q.get('Player_CollisionBits')))
    crossed = any(row['x'] >= pipe+16 if face == 1 else row['x'] <= pipe-2
                  for row in rows)
    false_ceiling = [row for row in rows if row['before']['vy'] >= 128
                     and row['y'] > row['before']['y']]
    return dict(variant=variant, mode=mode, face=face, pipe=pipe, kind=kind,
                crossed=crossed, false_ceiling=false_ceiling, rows=rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--expected-sha256', required=True)
    parser.add_argument('--parent', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    assert sha(args.rom) == args.expected_sha256
    candidate, parent = map(terrain.scoped_load, (args.rom, args.parent))
    negative = trajectory(parent, 0, 0, 1, 736, 'solid')
    assert not negative['crossed'] and negative['false_ceiling']
    cases = []
    for variant, mode, face, pipe, kind in itertools.product(
            range(3), (0, 1), (1, 2), (256, 736), ('solid', 'pipe')):
        result = trajectory(candidate, variant, mode, face, pipe, kind)
        assert result['crossed'], ('Still blocked', result)
        assert not result['false_ceiling'], ('Side became ceiling', result)
        cases.append(result)
    ceilings = []
    for variant, duck, vy, x in itertools.product(
            range(3), (0, 1), (250, 252, 255), (256, 352, 510)):
        head = terrain.HEAD[variant][duck]
        bottom = 160
        # Current head is one pixel into the lower plane after real ascent.
        q = terrain.fresh(candidate, variant, duck, x, bottom-head-1, vy)
        for col in range(x-16, x+33, 16):
            terrain.cell(q, col, 144, 0xc4)
        q.invoke('PlayerBGCollision')
        assert terrain.pos(q) == (x, bottom-head)
        assert q.get('Player_Y_Speed') == 1
        ceilings.append(dict(variant=variant, duck=duck, vy=vy, x=x))
    bindings = [dict(path=str(path), sha256=sha(path)) for path in (
        Path(__file__), Path(terrain.__file__), args.rom,
        args.rom.with_suffix('.dbg'), args.parent,
        args.parent.with_suffix('.dbg'),
        terrain.R/'src/little_mac_terrain.s')]
    args.output.write_text(json.dumps(dict(
        passed=True, native_run=False, ROM_sha256=sha(args.rom),
        predecessor_counterexample=negative, ordered_trajectories=cases,
        genuine_ceiling_crossings=ceilings, bindings=bindings,
        limits=['Typed movement then complete BG; no native map/PPU/cadence claim.',
                'Upward quantized speed conservatively bounds the last ascent step.']),
        indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(passed=True, trajectories=len(cases),
                          updates=120*len(cases), ceilings=len(ceilings))))


if __name__ == '__main__':
    main()
