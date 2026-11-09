"""Qualify exact Getsu no-op vectors and a same-bank cold-data relocation."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path

import check_getsu_owner_vectors_1110 as Cold
import check_getsu_sword_admission_1110 as Sword
from check_mini_funded_actor_1108_v3 import registers, slim_fork
from check_mini_inactive_weapon_gate_irq_1110_v1 import fork


R, S, O, H, N, W, SHA = Sword.R, Sword.S, Sword.O, Sword.H, Sword.N, Sword.W, Sword.SHA
SOURCE = R / 'tools/reference/getsu_fuma_empty_services_1110.s'
SWORD = R / 'build/getsu-sword-idle-1110/proof.json'
SELECTOR = R / 'build/dkjr-native-source-1102-v2/native-combined-selector-v101.s'
RESIDENT = R / 'build/bub-menu-candidate-1102-v2/combined-auth-v83.s'
PIN = 'ba8ea024fc04342273bfe37e044e1d350b97565eca999548ae4d85dce3e1c3b0'
ROWS = (0xb0aa, 0xb0b0, 0xb0b3)
EXISTING = bytes.fromhex('a007b9dca799e0df8810f760')
MOVES = {0xaf19: (0xbd, 0xabb4, 0xabad), 0xaf1e: (0xbd, 0xabbb, 0xabb4),
         0xaf5e: (0xbd, 0xabc2, 0xabbb), 0xaf66: (0xbd, 0xabc8, 0xabc1),
         0xae82: (0x20, 0xa7e4, 0xabc7)}
ALLOWED_NOOP_WRITES = {8, 9, 0x145, 0x7da1, 0x5115, 0x5116, *O.SMC}


def addr(pc):
    return S.FRONT.off(65, pc)


def opcode(op, operand):
    return bytes((op, operand & 255, operand >> 8))


def parent():
    proof = O.Page.load_json(SWORD)
    raw = bytearray(Sword.BASE.read_bytes())
    assert proof['passed'] and proof['parent_SHA256'] == SHA(raw)
    for row in proof['patches']:
        at, old, new = row['file_offset'], bytes.fromhex(row['old_hex']), bytes.fromhex(row['new_hex'])
        assert len(old) == len(new) and raw[at:at + len(old)] == old
        raw[at:at + len(new)] = new
    assert SHA(raw) == PIN == proof['expected_memory_only_SHA256']
    return bytes(raw), proof


def build(output):
    raw, proof = parent()
    old = raw[addr(0xa000):addr(0xa000) + 8192]
    assert old[0x7f2:0x7f8] == bytes.fromhex('ad6a014c40a7')
    assert '.byte $7b,$03' in SELECTOR.read_text()
    assert ' lda DkDescriptorData,y\n sta $dfe0,y\n dey\n bpl :-\n rts' in SELECTOR.read_text()
    assert ' jsr DkCopyDescriptor' in RESIDENT.read_text()
    linked, labels = O.assemble(output, SOURCE.read_text(), (
        ('G', 0xa7e4, 12, ('EMPTY',)), ('C', 0xabc7, 13, ('COLD_COPY',))))
    assert len(linked) == 24 and linked[12:] == EXISTING
    assert labels == {'GfEmptyService': 0xa7e4, 'DkCopyDescriptor': 0xabc7}
    assert linked[:12] == bytes.fromhex('ad0260492ad007ad6a011860')
    assert raw[addr(0xab9d):addr(0xaba4)] == b'\xea' * 7
    assert raw[addr(0xabce):addr(0xabd4)] == b'\xea' * 6
    original_prince = raw[addr(0xaba4):addr(0xabb4)]
    assert original_prince.hex() == 'a72602657b3e759d1533a69f8180f23d'
    compact = bytearray(raw[addr(0xaba4):addr(0xabce)])
    assert compact[17] == 0xa4 and compact[24] == 0xab  # Owner38 table entries.
    compact[17] = 0x9d
    assert len(compact) == 42

    trial, patches = bytearray(raw), []

    def add(pc, original, successor):
        at = addr(pc)
        assert len(original) == len(successor) and trial[at:at + len(original)] == original
        trial[at:at + len(original)] = successor
        patches.append(dict(physical_PRG=65, CPU_half_open=[pc, pc + len(original)], file_offset=at,
                            old_hex=original.hex(), new_hex=bytes(successor).hex()))

    readers = {}
    for pc, (op, previous, next_) in MOVES.items():
        ins = opcode(op, previous)
        uses = [0xa000 + i for i in range(len(old) - 2) if old[i:i + 3] == ins]
        assert uses == [pc], (hex(previous), uses)
        readers[hex(previous)] = [hex(pc)]
        add(pc, ins, opcode(op, next_))
    # The prior direct operands are not used by any other executable bank65
    # opcode. The four tables are consumed through the linked indexed bases.
    for old_data in (0xa7e4, 0xaba4, 0xabb4, 0xabbb, 0xabc2, 0xabc8):
        extra = [(pc, old[pc - 0xa000]) for pc in range(0xa000, 0xbffd)
                 if old[pc - 0xa000 + 1:pc - 0xa000 + 3] == old_data.to_bytes(2, 'little')
                 and old[pc - 0xa000] in (0x20, 0x4c, 0x6c, 0xad, 0xb9, 0xbd, 0xcd, 0xd9, 0xdd)]
        assert extra == [(pc, op) for pc, (op, target, _) in MOVES.items() if target == old_data], (old_data, extra)
    add(0xab9d, raw[addr(0xab9d):addr(0xabd4)], compact + linked[12:] + b'\xea')
    add(0xa7e4, EXISTING, linked[:12])
    kernel = (SWORD.parent / 'kernel.bin').read_bytes()
    assert SHA(kernel) == proof['kernel_SHA256']
    for pc in ROWS:
        index = pc - 0xb08c
        assert index % 3 == 0 and kernel[index:index + 3] == b'\x18\x60\xea'
        add(pc, opcode(0x4c, 0xa740), opcode(0x4c, 0xa7e4))
    assert raw[addr(0xb0a7):addr(0xb0aa)] == raw[addr(0xb0f2):addr(0xb0f5)] == opcode(0x4c, 0xa817)
    assert len(raw) == len(trial) and raw[1048592:] == trial[1048592:]
    return [W.bundle(x) for x in (raw, bytes(trial))], patches, readers


def call(m, pc, a=83, x=71, y=109, status=0x21, watch=None, limit=4_000_000):
    m[0x16a], m[0x16c], m[0x16d] = a, pc & 255, pc >> 8
    O.clear_logs(m)
    c = Sword.cpu_at(m, 0x15a, 193, x, y, status)
    for _ in range(limit):
        if Sword.done(c):
            return c
        if watch:
            watch(c)
        assert m[c.pc], ('Native dispatch BRK', hex(pc), H.point(c))
        c.step()
    raise AssertionError(('Native dispatch bound', pc, H.point(c)))


def clean_writes(m, skip=(), pointer=()):
    skip = set(skip)
    pointer = set(pointer)
    return [(at, 0xa4 if i in pointer and at == 8 and v == 0x9d else v) for i, (at, v) in enumerate(m.writes)
            if i not in skip and not 0x17b <= at < 0x200]


def compare(a, b, log_a, log_b):
    assert registers(a, 0xef) == registers(b, 0xef)
    assert W.memory(a.memory) == W.memory(b.memory)
    assert log_a == log_b and a.memory.ram_writes == b.memory.ram_writes


def captures():
    # Real mapper transactions can be removed only inside a statically known
    # raw42 empty vector, after verifying its entire write extent.
    seen, skipped, pointer = Counter(), [], []
    active = None

    def observe(c):
        nonlocal active
        tag, pc = H.point(c)
        m = c.memory
        if active and c.sp > active[0]:
            start = active[1]
            assert all(at in ALLOWED_NOOP_WRITES or 0x17b <= at < 0x200 for at, _ in m.writes[start:])
            skipped.extend(range(start, len(m.writes)))
            active = None
        if tag == 193:
            if pc in ROWS and m[0x6002] == 42:
                assert active is None
                active = c.sp, len(m.writes)
                seen['empty'] += 1
            if pc in MOVES or pc in (0xa7e4, 0xabc7):
                seen[hex(pc)] += 1
            if pc == 0xaf1c and c.a in (0xa4, 0x9d):
                pointer.append(len(m.writes))
    return observe, seen, skipped, pointer


def transactions(images):
    seen = Counter()
    seeds = {}

    def pair(buses, target, expected_c=None):
        result, logs = [], []
        for m in buses:
            observe, counts, skipped, pointer = captures()
            c = call(m, target, watch=observe)
            if expected_c is not None:
                assert c.p & 1 == expected_c
            result.append(c)
            logs.append(clean_writes(m, skipped, pointer))
            seen.update(counts)
        compare(*result, *logs)
        return result

    for owner in range(37, 43):
        buses = [O.blank(b) for b in images]
        for m in buses:
            O.scene(m, owner)
        pair(buses, O.COLD, 1)
        seeds[owner] = tuple(slim_fork(m) for m in buses)
        pair(buses, O.COLD, 1)
        assert all(not m.ram_writes for m in buses)
        pair(buses, O.AUTH, 1)
        pair(buses, O.RETIRE)
        assert all(O.headers(m)[0][0] == O.headers(m)[1][0] == 0 for m in buses)

    for owner in range(37, 42):
        for source, destination in ((owner, 42), (42, owner)):
            buses = [slim_fork(m) for m in seeds[source]]
            for m in buses:
                O.scene(m, destination)
            pair(buses, O.COLD, 1)
            assert all(O.headers(m) == O.headers(seeds[destination][0]) for m in buses)
    assert all(seen[hex(pc)] for pc in (*MOVES, 0xa7e4, 0xabc7))
    return seeds, dict(reader_sites=seen, cold_and_warm_pairs=12, complete_retire_pairs=6,
                       complete_transition_pairs=10, authentication_pairs=6)


def slots(images, seeds):
    generic = [N.fresh(b) for b in images]
    hist = Counter()
    for owner, pc, value, flags in product((*range(44), 255), ROWS, (0, 83, 255), (0x21, 0x60, 0xa5)):
        pair, logs = [], []
        for seed in seeds.get(owner, generic):
            m = slim_fork(seed)
            N.put(m, SelectedCharacter=owner, NmiDisable=255, OperMode=1, OperMode_Task=3, GameEngineSubroutine=8)
            observe, _, skipped, pointer = captures()
            c = call(m, pc, value, status=flags, watch=observe, limit=24_000)
            pair.append(c)
            logs.append(clean_writes(m, skipped, pointer))
        compare(*pair, *logs)
        hist['Getsu' if owner == 42 else 'foreign', pair[0].processorCycles - pair[1].processorCycles] += 1
    for owner in range(37, 43):
        for bank, poison in product((2, 3), range(16)):
            for pc in ROWS:
                pair, logs = [], []
                for seed in seeds[owner]:
                    m = slim_fork(seed)
                    m.ram[bank][0x1fe0 + poison] ^= 1
                    observe, _, skipped, pointer = captures()
                    c = call(m, pc, watch=observe, limit=24_000)
                    assert not c.p & 1
                    pair.append(c)
                    logs.append(clean_writes(m, skipped, pointer))
                compare(*pair, *logs)
    return dict(direct=[[role, cycles, n] for (role, cycles), n in sorted(hist.items())],
                both_header_poison_pairs=6 * 2 * 16 * len(ROWS))


def gameplay(images):
    buses = [H.prepare(b) for b in images]
    reports = {}
    for phase, key, frames in (('idle', 0, 24), ('walk', 1, 100)):
        savings, bypass = Counter(), Counter()
        for _ in range(frames):
            pair, logs, counts = [], [], []
            for m in buses:
                W.Match.controls(m, key)
                O.clear_logs(m)
                c = Sword.cpu_at(m, S.address(m.bundle, 'GameLoop'))
                watch, seen, skipped, pointer = captures()
                W.run(c, Sword.done, watch)
                pair.append(c)
                logs.append(clean_writes(m, skipped, pointer))
                counts.append(seen['empty'])
            compare(*pair, *logs)
            assert counts[0] == counts[1]
            bypass[counts[0]] += 1
            savings[pair[0].processorCycles - pair[1].processorCycles] += 1
            for m in buses:
                N.consume(m)
            assert W.memory(buses[0]) == W.memory(buses[1])
        reports[phase] = dict(updates=frames, cycles_saved=savings, empty_vectors=bypass)
    return reports


def vectors(images, seeds):
    counts, minimum = Counter(), 255
    for side, image in enumerate(images):
        for owner in range(37, 43):
            for kind in ('cold', 'retire', 'service'):
                m = O.blank(image) if kind == 'cold' else slim_fork(seeds[owner][side])
                O.scene(m, owner)
                cuts = set()

                def observe(c):
                    nonlocal minimum
                    tag, pc = H.point(c)
                    relevant = (pc in MOVES or 0xa7e4 <= pc < 0xa7f0 or 0xabc7 <= pc < 0xabd3
                                or pc in ROWS or 0xaf19 <= pc < 0xaf27 or 0xaf5e <= pc < 0xaf6a)
                    cut = pc, c.sp, c.p & 4, tuple(m.rawtags)
                    if tag != 193 or not relevant or cut in cuts:
                        return
                    cuts.add(cut)
                    for vector in ('FF', 'IRQ'):
                        if vector == 'IRQ' and c.p & 4:
                            continue
                        q = fork(c)
                        minimum = min(minimum, Cold.interrupt(q, vector))
                        counts[kind, vector] += 1

                call(m, {'cold': O.COLD, 'retire': O.RETIRE, 'service': ROWS[0]}[kind], watch=observe)
                assert cuts, (kind, owner, side)
    return dict(cuts=[[kind, vector, n] for (kind, vector), n in sorted(counts.items())], minimum_SP=minimum)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output', type=Path, required=True)
    output = cli.parse_args().output.resolve()
    assert output.is_relative_to(R / 'build')
    output.mkdir(exist_ok=True)
    images, patches, readers = build(output)
    print(json.dumps(dict(SHA256=SHA(images[1]['raw']), readers=readers)), flush=True)
    seeds, cold = transactions(images)
    print(json.dumps(dict(cold=cold)), flush=True)
    direct = slots(images, seeds)
    measured = gameplay(images)
    print(json.dumps(dict(direct=direct, measured=measured)), flush=True)
    irq = vectors(images, seeds)
    result = dict(passed=True, ROM_written=False, renderer_installed=True, parent_SHA256=PIN,
                  expected_memory_only_SHA256=SHA(images[1]['raw']), patches=patches, direct=direct,
                  gameplay=measured, cold_and_retire=cold, vector_checks=irq, source_readers=readers,
                  scope='Exact three physical no-op Getsu vectors under original FarCallCommon ingress. Only original '
                        'compiler-backed CLC/RTS rows bypass private reads. Valid loaded callbacks, foreign fallback, '
                        'cold and retire retain both full headers. Arbitrary direct mutation of immutable loaded code '
                        'under forged matching cookies is outside the supported lifetime.',
                  bindings={p.relative_to(R).as_posix(): SHA(p.read_bytes()) for p in
                            (Path(__file__), SOURCE, SELECTOR, RESIDENT, SWORD, Path(Cold.__file__))})
    (output / 'proof.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(passed=True, SHA256=result['expected_memory_only_SHA256'], irq=irq)))


if __name__ == '__main__':
    main()
