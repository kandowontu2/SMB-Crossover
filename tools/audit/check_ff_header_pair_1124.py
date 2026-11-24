"""Compare two-at-a-time validation of the Final Fantasy cache header."""

import argparse
from functools import cache
import json
from unittest.mock import patch

from py65.devices.mpu6502 import MPU

import check_shared_result_copy_1123 as Shared
import profile_roster_empty_draw_1123 as Roster


H = Shared.Prince.H
ROM = Shared.Prince.ROM
PARENT = Shared.Prince.CapSupport.CANDIDATE
CANDIDATES = {
    PARENT: 'e75044b53f561c43e539e3ca1f8a9d83f9ed126f31bea9c8bad3263bc3e4cfff',
    Shared.CANDIDATES[PARENT]: '24465988509464962100afcca7560aeb64d77eae8cb095a973ec1f52dbb25308',
}
CHECK, RESTORE, COOKIE = 0xAA2D, 0xBFF5, 0xAF0E
BANK = 62
OLD = bytes.fromhex('08488a48ada17d48ad0260c916d01da9038da17d8d1651a20fbde0dfdd0eafd00bca10f5'
                    'babd04010901d006babd040129fe9d0401688da17d8d165168aa682860')
FORMS = ('FF FIGHTER', 'FF WHITE MAGE', 'FF BLACK MAGE', 'FF THIEF')
CHECK_SOURCE = '''
 php
 pha
 txa
 pha
 lda CurrentBankC
 pha
 lda SelectedCharacter
 cmp #22
 bne Reject
 lda #3
 sta CurrentBankC
 sta $5116
 ldx #7
ComparePair:
 lda $dfe0,x
 cmp Cookie,x
 bne Reject
 lda $dfe8,x
 cmp CookieHigh,x
 bne Reject
 dex
 bpl ComparePair
 tsx
 lda $0104,x
 ora #1
 bne SaveResult
Reject:
 tsx
 lda $0104,x
 and #$fe
SaveResult:
 sta $0104,x
 pla
 jmp Restore
'''
def offset(address):
    return 16 + BANK * 8192 + (address & 8191)


@cache
def edits():
    fields = dict(CurrentBankC=0x7DA1, SelectedCharacter=0x6002, Cookie=COOKIE,
                  CookieHigh=COOKIE + 8, Restore=RESTORE)
    assemble = Shared.Prince.Reverse.Pipe.Cold.Lift.assemble
    check, _ = assemble(CHECK_SOURCE, fields, CHECK)
    # Move the original STA / restore epilogue byte for byte. The preceding
    # PLA stays in the checker, so both sites fit their original boundaries.
    restore = OLD[-11:]
    assert len(check) == len(OLD) and RESTORE + len(restore) == 0xC000
    return ((offset(CHECK), OLD, check), (offset(RESTORE), b'\xff' * len(restore), restore))


def check_allocation(raw):
    bank = raw[offset(0xA000):offset(0xA000) + 8192]
    assert bank[-14:-11] == b'\x68\x28\x60'  # Previous service ends in RTS.
    assert not any(bank[i] in (0x20, 0x4C) and
                   RESTORE <= int.from_bytes(bank[i+1:i+3], 'little') < 0xC000
                   for i in range(len(bank) - 2))
    bundle = Roster.W.Symbols.bundle()
    for rows, symbol in ((192, 'RdaLowerBankTable'), (32, 'RdaUpperRawBankTable')):
        at = Roster.W.location(bundle, symbol)
        assert all(tag & 127 != BANK for tag in raw[at:at + rows]), symbol


def compose(raw):
    expected = CANDIDATES[H(raw)]
    check_allocation(raw)
    image = bytearray(raw)
    for at, before, after in edits():
        assert image[at:at + len(before)] == before
        image[at:at + len(after)] = after
    image = bytes(image)
    assert H(image) == expected
    return image


def inverse(image):
    assert H(image) in CANDIDATES.values()
    raw = bytearray(image)
    for at, before, after in edits():
        assert raw[at:at + len(after)] == after
        raw[at:at + len(before)] = before
    raw = bytes(raw)
    assert CANDIDATES[H(raw)] == H(image)
    return raw


def component_controls(raw, image):
    machines = [MPU(memory=bytearray(65536)) for _ in range(2)]
    header = raw[offset(COOKIE):offset(COOKIE) + 16]
    for cpu, cartridge in zip(machines, (raw, image), strict=True):
        cpu.memory[0xA000:0xC000] = cartridge[offset(0xA000):offset(0xA000) + 8192]
    tests = [(22, header, p) for p in range(256)]
    tests.extend((22, header[:i] + bytes((header[i] ^ d,)) + header[i + 1:], (17 * i + d) & 255)
                 for i in range(16) for d in range(1, 256))
    tests.extend((owner, header, owner ^ 0x31) for owner in range(256) if owner != 22)
    cycle_pairs = []
    for owner, value, flags in tests:
        outcomes, cycles = [], []
        expected = owner == 22 and value == header
        for cpu in machines:
            cpu.memory[0xDFE0:0xDFF0] = value
            cpu.memory[0x6002] = owner
            cpu.memory[0x7DA1] = cpu.memory[0x5116] = 221
            cpu.pc, cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = CHECK, 0x81, 0x76, 0x24, flags, 214
            cpu.stPushWord(0x5AFF)
            start = cpu.processorCycles
            for _ in range(130):
                if cpu.pc == 0x5B00:
                    break
                cpu.step()
            else:
                raise AssertionError(('Cookie checker did not return', owner, value.hex()))
            outcomes.append((cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp, cpu.memory[0x7DA1], cpu.memory[0x5116]))
            cycles.append(cpu.processorCycles - start)
        assert outcomes[0] == outcomes[1] == (0x81, 0x76, 0x24, (flags & 0xFE) | 0x30 | expected,
                                               214, 221, 221), (owner, value.hex(), flags, outcomes)
        if expected:
            cycle_pairs.append(cycles)
    assert len({tuple(row) for row in cycle_pairs}) == 1
    return dict(cases=len(tests), successful_cycles=cycle_pairs[0])


def linked_controls(raw, image):
    slots = {name: (21, i) for i, name in enumerate(FORMS)}
    b = Roster.W.Symbols.bundle()
    with patch.dict(Roster.ROSTER, slots):
        for name in FORMS:
            pair = [Roster.start(cartridge, b, name) for cartridge in (raw, image)]
            times = {}
            for phase, pad, count in (('standing', 0, 18), ('walking', 1, 22), ('jump', 0x81, 1),
                                      ('air', 1, 17), ('attack', 0x40, 1), ('release', 0, 16)):
                total = [0, 0]
                for _ in range(count):
                    for i, model in enumerate(pair):
                        total[i] += Roster.B.main_step(model, pad)[0]
                    Shared.Linked.compare(*pair, name)
                times[phase] = (count, (total[0] - total[1]) / count)
            print(json.dumps(dict(character=name, updates_and_cycles_saved=times), separators=(',', ':')), flush=True)


def interrupt_controls(image):
    with patch.dict(Roster.ROSTER, {'FF FIGHTER': (21, 0)}):
        model = Roster.start(image, Roster.W.Symbols.bundle(), 'FF FIGHTER')
    cuts = {}

    class Observe:
        def run(self, cpu, stop):
            model.combined_terminal = stop
            for _ in range(180000):
                if (cpu.pc, cpu.sp) == stop:
                    return
                pc = cpu.pc
                if model.rawtags[1] == BANK | 128 and (CHECK <= pc < CHECK + len(OLD) or RESTORE <= pc < 0xC000):
                    key = pc, cpu.p & 4
                    if key not in cuts:
                        cuts[key] = Shared.Linked.Existing.clone(cpu)
                assert model[pc]
                cpu.step()
            raise AssertionError('Final Fantasy logical update did not return')

    Roster.B.main_step(model, 0, Observe())
    assert any(where == RESTORE for where, _ in cuts)
    result = Shared.Linked.Existing.interrupts(cuts)
    assert all(result['returns'].get(name) for name in ('IRQ', 'busyNMI'))
    print(json.dumps(result, separators=(',', ':')), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--component', action='store_true')
    mode.add_argument('--interrupts', action='store_true')
    args = parser.parse_args()
    raw = ROM.read_bytes()
    image = compose(raw)
    assert inverse(image) == raw
    print(H(image), json.dumps(component_controls(raw, image)), flush=True)
    if args.interrupts:
        interrupt_controls(image)
    elif not args.component:
        linked_controls(raw, image)
