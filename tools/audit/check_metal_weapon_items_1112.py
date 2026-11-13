"""Recover Metal Storm weapon-item decisions in memory; write no artifacts."""

from hashlib import sha256
from itertools import product
import argparse
import json
from pathlib import Path
import re
import zipfile

from py65.assembler import Assembler
from py65.disassembler import Disassembler

import metal_storm_cpu_1101_v2 as Donor
import recover_metal_storm_actor_1101_v2 as Actor


R = Donor.ROOT
PACKET = R / 'docs/qa/checkpoints/2026-11-02/metal-reservation-v42/inputs.zip'
PACKET_SHA = 'f1548d2f32972aa150939ab9b33ab829aa4f19f60013cf813031ac21888724e9'
SOURCE = R / 'tools/reference/metal_weapon_items_1112.inc'
STATE = 0xc000
ORIGIN = 0x9000
GRANTS = (0xe7b3, 0xe7c9, 0xe7f4)


def assemble(origin, state, *, item0_only=False):
    lines = []
    include = True
    for raw in SOURCE.read_text().splitlines():
        line = raw.split(';', 1)[0].strip()
        if line == '.ifndef MS_WEAPON_ITEM0_ONLY':
            assert include
            include = not item0_only
            continue
        if line == '.endif':
            include = True
            continue
        if include:
            lines.append(line)
    labels = {line[:-1]: origin for line in lines if line.endswith(':')}
    assembler = Assembler(Donor.NesMPU(memory=bytearray(65536)))
    for iteration in range(3):
        code = bytearray()
        for line in lines:
            if not line or line.startswith('.'):
                continue
            if line.endswith(':'):
                labels[line[:-1]] = origin + len(code)
                continue
            line = re.sub(r'MsState\+\$([0-9a-fA-F]+)',
                          lambda match: f'${state + int(match[1], 16):04x}', line)
            for name, value in labels.items():
                line = re.sub(r'\b' + name + r'\b', f'${value:04x}', line)
            if iteration == 2 and line[:3].lower() in ('bne', 'beq'):
                target = int(line.split('$')[1], 16)
                assert -128 <= target - (origin + len(code) + 2) <= 127
            code.extend(assembler.assemble(line, pc=origin + len(code)))
    return bytes(code), labels


def run(memory, entry, *, a=0x55, x=7, y=0x5b, p=0x61, stop=0x5fff, trace=None):
    cpu = Donor.NesMPU(memory=memory, pc=entry)
    cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = a, x, y, p, 0xf0
    cpu.stPushWord(0x5ffe)
    low = cpu.sp
    for _ in range(2000):
        if cpu.pc == stop:
            break
        low = min(low, cpu.sp)
        if trace is not None:
            trace(cpu)
        assert memory[cpu.pc] != 0, ('BRK', hex(cpu.pc))
        cpu.step()
    else:
        raise AssertionError(('Execution bound', hex(cpu.pc)))
    assert cpu.sp == (0xf0 if stop == 0x5fff else 0xee), (hex(stop), cpu.sp)
    return (cpu.a, cpu.x, cpu.y, cpu.p & 0xef, cpu.sp), cpu.processorCycles, low


def source_state(memory, base=0, *, stack=(0x1ef, 0x1f0)):
    # Only the two artificial top-level return-stack bytes differ. The relocated
    # source stack page otherwise remains part of the comparison.
    data = bytearray(memory[base:base + 2048])
    for at in stack:
        data[at] = 0
    return bytes(data)


def grant_pairs(original, port, labels, *, items=range(3)):
    total = 0
    aggregate = sha256()
    minimum = 255
    changes = {item: set() for item in items}
    for item, player, flags, incoming in product(items, range(8),
            product((0, 1, 0x7f, 0x80, 0xff), repeat=3), (0x20, 0x21, 0x60, 0xe1)):
        initial = bytearray((i * 29 + total * 7 + 11) & 255 for i in range(2048))
        initial[0x718], initial[0x717], initial[0x43c] = flags
        initial[0x4e0] = player
        original[:2048] = initial
        port[STATE:STATE + 2048] = initial
        old = run(original, GRANTS[item], p=incoming)
        new = run(port, labels[f'MsWeaponItem{item}'], p=incoming)
        assert old[:2] == new[:2], (item, player, flags, incoming, old, new)
        assert source_state(original) == source_state(port, STATE)
        minimum = min(minimum, old[2], new[2])
        for i, (before, after) in enumerate(zip(initial, original[:2048])):
            if before != after and i not in (0x1ef, 0x1f0):
                changes[item].add(i)
        aggregate.update(source_state(original))
        total += 1
    return dict(original_ported_pairs=total, minimum_standalone_SP=minimum,
                source_write_domains={str(item): [f'{i:04x}' for i in sorted(writes)]
                                      for item, writes in changes.items()},
                aggregate_SHA256=aggregate.hexdigest())


def dispatch(original):
    targets = [original[0xe79f + 2 * i] | original[0xe7a0 + 2 * i] << 8 for i in range(10)]
    assert targets == [0xe7b3, 0xe7c9, 0xe7f4, 0xe80d, 0xe833,
                       0xe84c, 0xe861, 0xe878, 0xe88d, 0xe8be]
    pairs = 0
    for slot, item in product((4, 5, 12, 23), range(3)):
        initial = bytearray(2048)
        initial[0x60] = slot
        initial[0x4f8 + slot] = item
        original[:2048] = initial
        visited = []
        run(original, 0xe77b, stop=0xe799,
            trace=lambda cpu: visited.append(cpu.pc) if cpu.pc in GRANTS else None)
        assert visited == [GRANTS[item]], (slot, item, visited)
        assert original[0x36] | original[0x37] << 8 == GRANTS[item]
        pairs += 1
    return dict(table_hex='e79f..e7b2', targets=[f'{target:04x}' for target in targets],
                actual_dispatch_cases=pairs, scope='Reached item selector after donor collection effects; '
                'not a controller-earned item or complete donor object transaction.')


def shot_pairs(original, port, labels, frozen):
    total = upgraded = blocked = 0
    birth_types = set()
    aggregate = sha256()
    for item0, slot_policy, direction, gravity, x, y, world_mode in product(
            (False, True), (2, 3, 0), (0x80, 0x40, 0x10, 0x20), (0, 0x80),
            (0, 240, 255, 256, 319), (64, 207, 239, 255), (0, 0x80)):
        initial = bytearray(2048)
        initial[0x31] = direction | 2
        initial[0x43f] = direction
        initial[0x734] = gravity
        initial[0x480:0x481] = bytes((x & 255,))
        initial[0x498] = x >> 8
        initial[0x4b0] = y
        initial[0x50] = world_mode
        if slot_policy != 2:
            initial[0x512] = 0x80
        if slot_policy == 0:
            initial[0x513] = 0x80
        original[:2048] = initial
        port[STATE:STATE + 2048] = initial
        if item0:
            run(original, GRANTS[0])
            run(port, labels['MsWeaponItem0'])
        before = bytes(original[:2048])
        old = run(original, 0xb057, stop=0xb07a)
        new = run(port, frozen['Ms_B057'], stop=frozen['Ms_B07A'])
        assert old[0] == new[0], (item0, slot_policy, direction, gravity, x, y, world_mode, old, new)
        # B0E1 PHA uses one additional real CPU stack byte; the relocated
        # source image does not own the host's corresponding stack location.
        stack = (0x1ee, 0x1ef, 0x1f0)
        assert source_state(original, stack=stack) == source_state(port, STATE, stack=stack), (
            item0, slot_policy, direction, gravity, x, y, world_mode,
            [(f'{i:04x}', a, b) for i, (a, b) in enumerate(zip(
                source_state(original, stack=stack), source_state(port, STATE, stack=stack))) if a != b][:20])
        if slot_policy:
            slot = slot_policy
            assert original[0x510 + slot] == 0x80
            assert original[0x528 + slot] == (0x81 if item0 else 0x80)
            assert original[0x4e0 + slot] == (0x80 if item0 else 0)
            assert original[0x7e3] == (4 if item0 else 3)
            assert original[0x600 + slot] == 0x0a
            birth_types.add(original[0x528 + slot])
            upgraded += item0
        else:
            expected = bytearray(before)
            expected[0x499] = 0x80  # B057's unconditional source slot1 offscreen mark.
            assert source_state(original) == source_state(expected)
            blocked += 1
        aggregate.update(source_state(original, stack=stack))
        total += 1
    return dict(original_current_frozen_shot_pairs=total, upgraded_births=upgraded,
                both_slots_busy_rejections=blocked, shot_types=sorted(birth_types),
                aggregate_SHA256=aggregate.hexdigest())


def preflight(port, labels, frozen):
    count = 0
    for item in range(3):
        for active in (False, True):
            port[STATE:STATE + 2048] = bytes(2048)
            if active:
                port[STATE + 0x512] = 0x80
                port[STATE + 0x52a] = 0x81
                port[STATE + 0x602] = 0x0a
            run(port, labels[f'MsWeaponItem{item}'])
            before = bytes(port[STATE:STATE + 2048])
            result = run(port, frozen['MsNativeObjectsReady'])
            assert bool(result[0][3] & 1) == (item != 1)
            assert bytes(port[STATE:STATE + 2048]) == before
            count += 1
    return dict(current_frozen_preflight_cases=count,
                item0_supported=True, GravityFire_rejected=True,
                item2_guard_alone_is_not_complete_object_support=True)


def instructions(cpu, start, end):
    dis = Disassembler(cpu)
    result = []
    pc = start
    while pc < end:
        size, text = dis.instruction_at(pc)
        result.append([f'{pc:04x}', bytes(cpu.memory[pc:pc + size]).hex(), text])
        pc += size
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inspect', action='store_true')
    args = parser.parse_args()
    assert sha256(PACKET.read_bytes()).hexdigest() == PACKET_SHA
    with zipfile.ZipFile(PACKET) as archive:
        source = archive.read('component.s').decode('utf-8')
        label_text = archive.read('component.lbl').decode('utf-8')
        actor = archive.read('native-actor.bin')
        renderer = archive.read('native-render.bin')
        extra = archive.read('native-extra.bin')
    frozen = {match[2]: int(match[1], 16) for match in
              re.finditer(r'^al ([0-9a-fA-F]+) \.(\S+)[ \t\r]*$', label_text, re.M)}
    cpu, code, _, fields, _ = Actor.graph()
    if not args.inspect:
        original = cpu.memory
        exact, original_labels = assemble(GRANTS[0], 0)
        assert len(exact) == 90
        assert exact == bytes(original[0xe7b3:0xe80d])
        for item in range(3):
            assert original_labels[f'MsWeaponItem{item}'] == GRANTS[item]
        portable, labels = assemble(ORIGIN, STATE)
        power_only, power_labels = assemble(ORIGIN, STATE, item0_only=True)
        assert len(power_only) == 41
        port = bytearray(65536)
        port[ORIGIN:ORIGIN + len(portable)] = portable
        port[0xa000:0xa000 + len(actor)] = actor
        port[0xc800:0xc800 + len(renderer)] = renderer
        port[0xdba0:0xdba0 + len(extra)] = extra
        assert re.search(r'\bMsState\s*=\s*\$c000\b', source, re.I)
        assert len(actor) == 8128 and len(renderer) == 2991 and len(extra) == 257

        nightly_path = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
        nightly = nightly_path.read_bytes()
        def page(number):
            start = 16 + 1048576 + 1024 * number
            return nightly[start:start + 1024]
        actor_storage = bytearray(actor.ljust(8192, b'\xff'))
        actor_storage[0x1fe0:0x1ff0] = bytes(16)
        assert b''.join(page(number) for number in (247, 248, 249, 250, 827, 828, 829, 830)) == actor_storage
        assert b''.join(page(number) for number in (831, 500, 494)) == renderer.ljust(3072, b'\x00')
        assert page(499)[672:672 + len(extra)] == extra

        power_port = bytearray(port)
        power_port[ORIGIN:ORIGIN + len(portable)] = bytes([0xea]) * len(portable)
        power_port[ORIGIN:ORIGIN + len(power_only)] = power_only

        result = dict(passed=True, donor_path=str(Donor.ROM), donor_SHA256=Donor.EXPECTED,
            current_nightly_SHA256=sha256(nightly).hexdigest(),
            frozen_packet_SHA256=PACKET_SHA, current_carrier_bytes_equal_frozen=True,
            recovered_source_bytes=len(exact), relocated_source_bytes=len(portable),
            item0_only_source_bytes=len(power_only),
            source_byte_exact=True, recovered_half_open=['e7b3', 'e80d'],
            source_SHA256=sha256(SOURCE.read_bytes()).hexdigest(),
            source_labels={name: f'{value:04x}' for name, value in original_labels.items()},
            frozen_labels={name: f'{frozen[name]:04x}' for name in
                           ('Ms_B057', 'Ms_B07A', 'Ms_B0B7', 'MsNativeObjectsReady')},
            dispatch=dispatch(original), grants=grant_pairs(original, port, labels),
            item0_only_grants=grant_pairs(original, power_port, power_labels, items=(0,)),
            shots=shot_pairs(original, power_port, power_labels, frozen),
            preflight=preflight(port, labels, frozen),
            current_layout=dict(actor_used=8128, actor_limit=8160,
                                renderer_used=2991, renderer_limit=3072,
                                extra_used=257, extra_limit=352),
            output_files=0, native_emulator=False, installed=False,
            scope='Exact donor item0/1/2 source and source-CPU grant comparisons. '
                  'Original versus current frozen shot births; caller phases are isolated. '
                  'No natural pickup, native item adapter, audio output, IRQ/NMI, '
                  'GravityFire/object1 admission or native gameplay qualification.')
        result['checker_SHA256'] = sha256(Path(__file__).read_bytes()).hexdigest()
        print('METAL_WEAPON_ITEMS ' + json.dumps(result, separators=(',', ':')), flush=True)
        return
    sites = []
    for field in (0x717, 0x716, 0x718, 0x719, 0x528):
        for site in fields.get(field, []):
            pc = site['pc']
            sites.append(dict(field=f'{field:04x}', instructions=[
                [f'{at:04x}', bytes(code[at]['bytes']).hex(), code[at]['text']]
                for at in sorted(code) if pc - 8 <= at < pc + 16]))
    print('METAL_ITEM_INSPECT ' + json.dumps(dict(donor=Donor.EXPECTED,
          item_dispatch=instructions(cpu, 0xe77b, 0xe79f),
          fixed_items=instructions(cpu, 0xe7b3, 0xe80d), actor_sites=sites,
          armor_references=[f'{i:04x}' for i in range(0x8000, 0xffff)
                            if bytes(cpu.memory[i:i+2]) == bytes.fromhex('bee8')],
          shot_spawn=[[f'{pc:04x}', bytes(code[pc]['bytes']).hex(), code[pc]['text']]
                      for pc in sorted(code) if 0xb057 <= pc < 0xb23c],
          frozen_source_matches=[line for line in source.splitlines()
                                 if any(term in line for term in ('Ms25Pickup', 'MsNativeObjectsReady',
                                                                 'MsState+$717', 'MsState+$716'))]),
          separators=(',', ':')), flush=True)


if __name__ == '__main__':
    main()
