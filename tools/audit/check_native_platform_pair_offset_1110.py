"""Qualify the resident platform box offset at the native collision call."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path

import check_native_platform_collision_dispatch_1110_v1 as Platform
import check_native_enemy_ordinary_dispatch_irq_1110 as IRQ
import check_mini_movement_prefix_1110 as Motion
from check_mini_funded_actor_1108_v3 import install, registers, run
from check_mini_inactive_weapon_gate_irq_1110_v1 import fork


P, N, R = Platform.P, Platform.N, Platform.R
BASE = R / 'build/mini-shared-game-loop-tail-native-1110/candidate.nes'
PIN = '29aa4f8df07425dfe6dcdaaa431421c78347adbca5979c332edce69c79367cf5'
PROFILE = R / 'build/mini-dd-clear-and-nmi-profile-1110/capture/instruction-sample.json'
OBJECT = R / 'src/object.s'
TABLE = R / 'tools/reference/native_enemy_pair_offsets_1110.s'
START, LEAF, JOIN = 0xB453, 0xB472, 0xB476
CORE = 0x9512


def span(raw, bank, pc, expected):
    at = 16 + 8192 * bank + (pc & 8191)
    assert raw[at:at + len(bytes.fromhex(expected))].hex() == expected, (bank, hex(pc))
    return at


def linked(raw):
    old, new = '8a204d9b', 'bcd098b8'  # LDY PairOffsets,X; CLV
    at = span(raw, 0, LEAF, old)
    span(raw, 126, 0x98D0, '04080c1014181c')
    span(raw, 126, 0x9B3A, 'ada005c9f0b009a4a488d004a5bdc9d060')
    span(raw, 126, 0x9B4D, '0a0a186904a8ada105290fc90f60')
    span(raw, 126, CORE, 'a2008409a901850ab95806dd5806')
    span(raw, 0, 0xB461, 'b517c924d006b51faa206db4203a9bb014')
    span(raw, 0, JOIN, 'b5be85038a4820129568aa90032063b9a60d60')
    bank = raw[16:16 + 8192]
    assert bank.count(bytes.fromhex('204d9b')) == bank.count(bytes.fromhex('206db4')) == 1
    source = OBJECT.read_text(encoding='utf-8')
    assert 'lda BalPlatformAlignment' in source and 'sty BalPlatformAlignment' in source
    assert 'PairOffsets:\n' in TABLE.read_text(encoding='utf-8')
    row = dict(physical_PRG=0, CPU_half_open=[LEAF, JOIN], file_offset=at, old_hex=old, new_hex=new)
    return install(raw, [row]), row


def fixture(seed, owner, slot, mate, kind, nibble, timer, flags, contact):
    cpu = Platform.actor_setup(seed, owner, int(owner == 4), kind, 0, 'contact', timer, flags)
    m = cpu.memory
    cpu.pc, cpu.x = START, slot
    N.put(m, ObjectOffset=slot, Enemy_OffscreenBits=nibble)
    for i in {slot, mate}:
        for name, value in (('Enemy_ID', kind), ('Enemy_State', 0xff if i != slot else mate if kind == 0x24 else 0),
                            ('Enemy_X_Position', 110), ('Enemy_Y_Position', 184), ('Enemy_Y_HighPos', 1),
                            ('Enemy_Flag', 1), ('Enemy_PageLoc', 0)):
            m[P.address(m.bundle, name) + i] = value
        at = P.address(m.bundle, 'BoundingBox_UL_Corner') + 4 * (i + 1)
        m[at:at + 4] = bytes((108, 184, 141, 196) if contact else (160, 170, 192, 182))
    return cpu


def foreground(before, after):
    seeds = [P.fixture(P.bundle(raw), 0, False, False) for raw in (before, after)]
    counts = Counter()
    for owner, slot, kind, nibble, timer, flags, contact in product(
            (0, 4, 10, 13, 25, 38, 41), range(6), (0x24, 0x25, 0x28), (0, 15, 255),
            (0, 1), (0x21, 0x65), (False, True)):
        mate = (slot + 2) % 6 if kind == 0x24 else slot
        pair = [fixture(seed, owner, slot, mate, kind, nibble, timer, flags, contact) for seed in seeds]
        visits = [0, 0]
        for i, cpu in enumerate(pair):
            def see(z):
                if Platform.point(z) == (128, LEAF):
                    assert 0 <= z.x <= 5
                    visits[i] += 1

            run(cpu, Platform.end, see)
        a, b = pair
        assert visits[0] == visits[1] == (0 if timer else 2 if kind == 0x24 else 1)
        assert Platform.state(a) == Platform.state(b), (owner, slot, mate, kind, nibble, timer, flags, contact)
        saved = a.processorCycles - b.processorCycles
        assert saved == visits[0] * 26, (saved, visits)
        counts[kind, visits[0], saved] += 1
    return dict(cases=sum(counts.values()), grouped=[[*k, v] for k, v in sorted(counts.items())])


def vectors(before, after):
    seeds = Motion.cold_seeds(before, after)
    lag, normal = IRQ.lag_pcs(seeds[41][0])
    counts = Counter()
    minimum = 255
    for owner, kind, nibble, contact in product(seeds, (0x24, 0x25, 0x28), (0, 15), (False, True)):
        pair = [fixture(seed, owner, 4, 1 if kind == 0x24 else 4, kind, nibble, 0, 0x21, contact)
                for seed in seeds[owner]]
        for cpu in pair:
            run(cpu, lambda z: Platform.point(z) == (128, JOIN))
        a, b = pair
        assert a.y == b.y and a.x == b.x and a.sp == b.sp
        assert (a.p ^ b.p) & ~0x83 == 0  # The native box entry overwrites carry and NZ.
        assert a.p & 0x40 == b.p & 0x40 == 0
        for interrupt in ('FF', 'IRQ', 'normal'):
            results = [fork(cpu) for cpu in pair]

            def watch(z):
                nonlocal minimum
                minimum = min(minimum, z.sp)

            costs = []
            for cpu in results:
                if interrupt == 'normal':
                    N.put(cpu.memory, NmiDisable=0)
                cpu.memory.writes.clear()
                cpu.memory.ram_writes.clear()
                cpu.memory.ppu_log.clear()
                costs.append(IRQ.interrupt(cpu, interrupt, lag, normal, watch))
            old, new = results
            assert costs[0] == costs[1] and IRQ.hardware(old) == IRQ.hardware(new), (owner, kind, nibble, interrupt)
            for cpu in results:
                run(cpu, Platform.end)
            assert Platform.state(old) == Platform.state(new), (owner, kind, nibble, interrupt)
            assert registers(old, 0xef) == registers(new, 0xef)
            counts[interrupt] += 1
    return dict(paired_resumes=dict(counts), minimum_SP=minimum)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output', type=Path, required=True)
    out = cli.parse_args().output.resolve()
    assert out.is_relative_to(R / 'build') and out != R / 'build'
    out.mkdir(exist_ok=True)
    dest = out / 'proof.json'
    assert not dest.exists()
    before = BASE.read_bytes()
    assert P.sha(before) == PIN
    after, row = linked(before)
    fg = foreground(before, after)
    print(fg, flush=True)
    irq = vectors(before, after)
    profile = json.loads(PROFILE.read_text())['foreground_opcodes']
    calls = profile['0:b472'] // 2
    proof = dict(passed=True, ROM_written=False, parent_SHA256=PIN, expected_memory_only_SHA256=P.sha(after),
                 patches=[row], foreground=fg, vectors=irq, sampled_1460_calls=calls,
                 bindings={str(p.resolve()): P.sha(p.read_bytes()) for p in
                           (Path(__file__), BASE, PROFILE, OBJECT, TABLE, Motion.KERNEL, Path(Motion.__file__))})
    dest.write_text(json.dumps(proof, indent=2) + '\n', encoding='utf-8')
    print(irq, 'sample1460', calls, 'calls', proof['expected_memory_only_SHA256'], flush=True)


if __name__ == '__main__':
    main()
