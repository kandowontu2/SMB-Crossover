"""Execute bounded actual Rogue Dawn ROM leaves without a native emulator.

Typed RAM inputs are component controls, not physical gameplay/acquisition.
No NMI, IRQ, PPU, mapper interruption, DMA, or whole-game timing is emulated.
Bomb draw joins stop at the genuine original draw branch before rendering.
"""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
from py65.devices.mpu6502 import MPU
import rogue_dawn_map_v1 as ref


def call(raw, pc, state=None, a=0, x=0, y=0, p=0x30, stop=None):
    memory = ref.cpu_image(raw)
    if state:
        for address, value in state.items():
            memory[address] = value
    cpu = MPU(memory=memory, pc=pc)
    cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = a, x, y, p, 0xfd
    cpu.stPushWord(0x5aff)
    for count in range(10000):
        if cpu.pc == (0x5b00 if stop is None else stop):
            return cpu, memory
        assert memory[cpu.pc] != 0, f'unexpected BRK at {cpu.pc:04X}'
        cpu.step()
    raise AssertionError(f'leaf did not return at {pc:04X}: {cpu.pc:04X}')


def signed(n):
    return n - 256 if n & 128 else n


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--rom', type=Path, default=ref.ROM)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    raw = args.rom.read_bytes()
    assert ref.digest(raw) == ref.EXPECTED
    result = dict(passed=False, native_run=False, scope=__doc__, rom=ref.binding(args.rom),
                  tool=ref.binding(__file__), mapper_tool=ref.binding(ref.__file__))
    jumps = []
    for gear, env, action in itertools.product([0, 2, 8, 10], [0, 128], [0, 1, 2, 3]):
        cpu, memory = call(raw, 0xcfc3, {0x6878: gear, 0x780e: env, 0x0300: action})
        assert memory[0x0308] == (0xfc if env else 0xfe)
        assert memory[0x0314] == ((0x12 if gear & 2 else 0x18) if env else (5 if gear & 2 else 7))
        assert memory[0x0305] == 12 and memory[0x0306] == 11 and memory[0x0304] == 4
        assert memory[0x030f] == 0 and memory[0x0681] == 2
        assert memory[0x0680] == (64 if action == 1 and gear & 8 else 0)
        state = {i: memory[i] for i in [0x0308, 0x0310, 0x0312, 0x0314]}
        deltas = []
        for tick in range(128):
            vc, vm = call(raw, 0xe3a5, state)
            state = {i: vm[i] for i in state}
            deltas.append(signed(vm[0]))
            if tick > 10 and sum(deltas) >= 0:
                break
        jumps.append(dict(gear=gear, environment_bit7=env, source_action=action,
                          init_cycles=cpu.processorCycles, VY=signed(memory[0x0308]),
                          gravity=memory[0x0314], free_space_delta_trace=deltas,
                          maximum_rise=-min(itertools.accumulate(deltas))))
    result['jump_initialization_cases'] = len(jumps)
    result['jump_reference_traces'] = [v for v in jumps if v['source_action'] == 0 and v['gear'] in [0, 2]]
    # Exact source Spring Ball branch supported by an already-frozen enemy.
    spring = []
    for gear, env, buttons, previous, vy in itertools.product([0, 16, 18], [0, 128], [0, 128], [0, 128], [0xfc, 0xfe, 0, 2]):
        state = {0x6878: gear, 0x780e: env, 0x7d: 1, 0x12: buttons,
                 0x14: buttons, 0xcd: previous, 0x0308: vy}
        cpu, m = call(raw, 0xa2ad, state)
        expected = (0xfc if env else 0xfe) if buttons and gear & 16 else vy
        if not buttons and previous and expected & 128 and expected < 0xfe:
            expected = 0xfe
        assert m[0x0308] == expected and m[0xcd] == buttons
        spring.append(cpu.processorCycles)
    result['spring_ball_frozen_support_cases'] = len(spring)
    result['spring_ball_cycles'] = [min(spring), max(spring)]
    # Complete source bomb allocator: B is bit40; A bit80 must not substitute.
    bombs = []
    for gear, buttons, repeat, elevator, occupied, vy in itertools.product([0, 1], [0, 64, 128], [0, 64], [0, 1], range(4), [0, 0xfc]):
        state = {0x6878: gear, 0x12: buttons, 0x16: repeat, 0x0307: elevator,
                 0x0308: vy, 0x030c: 1, 0x030d: 100, 0x030e: 120}
        for slot in range(3):
            state[0x03d0 + slot*16] = 1 if slot < occupied else 0
        cpu, m = call(raw, 0xd150, state)
        allowed = gear and ((buttons | repeat) & 64) and not elevator and occupied < 3
        if allowed:
            slot = 0x03d0 + occupied*16
            assert m[slot] == 8 and [m[slot+i] for i in [12, 13, 14]] == [1, 104, 120]
            assert m[0x0683] == 1
        else:
            assert [m[0x03d0 + i*16] for i in range(3)] == [state[0x03d0+i*16] for i in range(3)]
        bombs.append(cpu.processorCycles)
    result['complete_bomb_allocation_cases'] = len(bombs)
    result['bomb_allocation_cycles'] = [min(bombs), max(bombs)]
    init, im = call(raw, 0xd65e, {0x03d0: 8}, x=0xd0, stop=0xd66b)
    assert im[0x03df] == 12 and im[0x03d0] == 9
    countdown = []
    for parity, fuse in itertools.product([0, 1], [1, 2, 12, 255]):
        cpu, m = call(raw, 0xd670, {0x2d: parity, 0x03d0: 9, 0x03df: fuse}, x=0xd0, stop=0xd68e)
        assert m[0x03df] == ((fuse-1) & 255 if parity else fuse)
        assert m[0x03d0] == (10 if parity and fuse == 1 else 9)
        countdown.append(dict(parity=parity, initial_fuse=fuse, cycles_to_draw=cpu.processorCycles,
                              final_fuse=m[0x03df], final_action=m[0x03d0]))
    result['bomb_countdown_draw_join_cases'] = countdown
    result['bomb_fuse_contract'] = 'Initialize12; decrement only FrameCount bit0=1: 12 eligible updates, normally24 main updates. Native frame parity/pauses must be observed separately.'
    # Commit entry only: actual collector draw/contact admission is mapped separately.
    equipment = 0
    for gear, item in itertools.product(range(256), range(8)):
        cpu, m = call(raw, 0xa667, {0x6878: gear, 0x0748: item, 0x74: 0}, y=item)
        assert m[0x6878] == gear | (1 << item)
        assert m[0x0748] == 255
        equipment += 1
    result['equipment_commit_cases'] = equipment
    result['equipment_commit_limit'] = 'Actual commit entry A667, excluding physical contact/history; region-specific item0 branch atA257 is separate/unresolved.'
    tanks = []
    for current, maximum in itertools.product([0, 1, 249, 250, 251, 254, 255], repeat=2):
        cpu, m = call(raw, 0xdd97, {0x6879: current, 0x687a: maximum}, a=5)
        assert m[0x6879] == min(255, current + 5)
        assert m[0x687a] == min(255, maximum + 5)
        tanks.append(cpu.processorCycles)
    result['missile_tank_cases'] = len(tanks)
    result['missile_tank_cycles'] = [min(tanks), max(tanks)]
    result['passed'] = True
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k not in ['jump_reference_traces', 'scope']}))


if __name__ == '__main__':
    main()
