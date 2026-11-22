"""Bounded in-memory py65 behavior checks; no donor oracle or ROM output."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import argparse
import json

from py65.devices.mpu6502 import MPU
import compose_sonic_original_motion_1122 as C

STOP = 0x5b00
NATIVE_FRAME = 0xbbb0
COUNTS = Counter()


class Memory(list):
    active = False

    def __setitem__(self, at, value):
        if self.active and isinstance(at, int):
            assert (0xc000 <= at < 0xc140 or 0xc200 <= at < 0xc2b8 or 0xc300 <= at < 0xc31a or
                    0xc340 <= at < 0xc37b or
                    0x17b <= at <= 0x1e0 or at in (0xb583, 0xb584, 0xb593, 0xb594) or
                    at in getattr(self, 'native_writes', ())), ('Unowned motion/frame write', hex(at))
        super().__setitem__(at, value)


def signed(m, at):
    value = int.from_bytes(bytes(m[at:at+3]), 'little')
    return value - (1 << 24) if value & (1 << 23) else value


def put24(m, at, value):
    m[at:at+3] = (value & 0xffffff).to_bytes(3, 'little')


def invoke(m, pc=NATIVE_FRAME, a=0):
    cpu = MPU(memory=m, pc=pc)
    cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = a, 73, 109, 0x30, 224
    cpu.stPushWord(STOP-1)
    minimum = cpu.sp
    m.active = True
    try:
        for _ in range(20000):
            if cpu.pc == STOP:
                break
            assert 0xa000 <= cpu.pc < 0xbfe0 or 0xd000 <= cpu.pc < 0xdc00, hex(cpu.pc)
            assert m[cpu.pc], ('Motion BRK', hex(cpu.pc))
            minimum = min(minimum, cpu.sp)
            cpu.step()
        else:
            raise AssertionError(('Bounded motion invocation', hex(cpu.pc)))
    finally:
        m.active = False
    assert cpu.sp == 224
    COUNTS['calls'] += 1
    COUNTS['cycles'] += cpu.processorCycles
    COUNTS['max_cycles'] = max(COUNTS['max_cycles'], cpu.processorCycles)
    COUNTS['minimum_SP'] = min(COUNTS.get('minimum_SP', 224), minimum)
    return cpu


def floor(m, ceiling=False):
    x = int.from_bytes(bytes(m[0xc071:0xc073]), 'little')
    left = max(0, (x-128)//16)
    end = left+24
    for at, value in ((0x721, 255), (0x722, 0), (0x728, end//16), (0x729, end&15),
                      (0x4a0, end&31), (0x71d, left//16), (0x71f, (left&15)*16)):
        m[at] = value
    m[0x300:0x4a0] = bytes(416)
    for column in range(left, end):
        m[0x300+(column//16&1)*208+11*16+(column&15)] = 0x54
        if ceiling:
            m[0x300+(column//16&1)*208+6*16+(column&15)] = 0x54


def memory(raw):
    m = Memory([0]*65536)
    m[0xa000:0xc000] = C.kernel(raw)
    for pc, n in ((0xd000, 328), (0xd400, 333), (0xd800, 334)):
        m[pc:pc+1024] = C.page(raw, n)
    m[0xef36:0xf036] = raw[16+127*8192+0xf36:16+127*8192+0x1036]
    assert m[0xef36+0x54] & 1
    m[0xc0b4] = 1
    m[0xc030], m[0xc041], m[0xc042] = 0x88, 24, 32
    m[0xc0a0] = 255
    put24(m, 0xc070, 64*256)
    put24(m, 0xc073, 176*256)
    floor(m)
    return m


def clone(m):
    return Memory(m)


def frame(m, pad, ceiling=False):
    floor(m, ceiling)
    m[0xc0a8] = pad
    m[0xc092] = (m[0xc092]+1)&255
    cpu = invoke(m)
    assert cpu.p & 1 and m[0xc116] == 0, ('Rejected fixture frame', pad, m[0xc116])
    return dict(x=signed(m, 0xc070), foot=signed(m, 0xc073)+256*m[0xc042],
                vx=signed(m, 0xc020), vy=signed(m, 0xc060), flags=m[0xc030],
                charge=m[0xc098], height=m[0xc042], cue=m[0xc05e])


def reset_case(raw):
    m = memory(raw)
    m[0xc047], m[0xc097], m[0xc098] = 17, 255, 6
    invoke(m, C.program()['symbols']['OriginalMotionReset'])
    assert (m[0xc047], m[0xc097], m[0xc098]) == (0, 0, 0)


def walking(parent, candidate):
    old, new = memory(parent), memory(candidate)
    for pad in [0]*32 + [1]*60 + [0]*40 + [2]*60 + [0]*32:
        a, b = frame(old, pad), frame(new, pad)
        assert all(a[k] == b[k] for k in ('x', 'foot', 'vx', 'height')), ('Ordinary gait changed', pad, a, b)
    return dict(updates=224, incumbent_stationary_and_both_walk_directions_exact=True)


def jumping(raw):
    rows = []
    for hold in (1, 20, 120):
        m = memory(raw)
        for _ in range(8): frame(m, 0)
        foot = 208*256
        minimum = foot
        events, landed, airborne = 0, None, False
        for tick in range(160):
            s = frame(m, 128 if tick < hold else 0)
            minimum = min(minimum, s['foot'])
            events += s['cue'] == 1
            airborne |= not bool(s['flags']&128)
            if airborne and s['flags']&128 and landed is None:
                landed = tick
        assert landed is not None and events == 1, ('One jump per press', hold, landed, events)
        rows.append(dict(hold=hold, height=(foot-minimum)/256, landing_update=landed, jump_events=events))
    assert rows[1]['height'] > rows[0]['height']+24
    assert rows[2]['height'] >= rows[1]['height']
    return rows


def charging(raw):
    m = memory(raw)
    for _ in range(8): frame(m, 0)
    x0 = signed(m, 0xc070)
    frame(m, 4)
    for level in range(1, 7):
        s = frame(m, 132)
        assert s['charge'] == level and s['vx'] == 0 and s['cue'] != 1
        for _ in range(5):
            s = frame(m, 132)
            assert s['charge'] == level and s['x'] == x0 and s['foot']//256 == 208, s
        frame(m, 4)
    s = frame(m, 132)
    assert s['charge'] == 6
    s = frame(m, 0)
    assert s['charge'] == 0 and s['vx'] == int(6.5*256) and s['x'] > x0
    assert s['flags']&1 and s['height'] == 24 and s['cue'] != 1
    speed = s['vx']
    s = frame(m, 0)
    assert 0 < s['vx'] < speed
    s = frame(m, 2)
    assert 0 < s['vx'] < speed-6
    # Injury cannot turn suppressed input into a charge release.
    q = memory(raw)
    for pad in (0, 4, 132): frame(q, pad)
    q[0xc34f] = 0x40
    q[0xc030] &= 0xfa
    s = frame(q, 0)
    assert s['charge'] == 0 and s['vx'] == 0 and s['cue'] != 1
    # Running Down+A rolls and jumps; charging is a stationary action.
    q = memory(raw)
    for _ in range(40): frame(q, 1)
    s = frame(q, 133)
    assert s['charge'] == 0 and s['vx'] > 0 and s['vy'] < 0 and s['cue'] == 1
    # Facing-left charge has the same magnitude and opposite displacement.
    q = memory(raw)
    q[0xc030] |= 2
    start = signed(q, 0xc070)
    for pad in (4, 132, 4, 132, 4, 132, 4): frame(q, pad)
    s = frame(q, 0)
    assert s['charge'] == 0 and s['vx'] == -5*256 and s['x'] < start and s['cue'] != 1
    return dict(levels=6, held_button_does_not_add_charge=True,
                maximum_launch_speed=6.5, release_once=True, injury_cancels=True,
                moving_down_A_remains_jump=True, left_launch_speed=-5)


def rollback(raw):
    m = memory(raw)
    for pad in (0, 4, 132, 4): frame(m, pad)
    m[0xc0a8] = 132
    m[0x721] = 0
    old = bytes(m[0xc000:0xc0b4])
    smc = [m[at] for at in (0xb583, 0xb584, 0xb593, 0xb594)]
    cpu = invoke(m)
    assert not cpu.p&1 and m[0xc116] != 0
    assert bytes(m[0xc000:0xc0b4]) == old
    assert [m[at] for at in (0xb583, 0xb584, 0xb593, 0xb594)] == smc
    return dict(actual_native_frame_rejection=True, complete_existing_snapshot_restored=True,
                new_charge_and_button_edges_restored=True)


def ceiling_case(raw):
    m = memory(raw)
    for _ in range(8): frame(m, 0, ceiling=True)
    contact, events = None, 0
    for tick in range(100):
        s = frame(m, 128, ceiling=True)
        events += s['cue'] == 1
        assert int.from_bytes(bytes(m[0xc074:0xc076]), 'little') >= 144
        if m[0xc122] and contact is None:
            contact = tick
            assert m[0xc058] == 0 and s['vy'] >= 0
        if contact is not None:
            assert s['vy'] >= 0, ('Held A restarted ascent after ceiling', tick, s)
    assert contact is not None and events == 1
    return dict(actual_upward_native_contact=True, existing_ceiling_helper_clears_jump_latch=True,
                held_A_does_not_restart_ascent=True, contact_update=contact, jump_events=events)


def host_contract(parent, raw):
    # Current a6 supplies execution bytes. Existing strict metadata supplies
    # native symbols only; no old source factory or packet builder is run.
    import current_sonic_stock_binding_1122 as Metadata
    from sonic_sms_native_host_services_1110 import HOST
    ref = Metadata.reference(parent)
    b = Metadata.Sonic.bindings(ref)['bundle']
    address = lambda name: Metadata.W.address(b, name)
    m = memory(raw)
    m.native_writes = {address(name) for name in HOST}
    m.native_writes.add(address('PlayerSize'))
    put = lambda name, value: m.__setitem__(address(name), value)
    get = lambda name: m[address(name)]
    for name, value in dict(GameEngineSubroutine=8, GamePauseStatus=0, TimerControl=0,
                            FrameCounter=0, SavedJoypadBits=0, AreaType=1,
                            Player_X_Position=64, Player_PageLoc=0,
                            Player_Y_Position=176, Player_Y_HighPos=1,
                            WorldNumber=0, LevelNumber=0, AreaAddrsLOffset=0).items():
        put(name, value)
    m[0xc119:0xc122] = bytes((1, 0, 0, 64, 0, 176, 1, 0, 0))
    main = int.from_bytes(C.page(raw, 328)[48:50], 'little')
    assert main == 0xbd7a
    ctor = int.from_bytes(C.page(raw, 328)[58:60], 'little')
    m[0xc047], m[0xc097], m[0xc098] = 17, 255, 6
    invoke(m, ctor)
    assert (m[0xc047], m[0xc097], m[0xc098]) == (0, 0, 0)
    duplicates = 0
    for epoch, pad in ((254, 4), (255, 132), (0, 4)):
        floor(m)
        put('FrameCounter', epoch)
        put('SavedJoypadBits', pad)
        old_tick = m[0xc092]
        assert invoke(m, main).p&1 and m[0xc092] == (old_tick+1)&255
        old = bytes(m[0xc000:0xc140]), tuple(get(name) for name in HOST)
        assert invoke(m, main).p&1
        assert old == (bytes(m[0xc000:0xc140]), tuple(get(name) for name in HOST))
        duplicates += 1
    assert m[0xc098] == 1 and m[0xc097] == 4
    freezes = 0
    for name, value in (('GamePauseStatus', 1), ('TimerControl', 255), ('GameEngineSubroutine', 7)):
        before = bytes(m[0xc000:0xc0b4])
        put(name, value)
        invoke(m, main)
        assert bytes(m[0xc000:0xc0b4]) == before and m[0xc11a] == 0
        put(name, 8 if name == 'GameEngineSubroutine' else 0)
        tick = m[0xc092]
        invoke(m, main)
        assert m[0xc092] == (tick+1)&255
        freezes += 1
    # The real host wrapper rolls back its tick and pad around a failed sweep.
    put('FrameCounter', 1)
    put('SavedJoypadBits', 132)
    m[0x721] = 0
    before = bytes(m[0xc000:0xc0b4])
    x, y = get('Player_X_Position'), get('Player_Y_Position')
    cpu = invoke(m, main)
    assert cpu.p&1 and m[0xc116] != 0
    assert bytes(m[0xc000:0xc0b4]) == before
    assert (get('Player_X_Position'), get('Player_Y_Position')) == (x, y)
    return dict(actual_a6_host_entry=main, duplicate_calls_unchanged=duplicates,
                actual_constructor_resets_new_fields=True,
                epoch_wrap255_to0=True, freeze_and_same_epoch_resume=freezes,
                failed_sweep_restores_tick_pad_charge_edges_and_native_position=True,
                native_symbols_only_from_strict_9826_reference=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', action='store_true', help='Also load strict retained native symbols and test the real host wrapper/constructor.')
    args = parser.parse_args()
    parent = C.ROM.read_bytes()
    candidate, record = C.proposal(parent)
    reset_case(candidate)
    result = dict(passed=True, composition=record, walking=walking(parent, candidate),
                  jumping=jumping(candidate), charging=charging(candidate), rollback=rollback(candidate),
                  ceiling=ceiling_case(candidate),
                  host_contract=host_contract(parent, candidate) if args.host else None,
                  CPU=dict(COUNTS), output_files=0, Mesen=False,
                  scope='Actual in-memory candidate6502 and native16px swept floor contacts. Explicit flat/parser fixtures, not a native stage/controller/cold/interrupt or physical-cadence qualification.')
    print('RESULT '+json.dumps(result, separators=(',', ':')), flush=True)


if __name__ == '__main__':
    def deny(*a, **kw): raise AssertionError('Motion check attempted an output/process')
    with patch.object(Path, 'write_bytes', deny), patch.object(Path, 'write_text', deny), patch('subprocess.Popen', deny):
        main()
