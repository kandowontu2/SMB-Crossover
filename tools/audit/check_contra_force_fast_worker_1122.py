"""Exercise the proposed private dispatcher against reached native service calls.

The runner explicitly supplies the admitted C2 frame in an isolated pair.
The installed ROM runs the actual stage. A candidate worker runs only in
forked emulator memory and rejoins the actual service caller.
"""

from collections import Counter, defaultdict
from functools import cache
import json
from string import Formatter
from unittest.mock import patch

from py65.assembler import Assembler
from py65.devices.mpu6502 import MPU

import check_contra_force_fixed_layout_1122 as Layout


N, W, Frames = Layout.N, Layout.W, Layout.Frames
C_SHADOW = 0x7DA1
C_MAPPER = 0x5116
R87_ENTRY = 0xB0A9
FAST_ENTRY = 0xDFA6
FAILURE = 0xDF91
NATIVE_C = 0x1F2
TAIL = 0x1F91
COOKIE = 0x1FE0
SMC_START = 0x15A
SMC_END = 0x17B


def assemble(start, source):
    """Assemble this small block in memory with normal 6502 branch encoding."""
    assembler = Assembler(MPU())
    labels = {}
    lines = [line.strip() for line in source.splitlines() if line.strip()]
    pc = start
    for line in lines:
        if line.endswith(':'):
            labels[line[:-1]] = pc
        else:
            replacements = {name: pc for _, name, _, _ in Formatter().parse(line) if name}
            pc += len(assembler.assemble(line.format(**replacements), pc))
    result = bytearray()
    for line in lines:
        if not line.endswith(':'):
            result.extend(assembler.assemble(line.format(**labels), start + len(result)))
    assert start + len(result) == pc
    return bytes(result)


@cache
def worker_code(entry=FAST_ENTRY, bank_selector=None):
    # On entry native87 has saved P,A,X,Y. X holds the byte offset into its
    # three-byte service vectors. Y=2 identifies the Contra Force cohort and
    # the admission gate's successful comparison supplies carry set.
    # Subtraction leaves FD, FE or FF. ROL folds in the range comparison's
    # carry, so only an aligned, in-range service gives FA.
    select_bank = f'JSR ${bank_selector:04X}' if bank_selector is not None else 'INY\nSTY $C2EE'
    code = assemble(entry, '''
        TXA
        LDX #$FF
    subtract:
        INX
        SBC #$03
        BCS ${subtract:04x}
        CPX #$24
        ROL A
        CMP #$FA
        BNE $DF91
        CPX #$06
        BNE ${target:04x}
        LDA $C2DF
        BPL ${target:04x}
        LDA $01F2
        STA $DDD1
    target:
        LDA $DF49,X
        STA $C2EC
        LDA $DF6D,X
        STA $C2ED
        BANK_SELECT
        PLA
        TAY
        PLA
        TAX
        PLA
        PLP
        JMP $CA0B
    '''.replace('BANK_SELECT', select_bank))
    assert len(code) <= COOKIE - (entry & 8191)
    return code


def tail_code():
    # Leave the 18-byte wrapper reservation untouched until admission is proved.
    return bytes.fromhex('4ce3b0') + b'\xff' * (FAST_ENTRY - FAILURE - 3) + worker_code()


def check_decoder(raw):
    # This test stops at the real leaf transport. The paired scene test
    # below additionally executes the workers reached in play.
    start = Layout.Current.P.CHR + (935 + 8) * 1024
    tables = raw[start + 0x1F49:start + TAIL]
    assert len(tables) == 72
    ram = bytearray(65536)
    ram[0xDF49:FAILURE] = tables
    ram[FAILURE:FAILURE + len(tail_code())] = tail_code()
    ram[0x1C1:0x1C5] = bytes((21, 43, 65, 0xB5))  # Native87's saved Y/X/A/P.
    ram[NATIVE_C] = 0xD0
    cpu = MPU(memory=ram)
    passed, rejected = 0, 0
    for owned in (0, 0x80):
        for command in range(256):
            cpu.pc, cpu.sp, cpu.x, cpu.y = FAST_ENTRY, 0xC0, command, 2
            cpu.a, cpu.p, cpu.processorCycles = 0x40, 0x31, 0
            ram[0xC2EC:0xC2EF] = b'\xff' * 3
            ram[0xC2DF], ram[0xDDD1] = owned, 0xFF
            while cpu.pc not in (0xCA0B, 0xB0E3):
                assert cpu.processorCycles < 1200, (owned, command, cpu.pc)
                cpu.step()
            slot, remainder = divmod(command, 3)
            if remainder == 0 and slot < 36:
                assert cpu.pc == 0xCA0B and registers(cpu) == (65, 43, 21, 0xB5, 0xC4)
                assert bytes(ram[0xC2EC:0xC2EF]) == bytes((tables[slot], tables[36 + slot], 3))
                passed += 1
            else:
                assert cpu.pc == 0xB0E3 and cpu.sp == 0xC0
                assert bytes(ram[0xC2EC:0xC2EF]) == b'\xff' * 3
                rejected += 1
            assert ram[0xDDD1] == (0xD0 if owned and command == 18 else 0xFF)
    return dict(valid_inputs=passed, invalid_inputs=rejected)


def registers(cpu):
    return cpu.a, cpu.x, cpu.y, cpu.p | 48, cpu.sp


def caller_boundary(cpu):
    m = cpu.memory
    return_at = 0x105 + cpu.sp
    assert bytes(m[return_at:return_at + 2]) == bytes.fromhex('6d01')
    return (m[return_at + 3] + 256 * m[return_at + 4] + 1, cpu.sp + 9, m[return_at + 2])


def replay(base, captured, *, fast, command=None):
    original = captured.memory
    model = N.fork(original)
    native_c = model[C_SHADOW]
    assert model.rawtags[1:3] == [215, native_c]
    assert captured.pc == R87_ENTRY and captured.y == 2 and model[0x6002] == 31
    cpu = base(memory=model, pc=FAST_ENTRY if fast else R87_ENTRY)
    cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = registers(captured)
    if command is not None:
        cpu.x = command
    # Below saved Y/X/A/P: the worker return to $016E, old A bank,
    # and the actual outer farcall's return word. Its epilogue reloads
    # A and sets N/Z. Stopping before it gives a misleading flags mismatch.
    caller_return, expected_sp, caller_a_bank = caller_boundary(captured)
    assert 0x100 + expected_sp < NATIVE_C
    model[NATIVE_C] = native_c
    if fast:
        cpu.p |= 1  # The admitted native comparison sets C before jumping.
        assert model.ram[2][TAIL:COOKIE] == b'\xff' * (COOKIE - TAIL)
        code = tail_code()
        model.ram[2][TAIL:TAIL + len(code)] = code
        model[C_SHADOW] = 2
        model[C_MAPPER] = 2
    workers = []
    low = cpu.sp
    for _ in range(32000):
        if (cpu.pc, cpu.sp) == (caller_return, expected_sp):
            break
        assert model[cpu.pc], ('Dispatcher BRK', fast, command, hex(cpu.pc), model.rawtags)
        tag = model.rawtags[(cpu.pc - 0x8000) // 8192] if cpu.pc >= 0x8000 else None
        if tag == 2 and cpu.pc == 0xCA0B:
            target_bank = model[0xC2EE]
            if not workers:
                assert target_bank == 3
            workers.append((target_bank, model[0xC2EC] + 256 * model[0xC2ED], *registers(cpu)[:4]))
        low = min(low, cpu.sp)
        cpu.step()
    else:
        raise AssertionError(('Bounded service return', fast, command, hex(cpu.pc)))
    assert cpu.sp == expected_sp and low >= 0x7B
    assert model[0x145] == model.rawtags[1] == caller_a_bank
    assert model[C_SHADOW] == model.rawtags[2] == (2 if fast else native_c)
    if fast:
        model.ram[2][TAIL:TAIL + len(code)] = original.ram[2][TAIL:TAIL + len(code)]
        model[C_SHADOW] = native_c
        model[C_MAPPER] = native_c
    return model, dict(registers=registers(cpu), workers=workers, cycles=cpu.processorCycles, minimum_sp=low)


def compare(old, fast):
    a, old_result = old
    b, new_result = fast
    assert old_result['registers'] == new_result['registers'], (old_result, new_result)
    assert old_result['workers'] == new_result['workers'] and old_result['workers'], (old_result, new_result)
    assert a.rawtags == b.rawtags and a.chr_latches == b.chr_latches
    assert a.vram == b.vram and a.ppuctrl == b.ppuctrl
    for bank, (before, after) in enumerate(zip(a.ram, b.ram, strict=True)):
        if before != after:
            differs = {hex(i): (x, y) for i, (x, y) in enumerate(zip(before, after, strict=True)) if x != y}
            raise AssertionError(('Actual worker RAM differs', bank, differs))
    sp = old_result['registers'][-1]
    exact = (*range(SMC_START), *range(0x101 + sp, 0x800), *range(0x5C00, 0x8000))
    differences = {hex(i): (a[i], b[i]) for i in exact if a[i] != b[i]}
    assert not differences, ('Native gameplay RAM or live stack differs', differences)
    # Identify instruction-parameter publications for later caller
    # qualification. The enclosing old-C slot is an explicit test input.
    return {hex(i): (a[i], b[i]) for i in (*range(SMC_START, SMC_END), 0x179) if a[i] != b[i]}


def rejected(base, captured):
    sp = captured.sp
    y, x, a, p = captured.memory[0x101 + sp:0x105 + sp]
    offsets = (1, 2, 17, 19, 106, 107, 108, 255)
    for command in offsets:
        _, result = replay(base, captured, fast=True, command=command)
        assert not result['workers'], (command, result)
        # The caller's farcall epilogue derives N/Z from the returned A.
        flags = ((p | 48) & ~0x83) | (a & 0x80) | (2 if a == 0 else 0)
        assert result['registers'][:4] == (a, x, y, flags), (command, result)
    return len(offsets)


def observe(m):
    base = N.NesMPU
    samples, deltas = Counter(), Counter()
    latches = defaultdict(set)
    min_sp = 255
    invalid = 0
    phase = 'idle'
    reader, writer = type(m).__getitem__, type(m).__setitem__
    active = None
    watched = {}
    awaiting_return = {}
    next_access = Counter()

    def touch(bus, at, access):
        if bus is not m or active is None or not isinstance(at, int) or at not in watched:
            return
        pc, bank = active
        for origin in watched.pop(at):
            next_access[at, access, bank, pc, origin] += 1

    def read(bus, at):
        touch(bus, at, 'read')
        return reader(bus, at)

    def write(bus, at, value):
        touch(bus, at, 'write')
        return writer(bus, at, value)

    class CPU(base):
        def step(self):
            nonlocal invalid, min_sp, active
            returned = (id(self), self.pc, self.sp, m.rawtags[1])
            for at, origin in awaiting_return.pop(returned, []):
                watched.setdefault(at, []).append(origin)
            if self.pc == R87_ENTRY and m.rawtags[1] == 215 and m[0x6002] == 31:
                offset = self.x
                assert offset % 3 == 0 and offset < 108
                if not invalid:
                    invalid = rejected(base, self)
                old = replay(base, self, fast=False)
                new = replay(base, self, fast=True)
                try:
                    differences = compare(old, new)
                except AssertionError as error:
                    raise AssertionError((phase, offset // 3, *error.args)) from None
                boundary = (id(self), *caller_boundary(self))
                assert boundary not in awaiting_return
                awaiting_return[boundary] = [(int(at, 16), offset // 3) for at in differences]
                for address, pair in differences.items():
                    latches[address].add(pair)
                samples[phase, offset // 3] += 1
                deltas[phase, offset // 3] += old[1]['cycles'] - new[1]['cycles']
                min_sp = min(min_sp, old[1]['minimum_sp'], new[1]['minimum_sp'])
            bank = m.rawtags[(self.pc - 0x8000) // 8192] if self.pc >= 0x8000 else -1
            active = (self.pc, bank)
            try:
                return base.step(self)
            finally:
                active = None

    for phase, pad in (('idle', 0), ('walk', 1)):
        m.controller_pad = pad
        with patch.object(N, 'NesMPU', CPU), patch.object(type(m), '__getitem__', read), patch.object(type(m), '__setitem__', write):
            Frames.frame(m, whole_pass=True)
        Layout.Current.P.empty(m)
        progress = {str(slot): n for (key, slot), n in sorted(samples.items()) if key == phase}
        assert sum(progress.values()) >= 12, progress
        print('PHASE ' + json.dumps(dict(name=phase, calls=progress,
            cycles_removed=sum(v for (key, _), v in deltas.items() if key == phase))), flush=True)
    assert not awaiting_return, awaiting_return
    accesses = Counter()
    for (at, mode, bank, pc, _slot), n in next_access.items():
        accesses[hex(at), mode, bank, hex(pc)] += n
    return dict(calls=sum(samples.values()), invalid_offsets_rejected=invalid, minimum_sp=min_sp,
        smc_publication_differences={k: sorted(v) for k, v in latches.items()},
        first_access_after_public_return=[list(site) + [n] for site, n in sorted(accesses.items())],
        sites_without_a_later_access={hex(at): len(origins) for at, origins in watched.items()},
        leaf_deltas={f'{p}:{s}': d for (p, s), d in sorted(deltas.items())})


def project_frames(seed):
    """Check how the fast workers compose within whole Main updates.

    The model supplies per-call admission and C mapping here. CPU cycles for
    a real native gate, scope and mapper bridge are absent from this result.
    """
    original = N.fork(seed)
    fast = N.fork(seed)
    code = tail_code()
    old_tail = bytes(fast.ram[2][TAIL:TAIL + len(code)])
    active = None
    entered = 0

    def route(model, cpu):
        nonlocal active, entered
        if active is not None:
            pc, sp, bank, native_c, old_slot = active
            if (cpu.pc, cpu.sp, model.rawtags[1]) == (pc, sp, bank):
                assert model[C_SHADOW] == model.rawtags[2] == 2
                model[NATIVE_C] = old_slot
                model[C_SHADOW] = native_c
                model[C_MAPPER] = native_c
                active = None
        if cpu.pc == R87_ENTRY and model.rawtags[1] == 215 and model[0x6002] == 31:
            assert active is None and cpu.x % 3 == 0 and cpu.x < 108 and cpu.y == 2
            pc, sp, bank = caller_boundary(cpu)
            native_c = model[C_SHADOW]
            assert native_c == model.rawtags[2] and 0x100 + sp < NATIVE_C
            active = (pc, sp, bank, native_c, model[NATIVE_C])
            model[NATIVE_C] = native_c
            model[C_SHADOW] = 2
            model[C_MAPPER] = 2
            cpu.p |= 1
            cpu.pc = FAST_ENTRY
            entered += 1

    receipts = []
    for pad, phase in ((0, 'idle'), (1, 'walk')):
        for m in (original, fast):
            m.controller_pad = pad
        entered = 0
        old_cycles = Frames.frame(original, whole_pass=True)
        fast.ram[2][TAIL:TAIL + len(code)] = code
        new_cycles = Frames.frame(fast, observe=route, whole_pass=True)
        fast.ram[2][TAIL:TAIL + len(code)] = old_tail
        assert active is None and entered == 14
        Layout.compare(original, fast)
        receipts.append(dict(phase=phase, calls=entered, original=old_cycles,
            projected_fast=new_cycles, cycles_removed=old_cycles - new_cycles))
    return receipts


def main():
    parent = Layout.Hud.ROM.read_bytes()
    assert Layout.Hud.H(parent) == Layout.Hud.CANDIDATE
    tail = tail_code()
    print('LAYOUT ' + json.dumps(dict(bytes=len(tail), assembled_worker=len(tail) - 21,
          start=hex(FAILURE), end=hex(FAILURE + len(tail)), SHA256=Layout.Hud.H(tail),
          decoder=check_decoder(parent))), flush=True)
    model = Layout.cold(parent)
    for _ in range(4):
        model.controller_pad = 0
        Frames.frame(model, whole_pass=True)
    projection_seed = N.fork(model)
    print('RESULT ' + json.dumps(observe(model), sort_keys=True), flush=True)
    print('PROJECTION ' + json.dumps(project_frames(projection_seed)), flush=True)


if __name__ == '__main__':
    main()
