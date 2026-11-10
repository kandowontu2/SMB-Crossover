"""Source-funded resident-byte proposal for Sonic, entirely in memory.

Retires the user's disabled demo entry/data and factors Sh's carry-only result
patch. This grants neither a Sonic identity nor a cold-loader/router hook.
No file or cartridge is written. All new bytes remain an unpublished proposal.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import re

from py65.assembler import Assembler
import check_remaining_roster_starts_1110 as C
from check_tmnt_render_oa import address, location

R = Path(__file__).resolve().parents[2]
ROM = R / 'build/complete-roster-native-1110/candidate.nes'
PIN = 'c10b7d87f466bf028096bddd33b7ac2baee242870ee83ccc4eebd529af57bd7f'
N = C.I.N
SH_START, SH_NEW, SH_END = 0xabd4, 0xabd5, 0xac15
COOKIE = 0xaa78
STOP = 0x5b00
SOURCE = '''
 php
 pha
 txa
 pha
 tya
 pha
 jsr $a800
 bcc PatchCarry
 ldx #3
PageLoop:
 lda $ac15,x
 sta $014b,x
 lda $ac19,x
 sta $73e4,x
 dex
 bpl PageLoop
 lda #0
 sta $7e05
 lda #1
 sta $73ee
 sta $0146
PatchCarry:
 ; Auth returns C. Every accepted publication opcode preserves that C.
 ; NES2A03 ADC ignores decimal mode; saved caller flags are restored below.
 tsx
 lda $0104,x
 and #$fe
 adc #0
 sta $0104,x
 pla
 tay
 pla
 tax
 pla
 plp
 rts
'''


def digest(data):
    return sha256(data).hexdigest()


def off(bank, pc):
    return 16 + bank * 8192 + (pc & 8191)


def assemble():
    lines = [s.split(';', 1)[0].strip() for s in SOURCE.splitlines()]
    labels = {}
    assembler = Assembler(N.NesMPU(memory=[0] * 65536))
    for _ in range(3):
        pc, data = SH_NEW, bytearray()
        for line in lines:
            if not line:
                continue
            if line.endswith(':'):
                labels[line[:-1]] = pc
                continue
            op, _, operand = line.partition(' ')
            if operand and operand[0].isalpha() and not operand.startswith('a,'):
                operand = '$%04x' % labels.get(operand, pc)
            blob = assembler.assemble(op + (' ' + operand if operand else ''), pc=pc)
            data.extend(blob)
            pc += len(blob)
    assert len(data) == 59 and pc == 0xac10, (len(data), hex(pc))
    assert data[labels['PatchCarry'] - SH_NEW:][:8] == bytes.fromhex('babd040129fe6900')
    return bytes(data), labels


def proposal(base):
    raw = base['raw']
    old = bytes.fromhex(
        '08488a4898482000a89026a203bd15ac9d4b01bd19ac9de473ca10f1'
        'a9008d057ea9018dee738d4601babd04010901d006babd040129fe9d0401'
        '68a868aa682860')
    at = off(65, SH_START)
    assert len(old) == SH_END - SH_START and raw[at:at + len(old)] == old
    body, labels = assemble()
    shifted = b'\xea' + body + b'\xea' * (SH_END - SH_NEW - len(body))
    assert len(shifted) == len(old)
    image = bytearray(raw)
    image[at:at + len(old)] = shifted
    imports = []
    for opcode, expected in ((0x20, [(65, 0xac47)]), (0x4c, [(65, 0xaa8b)])):
        pattern = bytes((opcode, 0xd4, 0xab))
        positions = [m.start() for m in re.finditer(re.escape(pattern), raw[16:1048592])]
        assert [(p // 8192, 0xa000 + p % 8192) for p in positions] == expected
        for p in positions:
            image[16 + p + 1] = SH_NEW & 255
            imports.append(dict(bank=p // 8192, pc=0xa000 + p % 8192))
    assert raw[off(65, 0xac15):off(65, 0xac1d)] == bytes.fromhex('f7f8f90581818182')
    return bytes(image), dict(entry=SH_NEW, body_bytes=len(body),
                             freed_front=[SH_START, SH_NEW], freed_tail=[0xac10, SH_END],
                             imports=imports, labels=labels)


def retired_demo(base):
    raw = base['raw']
    assert address(base, 'DemoEngine') == 0x88d8
    fixed = location(base, 'DemoEngine')
    assert fixed == off(126, 0x88d8)
    stub = bytes.fromhex('8d6a01a9548d6c01a9bc8d6d01a9894caa94')
    assert raw[fixed:fixed + 18] == stub
    # Source ENABLE_CROSSOVER has no vanilla menu or attract branch. Bind the
    # actual compiled UI farcall, zero-result exit and confirmed-start tail.
    source = (R / 'src/bill_native_rare.s').read_text(encoding='utf-8')
    assert '.proc NativeRareGameMenuRoutineCore\n.if ::ENABLE_CROSSOVER\n  farcall CrossoverMenuInput\n  cmp #0\n  beq ExitMenu\n  jmp ChkContinue\n.else' in source
    entry = location(base, 'NativeRareGameMenuRoutineCore')
    compiled = raw[entry:entry + 27]
    assert compiled[:20] == bytes.fromhex('8d6a01a9a88d6c01a9a48d6d01a9c2205a01c900')
    assert compiled[20] == 0xf0 and compiled[22] == 0x4c
    prg = raw[16:1048592]
    # No direct call, jump, data pointer or marshaled address to fixed88D8
    # remains anywhere in current PRG. The only farcall to native9:BC54 is
    # the retired fixed wrapper itself.
    assert bytes.fromhex('d888') not in prg
    far = bytes.fromhex('a9548d6c01a9bc8d6d01a989')
    assert prg.count(far) == 1 and prg.find(far) + 16 == fixed + 3
    start = location(base, 'NativeRareDemoEngine')
    core = location(base, 'NativeRareDemoEngineCore')
    end = location(base, 'NativeRareVictoryMode')
    assert (start, core, end) == (off(9, 0xbc54), off(9, 0xbc60), off(9, 0xbcaa))
    assert raw[start:core] == bytes.fromhex('2060bc209594a9008df67f60')
    assert raw[off(9, 0xbc7f):off(9, 0xbc94)] == bytes.fromhex('0180028141800142c2028041c141c101c101028000')
    assert raw[off(9, 0xbc94):end] == bytes.fromhex('9b1018052c2024155a1020283020108020303001ff00')
    poisoned = bytearray(raw)
    poisoned[fixed:fixed + 18] = b'\x00' * 18
    poisoned[start:end] = b'\x00' * (end - start)
    return bytes(poisoned), dict(fixed=dict(bank=126, start=0x88d8, end=0x88ea, bytes=18),
                                switchable=dict(bank=9, start=0xbc54, end=0xbcaa, bytes=86))


def invoke(model, pc, p):
    cpu = N.NesMPU(memory=model, pc=pc)
    cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = 83, 71, 109, p, 242
    cpu.stPushWord(STOP - 1)
    minimum = cpu.sp
    for _ in range(50000):
        if cpu.pc == STOP:
            break
        assert model[cpu.pc] != 0, ('BRK', hex(cpu.pc), model.rawtags)
        minimum = min(minimum, cpu.sp)
        cpu.step()
    else:
        raise AssertionError(('Gate bound', hex(cpu.pc)))
    assert cpu.sp == 242
    return (cpu.a, cpu.x, cpu.y, cpu.p & 0xef, cpu.sp), minimum


def main():
    raw = ROM.read_bytes()
    assert digest(raw) == PIN
    base = C.W.bundle(raw)
    image, sh = proposal(base)
    poison, demo = retired_demo(base)
    combined = bytearray(image)
    for bank, lo, count in ((126, 0x88d8, 18), (9, 0xbc54, 86)):
        at = off(bank, lo)
        combined[at:at + count] = poison[at:at + count]
    bundles = [base, C.W.bundle(bytes(combined))]
    totals = Counter()
    minimum = 255
    cookie = raw[off(65, COOKIE):off(65, COOKIE) + 16]
    assert cookie[:3] == bytes((0xa7, 36, 1))
    # Full current cookie byte controls, both live/foreign selections and all
    # relevant saved-flag combinations, including decimal-set NES2A03 inputs.
    for owner in (0, 36, 37, 38, 39, 40, 41, 42, 43):
        for corrupt in (None, *range(32)):
            for flags in (0x20, 0x21, 0x61, 0xf9):
                pair = []
                for index, bundle in enumerate(bundles):
                    model = N.fresh(bundle)
                    model.raw_page(1, 193)
                    model.raw_page(2, 2)
                    N.put(model, CurrentBank=193, CurrentBankC=2, SelectedCharacter=owner,
                          ReloadCHRBank=17)
                    for bank in (2, 3):
                        model.ram[bank][0x1fe0:0x1ff0] = cookie
                    if corrupt is not None:
                        model.ram[2 + corrupt // 16][0x1fe0 + corrupt % 16] ^= 1
                    before = (bytes(model[3:11]), bytes(model[0x15a:0x17b]))
                    registers, sp = invoke(model, SH_START if index == 0 else SH_NEW, flags)
                    minimum = min(minimum, sp)
                    assert before == (bytes(model[3:11]), bytes(model[0x15a:0x17b]))
                    assert registers[:3] == (83, 71, 109)
                    assert bool(registers[3] & 1) == (owner == 36 and corrupt is None)
                    pair.append((registers, bytes(model[:0x100]), bytes(model[0x200:0x8000]),
                                 tuple(bytes(bank) for bank in model.ram), tuple(model.rawtags), tuple(model.chr_latches)))
                assert pair[0] == pair[1], (owner, corrupt, flags)
                totals['Sh_actual_header_flags_publication'] += 1
    print('Sh result factoring/header/carry/palette publication:', dict(totals), flush=True)
    inventories = [C.inventory(bundle['raw']) for bundle in bundles]
    assert inventories[0] == inventories[1]
    assert inventories[0]['distinct_named_entries'] == 100 and not inventories[0]['locked']
    print(dict(passed=True, source_proposal_only=True, files_written=0, ROM_written=False,
               parent_SHA256=PIN, memory_only_poison_candidate_SHA256=digest(combined),
               demo=demo, Sh=sh, counts=dict(totals), minimum_SP=minimum,
               complete_menu_entries=100, raw43_admitted=False,
               scope='Disabled demo storage and lossless Sh carry-result factor only. No Sonic cookie, descriptor, cold worker, shared router or gameplay installed.'), flush=True)


if __name__ == '__main__':
    main()
