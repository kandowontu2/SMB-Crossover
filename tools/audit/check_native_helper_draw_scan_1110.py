"""Qualify the shared descriptor scan against the installed native routine."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
import subprocess
import tempfile

import check_native_contact_tank_precheck_1110 as C


SOURCE = C.R / 'src/native_platform16_v2.s'
ENTRY, END, BANK = 0xB07C, 0xB0F0, 26
HI, LO, DESCRIPTOR = 0x73C1, 0x73BA, 0x73C8
OLD = bytes.fromhex(
    'a206a9009dc173ca10faade106c9e9d00cad066b8dba73ad076b8dc173'
    'a000a206b50fc901d03bb516c925f004c928d031b51e29e0c940f008'
    'c960d025a954d013bd4506c906f004a954d002a9569de1064cdeb0'
    '9de106a9c89dba73a9739dc173c8cad0bc98f00ba208bd42b09dc873ca10f760'
)


def link(raw, out):
    at = C.at(BANK, ENTRY)
    assert len(OLD) == END - ENTRY and raw[at:at + len(OLD)] == OLD
    with tempfile.TemporaryDirectory(dir=out, prefix='draw-') as name:
        tmp = Path(name)
        src, cfg, obj, binary = (tmp / f'scan.{ext}' for ext in ('s', 'cfg', 'o', 'bin'))
        src.write_text('''HpNativeDrawHi = $73c1
HpNativeDrawLo = $73ba
HpNativeSmallDescriptor = $73c8
.scope HpNativeInitSmallDescriptor
Descriptor = $b042
.endscope
ObjectMetasprite = $06e1
SmPosePtr = $6b06
Enemy_Flag = $10
Enemy_ID = $17
Enemy_State = $1f
Enemy_BoundBoxCtrl = $0646
EnemyMetasprite = $06e2
METASPRITE_SAMUS_BODY = $e9
METASPRITE_PLATFORM_GIRDER_SMALL = $54
METASPRITE_PLATFORM_GIRDER_LARGE = $56
''' + SOURCE.read_text(encoding='utf-8'), encoding='utf-8')
        cfg.write_text('MEMORY { C:start=$B07C,size=116,file=%O; } '
                       'SEGMENTS { CROSSOVER_HELPERS:load=C,type=ro; }\n')
        cc = C.R / 'tools/Windows/cc65/bin'
        subprocess.run([cc / 'ca65.exe', src, '-o', obj], check=True)
        subprocess.run([cc / 'ld65.exe', '-C', cfg, obj, '-o', binary], check=True)
        new = binary.read_bytes()
    assert len(new) == len(OLD)
    patch = dict(physical_PRG=BANK, CPU_half_open=[ENTRY, END], file_offset=at,
                 old_hex=OLD.hex(), new_hex=new.hex(), role='Shared native draw pointer scan')
    return C.install(raw, [patch]), patch


def start(cpu, flags):
    cpu.pc, cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = ENTRY, 123, 19, 217, flags, 241
    cpu.processorCycles = 0
    cpu.stPushWord(C.STOP - 1)


def done(cpu):
    return (cpu.pc, cpu.sp) == (C.STOP, 241)


def populate(memory, slots, player):
    for i, (flag, eid, state, box) in enumerate(slots):
        memory[0x10 + i] = flag
        memory[0x17 + i] = eid
        memory[0x1F + i] = state
        memory[0x646 + i] = box
        memory[0x6E2 + i] = 0x90 + i
    memory[0x6E1] = player
    memory[0x6B06], memory[0x6B07] = 0x72, 0x61
    memory[LO:DESCRIPTOR + 9] = bytes(range(111, 134))


def foreground(before, after):
    cpus = []
    for image in (before, after):
        memory = bytearray(65536)
        at = C.at(BANK, 0xA000)
        memory[0xA000:0xC000] = image[at:at + 8192]
        cpus.append(C.N.NesMPU(memory=memory))
    other = ((0, 0x25, 0x60, 5), (1, 0x28, 0x40, 6), (1, 0x25, 0x60, 5),
             (1, 0x29, 0x40, 5), (2, 0x28, 0x60, 5), (1, 0x25, 0xC0, 6))
    savings = Counter()
    for slot, flag, eid, tag, box in product(range(6), (0, 1, 2, 255), (0, 0x24, 0x25, 0x28, 0x29, 255),
                                            (0, 0x20, 0x40, 0x60, 0x80, 0xA0, 0xC0, 0xE0), (0, 5, 6, 7)):
        case = list(other)
        case[slot] = (flag, eid, tag | (slot + 1), box)
        player, flags = (0xE9 if (flag ^ box) & 1 else 0x54), (0x20, 0x21, 0x60, 0x61)[box & 3]
        states = []
        for cpu in cpus:
            m = cpu.memory
            populate(m, case, player)
            start(cpu, flags)
            C.run(cpu, done)
            states.append((C.registers(cpu), bytes(m[LO:DESCRIPTOR + 9]), bytes(m[0x6E1:0x6E8]),
                           cpu.processorCycles))
        old, new = states
        assert old[:-1] == new[:-1], (case, player, states)
        savings[old[-1] - new[-1]] += 1
    return dict(cases=sum(savings.values()), savings_cycles=dict(savings))


class DrawBus(C.IRQ.Q.DispatchBus):
    watch_draw = False

    def __getitem__(self, address):
        if self.watch_draw and isinstance(address, int):
            assert not LO <= address < DESCRIPTOR + 9, ('Descriptor read during interrupt', self.dispatch_site, address)
        return super().__getitem__(address)

    def __setitem__(self, address, value):
        if self.watch_draw and isinstance(address, int):
            assert not LO <= address < DESCRIPTOR + 9, ('Descriptor write during interrupt', self.dispatch_site, address)
        super().__setitem__(address, value)


def vectors(before, after):
    # The descriptor is shared with menu audio. Check normal game and the
    # roster drawing context separately, at every instruction boundary.
    images = C.Contact.L.bundles(before, after)
    original = C.IRQ.Q.DispatchBus
    C.IRQ.Q.DispatchBus = DrawBus
    try:
        seeds = {owner: [C.cold(image, owner) for image in images] for owner in (0, 2, 25, 39, 41)}
    finally:
        C.IRQ.Q.DispatchBus = original
    lag, normal = C.lag_pcs(seeds[41][0])
    counts = Counter()
    slots = ((1, 0x25, 0x40, 5), (1, 0x28, 0x60, 5), (0, 0x25, 0x60, 6),
             (1, 0x25, 0x40, 6), (2, 0x28, 0x60, 5), (1, 0x25, 0x60, 5))
    for owner, pair in seeds.items():
        finals = []
        for seed in pair:
            m = C.slim_fork(seed)
            m.raw_page(1, BANK | 128)
            C.N.put(m, CurrentBank=BANK | 128, NmiDisable=255, SelectedCharacter=owner)
            populate(m, slots, 0xE9)
            cpu = C.N.NesMPU(memory=m, pc=ENTRY)
            start(cpu, 0x21)

            def observe(z):
                for kind in ('FF', 'IRQ', 'normal'):
                    q = C.fork(z)
                    if kind == 'normal':
                        C.N.put(q.memory, NmiDisable=0)
                    q.memory.watch_draw = True
                    C.IRQ.interrupt(q, kind, lag, normal)
                    counts[kind] += 1

            C.run(cpu, done, observe)
            finals.append(cpu)
        a, b = finals
        C.Contact.A.P.compare_memory(a.memory, b.memory)
        assert C.registers(a) == C.registers(b) and a.processorCycles - b.processorCycles == 25
    return dict(interrupt_boundaries=dict(counts), descriptor_access_during_interrupts=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve()
    assert out.is_relative_to(C.R / 'build') and out != C.R / 'build'
    out.mkdir(exist_ok=True)
    before = C.BASE.read_bytes()
    assert C.M.sha(before) == C.PIN
    after, patch = link(before, out)
    cases = foreground(before, after)
    assert cases == dict(cases=4608, savings_cycles={25: 4608}), cases
    print(cases, flush=True)
    irq = vectors(before, after)
    proof = dict(passed=True, ROM_written=False, parent_SHA256=C.PIN, expected_memory_only_SHA256=C.M.sha(after),
                 patches=[patch], foreground=cases, vectors=irq,
                 bindings={str(p.resolve()): C.M.sha(p.read_bytes()) for p in (Path(__file__), SOURCE, C.BASE)})
    (out / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n', encoding='utf-8')
    print(irq, proof['expected_memory_only_SHA256'], flush=True)


if __name__ == '__main__':
    main()
