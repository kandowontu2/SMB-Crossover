"""Independent executed classifier ABI; explicit component fixtures, not play."""
from hashlib import sha256
from pathlib import Path
from collections import Counter
import json
from py65.devices.mpu6502 import MPU
import compose_sonic_hidden_heads_1327_1116 as C

COMPOSER = 'ae3eecbb90b95ba3768cea6c1f1fc76baec9aadbd5bed35c48901b1616461865'
ANCHORS = (0xbb39, 0xbb5f, 0xbb9d)


class Memory(bytearray):
    def __init__(self, value):
        super().__init__(value)
        self.writes = []

    def __setitem__(self, address, value):
        self.writes.append((address, value))
        return super().__setitem__(address, value)

    def fixture(self, address, value):
        bytearray.__setitem__(self, address, value)


def machine(raw, cookie):
    assert len(raw) == 2097168
    page = lambda n: raw[1048592+n*1024:1048592+(n+1)*1024]
    memory = bytearray((i*73+19)&255 for i in range(65536))
    memory[0xa000:0xc000] = b''.join(page(n) for n in (*range(321, 328), 330))
    memory[0xd000:0xd400] = page(328)
    memory[0xd400:0xd800] = page(333)
    memory[0xd800:0xdc00] = page(334)
    memory[0xbfe0:0xbff0] = memory[0xdfe0:0xdff0] = cookie
    return MPU(memory=Memory(memory))


def execute(cpu, tile, axis, negative, p, sp, registers, cursor):
    m = cpu.memory
    for address, value in ((0xc104, tile), (0xc0b7, axis),
                           (0xc0b8, negative), (0xc0d5, cursor)):
        m.fixture(address, value)
    m.writes.clear()
    cpu.pc, cpu.sp, cpu.p = 0xbb26, sp, p
    cpu.a, cpu.x, cpu.y = registers
    cpu.processorCycles = 0
    count = 0
    while cpu.pc not in ANCHORS:
        # Both current streams must stay in their two real code owners.
        assert 0xbb26 <= cpu.pc < 0xbb39 or 0xd344 <= cpu.pc < 0xd371
        cpu.step()
        count += 1
        assert count <= 24
    assert not m.writes, 'Classifier must not write stack, RAM, mapper or SMC'
    assert (cpu.x, cpu.y, cpu.sp) == (registers[1], registers[2], sp)
    assert (cpu.p & 0x5c) == (p & 0x5c), 'Preserve V/B/D/I'
    return (cpu.pc, cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp, cpu.processorCycles)


def run():
    assert C.H(Path(C.__file__).read_bytes()) == COMPOSER
    parent = C.ROM.read_bytes()
    assert C.H(parent) == C.PIN
    raw, composition = C.proposal(parent)
    assert C.inverse(raw) == parent and C.H(raw) == C.CANDIDATE
    old, new = machine(parent, C.OLD_COOKIE), machine(raw, C.COOKIE)
    stack_old, stack_new = bytes(old.memory[0x100:0x200]), bytes(new.memory[0x100:0x200])
    assert stack_old == stack_new
    counts = Counter()
    costs = Counter()
    flags = [p for p in range(256) if p & 0x20 and not p & 0x10]
    directions = ((0, 0), (0, 1), (1, 0), (1, 1))
    malformed = [(a, n) for a in (0, 1, 2, 255) for n in (0, 1, 128, 255)
                 if (a, n) not in directions]
    for tile in range(256):
        cases = list(directions)
        if tile in (0x5f, 0x60, 0x67, 0x68):
            cases += malformed
        for axis, negative in cases:
            for p in flags:
                for sp in (0xe0, 1):
                    for x, y in ((0, 0), (0xa5, 0x5a)):
                        registers = ((tile ^ p ^ x)&255, x, y)
                        cursor = (tile*29+p)&255
                        before = execute(old, tile, axis, negative, p, sp, registers, cursor)
                        after = execute(new, tile, axis, negative, p, sp, registers, cursor)
                        if tile not in (0x5f, 0x60):
                            assert before[:-1] == after[:-1], 'Nonhidden AXYP/SP/anchor must be exact'
                            assert after[-1]-before[-1] == 6
                            counts['unchanged_nonhidden'] += 1
                            costs['extra_nonhidden_cycles_6'] += 1
                        else:
                            assert before[0] == 0xbb9d, 'Parent causal rejection remains represented'
                            if (axis, negative) == (1, 1):
                                assert after[0] == 0xbb39
                                # The original stage immediately kills transient A/C/N/Z
                                # with SEC and LDA CursorLo. Verify those actual bytes.
                                assert new.memory[0xbb39:0xbb3d] == bytes.fromhex('38add5c0')
                                new.step()
                                new.step()
                                expected_p = (p & ~0x83) | 1 | (0x80 if cursor&128 else 0) | (2 if cursor == 0 else 0)
                                assert (new.pc, new.a, new.x, new.y, new.p, new.sp) == (0xbb3d, cursor, x, y, expected_p, sp)
                                assert not new.memory.writes
                                counts['hidden_up_to_original_stage'] += 1
                            else:
                                assert after[0] == 0xbb5f
                                counts['hidden_other_to_original_empty'] += 1
                        counts['total'] += 1
    assert bytes(old.memory[0x100:0x200]) == stack_old
    assert bytes(new.memory[0x100:0x200]) == stack_new
    assert not old.memory.writes and not new.memory.writes
    report = dict(passed=True, parent_SHA256=C.PIN, actual_candidate_SHA256=C.CANDIDATE,
                  source_SHA256=C.H(Path(__file__).read_bytes()), composer_SHA256=COMPOSER,
                  cases=dict(counts), costs=dict(costs), valid_processor_flags=len(flags),
                  live_stack_bytes=256, stack_pointer_samples=[0xe0, 1],
                  all_stack_RAM_mapper_SMC_writes=0, original_stage_prefix_executed=True,
                  component_model='Actual leased raw3 A-window and raw2 C-window bytes in a flat6502 '
                      'component map; no mapper writes/interrupts occur in this leaf. Register/context '
                      'fixtures are explicit ABI tests, not natural gameplay or guard/ISR proof.',
                  outputs=0, Mesen=False, natural_gameplay=False, composition=composition)
    report['receipt_SHA256'] = C.H(json.dumps(report, sort_keys=True, separators=(',', ':')).encode())
    return report


if __name__ == '__main__':
    print('RESULT '+json.dumps(run(), separators=(',', ':')), flush=True)
