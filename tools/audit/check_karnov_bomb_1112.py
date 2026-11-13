"""Qualify Karnov's installed carrier, original Bomb phases and native contact."""
import argparse
from collections import Counter
from itertools import product
import json

import check_metal_head_bridge_1112 as Cpu
import compose_karnov_bomb_1112 as Compose
from recover_karnov_art_1101_v1 import Memory as DonorMemory

M = Cpu.M


def cold(raw, cookie, *, readback=None):
    bundle = Cpu.Flower.Host.C.Start.W.bundle(raw)
    model = M.fresh(bundle)
    for bank in (2, 3):
        model.ram[bank][:] = bytes((i * 17 + bank * 29 + 7) & 255 for i in range(8192))
    model.raw_page(1, 151)
    model.raw_page(2, 215)
    M.put(model, SelectedCharacter=34, FmAlts=1, OperMode=1, OperMode_Task=3,
          GameEngineSubroutine=8, FamilyMainCommit=1, DisableScreenFlag=1,
          Mirror_PPUMASK=0, Mirror_PPUCTRL=160, NmiDisable=255, CurrentBank=151,
          CurrentBankC=215, HorizontalScroll=73, VerticalScroll=32,
          ReloadCHRBank=7, X5WideChrActive=0)
    model.ppuctrl = 160
    for i, value in enumerate((18, 20, 21, 22, 23, 24, 25, 26, 4, 5, 6, 7)):
        model[M.address(bundle, 'CurrentCHRBank') + i] = value
        model[M.address(bundle, 'X5ChrMode') + i] = 0
    before = model.ppu_reads
    if readback is not None:
        bank, offset, expected = readback
        native_bus = type(model)
        class Fault(native_bus):
            def __getitem__(self, at):
                value = native_bus.__getitem__(self, at)
                if (isinstance(at, int) and 0x8000 <= at < 0xe000 and at & 0x1fff == offset
                        and self.rawtags[(at - 0x8000) // 8192] == bank
                        and self.ppu_reads > before + 1000 and value == expected and not self.failed):
                    self.failed = True
                    self.failure_read = self.ppu_reads
                    return value ^ 1
                return value
        model.__class__ = Fault
        model.failed = False
    load = M.invoke(model, 'KrLoad', p=0x21)
    if readback is not None:
        assert model.failed and not load['P'] & 1, (readback, model.failed, load)
        assert all(bytes(model.ram[b][0x1fe0:0x1ff0]) != cookie for b in (2, 3))
        return dict(bank=bank, offset=offset, PPU_read=model.failure_read - before,
                    carry_clear=True, both_headers_unpublished=True)
    assert load['P'] & 1 and model.ppu_reads - before == 23064, (load, model.ppu_reads - before)
    assert all(bytes(model.ram[b][0x1fe0:0x1ff0]) == cookie for b in (2, 3))
    for name, bank, offset, length in (('actor', 3, 0, 8192), ('options', 2, 0x1600, 2048), ('combat', 2, 0x900, 1280)):
        at = Compose.CHR + 1024 * Compose.OWNED[name][0]
        assert bytes(model.ram[bank][offset:offset + length]) == raw[at:at + length], name
    M.put(model, FrameCounter=0,
          GamePauseStatus=0, Player_X_Position=120, Player_PageLoc=0,
          Player_Y_Position=176, Player_Y_HighPos=1, Player_Y_Speed=0,
          CurrentPlayer=0, NumberofLives=2, SavedJoypadBits=0,
          ScreenLeft_X_Pos=0, ScreenLeft_PageLoc=0, ScreenRight_X_Pos=255,
          ScreenRight_PageLoc=0, TimerControl=0, AreaType=1)
    Cpu.Flower.Host.terrain(model, lambda x, y: 0x61 if y >= 208 else 0)
    constructed = M.invoke(model, 'HuFresh', p=0x21)
    assert constructed['P'] & 1 and model.ram[2][0x810] == 0xa7, constructed
    M.put(model, DisableScreenFlag=0, Mirror_PPUMASK=24)
    return model, dict(PPU_reads=model.ppu_reads - before, minimum_SP=load['minimum_SP'],
                       complete_headers=cookie.hex(), actual_cold_constructor=True)


def input_step(model, pad, epoch):
    M.put(model, FrameCounter=epoch & 255, SavedJoypadBits=pad, SavedJoypad1Bits=pad,
          A_B_Buttons=pad & 192, Left_Right_Buttons=pad & 3, Up_Down_Buttons=pad & 12)
    result = M.invoke(model, 'HuMovement', p=0x21)
    assert result['P'] & 1, (pad, epoch, result)
    return result


def pickup(model, *, cycle=1):
    M.put(model, ObjectOffset=5, PlayerStatus=0)
    model.ram[2][0x65], model.ram[2][0x860] = 2, cycle
    for name, value in dict(Enemy_Flag=1, Enemy_State=128, Enemy_ID=46,
                            PowerUpType=1, Enemy_X_Position=120, Enemy_PageLoc=0,
                            Enemy_Y_Position=176, Enemy_Y_HighPos=1).items():
        model[M.address(model.bundle, name) + 5] = value
    result = M.invoke(model, 'HandlePowerUpCollision', x=5, p=0x21)
    assert M.get(model, 'Enemy_Flag', 5) == 0 and model.ram[2][0xbb] == 1, result
    assert model.ram[2][0x8f] & 2 and model.ram[2][0x8e] == 1


def episode(parent, candidate):
    old, model = M.fork(parent), M.fork(candidate)
    for seed in (old, model):
        pickup(seed)
        input_step(seed, 0, 1)
        input_step(seed, 68, 2)
    assert old.ram[2][0xbb] == 1 and not old.ram[2][0xc0]
    assert model.ram[2][0xbb] == 0 and model.ram[2][0xc0] == 128, list(model.ram[2][0xbb:0xc4])
    assert not model.ram[2][0x8f] & 2
    phases = [(2, 128)]
    for age in range(3, 220):
        before = model.ram[2][0xc0]
        input_step(model, 0, age)
        current = model.ram[2][0xc0]
        if current != before:
            phases.append((age, current))
        if not current:
            break
    assert [v for _, v in phases] == [128, 129, 130, 131, 0], phases
    assert phases[2][0] - phases[1][0] == 1 and phases[3][0] - phases[2][0] == phases[4][0] - phases[3][0] == 16
    return dict(original_mature_flower_grant=True, actual_input_activation=True,
                old_candidate_Bomb_refused=True, phases=phases, BCD_stock=model.ram[2][0xbb])


def call_donor(memory, entry, *, a=85, x=7, y=91, p=0x61):
    cpu = M.NesMPU(memory=memory, pc=entry)
    cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = a, x, y, p, 224
    cpu.stPushWord(0x5ffe)
    for _ in range(300):
        if cpu.pc == 0x5fff:
            return
        assert memory[cpu.pc], hex(cpu.pc)
        cpu.step()
    raise AssertionError(('Donor Bomb leaf bound', hex(cpu.pc)))


def donor_tick(candidate, pc):
    model = M.fork(candidate)
    model.raw_page(2, 2)
    M.put(model, CurrentBankC=2)
    original = DonorMemory(Compose.ROM.read_bytes(), [0] * 2048)
    count = 0
    for phase, x, y, timer in product((0, 128, 129, 130, 131), (7, 8, 130, 247, 248),
                                       (31, 32, 160, 191), (1, 2, 16)):
        initial = (phase, x, y, timer)
        original[0xc0:0xc4] = initial
        model.ram[2][0xc0:0xc4] = bytes(initial)
        original[0x61] = 0
        call_donor(original, 0xae3d)
        Cpu.call(model, pc, 157, p=0x21)
        assert bytes(original[0xc0:0xc4]) == bytes(model.ram[2][0xc0:0xc4]), (initial,
            original[0xc0:0xc4], list(model.ram[2][0xc0:0xc4]))
        count += 1
    return dict(original_Bomb_phase_position_timer_pairs=count,
                host_lower_bound=224, native_floor_source_y=208)


def contact(candidate):
    counts = Counter()
    for phase, dx, dy in product((128, 129, 130, 131), (-16, -15, 0, 16, 17), (-8, -7, 0, 8, 9)):
        model = M.fork(candidate)
        input_step(model, 0, 1)
        M.put(model, Square1SoundQueue=0, Square2SoundQueue=0, ObjectOffset=3)
        model.ram[2][0xc0:0xc4] = bytes((phase, 128, 208, 16))
        for name, value in dict(Enemy_Flag=1, Enemy_State=0, Enemy_ID=6,
                                Enemy_X_Position=128 + dx, Enemy_PageLoc=0,
                                Enemy_Y_Position=192 + dy, Enemy_Y_HighPos=1).items():
            model[M.address(model.bundle, name) + 5] = value
        result = M.invoke(model, 'HuWeaponTail', x=7, p=0x21)
        hit = bool(M.get(model, 'Enemy_State', 5) & 0x20) or not M.get(model, 'Enemy_Flag', 5)
        expected = phase != 128 and -15 <= dx <= 16 and -7 <= dy <= 8
        assert hit == expected and M.get(model, 'ObjectOffset') == 3, (phase, dx, dy, result, hit)
        assert result['counts'].get('ShellOrBlockDefeat', 0) == int(expected), (phase, dx, dy, result)
        again = M.invoke(model, 'HuWeaponTail', x=7, p=0x21)
        assert not again['counts'].get('ShellOrBlockDefeat', 0)
        counts['native_donor_rectangle_hits' if expected else 'native_non_contacts'] += 1
    return dict(counts)


def draw_hud(candidate):
    counts = Counter()
    expected = {0x80: (0xc2,), 0x81: (0xc6, 0xfa), 0x82: (0xc6, 0xfa), 0x83: (0xfc, 0xfe)}
    for phase, clock in product(expected, (0, 8)):
        model = M.fork(candidate)
        input_step(model, 0, 1)
        model.ram[2][0xc0:0xc4] = bytes((phase, 128, 208, 16))
        model.ram[2][0xe8] = clock
        model[0x200:0x300] = [240, 0, 0, 0] * 64
        M.put(model, CurrentOAMOffset=0, GuestOamRotationActive=0, RgOamRotation=0)
        result = M.invoke(model, 'HuDraw', p=0x21)
        rows = [tuple(model[0x200 + i:0x204 + i]) for i in range(0, 256, 4)]
        actual = [row for row in rows if row[1] in (0xc2, 0xc4, 0xc6, 0xfa, 0xfc, 0xfe)]
        tiles = (0xc4,) if phase == 128 and clock else expected[phase]
        xy = ((124, 192),) if phase == 128 else ((120, 192), (128, 192))
        assert actual == [(y, tile, 0, x) for tile, (x, y) in zip(tiles, xy)], (phase, clock, actual, result)
        counts['native_original_Bomb_OAM_phases'] += 1
    model = M.fork(candidate)
    model.ram[2][0x8e], model.ram[2][0x8f], model.ram[2][0xbb], model.ram[2][0xe8] = 1, 2, 0x12, 0x80
    M.put(model, VRAM_Buffer1_Offset=0, VRAM_Buffer_AddrCtrl=0, InvHudActive=0)
    at = M.address(model.bundle, 'VRAM_Buffer1')
    model[at] = 0
    result = M.invoke(model, 'HuUi', p=0x21)
    packet = bytes(model[at:at + 36])
    assert result['P'] & 1 and M.get(model, 'InvHudActive') == 233, (result, packet.hex())
    assert packet[3:12] == bytes.fromhex('0b18160b2424242424') and packet[13:15] == b'\x01\x02', packet.hex()
    assert [packet[i] for i in (28, 29, 33, 34)] == [60, 61, 62, 63]
    assert packet[22] == 0x24
    return dict(counts, native_HUD_original_icon_and_BCD=True)


def lifetimes(parent, candidate):
    counts = Counter()
    for delta in (-24, -8, 0, 8, 24):
        model = M.fork(candidate)
        M.put(model, Player_PageLoc=1, Player_X_Position=100,
              ScreenLeft_X_Pos=248, ScreenLeft_PageLoc=0)
        input_step(model, 0, 1)
        state = model.ram[2]
        assert state[0x821] == 248 and state[0x822] == 0
        state[0xc0:0xc4] = bytes((130, 128, 208, 16))
        scroll = 248 + delta
        M.put(model, ScreenLeft_X_Pos=scroll & 255, ScreenLeft_PageLoc=scroll >> 8)
        input_step(model, 0, 2)
        assert state[0xc0:0xc4] == bytes((130, 128 - delta, 208, 15)), (delta, list(state[0xc0:0xc4]))
        input_step(model, 0, 2)
        assert state[0xc0:0xc4] == bytes((130, 128 - delta, 208, 15))
        M.put(model, GamePauseStatus=1, FrameCounter=3)
        M.invoke(model, 'HuMovement', p=0x21)
        assert state[0xc0:0xc4] == bytes((130, 128 - delta, 208, 15))
        counts['signed_camera_rebases_duplicate_pause'] += 1
    model = M.fork(candidate)
    input_step(model, 0, 1)
    model.ram[2][0xc0:0xc4] = bytes((128, 10, 208, 0))
    M.put(model, ScreenLeft_X_Pos=24)
    input_step(model, 0, 2)
    assert model.ram[2][0xc0] == 0
    counts['no_offscreen_wrap'] += 1
    model = M.fork(candidate)
    model.ram[2][0xc0], model.ram[2][0xbb], model.ram[2][0x8e], model.ram[2][0x8f] = 128, 2, 1, 2
    M.put(model, DisableScreenFlag=1, Mirror_PPUMASK=0, AreaAddrsLOffset=1)
    assert M.invoke(model, 'HuFresh', p=0x21)['P'] & 1
    assert (model.ram[2][0xc0], model.ram[2][0xbb], model.ram[2][0x8e], model.ram[2][0x8f]) == (0, 2, 1, 2)
    counts['same_life_retires_bomb_retains_gear'] += 1
    # All original supported activation rows and unsupported control IDs use
    # the exact host public movement, including native saved input conversion.
    for option, stock in ((0, 0xbd), (2, 0xbb), (3, 0xbe), (4, 0xbc), (5, 0xbb), (6, 0xbb), (7, 0xbf), (8, 0xbb)):
        left, right = M.fork(parent), M.fork(candidate)
        for model in (left, right):
            state = model.ram[2]
            state[0x65], state[0x8e], state[0x8f], state[stock] = 2, option, 1 << (option & 7), 2
            state[0x90] = int(option == 8)
            input_step(model, 0, 1)
            input_step(model, 68, 2)
        assert left.ram[2][:0x800] == right.ram[2][:0x800], option
        counts['original_supported_and_excluded_activation_pairs'] += 1
    for selected in (0, 7, 28, 32, 33, 35, 36, 38, 39, 42):
        left, right = M.fork(parent), M.fork(candidate)
        for model in (left, right):
            M.put(model, SelectedCharacter=selected, FmAlts=0)
        a = M.invoke(left, 'HuHead', p=0x21)
        b = M.invoke(right, 'HuHead', p=0x21)
        assert all(a[k] == b[k] for k in ('A', 'X', 'Y', 'P'))
        counts['foreign_head_owners'] += 1
    return dict(counts)


def interrupts(candidate, layout):
    native = M.NesMPU
    points, counts = set(), Counter()
    minimum = 255
    watch = (*Compose.LOANS, (0xcd79, 0xcdd4))
    class Probe(native):
        def step(self):
            nonlocal minimum
            tag = self.memory.rawtags[2]
            if tag == 2 and any(lo <= self.pc < hi for lo, hi in watch):
                point = (self.pc, self.sp, self.p & 4)
                if point not in points:
                    points.add(point)
                    for kind in ('IRQ', 'lagNMI'):
                        if kind == 'IRQ' and self.p & 4:
                            continue
                        trial = M.fork(self.memory)
                        clone = native(memory=trial, pc=self.pc)
                        for field in ('a', 'x', 'y', 'p', 'sp'):
                            setattr(clone, field, getattr(self, field))
                        try:
                            depth = Cpu.inject(clone, native, kind)
                        except AssertionError as error:
                            raise AssertionError((kind, hex(self.pc), self.sp, dict(counts))) from error
                        minimum = min(minimum, depth)
                        counts[kind] += 1
            return native.step(self)
    model = M.fork(candidate)
    pickup(model)
    input_step(model, 0, 1)
    M.NesMPU = Probe
    try:
        input_step(model, 68, 2)
        input_step(model, 0, 3)
        model.ram[2][0xc0:0xc4] = bytes((130, 128, 208, 16))
        for name, value in dict(Enemy_Flag=1, Enemy_State=0, Enemy_ID=6,
                                Enemy_X_Position=128, Enemy_PageLoc=0,
                                Enemy_Y_Position=192, Enemy_Y_HighPos=1).items():
            model[M.address(model.bundle, name) + 5] = value
        M.invoke(model, 'HuWeaponTail', p=0x21)
        M.invoke(model, 'HuDraw', p=0x21)
        M.put(model, VRAM_Buffer1_Offset=0, VRAM_Buffer_AddrCtrl=0, InvHudActive=0)
        model[M.address(model.bundle, 'VRAM_Buffer1')] = 0
        model.ram[2][0x8e], model.ram[2][0x8f], model.ram[2][0xbb], model.ram[2][0xe8] = 1, 2, 1, 128
        M.invoke(model, 'HuUi', p=0x21)
    finally:
        M.NesMPU = native
    assert counts['IRQ'] and counts['lagNMI'] and minimum >= 128
    return dict(cuts=dict(counts), minimum_SP=minimum, public_service_scope=True,
                instruction_SP_points=len(points))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--basic', action='store_true')
    args = parser.parse_args()
    raw = Compose.NIGHTLY.read_bytes()
    changed, layout = Compose.transform(raw)
    assert Compose.inverse(changed, layout) == raw
    parent, before = cold(raw, Compose.OLD_COOKIE)
    candidate, after = cold(changed, bytes.fromhex(layout['cookie']))
    printed_layout = {k: v for k, v in layout.items() if k not in ('patches', 'symbols')}
    print('KARNOV_BOMB_BASIC ' + json.dumps(dict(layout=printed_layout, parent_cold=before,
          candidate_cold=after, episode=episode(parent, candidate)), separators=(',', ':')), flush=True)
    if not args.basic:
        print('KARNOV_BOMB_DONOR ' + json.dumps(donor_tick(candidate,
            layout['symbols']['KrBombTick']), separators=(',', ':')), flush=True)
        print('KARNOV_BOMB_CONTACT ' + json.dumps(contact(candidate), separators=(',', ':')), flush=True)
        print('KARNOV_BOMB_DRAW ' + json.dumps(draw_hud(candidate), separators=(',', ':')), flush=True)
        print('KARNOV_BOMB_LIFETIMES ' + json.dumps(lifetimes(parent, candidate), separators=(',', ':')), flush=True)
        cases = ((2, 0x16e5, 0xc9), (2, 0xd79, 0xb5), (3, 0x1184, 0x20))
        print('KARNOV_BOMB_READBACK ' + json.dumps([cold(changed, bytes.fromhex(layout['cookie']),
            readback=case) for case in cases], separators=(',', ':')), flush=True)
        print('KARNOV_BOMB_INTERRUPTS ' + json.dumps(interrupts(candidate, layout), separators=(',', ':')), flush=True)


if __name__ == '__main__':
    main()
