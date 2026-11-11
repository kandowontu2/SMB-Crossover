"""Link and exercise Steve's Shatterhand movement through the real Main caller."""

import argparse
from collections import Counter
import json

import check_steve_shatterhand_live_1111 as Live
import check_steve_shatterhand_motion_carrier_1111 as Carrier
import compose_steve_shatterhand_1111 as S
import trace_steve_shatterhand_motion_1111 as Motion


BRIDGE = S.H.ROOT / 'tools/reference/steve_shatterhand_move_live_1111.s'
LAYOUT = {'BRIDGE': (0xdc00, 0x2c0), 'MOTION': (0xdec0, 0x120)}
NATIVE = ('OperMode', 'OperMode_Task', 'GameEngineSubroutine', 'GamePauseStatus',
          'SwimmingFlag', 'JumpspringAnimCtrl', 'MmDeathFlag', 'NmiDisable',
          'FamilyMainCommit', 'Player_State', 'JnEnsure', 'JnInputs', 'JnEffectiveTier',
          'PlayerFacingDir', 'Player_X_Position', 'Player_PageLoc', 'Player_Y_Position',
          'Player_Y_HighPos', 'Player_X_Speed', 'Player_Y_Speed', 'Player_XSpeedAbsolute',
          'Player_X_Scroll', 'XgWallContact', 'JnPressed', 'SavedJoypadBits', 'JnAttack',
          'Square1SoundQueue', 'CrouchingFlag', 'MmVY', 'MmVX', 'MmXFraction', 'MmYFraction',
          'Sfx_BigJump')
HOST = {'SteveHostReady': 0x5c8d, 'SteveHostXFrac': 0x5c8e, 'SteveHostYFrac': 0x5c8f,
        'SteveHostLastX': 0x5c9b, 'SteveHostLastPage': 0x5c9c,
        'SteveHostLastY': 0x5c9d, 'SteveHostLastYPage': 0x5c9e}
PRELUDE = bytes.fromhex('ee035cad045cf003ce045cad3e5f0aa9002a8d5b07a900'
                        '8d59078db0688d006b8d0f6c8d17078d14608dc1688dc068a5758d095c8db568')


def proposal(raw):
    assert S.C.digest(raw) == S.LIVE_PIN
    bundle = S.W.Symbols.bundle()
    aliases = {name: S.W.address(bundle, name) for name in NATIVE}
    assert aliases['XgWallContact'] == 0x6eba and aliases['JnPressed'] == 0x5c02
    assert S.code(raw, 96, 0xa2cb, 9) == bytes.fromhex('200ea020f5a020c8a0')
    assert S.code(raw, 96, 0xa2d4, len(PRELUDE)) == PRELUDE
    aliases.update(HOST)
    aliases.update({f'SteveMove{name}': address for name, address in Motion.FIELDS.items()})
    definitions = ''.join(f'{name} = ${address:04x}\n' for name, address in aliases.items())
    bridge = BRIDGE.read_text().replace('StockPreludeBytes', ','.join(map(str, PRELUDE)))
    linked = S.H.assemble(definitions + bridge + Motion.SOURCE.read_text(), LAYOUT)
    worker = linked['images']['BRIDGE'].ljust(LAYOUT['BRIDGE'][1], b'\xea') + linked['images']['MOTION']
    punch = S.link(bundle, movement_entry=linked['symbols']['SteveLiveMovement'])
    original = S.link(bundle)['images']
    changed = {name: code for name, code in punch['images'].items() if original[name] != code}
    assert changed.keys() == {'COMBAT', 'BIRTH'}
    candidate, cookie, _ = Carrier.proposal(raw, worker=worker, residents=changed)
    return candidate, linked, punch, cookie


def snapshot(m):
    x, y = Live.player(m)
    return (x * 16 + m[HOST['SteveHostXFrac']], y * 16 + m[HOST['SteveHostYFrac']],
            m[Motion.FIELDS['State']], Motion.signed(m[Motion.FIELDS['VX']]),
            Motion.signed(m[Motion.FIELDS['VY']]), S.N.get(m, 'PlayerFacingDir'),
            S.N.get(m, 'Player_State'), S.N.get(m, 'CrouchingFlag'), S.N.get(m, 'XgWallContact'))


def run(seed, program, pads, *, debug=False):
    m = S.C.Vector.clone(seed)
    symbols = program['symbols']
    calls = Counter()
    rows = []
    for update, pad in enumerate(pads, 1):
        m.controller_pad = pad

        def observe(memory, cpu):
            if (memory.rawtags[2], cpu.pc) == (2, symbols['SteveLiveMovement']):
                calls[f'caller_{cpu.y:02x}'] += 1
            if (memory.rawtags[2], cpu.pc) == (2, symbols['SteveMotionProject']):
                calls['project'] += 1
            if (memory.rawtags[1], cpu.pc) == (0xe0, 0xa2cb):
                calls['legacy'] += 1

        S.C.Game.frame(m, observe)
        rows.append(snapshot(m))
        if debug:
            print(update, pad, rows[-1], flush=True)
    assert calls == {'caller_e0': len(pads), 'caller_d6': len(pads), 'project': len(pads)}, calls
    assert S.N.get(m, 'NumberofLives') == 2 and Live.mode(m) == S.PLAY
    return m, rows


def flat_controller(seed, program, *, debug=None):
    result = {}
    expected = {'walk_right': (204, 0), 'walk_left': (-204, 0), 'reverse': (115, 0),
                'jump_tap': (0, 722), 'jump_hold': (0, 1092), 'jump_right': (333, 1092),
                'crouch': (0, 0), 'crouch_from_walk': (326, 0), 'down_a_from_idle': (0, 1092),
                'jump_repress': (0, 870), 'both_directions': (-66, 0)}
    x, y = Live.player(seed)
    for name in (debug,) if debug else Motion.PADS:
        pads = [int(f'{pad:08b}'[::-1], 2) for pad in Motion.PADS[name]]
        m, rows = run(seed, program, pads, debug=bool(debug))
        dx = rows[-1][0] - x * 16
        apex = y * 16 - min(row[1] for row in rows)
        assert (dx, apex) == expected[name], (name, x, y, dx, apex, rows)
        assert all((row[2] == 3) == bool(row[7]) for row in rows), (name, rows)
        result[name] = dict(updates=len(rows), dx_Q4=dx, apex_Q4=apex, terminal=Live.player(m))
    return result


def foreign(raw, candidate):
    result = {}
    for variant, name in enumerate(('Mike', 'Jay')):
        old, old_open = Live.opening(raw, variant)
        new, new_open = Live.opening(candidate, variant)
        assert old_open == new_open == 167
        pads = [0] * 6 + [64] * 12 + [1] * 19 + [129] * 9 + [2] * 15 + [0] * 10 + [64] * 9
        for pad in pads:
            old.controller_pad = new.controller_pad = pad
            S.C.Game.frame(old)
            S.C.Game.frame(new)
            before, after = S.C.Vector.app(old), S.C.Vector.app(new)
            if variant:
                before, after = before[:3] + before[4:], after[:3] + after[4:]
            assert before == after and old.vram == new.vram and old.chr_latches == new.chr_latches, (name, pad)
        result[name] = dict(updates=len(pads), player=Live.player(new), reads=new.ppu_reads)
    return result


def first_pipe(seed, program, punch):
    m = S.C.Vector.clone(seed)
    first = Live.natural_goomba(m, punch)
    wall_at = None
    symbols = program['symbols']
    cost = []

    def tick(pad):
        m.controller_pad = pad
        started = None

        def observe(memory, cpu):
            nonlocal started
            if memory.rawtags[2] != 2:
                return
            if cpu.pc == symbols['SteveLiveMovement'] and cpu.y == 0xe0:
                started = cpu.processorCycles
            if cpu.pc == symbols['SteveMovementClaim']:
                assert started is not None
                cost.append(cpu.processorCycles - started + 8)

        S.C.Game.frame(m, observe)
        assert Live.mode(m) == S.PLAY and S.N.get(m, 'NumberofLives') == 2, Live.player(m)

    for update in range(320):
        x, _ = Live.player(m)
        enemies = Live.goombas(m)
        close = any(0 < enemy[1] - x <= 38 for enemy in enemies)
        pad = 1 | (64 if close and not m.controller_pad & 64 else 0)
        tick(pad)
        if S.N.get(m, 'XgWallContact') and Live.player(m)[0] > 400:
            wall_at = Live.player(m)
            break
    assert wall_at and wall_at[0] < 448, (wall_at, Live.player(m), Live.goombas(m))
    assert S.N.get(m, 'Player_X_Speed') == 0 and S.N.get(m, 'Player_X_Scroll') == 0
    tick(1)
    assert m[Motion.FIELDS['DX']] == 0 and m[Motion.FIELDS['VX']] == 2, snapshot(m)
    assert Live.player(m) == wall_at

    apex = wall_at[1]
    for crossing in range(100):
        tick(129 if crossing < 48 else 1)
        x, y = Live.player(m)
        apex = min(apex, y)
        if x >= 488 and y == 176 and S.N.get(m, 'Player_State') == 0:
            break
    else:
        raise AssertionError(('first native pipe crossing', wall_at, Live.player(m), apex, snapshot(m)))
    assert S.N.get(m, 'ScreenLeft_PageLoc') > 0
    return dict(first_goomba=first, wall_at=wall_at, crossing_updates=crossing+1, apex=apex,
                terminal=Live.player(m), health=S.N.get(m, 'JnHealth'),
                bridge_cycles=(min(cost), max(cost)), timed_updates=len(cost))


def authentication(seed, program):
    entry = program['symbols']['SteveLiveMovement']
    for bank in (2, 3):
        for index in range(16):
            m = S.C.Vector.clone(seed)
            m.ram[bank][0x1fe0 + index] ^= 1
            m.controller_pad = 129
            stock = []

            def observe(memory, cpu):
                assert (memory.rawtags[2], cpu.pc) != (2, entry), (bank, index)
                if (memory.rawtags[1], cpu.pc) == (0xe0, 0xa2cb):
                    stock.append(cpu.pc)

            S.C.Game.frame(m, observe)
            assert stock == [0xa2cb] and not m[HOST['SteveHostReady']]
    return 32


def nonwalking(parent, seed):
    result = {}
    for values in ({'SwimmingFlag': 1}, {'Player_State': 3}, {'GameEngineSubroutine': 7},
                   {'MmDeathFlag': 1}, {'JumpspringAnimCtrl': 1}):
        old, new = (S.C.Vector.clone(m) for m in (parent, seed))
        for m in (old, new):
            S.N.put(m, SavedJoypadBits=1, **values)
            S.C.Vector.call(m, 'JnMovementDispatch')
        before, after = S.C.Vector.app(old), S.C.Vector.app(new)
        assert before[:3] + before[4:] == after[:3] + after[4:], (values, Live.player(old), Live.player(new))
        result.update(values)
    return result


def interrupts(seed, program):
    symbols = program['symbols']
    points = {symbols[name] for name in ('SteveLiveMovement', 'SteveMoveStep', 'ImportMotion',
              'SteveMotionProject', 'SteveMotionFinish', 'SteveIntegrateQ4', 'SteveMovementClaim')}
    points.add(symbols['SteveMoveMikeCall'] + 3)
    found = set()

    def state(m, cpu):
        return (tuple(bytes(ram) for ram in m.ram), tuple(m.rawtags), bytes(m[3:11]),
                bytes(m[0x15a:0x17b]), bytes(m[0x101 + cpu.sp:0x200]), bytes(m[0x200:0x300]),
                bytes(m[0x5c80:0x5c9f]))

    def observe(memory, cpu):
        if memory.rawtags[2] != 2 or cpu.pc not in points - found:
            return
        if cpu.pc == symbols['SteveLiveMovement'] and cpu.y != 0xe0:
            return
        for kind in ('NMI', 'IRQ'):
            m, vector = S.C.Vector.clone(memory, cpu)
            before = state(m, vector)
            assert S.C.Vector.isr(m, vector, kind) == 'returned'
            assert before == state(m, vector), (hex(cpu.pc), kind)
        found.add(cpu.pc)

    m = S.C.Vector.clone(seed)
    for pad in (0, 129, 129, 1):
        m.controller_pad = pad
        S.C.Game.frame(m, observe)
    assert found == points, points - found
    return dict(NMI=len(found), IRQ=len(found))


def rebase(raw, candidate):
    from check_prince_exposed_brick_idle_1111 import replace_workers, source_workers
    from deliver_prince_exposed_brick_idle_1111 import PIN, recover_parent
    from deliver_steve_move_1111 import PIN as MOVED, recover_parent as without_movement

    installed = S.Donor.HOST.read_bytes()
    if S.C.digest(installed) == S.LIVE_PIN:
        return None
    if S.C.digest(installed) == MOVED:
        installed = without_movement(installed)
    assert S.C.digest(installed) == PIN and recover_parent(installed) == raw
    old, new = source_workers()
    combined, _ = replace_workers(candidate, old, new)
    movement_changes = {i for i, (old, new) in enumerate(zip(raw, candidate, strict=True)) if old != new}
    prince_changes = {i for i, (old, new) in enumerate(zip(raw, installed, strict=True)) if old != new}
    assert not movement_changes & prince_changes
    assert bytes(combined[i] for i in movement_changes) == bytes(candidate[i] for i in movement_changes)
    assert bytes(combined[i] for i in prince_changes) == bytes(installed[i] for i in prince_changes)
    return dict(candidate_SHA256=S.C.digest(combined), steve_bytes=len(movement_changes),
                prince_bytes=len(prince_changes), intersection=0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--debug', choices=Motion.PADS)
    args = parser.parse_args()
    raw = Carrier.pinned_parent()
    candidate, program, punch, cookie = proposal(raw)
    print('Live candidate', S.C.digest(candidate), program['used'], cookie.hex(), flush=True)
    seed, count = Live.opening(candidate, 2)
    assert count == 167 and S.C.Common.headers(seed) == (cookie,) * 2 and seed.ppu_reads == 16400
    prints = dict(interrupts=interrupts(seed, program), rebase=rebase(raw, candidate))
    print('Movement vectors and rebase', json.dumps(prints, sort_keys=True), flush=True)
    print('Controller movement', json.dumps(flat_controller(seed, program, debug=args.debug), sort_keys=True), flush=True)
    if args.debug:
        return
    left, _ = run(seed, program, [2])
    prints.update(punch_right=Live.punch_trace(S.C.Vector.clone(seed), punch),
                  punch_left=Live.punch_trace(left, punch),
                  native_first_pipe=first_pipe(seed, program, punch),
                  foreign=foreign(raw, candidate),
                  corrupt_headers=authentication(seed, program),
                  nonwalking=nonwalking(Live.opening(raw, 2)[0], seed))
    print(json.dumps(dict(passed=True, output_files=0, **prints), sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
