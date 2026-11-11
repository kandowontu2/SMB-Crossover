"""Zero-output current-roster active-stage and opening-control CPU audit.

Starts from the established cold native menu fixture. Actual Select/Start,
native continue, GameLoop, scene parser, cold constructors and NMI execute.
Only controller input/scheduling changes after confirmation. This is not a
Mesen capture, cadence measurement, graphical review or full-stage clear.
"""
import argparse
from collections import deque
from hashlib import sha256
import json
from pathlib import Path
import traceback

import check_ff_white_mushroom_current_1110 as F
import check_remaining_roster_starts_1110 as C

R, N, UI = F.R, F.N, F.UI


def stage(bundle, row):
    original_bus = N.Bus
    N.Bus = F.ControllerBus
    try:
        m = UI.seed(bundle, row['slot'])
    finally:
        N.Bus = original_bus
    for _ in range(row['cycle']):
        UI.key(m, 32)
    assert UI.menu_name(m)[0] == row['name'], (row, UI.menu_name(m)[0])
    menu_selected = N.get(m, 'SelectedCharacter')
    assert menu_selected == row['raw']
    start = UI.key(m, 16)
    assert N.get(m, 'CrossoverMenuState') == 0
    N.invoke(m, 'NativeRareGameMenuRoutineCore::ChkContinue',
             a=start['A'], x=start['X'], y=start['Y'], p=start['P'])
    N.invoke(m, 'PauseRoutine', a=0)
    selected = N.get(m, 'SelectedCharacter')
    # Getsu's existing native confirmation promotes Simon's pending profile
    # to owner42. Every other resolved identity must remain unchanged.
    assert selected == menu_selected or (row['name'] == 'GETSU FUMA'
                                         and (menu_selected, selected) == (5, 42))
    idle = F.address(bundle, 'IdleLoop')
    loop = F.address(bundle, 'GameLoop')
    assert bytes(m[idle + 9:idle + 12]) == b'\x20' + loop.to_bytes(2, 'little')
    active, ticks, trace = None, 0, deque(maxlen=12)

    def state():
        return dict(x=N.get(m, 'Player_X_Position') + 256 * N.get(m, 'Player_PageLoc'),
                    y=N.get(m, 'Player_Y_Position'), source=N.get(m, 'Player_State'),
                    engine=N.get(m, 'GameEngineSubroutine'), lives=N.get(m, 'NumberofLives'),
                    mode=N.get(m, 'OperMode'), task=N.get(m, 'OperMode_Task'),
                    selected=N.get(m, 'SelectedCharacter'))

    for epoch in range(700):
        now = state()
        if (now['mode'], now['task'], now['engine']) == (1, 3, 8):
            assert now['selected'] == selected, (row['name'], 'identity changed', now)
            assert now['lives'] == 2, (row['name'], 'life lost', now)
            assert N.get(m, 'WorldNumber') == N.get(m, 'LevelNumber') == 0
            assert N.get(m, 'CheatInvincible') == N.get(m, 'CheatStartLevel') == 0
            if active is None:
                active = dict(epoch=epoch, **now)
                assert any(m[F.address(bundle, 'Block_Buffer_1'):F.address(bundle, 'Block_Buffer_1') + 416])
            if ticks >= 60:
                return dict(passed=True, name=row['name'], slot=row['slot'], cycle=row['cycle'],
                            active=active, opening_updates=ticks, final=now,
                            moved_right=now['x'] > active['x'],
                            scope='CPU active1-1 constructor plus60 ordinary input updates; no cadence/art/fullstage claim')
            pad = 0 if ticks < 4 else 1 if ticks < 36 else 129 if ticks < 52 else 1
            ticks += 1
        else:
            assert active is None, (row['name'], 'left active gameplay during opening', epoch, now, list(trace))
            pad = 0
        if epoch % 8 == 0:
            trace.append(dict(epoch=epoch, ticks=ticks, **now))
        m.controller_pad = pad
        F.clear_logs(m)
        N.consume(m)
        # Reuse the earned-pickup checker's literal native IdleLoop frame
        # boundary. The game's stack scheduler intentionally returns at
        # IdleLoop+12/SP252, rather than at a synthetic C-style call return.
        c = N.NesMPU(memory=m, pc=idle)
        c.sp, c.p = 255, 0x31
        c.stPushWord(0xe33b)
        # Prince's real forced-blank compressed constructor is substantially
        # longer than a rendered frame. Native Mesen startup already passes;
        # use the actual common cold qualification's four-million-op bound.
        for _ in range(4_000_000 if active is None else 400000):
            if (c.pc, c.sp) == (idle + 12, 252):
                break
            assert m[c.pc], (row['name'], 'BRK', hex(c.pc), m.rawtags, now)
            c.step()
        else:
            raise AssertionError((row['name'], 'GameLoop bound', hex(c.pc), now))
        assert not m.blocked
    raise AssertionError((row['name'], 'No active stage/opening bound', state(), list(trace)))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--first-slot', type=int, default=0)
    p.add_argument('--last-slot', type=int, default=31)
    p.add_argument('--name', help='Optional one-name fixture/scheduler diagnosis')
    p.add_argument('--rom', type=Path, default=F.ROM)
    p.add_argument('--expected', default=F.PIN)
    args = p.parse_args()
    assert 0 <= args.first_slot <= args.last_slot < 32
    raw = args.rom.read_bytes()
    assert sha256(raw).hexdigest() == args.expected
    # The compact menu inventory bundle deliberately omits local labels.
    # Continue/IdleLoop need the full retained native symbol table instead.
    bundle = F.Symbols.bundle()
    bundle['raw'] = raw
    for symbol in ('NativeRareGameMenuRoutineCore::ChkContinue', 'PauseRoutine', 'GameLoop', 'IdleLoop'):
        assert symbol in bundle['syms'], ('Incomplete active-stage symbols', symbol)
    inventory = C.inventory(raw)
    unique = {(row['slot'], row['raw'], row['name']): row for row in inventory['rows']}
    rows = [row for row in unique.values() if args.first_slot <= row['slot'] <= args.last_slot
            and (args.name is None or args.name == row['name'])]
    assert rows
    results = []
    for row in rows:
        print('Actual CPU stage ingress', row['slot'], row['cycle'], row['name'], flush=True)
        try:
            result = stage(bundle, row)
        except Exception as error:
            result = dict(passed=False, name=row['name'], slot=row['slot'], cycle=row['cycle'],
                          error=repr(error), traceback=traceback.format_exc(limit=4))
        results.append(result)
        print(json.dumps(result, sort_keys=True), flush=True)
    passed = all(row['passed'] for row in results)
    print(json.dumps(dict(passed=passed, source_only=True, outputs_written=0, ROM_written=False,
                          ROM_SHA256=args.expected, source_SHA256=sha256(Path(__file__).read_bytes()).hexdigest(),
                          first_slot=args.first_slot, last_slot=args.last_slot, cases=len(results),
                          passing=sum(row['passed'] for row in results),
                          failures=[row for row in results if not row['passed']]), sort_keys=True), flush=True)
    raise SystemExit(0 if passed else 1)


if __name__ == '__main__':
    main()
