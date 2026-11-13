"""Qualify a composable Metal flower candidate in memory, with zero outputs."""

import argparse
from collections import Counter
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

import compose_metal_flower_1112 as Compose
import check_prince_brick_support_1111 as Host
import check_hogan_current_bounded_v1 as M


R = Compose.R
NIGHTLY = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')


def cold(raw, cookie, *, fault_at=None):
    bundle = Host.C.Start.W.bundle(raw)
    model = M.fresh(bundle)
    for bank in (2, 3):
        model.ram[bank][:] = bytes((i * 17 + bank * 29 + 7) & 255 for i in range(8192))
    model.raw_page(1, 151)
    model.raw_page(2, 215)
    M.put(model, SelectedCharacter=35, OperMode=1, GameEngineSubroutine=8,
          FamilyMainCommit=1, DisableScreenFlag=1, Mirror_PPUMASK=0,
          Mirror_PPUCTRL=160, NmiDisable=255, CurrentBank=151, CurrentBankC=215,
          HorizontalScroll=73, VerticalScroll=32, ReloadCHRBank=7, X5WideChrActive=0)
    model.ppuctrl = 160
    for i, value in enumerate((18, 20, 21, 22, 23, 24, 25, 26, 4, 5, 6, 7)):
        model[M.address(bundle, 'CurrentCHRBank') + i] = value
        model[M.address(bundle, 'X5ChrMode') + i] = 0
    _, labels = Compose.inputs()
    entry = labels['Ms8Load']
    model[0x16a], model[0x16c], model[0x16d] = 85, entry & 255, entry >> 8
    if fault_at is not None:
        native_bus = type(model)
        model.fault_seen = False
        model.fault_value = None
        model.fault_alias = None
        expected_value = raw[Compose.EXTRA_AT + fault_at - Compose.EXTRA_PC]
        class Fault(native_bus):
            def __getitem__(self, at):
                value = native_bus.__getitem__(self, at)
                if (isinstance(at, int) and 0x8000 <= at < 0xe000
                        and self.rawtags[(at - 0x8000) // 8192] == 2
                        and at & 0x1fff == fault_at & 0x1fff
                        and self.ppu_reads > before_reads and value == expected_value
                        and not self.fault_seen):
                    self.fault_seen = True
                    self.fault_value = value
                    self.fault_alias = at
                    return value ^ 1
                return value
        model.__class__ = Fault
    cpu = M.NesMPU(memory=model, pc=M.address(bundle, 'FarCallCommon'))
    cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = 244, 7, 91, 0x71, 224
    cpu.stPushWord(0x5ffe)
    minimum = 224
    before_reads = model.ppu_reads
    for _ in range(1000000):
        if cpu.pc == 0x5fff:
            break
        minimum = min(minimum, cpu.sp)
        if cpu.pc >= 0x8000:
            assert model.rawtags[(cpu.pc - 0x8000) // 8192] & 128, ('Cold RAM opcode', hex(cpu.pc))
        assert model[cpu.pc] != 0, ('Cold BRK', hex(cpu.pc))
        cpu.step()
    else:
        raise AssertionError(('Cold bound', hex(cpu.pc)))
    assert cpu.sp == 224
    if fault_at is not None:
        assert model.fault_seen and not cpu.p & 1
        assert all(bytes(model.ram[bank][0x1fe0:0x1ff0]) != cookie for bank in (2, 3))
        return model, dict(fault_at=f'{fault_at:04x}', read_value=model.fault_value,
                           observed_alias=f'{model.fault_alias:04x}',
                           PPU_reads=model.ppu_reads - before_reads,
                           both_headers_unpublished=True, minimum_SP=minimum)
    assert cpu.p & 1
    assert all(bytes(model.ram[bank][0x1fe0:0x1ff0]) == cookie for bank in (2, 3))
    assert model.ppu_reads - before_reads == 24600
    start = 16 + 1048576 + 499 * 1024
    assert bytes(model.ram[2][0x1900:0x1d00]) == raw[start:start + 1024]
    M.put(model, DisableScreenFlag=0, Mirror_PPUMASK=24, FrameCounter=1,
          GamePauseStatus=0, Player_X_Position=40, Player_PageLoc=0,
          Player_Y_Position=176, Player_Y_HighPos=1, Player_Y_Speed=0,
          CurrentPlayer=0, NumberofLives=2, SavedJoypadBits=0)
    M.invoke(model, 'HuMovement')
    assert model.ram[2][0x800] == 0xa7
    return model, dict(PPU_reads=model.ppu_reads - before_reads, minimum_SP=minimum,
                       full_headers=cookie.hex(), actual_cold_code_only=True)


def pickup(seed, slot, typ, *, mature=0x80, native_status=1):
    model = M.fork(seed)
    M.put(model, ObjectOffset=slot, PlayerStatus=native_status,
          Square2SoundQueue=0, PlayerSize=0)
    for name, value in (('Enemy_Flag', 1), ('Enemy_ID', 0x2e), ('Enemy_State', mature),
                        ('PowerUpType', typ), ('Enemy_X_Position', 80), ('Enemy_PageLoc', 0),
                        ('Enemy_Y_Position', 176), ('Enemy_Y_HighPos', 1),
                        ('InvPickupOwner', 35), ('InvPickup', 1), ('InvRisePhase', 1),
                        ('InvPickupSaveLo', 19), ('InvPickupSaveHi', 23)):
        model[M.address(model.bundle, name) + slot] = value
    return model


def equivalent(a, b):
    assert bytes(a[:0x100]) == bytes(b[:0x100])
    assert bytes(a[0x200:0x800]) == bytes(b[0x200:0x800])
    for bank, (left, right) in enumerate(zip(a.ram, b.ram)):
        left, right = bytearray(left), bytearray(right)
        if bank in (2, 3):
            left[0x1fe0:0x1ff0] = right[0x1fe0:0x1ff0] = bytes(16)
        if bank == 2:
            left[0x1ba0:0x1d00] = right[0x1ba0:0x1d00] = bytes(352)
        assert left == right, (bank, [(i, x, y) for i, (x, y) in enumerate(zip(left, right)) if x != y][:12])
    assert a.rawtags == b.rawtags and a.chr_latches == b.chr_latches


def item_controls(parent, candidate):
    counts = Counter()
    for slot, armor, status in product(range(6), (0, 0x80), range(3)):
        a, b = pickup(parent, slot, 0, native_status=status), pickup(candidate, slot, 0, native_status=status)
        a.ram[2][0x5d0] = b.ram[2][0x5d0] = armor
        old, new = M.invoke(a, 'HandlePowerUpCollision', x=slot), M.invoke(b, 'HandlePowerUpCollision', x=slot)
        assert all(old[key] == new[key] for key in ('A', 'X', 'Y', 'P'))
        equivalent(a, b)
        counts['unchanged_mushrooms'] += 1
    for slot, typ in product(range(6), (2, 3)):
        a, b = pickup(parent, slot, typ), pickup(candidate, slot, typ)
        old, new = M.invoke(a, 'HandlePowerUpCollision', x=slot), M.invoke(b, 'HandlePowerUpCollision', x=slot)
        assert all(old[key] == new[key] for key in ('A', 'X', 'Y', 'P'))
        equivalent(a, b)
        counts['unchanged_native_star_life'] += 1
    for slot, typ, phase in product(range(6), (0, 1), (0, 1, 16, 127)):
        a, b = pickup(parent, slot, typ, mature=phase), pickup(candidate, slot, typ, mature=phase)
        initial = bytes(b.ram[2][:0x800])
        old, new = M.invoke(a, 'HuPickup', x=slot), M.invoke(b, 'HuPickup', x=slot)
        assert not new['P'] & 1 and bytes(b.ram[2][:0x800]) == initial
        assert all(old[key] == new[key] for key in ('A', 'X', 'Y', 'P'))
        assert M.get(b, 'Enemy_Flag', slot) == 1
        equivalent(a, b)
        counts['immature_rejections'] += 1
    for byte in range(32):
        model = pickup(candidate, 0, 1)
        model.ram[2 + byte // 16][0x1fe0 + byte % 16] ^= 1
        before = tuple(map(bytes, model.ram))
        result = M.invoke(model, 'HuPickup', x=0)
        assert not result['P'] & 1 and tuple(map(bytes, model.ram)) == before
        counts['complete_header_rejections'] += 1
    for selected in (0, 1, 5, 11, 34, 36, 38, 40, 42):
        a, b = pickup(parent, 0, 1), pickup(candidate, 0, 1)
        M.put(a, SelectedCharacter=selected)
        M.put(b, SelectedCharacter=selected)
        old, new = M.invoke(a, 'HuPickup', x=0), M.invoke(b, 'HuPickup', x=0)
        assert all(old[key] == new[key] for key in ('A', 'X', 'Y', 'P'))
        equivalent(a, b)
        counts['foreign_owner_pairs'] += 1
    return dict(counts)


def source_grant_controls(candidate):
    count = 0
    oracle = Compose.Source.Donor.machine().memory
    for slot, player_state, old_mode, armor in product(range(6), (0, 5), range(4), (0, 0x80)):
        model = pickup(candidate, slot, 1, native_status=2 if old_mode == 1 else 1)
        model.ram[2][0x4e0] = player_state
        model.ram[2][0x5d0] = armor
        model.ram[2][0x718] = 0x80 if old_mode == 1 else 0
        model.ram[2][0x717] = 0x80 if old_mode == 2 else 0
        model.ram[2][0x43c] = 0x80 if old_mode == 3 else 0
        oracle[:2048] = bytes(model.ram[2][:0x800])
        Compose.Source.run(oracle, 0xe7b3)
        M.invoke(model, 'HandlePowerUpCollision', x=slot)
        assert Compose.Source.source_state(oracle) == Compose.Source.source_state(model.ram[2])
        assert model.ram[2][0x5d0] == armor
        assert M.get(model, 'PlayerStatus') == 2 and M.get(model, 'Enemy_Flag', slot) == 0
        count += 1
    return dict(actual_native_pickup_original_grant_pairs=count,
                native_sfx='PowerUpGrab; original source07E7 remains donor-controlled')


def source_shots(candidate):
    _, labels = Compose.inputs()
    native = M.NesMPU
    comparisons = 0
    runs = []
    enemies = []
    for keys, desired_slot in product((65, 66, 72, 68), (2, 3)):
        model = pickup(candidate, 0, 1)
        M.invoke(model, 'HandlePowerUpCollision', x=0)
        Host.terrain(model, lambda _x, y: 0x61 if y >= 208 else 0)
        model.ram[2][0x43f] = 0x80
        if desired_slot == 3:
            for at, value in ((0x512, 0x80), (0x52a, 0x81), (0x602, 0x0a),
                              (0x4e2, 0x80), (0x482, 100), (0x49a, 0),
                              (0x4b2, 100), (0x4ca, 0), (0x662, 20),
                              (0x58a, 0x80), (0x5a2, 3)):
                model.ram[2][at] = value
        oracle = Compose.Source.Donor.machine().memory
        oracle.regs[6:8] = [0, 1]
        oracle.map()
        expected = None
        observed = []
        class Trace(native):
            def step(self):
                nonlocal expected, comparisons
                tag = self.memory.rawtags[(self.pc - 0x8000) // 8192] if self.pc >= 0x8000 else -1
                if tag == 3 and self.pc == labels['Ms_B057']:
                    assert expected is None
                    oracle[:2048] = bytes(self.memory.ram[2][:0x800])
                    result = Compose.Source.run(oracle, 0xb057, a=self.a, x=self.x,
                                               y=self.y, p=self.p, stop=0xb07a)
                    expected = (result[0][:4], Compose.Source.source_state(
                        oracle, stack=(0x1ee, 0x1ef, 0x1f0)))
                elif tag == 3 and self.pc == labels['Ms_B07A'] and expected is not None:
                    assert (self.a, self.x, self.y, self.p & 0xef) == expected[0]
                    assert Compose.Source.source_state(self.memory.ram[2],
                        stack=(0x1ee, 0x1ef, 0x1f0)) == expected[1]
                    expected = None
                    comparisons += 1
                    observed.append(dict(slot2=self.memory.ram[2][0x512],
                        slot3=self.memory.ram[2][0x513], type2=self.memory.ram[2][0x52a],
                        type3=self.memory.ram[2][0x52b]))
                return native.step(self)
        M.NesMPU = Trace
        try:
            for age in range(8):
                M.put(model, SavedJoypadBits=keys, SavedJoypad1Bits=keys,
                      A_B_Buttons=keys & 192, Left_Right_Buttons=keys & 3,
                      Up_Down_Buttons=keys & 12, FrameCounter=(age + 2) & 255)
                M.invoke(model, 'HuMovement')
                if model.ram[2][0x510 + desired_slot] & 0x80:
                    assert model.ram[2][0x528 + desired_slot] == 0x81
                    break
            else:
                raise AssertionError(('Earned upgraded shot bound', keys, desired_slot, observed))
        finally:
            M.NesMPU = native
        assert expected is None and observed
        if keys == 65:
            slot = desired_slot
            world = model.ram[2][0x480 + slot] | model.ram[2][0x498 + slot] << 8
            yy = model.ram[2][0x4b0 + slot]
            for name, value in (('Enemy_Flag', 1), ('Enemy_ID', 6), ('Enemy_State', 0),
                    ('Enemy_X_Position', world & 255), ('Enemy_PageLoc', world >> 8),
                    ('Enemy_Y_Position', yy), ('Enemy_Y_HighPos', 1), ('Enemy_BoundBoxCtrl', 9)):
                model[M.address(model.bundle, name) + 5] = value
            M.put(model, ObjectOffset=4)
            hit = M.invoke(model, 'HuWeaponTail')
            assert model.ram[2][0x510 + slot] == 0
            assert M.get(model, 'Enemy_State', 5) & 0x20 or M.get(model, 'Enemy_Flag', 5) == 0
            assert hit['counts'].get('ShellOrBlockDefeat', 0)
            enemies.append(dict(slot=slot, world_x=world, y=yy, native_defeats=hit['counts']))
        runs.append(dict(native_keys=keys, slot=desired_slot, updates=age + 1,
                         type=model.ram[2][0x528 + desired_slot],
                         donor_phase_pairs=len(observed)))
    return dict(actual_public_movement_donor_shot_pairs=comparisons,
                earned_upgrade_runs=runs, native_enemy_contacts=enemies)


def composition(raw, candidate):
    _, initial = Compose.transform(raw)
    foreign = (16 + 123, 16 + 8192 * 42 + 99, 16 + 1048576 + 329 * 1024 + 17)
    for at in foreign:
        other = bytearray(raw)
        other[at] ^= 1
        result, layout = Compose.transform(bytes(other))
        assert layout['cookie'] == initial['cookie'] and result[at] == other[at]
        assert Compose.transform(result, True)[0] == other
        assert result[:at] == candidate[:at] and result[at + 1:] == candidate[at + 1:]
    rejected = 0
    for at in (Compose.EXTRA_AT, Compose.EXTRA_AT + 340, 212910, 817022,
               16 + 1048576 + 247 * 1024, 16 + 1048576 + 831 * 1024):
        broken = bytearray(raw)
        broken[at] ^= 1
        try:
            Compose.transform(bytes(broken))
        except AssertionError:
            rejected += 1
        else:
            raise AssertionError(('Unowned preimage silently accepted', at))
    return dict(unrelated_canaries_preserved=len(foreign), conflicting_preimages_rejected=rejected,
                exact_inverse=True, synthetic_canary_scope='Composition algebra only; altered canary ROMs are not run.')


def interrupts(candidate, layout):
    native = M.NesMPU
    totals = Counter()
    minimum = 255
    points = set()
    seed = pickup(candidate, 0, 1)
    class Probe(native):
        def step(self):
            nonlocal minimum
            tag = self.memory.rawtags[(self.pc - 0x8000) // 8192] if self.pc >= 0x8000 else -1
            if tag == 2 and layout['extension_pc'] <= self.pc < layout['extension_pc'] + 56:
                key = (self.pc, self.sp, self.p & 4)
                if key not in points:
                    points.add(key)
                    for kind in ('IRQ', 'lagNMI'):
                        if kind == 'IRQ' and self.p & 4:
                            continue
                        model = M.fork(self.memory)
                        cpu = native(memory=model, pc=self.pc)
                        for field in ('a', 'x', 'y', 'p', 'sp', 'pc'):
                            setattr(cpu, field, getattr(self, field))
                        depth = Host.Async.inject(cpu, native, kind)
                        minimum = min(minimum, depth)
                        totals[kind] += 1
            return native.step(self)
    M.NesMPU = Probe
    try:
        M.invoke(seed, 'HandlePowerUpCollision', x=0, p=0x21)
    finally:
        M.NesMPU = native
    assert totals['IRQ'] and totals['lagNMI']
    return dict(actual_cuts=dict(totals), minimum_SP=minimum,
                changed_instruction_sp_points=len(points), scope='Direct native pickup caller, actual IRQ/FF lag-NMI; not deepest GameLoop or nested ISR.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, default=NIGHTLY)
    parser.add_argument('--layout-only', action='store_true')
    args = parser.parse_args()
    raw = args.rom.read_bytes()
    candidate, layout = Compose.transform(raw)
    assert Compose.transform(candidate, True)[0] == raw
    result = dict(layout=layout, output_files=0)
    print('METAL_FLOWER_LAYOUT ' + json.dumps(result, separators=(',', ':')), flush=True)
    if args.layout_only:
        return
    before, old_cold = cold(raw, bytes.fromhex(layout['old_cookie']))
    after, new_cold = cold(candidate, bytes.fromhex(layout['cookie']))
    result['cold'] = [old_cold, new_cold]
    examples = []
    for slot in range(6):
        parent, changed = pickup(before, slot, 1), pickup(after, slot, 1)
        parent.ram[2][0x5d0] = changed.ram[2][0x5d0] = 0x80
        original = bytes(changed.ram[2][:0x800])
        old = M.invoke(parent, 'HandlePowerUpCollision', x=slot)
        new = M.invoke(changed, 'HandlePowerUpCollision', x=slot)
        assert parent.ram[2][0x718] == 0
        assert changed.ram[2][0x718] == 0x80
        assert changed.ram[2][0x5d0] == 0x80
        assert M.get(changed, 'PlayerStatus') == 2
        assert M.get(changed, 'Enemy_Flag', slot) == 0
        for name in ('InvPickupOwner', 'InvPickup', 'InvRisePhase', 'InvPickupSaveLo', 'InvPickupSaveHi'):
            assert M.get(changed, name, slot) == 0
        examples.append(dict(slot=slot, parent=old, candidate=new,
                             original_source_718=original[0x718], final_source_718=changed.ram[2][0x718]))
    result.update(passed=True, native_flowers=examples,
                  composition=composition(raw, candidate),
                  unchanged_controls=item_controls(before, after),
                  original_grants=source_grant_controls(after),
                  public_shots=source_shots(after),
                  cold_readback_faults=[cold(candidate, bytes.fromhex(layout['cookie']), fault_at=pc)[1]
                      for pc in (layout['extension_pc'], layout['grant_pc'], layout['grant_pc'] + 40)],
                  interrupts=interrupts(after, layout),
                  checker_SHA256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  scope='In-memory composable transform and actual cold/native pickup CPU flow; '
                        'directed item fixtures, no natural controller pickup or Mesen.')
    print('METAL_FLOWER_CPU ' + json.dumps(result, separators=(',', ':')), flush=True)


if __name__ == '__main__':
    main()
