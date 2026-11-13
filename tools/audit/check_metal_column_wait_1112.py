"""Check original NMI acknowledgment and host column continuation in memory."""
from collections import Counter
from itertools import product
import argparse
import json
from pathlib import Path

import check_metal_head_bridge_1112 as Head
import compose_metal_column_wait_1112 as Compose

Flower, M = Head.Flower, Head.M


def donor_acknowledgment():
    donor = Flower.Compose.Source.Donor
    cpu = donor.machine()
    memory = cpu.memory
    memory.regs[6:8] = [0, 1]
    memory.map()
    cpu.pc, cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = 0xba86, 0x52, 4, 0, 0x21, 224
    # Original terminator queued at index zero. Avoid re-entering the donor
    # foreground frame inside NMI, as when its foreground routine is busy.
    memory[0x80], memory[0xed], memory[0xee], memory[0x30] = 0, 0, 1, 0x80
    cpu.step()
    cpu.step()
    assert cpu.pc == 0xba86 and memory[0xed] == 0
    cpu.nmi()
    hits = Counter()
    for _ in range(20000):
        if cpu.pc == 0xba86 and cpu.sp == 224:
            break
        if cpu.pc in (0xfcfd, 0xd7da, 0xd872, 0xd876):
            hits[f'{cpu.pc:04x}'] += 1
        assert memory[cpu.pc], hex(cpu.pc)
        cpu.step()
    else:
        raise AssertionError(('Original donor NMI bound', hex(cpu.pc)))
    assert all(hits[k] == 1 for k in ('fcfd', 'd7da', 'd872', 'd876')), hits
    assert (memory[0xed], memory[0xee]) == (1, 0)
    cpu.step()
    cpu.step()
    assert (cpu.pc, cpu.a, cpu.x, cpu.y, cpu.p & 0xcf) == (0xba8a, 1, 4, 0, 1)
    return dict(original_NMI_hits=dict(hits), queue_read_index=memory[0xed],
                queue_write_index=memory[0xee], original_resume_PC=hex(cpu.pc))


def fixture(seed, *, world=1245, current=0x47, prev_delta=255, control=0):
    model = M.fork(seed)
    model.raw_page(2, 2)
    M.put(model, CurrentBankC=2)
    state = model.ram[2]
    for at, value in ((0x480, world & 255), (0x498, world >> 8),
                      (0x733, 127), (0x71c, current), (0x558, prev_delta),
                      (0x31, control), (0xed, 0), (0x43b, 0), (0x83f, 0)):
        state[at] = value
    return model


def continuation(parent, candidate):
    _, labels = Flower.Compose.inputs()
    count = Counter()
    for world, current, delta, p in product((119, 120, 255, 256, 1245, 1253, 4095),
                                            (0, 1, 0x46, 0x47), (0, 1, 255),
                                            (0x20, 0x21, 0x60, 0xa1)):
        old = fixture(parent, world=world, current=current, prev_delta=delta, control=0x80)
        new = fixture(candidate, world=world, current=current, prev_delta=delta, control=0x80)
        old.ram[2][0xed] = 1
        a = Head.call(old, labels['Ms_BC04'], 3, p=p)
        b = Head.call(new, labels['Ms_BC04'], 3, p=p)
        assert all(a[key] == b[key] for key in ('A', 'X', 'Y', 'P')), (world, current, delta, p, a, b)
        assert old.ram[2][0xed] == 1 and new.ram[2][0xed] == 0
        assert (old.ram[2][:0xed] == new.ram[2][:0xed]
                and old.ram[2][0xee:0x1000] == new.ram[2][0xee:0x1000]), (world, current, delta, p)
        assert old.rawtags == new.rawtags and old.chr_latches == new.chr_latches
        count['original_acknowledged_AXYP_and_state_pairs'] += 1
        count['real_source_column_handoffs'] += new.ram[2][0x83f] == 1

    stuck = fixture(parent)
    try:
        Head.call(stuck, labels['Ms_BC04'], 3, p=0x21, limit=300)
    except AssertionError as error:
        assert error.args[0][0] == 'CPU bound' and error.args[0][1] in ('0xb0a3', '0xb0a6'), error
    else:
        raise AssertionError('Original host wait did not reproduce')
    fixed = fixture(candidate)
    Head.call(fixed, labels['Ms_BC04'], 3, p=0x21, limit=300)
    assert fixed.ram[2][0x83f] == 1 and fixed.ram[2][0xed] == 0
    assert bytes(fixed.ram[2][0x80:0x83]) == bytes((2, 0x20, 10))
    return dict(count, reproduced_original_wait=True, corrected_host_completed=True)


def interrupts(candidate):
    _, labels = Flower.Compose.inputs()
    native = M.NesMPU
    counts = Counter()
    minimum = 255
    class Trace(native):
        def step(self):
            nonlocal minimum
            if self.memory.rawtags[1] == 3 and 0xb0a3 <= self.pc < 0xb0a8:
                for kind in ('IRQ', 'lagNMI'):
                    clone = M.fork(self.memory)
                    cpu = native(memory=clone, pc=self.pc)
                    for field in ('a', 'x', 'y', 'p', 'sp'):
                        setattr(cpu, field, getattr(self, field))
                    minimum = min(minimum, Head.inject(cpu, native, kind))
                    counts[kind] += 1
            return native.step(self)
    M.NesMPU = Trace
    try:
        Head.call(fixture(candidate), labels['Ms_BC04'], 3, p=0x21)
    finally:
        M.NesMPU = native
    assert counts == {'IRQ': 4, 'lagNMI': 4}
    return dict(cuts=dict(counts), minimum_SP=minimum)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, default=Flower.NIGHTLY)
    args = parser.parse_args()
    parent_raw, parent_layout = Compose.Maturity.compose(args.rom.read_bytes())
    raw, layout = Compose.transform(parent_raw)
    assert Compose.transform(raw, True)[0] == parent_raw
    parent, _ = Head.cold(parent_raw, bytes.fromhex(parent_layout['cookie']))
    candidate, cold = Head.cold(raw, bytes.fromhex(layout['cookie']))
    faults = Head.readback_faults(raw, layout, ((3, 0xb0a3, 0xa9),))
    print('METAL_COLUMN_WAIT ' + json.dumps(dict(layout=layout, cold=cold,
        original_donor=donor_acknowledgment(), continuation=continuation(parent, candidate),
        interrupts=interrupts(candidate), readback_faults=faults), separators=(',', ':')), flush=True)


if __name__ == '__main__':
    main()
